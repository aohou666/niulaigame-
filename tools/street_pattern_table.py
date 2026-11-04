"""Emit street-fx-table.js preferring PATTERN containers for single-consumer keys.

Priority per original key:
  * single-consumer key with a finished pattern container -> redirect the key to "<key>_pattern_bin"
  * single-consumer key otherwise                         -> the recoloured key container
  * shared key                                            -> the per-hero recolour containers (dispatch),
                                                             because one Qwen pattern pass cannot carry
                                                             different materials for several heroes
"""
import json, sys
from pathlib import Path
import io
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
KIT = ROOT / "outputs" / "fx-handoff-20261102"
GEN = ROOT / "art-migration/generation/fx-batch-recolor-20261103"
PAT = ROOT / "art-migration/generation/fx-qwen-pattern-20261103"
OUT = ROOT / "local_game/street-fx-table.js"

plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
job_by_id = {j["jobId"]: j for j in plan["jobs"]}
by_key = {}
for j in plan["jobs"]:
    by_key.setdefault(j["originalResourceKey"], []).append(j)
shared_keys = {k for k, v in by_key.items() if len({x["heroId"] for x in v}) > 1}

pattern = {}
pman = PAT / "manifest.jsonl"
if pman.exists():
    for line in pman.read_text("utf-8-sig").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("status") == "built":
            pattern[rec["key"]] = rec

resources, redirect, table = [], {}, {}
used_pattern = used_recolor = 0
rejected = []


def pattern_quality(key: str, rec: dict):
    """Reject patterns whose matte/collorisation went wrong, so those keys keep the recolour art."""
    try:
        job = by_key[key][0]
        rel = job["normal"].get("path") or job["normal"]["candidates"][0]
        orig = decode(ROOT / rel)
        new = decode(ROOT / rec["path"])
        oa = np.asarray(Image.open(io.BytesIO(orig["image"])).convert("RGBA"))[..., 3].astype(np.float64)
        arr = np.asarray(Image.open(io.BytesIO(new["image"])).convert("RGBA")).astype(np.float64)
        na, rgb = arr[..., 3], arr[..., :3]
        mass = (na.sum() / oa.sum()) if oa.sum() > 0 else 1.0
        lit = na > 128
        if lit.sum() == 0:
            return False, "empty", mass, 0.0
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])[lit]
        blown = float((lum > 250).mean())
        mean = float(lum.mean())
        # "luminance as alpha" only holds for luminous effects. Solid art (clouds, plaques, dust)
        # gets hollowed into an outline or bleached, so compare how solid each side is.
        def solidity(alpha):
            mask = alpha > 8
            if mask.sum() == 0:
                return 0.0
            return float((alpha[mask] > 230).mean())

        s_orig = solidity(oa)
        s_new = solidity(na)
        hollow = s_orig > 0.25 and s_new < s_orig * 0.6
        ok = (0.70 <= mass <= 1.25) and blown < 0.45 and mean < 236 and not hollow
        return ok, {"mass": round(mass, 3), "blown": round(blown, 3), "meanLum": round(mean, 1),
                    "solidityOrig": round(s_orig, 3), "solidityNew": round(s_new, 3),
                    "hollowed": hollow}, mass, mean
    except Exception as exc:
        return False, {"error": str(exc)[:80]}, 0.0, 0.0

for rec in json.loads((GEN / "keys-manifest.json").read_text("utf-8")):
    key = rec["key"]
    if key in shared_keys:
        continue
    pat = pattern.get(key)
    if pat:
        ok, why, mass, mean = pattern_quality(key, pat)
        if ok:
            resources.append({"name": pat["db"] + "_bin",
                              "url": "/" + pat["path"].replace("local_game/", "", 1)})
            redirect[key + "_bin"] = pat["db"] + "_bin"
            # EZ bundle built by tools/street_pattern_ez.py; the engine prefers it whenever present.
            ez_rel = Path(pat["path"]).with_name(Path(pat["path"]).stem + "_ez.bin")
            if (ROOT / ez_rel).is_file():
                resources.append({"name": pat["db"] + "_ez_bin",
                                  "url": "/" + ez_rel.as_posix().replace("local_game/", "", 1)})
                redirect[key + "_ez_bin"] = pat["db"] + "_ez_bin"
            used_pattern += 1
            continue
        rejected.append({"key": key, "reason": why})
    for variant, v in rec["variants"].items():
        if v.get("status") != "built":
            continue
        resources.append({"name": v["resName"], "url": "/" + v["path"].replace("local_game/", "", 1)})
        redirect[v["redirectFrom"]] = v["resName"]
        used_recolor += 1

for line in (GEN / "manifest.jsonl").read_text("utf-8").splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    job = job_by_id[rec["jobId"]]
    if job["originalResourceKey"] not in shared_keys:
        continue
    for variant in ("normal", "ez"):
        v = rec["variants"].get(variant) or {}
        if v.get("status") != "built":
            continue
        resources.append({"name": v["db"] + "_bin", "url": "/" + v["path"].replace("local_game/", "", 1)})
        if variant == "normal":
            table.setdefault(job["originalResourceKey"], {})[str(rec["heroId"])] = v["db"]
        else:
            table.setdefault(job["originalResourceKey"] + "_ez", {})[str(rec["heroId"])] = job["targetResourceKey"]

resources = sorted({r["name"]: r for r in resources}.values(), key=lambda r: r["name"])
body = ("/* AUTO-GENERATED by tools/street_pattern_table.py -- do not edit by hand.\n"
        f" * resources {len(resources)} | redirects {len(redirect)} | shared keys {len(table)}\n"
        f" * single-consumer keys using PATTERN {used_pattern}, using recolour {used_recolor}\n"
        " */\n"
        "window.StreetFXResources = " + json.dumps(resources, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "window.StreetFXRedirect = " + json.dumps(redirect, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "window.StreetFXBatchTable = " + json.dumps(table, ensure_ascii=False, separators=(",", ":")) + ";\n")
OUT.write_text(body, encoding="utf-8")
print(json.dumps({"out": str(OUT), "resources": len(resources), "redirects": len(redirect),
                  "sharedKeys": len(table), "patternKeys": used_pattern, "recolorContainers": used_recolor,
                  "bytes": len(body)}, ensure_ascii=False))
