import concurrent.futures
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.request
import urllib.parse

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECOVERED_GAME = os.path.join(
    WORKSPACE,
    r"recovered_runtime\extracted\files\games\https\h5.bhsg.lintey.com\sglite_web\lite3zbtest",
)
RAW_RESOURCE = os.path.join(WORKSPACE, r"apk_analysis\raw\assets\game\resource")
OUTPUT = os.path.join(WORKSPACE, "local_game")
RESOURCE_BASE = "https://h5.bhsg.lintey.com/sglite_web/lite3zbtest/resource/"
GAME_THEME_URL = (
    "https://h5.bhsg.lintey.com/sglite_web/lite3zbtest/js/"
    "game.thm.min_4113e36a.js"
)


def copy_recovered_web():
    for root, _, files in os.walk(RECOVERED_GAME):
        for filename in files:
            if filename.endswith("#header"):
                continue
            source = os.path.join(root, filename)
            relative = os.path.relpath(source, RECOVERED_GAME)
            target = os.path.join(OUTPUT, relative)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)


def patch_local_index():
    index_path = os.path.join(OUTPUT, "index_bh_lite3zbtest_andr.html")
    with open(index_path, encoding="utf-8") as handle:
        text = handle.read()
    text = text.replace(
        'var agentUrl = "cfgdat.bhsg.lintey.com/sglite_web/agent/lite3zbtest/bh_lite3zbtest_andr/agent.json"',
        'var agentUrl = "./agent.local.json"',
    )
    text = text.replace(
        "xhr.open('GET', getProtocolPrefix() + agentUrl + '?v=' + now, true);",
        "xhr.open('GET', agentUrl + '?v=' + now, true);",
    )
    with open(index_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def unhashed_path(url):
    return re.sub(r"_[0-9a-fA-F]{6,16}(?=\.[^./\\]+$)", "", url)


def download(url, target, retries=3):
    if os.path.isfile(target) and os.path.getsize(target) > 0:
        return "cached", os.path.getsize(target), None
    os.makedirs(os.path.dirname(target), exist_ok=True)
    partial = target + ".part"
    for attempt in range(retries):
        try:
            safe_url = urllib.parse.quote(url, safe=":/?=&%")
            request = urllib.request.Request(safe_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as response, open(partial, "wb") as out:
                shutil.copyfileobj(response, out, length=1024 * 1024)
            os.replace(partial, target)
            return "downloaded", os.path.getsize(target), None
        except Exception as exc:
            if os.path.exists(partial):
                os.remove(partial)
            if attempt + 1 == retries:
                return "failed", 0, str(exc)
            time.sleep(0.4 * (attempt + 1))


def main():
    os.makedirs(OUTPUT, exist_ok=True)
    copy_recovered_web()
    patch_local_index()

    manifest_path = os.path.join(OUTPUT, "resource", "default.res_49784.json")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)

    copied = 0
    copy_bytes = 0
    pending = []
    for item in manifest["resources"]:
        url = item["url"]
        target = os.path.join(OUTPUT, "resource", *url.split("/"))
        if os.path.isfile(target) and os.path.getsize(target) > 0:
            continue
        source = os.path.join(RAW_RESOURCE, *unhashed_path(url).split("/"))
        if os.path.isfile(source):
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            copied += 1
            copy_bytes += os.path.getsize(target)
        else:
            pending.append((RESOURCE_BASE + url, target, url))

    game_theme_target = os.path.join(OUTPUT, "js", "game.thm.min_4113e36a.js")
    if not os.path.isfile(game_theme_target):
        pending.append((GAME_THEME_URL, game_theme_target, "js/game.thm.min_4113e36a.js"))

    print(
        f"copied_from_apk={copied} bytes={copy_bytes} pending_downloads={len(pending)}",
        flush=True,
    )
    lock = threading.Lock()
    progress = {"done": 0, "downloaded": 0, "bytes": 0, "failed": []}

    def worker(task):
        url, target, relative = task
        status, size, error = download(url, target)
        with lock:
            progress["done"] += 1
            if status == "downloaded":
                progress["downloaded"] += 1
                progress["bytes"] += size
            elif status == "failed":
                progress["failed"].append((relative, error))
            if progress["done"] % 250 == 0 or progress["done"] == len(pending):
                print(
                    "progress={}/{} downloaded={} bytes={} failed={}".format(
                        progress["done"],
                        len(pending),
                        progress["downloaded"],
                        progress["bytes"],
                        len(progress["failed"]),
                    ),
                    flush=True,
                )

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(executor.map(worker, pending))

    failed_path = os.path.join(OUTPUT, "download_failures.json")
    with open(failed_path, "w", encoding="utf-8") as handle:
        json.dump(progress["failed"], handle, ensure_ascii=False, indent=2)
    print(f"output={OUTPUT}", flush=True)
    print(f"failures={len(progress['failed'])} report={failed_path}", flush=True)
    return 1 if progress["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
