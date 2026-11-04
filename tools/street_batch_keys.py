"""Build key-level recoloured containers for SINGLE-consumer effect keys.

A key used by exactly one hero does not need per-hero dispatch at all: redirecting the key itself
covers every engine path (pia, target, fly, special controllers). The container keeps the ORIGINAL
data/armature/animation/atlas names, because the engine passes the original key as the armature name;
only the texture pixels change.
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B

KIT = ROOT / "outputs" / "fx-handoff-20261102"
OUTDIR = ROOT / "local_game/assets/street/fx/keys"
GEN = ROOT / "art-migration/generation/fx-batch-recolor-20261103"

plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
chars = {c["heroId"]: c for c in plan["characters"]}

by_key = {}
for j in plan["jobs"]:
    by_key.setdefault(j["originalResourceKey"], []).append(j)

single = {k: v for k, v in by_key.items() if len({x["heroId"] for x in v}) == 1}
print("single-consumer keys:", len(single))

OUTDIR.mkdir(parents=True, exist_ok=True)
rows = []
for key, jobs in sorted(single.items()):
    job = jobs[0]
    palette = (chars.get(job["heroId"], {}).get("profile") or {}).get("palette") or "未锁定"
    lut = B.build_lut(palette)
    rec = {"key": key, "heroId": job["heroId"], "palette": palette, "jobs": [j["jobId"] for j in jobs], "variants": {}}
    for variant, suffix in (("normal", ""), ("ez", "_ez")):
        spec = job.get(variant) or {}
        rel = spec.get("path") or next(iter(spec.get("candidates") or []), None)
        if not rel or not (ROOT / rel).is_file():
            rec["variants"][variant] = {"status": "missing-source"}
            continue
        src = ROOT / rel
        blob = src.read_bytes()
        d = decode(src)
        atlas, same_alpha = B.recolour(d, lut)
        arm = d["skeleton"]["armature"][0]
        old_arm = arm["name"]
        db = f"{key}_streetfx{suffix}"
        rebuilt = B.rebuild(blob, atlas, old_arm, d["atlas"].get("name"))
        dst = OUTDIR / f"{db}.bin"
        dst.write_bytes(rebuilt)
        chk = decode(dst)
        ok = (chk["skeleton"]["armature"][0]["name"] == old_arm
              and chk["atlas"]["name"] == d["atlas"].get("name")
              and len(chk["atlas"]["SubTexture"]) == len(d["atlas"]["SubTexture"]))
        rec["variants"][variant] = {
            "status": "built" if ok and same_alpha else "verify-failed",
            "db": db, "resName": db + "_bin",
            "redirectFrom": key + ("_ez" if suffix else "") + "_bin",
            "path": dst.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(rebuilt).hexdigest(),
            "sourceSha256": hashlib.sha256(blob).hexdigest(),
            "regions": len(chk["atlas"]["SubTexture"]),
            "alphaIdentical": same_alpha, "namePreserved": ok,
        }
    rows.append(rec)

(GEN / "keys-manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
built = sum(1 for r in rows for v in r["variants"].values() if v.get("status") == "built")
bad = [(r["key"], k, v.get("status")) for r in rows for k, v in r["variants"].items() if v.get("status") != "built"]
print(json.dumps({"keys": len(rows), "containersBuilt": built, "problems": bad[:6]}, ensure_ascii=False))
