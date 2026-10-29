#!/usr/bin/env python3
"""电脑端离线游戏资源与存档服务器。"""

from __future__ import annotations

import argparse
import json
import os
import base64
import mimetypes
import re
import threading
import time
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit


ROOT = Path(__file__).resolve().parent

TRAIN_RPC_MODULES = {
    "champion", "newChampion", "seasonArena", "spectralTower", "trialBoss", "dojo",
    "teamExpedition", "battleBridge", "risk", "peakWar", "worldKing",
    "raceTower", "stormWar", "eightDiagram", "newSeasonArena",
    "fairArena", "abyssMaze", "abyssMazeHero",
}

# Only actions that change a training run are persisted.  The recovered client
# polls several Get* methods every time a view is laid out; treating those reads
# as writes used to rewrite the whole save hundreds of times while the training
# page was open and made later callbacks race with stale state.
TRAIN_PROGRESS_ACTIONS = {
    "challenge", "freedomchallenge", "highladderchallenge", "joinmatching",
    "championbattle", "mopupchallenge", "sweep", "mopup",
    "knockfloor", "triggerevent", "startgame", "walk", "fight",
    "interact", "passcustoms",
}
TRAIN_NON_MUTATING_ACTIONS = {
    "champion", "refresh", "freedomrefresh", "highladderrefresh",
    "searchteam", "getstormwarplayer",
}


class OfflineHandler(SimpleHTTPRequestHandler):
    server_version = "OfflineReplica/0.17"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    @property
    def save_path(self) -> Path:
        return self.server.save_path  # type: ignore[attr-defined]

    @property
    def config_path(self) -> Path:
        return self.server.config_path  # type: ignore[attr-defined]

    @property
    def catalog_path(self) -> Path:
        return self.server.catalog_path  # type: ignore[attr-defined]

    def send_json(self, value, status=200):
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_json_body(self, max_size=32 * 1024 * 1024):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > max_size:
            raise ValueError("请求大小无效")
        value = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("根节点必须是对象")
        return value

    def read_save(self):
        if not self.save_path.exists():
            return {}
        text = self.save_path.read_text("utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            # Preserve the first complete document if an older dual-port run
            # left a duplicated closing tail. The next atomic write repairs it.
            if error.msg == "Extra data":
                value, _ = json.JSONDecoder().raw_decode(text)
                return value
            raise

    @staticmethod
    def write_atomic(path: Path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp_path, path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            # The launcher script advertises the server root as the website.
            # Serve the actual launcher there instead of a directory listing.
            self.path = "/offline-launcher.html"
            super().do_GET()
            return
        if parsed.path.startswith("/asset-by-key/"):
            key = parsed.path.split("/asset-by-key/", 1)[1]
            match = self.server.asset_key_map.get(key)  # type: ignore[attr-defined]
            if not match:
                self.send_error(404, "resource key not found")
                return
            self.send_response(302)
            self.send_header("Location", "/" + quote(match["path"], safe="/"))
            self.end_headers()
            return
        if parsed.path == "/api/resolve-assets":
            query = parse_qs(parsed.query)
            keys = [value for value in query.get("key", []) if value]
            key_map = self.server.asset_key_map  # type: ignore[attr-defined]
            self.send_json({key: key_map.get(key) for key in keys})
            return
        if parsed.path == "/api/save":
            payload = self.save_path.read_bytes() if self.save_path.exists() else b"null"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path == "/api/train-rpc":
            value = self.read_save()
            if not isinstance(value, dict):
                value = {}
            self.send_json({"ok": True, "training": value.get("training", {})})
            return
        if parsed.path == "/api/config":
            value = json.loads(self.config_path.read_text("utf-8")) if self.config_path.exists() else {}
            self.send_json(value)
            return
        if parsed.path == "/api/runtime-catalog":
            value = json.loads(self.catalog_path.read_text("utf-8")) if self.catalog_path.exists() else {"heroes": [], "skills": [], "skins": [], "equips": []}
            self.send_json(value)
            return
        if parsed.path == "/api/assets":
            query = parse_qs(parsed.query)
            needle = query.get("q", [""])[0].lower()
            page = max(1, int(query.get("page", ["1"])[0]))
            size = min(200, max(20, int(query.get("size", ["80"])[0])))
            files = self.server.asset_catalog  # type: ignore[attr-defined]
            if needle:
                files = [item for item in files if needle in item["path"].lower()]
            start = (page - 1) * size
            self.send_json({"total": len(files), "page": page, "size": size, "pages": max(1, (len(files) + size - 1) // size), "items": files[start:start + size]})
            return
        super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/api/battle-entities":
            try:
                request = self.read_json_body(2 * 1024 * 1024)
                source_entities = request.get("entities") or []
                if not isinstance(source_entities, list) or not source_entities or len(source_entities) > 4:
                    raise ValueError("战斗助战实体数量无效")
                normalized = []
                used_ids = set()
                allowed_types = {4, 5, 7}
                for source in source_entities:
                    if not isinstance(source, dict):
                        raise ValueError("战斗助战实体必须是对象")
                    entity_type = int(source.get("type", 0))
                    entity_id = int(source.get("entityId", 0))
                    code = int(source.get("code", 0))
                    if entity_type not in allowed_types or code <= 0:
                        raise ValueError("不允许的战斗助战实体")
                    if entity_id < 10000 or entity_id > 29999 or entity_id in used_ids:
                        raise ValueError("战斗助战实体编号无效")
                    used_ids.add(entity_id)
                    skill_ids = [int(value) for value in source.get("skillIds", []) if int(value) > 0]
                    if not skill_ids or len(skill_ids) > 16:
                        raise ValueError("战斗助战实体技能无效")
                    attrs = source.get("attr", "{}")
                    if isinstance(attrs, str):
                        attrs_obj = json.loads(attrs)
                    else:
                        attrs_obj = attrs
                    if not isinstance(attrs_obj, dict):
                        raise ValueError("战斗助战实体属性无效")
                    ext = source.get("ext", "{}")
                    if isinstance(ext, str):
                        ext_obj = json.loads(ext)
                    else:
                        ext_obj = ext
                    if not isinstance(ext_obj, dict):
                        raise ValueError("战斗助战实体扩展信息无效")
                    life_max = max(1, int(source.get("lifeMax", attrs_obj.get("2", 1))))
                    normalized.append({
                        "entityId": entity_id,
                        "code": code,
                        # Original SBattleEntity leaves type at zero for magical and
                        # mythical-beast entries; their enclosing SBattleTeam field
                        # determines the category. A non-zero value makes the client
                        # incorrectly resolve them through the hero table.
                        "type": 0,
                        "life": min(life_max, max(0, int(source.get("life", life_max)))),
                        "lifeMax": life_max,
                        "anger": max(0, int(source.get("anger", 0))),
                        "angerMax": max(0, int(source.get("angerMax", 0))),
                        "level": max(1, int(source.get("level", 1))),
                        "dermaCode": max(0, int(source.get("dermaCode", 0))),
                        "trialLevel": max(0, int(source.get("trialLevel", 0))),
                        "raceType": max(1, int(source.get("raceType", 1))),
                        "attr": json.dumps(attrs_obj, ensure_ascii=False, separators=(",", ":")),
                        "skillIds": skill_ids,
                        "ext": json.dumps(ext_obj, ensure_ascii=False, separators=(",", ":")),
                        "pos": max(0, int(source.get("pos", 0))),
                    })
                with self.server.save_lock:  # type: ignore[attr-defined]
                    value = self.read_save()
                    if not isinstance(value, dict):
                        value = {}
                    value["battleEntities"] = normalized
                    self.write_atomic(self.save_path, value)
                self.send_json({"err": 0, "ok": True, "local": True, "entities": normalized})
            except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
                self.send_json({"ok": False, "error": str(error)}, 400)
            return
        if path == "/api/train-rpc":
            try:
                request = self.read_json_body(2 * 1024 * 1024)
                module = str(request.get("module", ""))
                action = str(request.get("action", ""))
                request_data = request.get("data") or {}
                verify_only = bool(request_data.get("__verifyOnly"))
                if module not in TRAIN_RPC_MODULES or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", action):
                    raise ValueError("不允许的历练本地请求")
                with self.server.save_lock:  # type: ignore[attr-defined]
                    value = self.read_save()
                    if not isinstance(value, dict):
                        value = {}
                    training = value.setdefault("training", {})
                    module_state = training.setdefault(module, {"progress": 0, "attempts": 0, "wins": 0, "losses": 0, "claims": {}, "actions": {}, "passed": [], "completedBattles": {}})
                    module_state.setdefault("wins", int(module_state.get("progress", 0)))
                    module_state.setdefault("losses", 0)
                    module_state.setdefault("passed", [])
                    module_state.setdefault("completedBattles", {})
                    if verify_only:
                        self.send_json({"err": 0, "ok": True, "local": True, "verified": True, "module": module, "action": action, "state": module_state, "progressed": False, "firstClaim": False})
                        return
                    lower_action = action.lower()
                    mutating = not lower_action.startswith("get") and lower_action not in TRAIN_NON_MUTATING_ACTIONS
                    progressed = False
                    first_claim = False
                    # Read APIs such as GetBattleRecord and GetOfflineBattleRecord
                    # contain the word "battle" but must never consume an attempt or
                    # advance local progression. Only original gameplay mutations do.
                    prepare_battle = bool(request_data.get("__prepareBattle"))
                    commit_battle = lower_action == "commitbattleresult"
                    if mutating and not commit_battle:
                        module_state["actions"][action] = int(module_state["actions"].get(action, 0)) + 1
                    if prepare_battle:
                        module_state["attempts"] = int(module_state.get("attempts", 0)) + 1
                    elif commit_battle:
                        battle_id = str(request_data.get("battleId", "")).strip()
                        won = bool(request_data.get("won"))
                        completed = module_state["completedBattles"]
                        # Fight result callbacks may be replayed while restoring a
                        # WebView. A battle UUID can advance its mode at most once.
                        if battle_id and battle_id not in completed:
                            completed[battle_id] = {"won": won, "at": int(time.time())}
                            if won:
                                module_state["progress"] = int(module_state.get("progress", 0)) + 1
                                module_state["wins"] = int(module_state.get("wins", 0)) + 1
                                module_state["passed"].append({
                                    "progress": module_state["progress"],
                                    "battleId": battle_id,
                                    "at": int(time.time()),
                                })
                                del module_state["passed"][:-200]
                                progressed = True
                            else:
                                module_state["losses"] = int(module_state.get("losses", 0)) + 1
                            # Bound the idempotency ledger without losing recent fights.
                            if len(completed) > 256:
                                for old_id in list(completed)[:-256]:
                                    completed.pop(old_id, None)
                    elif lower_action in TRAIN_PROGRESS_ACTIONS:
                        module_state["attempts"] = int(module_state.get("attempts", 0)) + 1
                        module_state["progress"] = int(module_state.get("progress", 0)) + 1
                        module_state["wins"] = int(module_state.get("wins", 0)) + 1
                        module_state["passed"].append({"progress": module_state["progress"], "action": action, "at": int(time.time())})
                        del module_state["passed"][:-200]
                        progressed = True
                    if "reward" in lower_action or "achievement" in lower_action:
                        claim_key = str(request_data.get("id", action))
                        first_claim = not bool(module_state["claims"].get(claim_key))
                        module_state["claims"][claim_key] = True
                    if mutating:
                        log = training.setdefault("rpcLog", [])
                        log.append({"module": module, "action": action, "data": request_data})
                        del log[:-200]
                        self.write_atomic(self.save_path, value)
                self.send_json({"err": 0, "ok": True, "local": True, "module": module, "action": action, "state": module_state, "progressed": progressed, "firstClaim": first_claim})
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
                self.send_json({"ok": False, "error": str(error)}, 400)
            return
        if path == "/api/upload":
            try:
                value = self.read_json_body(24 * 1024 * 1024)
                name = re.sub(r"[^A-Za-z0-9._-]", "_", str(value.get("name", "asset.png")))
                if not name or name.startswith("."):
                    raise ValueError("文件名无效")
                raw = str(value.get("data", ""))
                if "," in raw:
                    raw = raw.split(",", 1)[1]
                data = base64.b64decode(raw, validate=True)
                if len(data) > 16 * 1024 * 1024:
                    raise ValueError("文件不能超过16 MB")
                target = ROOT / "admin_uploads" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                self.send_json({"ok": True, "url": "/admin_uploads/" + name, "size": len(data)})
            except Exception as error:
                self.send_json({"ok": False, "error": str(error)}, 400)
            return
        if path not in ("/api/save", "/api/config", "/api/runtime-catalog"):
            self.send_error(404)
            return
        try:
            value = self.read_json_body()
            target = self.save_path if path == "/api/save" else self.config_path if path == "/api/config" else self.catalog_path
            # Startup can issue more than one save/config PUT at once. On
            # Windows all atomic writes share the same .tmp path, so serialize
            # them to prevent intermittent PermissionError/disconnected replies.
            with self.server.save_lock:  # type: ignore[attr-defined]
                self.write_atomic(target, value)
            self.send_json({"ok": True})
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            payload = json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def do_PUT(self):
        self.do_POST()

    def log_message(self, format, *args):
        line = "[%s] %s" % (self.log_date_time_string(), format % args)
        # Logging must not abort a valid resource response on Windows GBK streams.
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(line.encode(encoding, errors="backslashreplace").decode(encoding), flush=True)


def main():
    parser = argparse.ArgumentParser(description="电脑端离线复刻服务器")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--save", type=Path, default=ROOT / "server_data" / "offline-replica-save.json")
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), OfflineHandler)
    server.save_path = args.save.resolve()
    server.config_path = (args.config or args.save.with_name("offline-replica-config.json")).resolve()
    server.catalog_path = args.save.with_name("offline-runtime-catalog.json").resolve()
    server.save_lock = threading.Lock()
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".json", ".fnt", ".ttf", ".mp3", ".dbbin", ".bin"}
    server.asset_catalog = []
    server.asset_key_map = {}
    for folder_name in ("resource", "assets", "admin_uploads", "original_apk_supplement"):
        folder = ROOT / folder_name
        if not folder.exists():
            continue
        for file in folder.rglob("*"):
            if file.is_file() and file.suffix.lower() in extensions:
                rel = file.relative_to(ROOT).as_posix()
                mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                stem = file.stem
                key = re.sub(r"_[0-9a-fA-F]{7,10}$", "", stem)
                item = {"path": rel, "url": "/" + rel, "size": file.stat().st_size, "type": mime, "key": key}
                server.asset_catalog.append(item)
                current = server.asset_key_map.get(key)
                if current is None or (mime.startswith("image/") and not current["type"].startswith("image/")):
                    server.asset_key_map[key] = item
    server.asset_catalog.sort(key=lambda item: item["path"])
    print(f"离线服务器：http://{args.host}:{args.port}/offline-launcher.html", flush=True)
    print(f"电脑端存档：{server.save_path}", flush=True)
    print(f"可视化配置：{server.config_path}", flush=True)
    print(f"美术资源索引：{len(server.asset_catalog)} 份", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
