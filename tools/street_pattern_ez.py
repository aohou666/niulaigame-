"""Build EZ variants of the PATTERN containers.

The pattern batch only produced normal-resolution containers.  In battle the engine prefers the EZ
bundle whenever `RES.hasRes("<key>_ez_bin")` is true and halves the display scale, so every covered
skill kept showing the ORIGINAL ez art.  This script takes each original EZ container (proven
skeleton/atlas layout + clock), replaces its atlas regions with the matching pattern regions scaled
into the EZ rects, and repacks the bundle byte-for-byte apart from the texture image.  Data /
armature / animation / atlas names stay ORIGINAL, exactly like the key-level recolour containers.

usage:
  py street_pattern_ez.py --limit 3
  py street_pattern_ez.py
"""
from __future__ import annotations
import argparse, hashlib, io, json, struct, sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B

KIT = ROOT / "outputs" / "fx-handoff-20261102"
PAT = ROOT / "art-migration/generation/fx-qwen-pattern-20261103"
GAME = ROOT / "local_game/assets/street/fx/pattern"


def repack_image(blob: bytes, image: Image.Image) -> bytes:
    """Replace only the PNG part of an audited bundle; skeleton/atlas JSON bytes untouched."""
    parts = B.split(blob)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    packed = [parts[0], parts[1], B.pack(blob, buf.getvalue())]
    return blob[:12] + b"".join(struct.pack("<I", len(p)) + p for p in packed)


def build(keys_limit: int = 0):
    plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
    by_key = {}
    for job in plan["jobs"]:
        by_key.setdefault(job["originalResourceKey"], []).append(job)

    records = []
    manifest = PAT / "manifest.jsonl"
    for line in manifest.read_text("utf-8-sig").splitlines():
        if line.strip():
            records.append(json.loads(line))
    if keys_limit:
        records = [r for r in records if r.get("status") == "built"][:keys_limit]

    out_rows = []
    for rec in records:
        key = rec["key"]
        row = {"key": key, "status": "skipped"}
        if rec.get("status") != "built":
            out_rows.append(row)
            continue
        job = by_key[key][0]
        ez_spec = job.get("ez") or {}
        ez_rel = ez_spec.get("path") or next(iter(ez_spec.get("candidates") or []), None)
        if not ez_rel or not (ROOT / ez_rel).is_file():
            row.update(status="missing-ez-source")
            out_rows.append(row)
            continue

        pat_path = ROOT / rec["path"]
        pat = decode(pat_path)
        ez = decode(ROOT / ez_rel)
        pat_atlas = Image.open(io.BytesIO(pat["image"])).convert("RGBA")
        ez_atlas = Image.open(io.BytesIO(ez["image"])).convert("RGBA").copy()
        pat_by_name = {r["name"]: r for r in pat["atlas"]["SubTexture"]}

        replaced = 0
        missing = []
        for region in ez["atlas"]["SubTexture"]:
            src = pat_by_name.get(region["name"])
            if not src:
                missing.append(region["name"])
                continue
            box = (src["x"], src["y"], src["x"] + src["width"], src["y"] + src["height"])
            sprite = pat_atlas.crop(box).resize((region["width"], region["height"]), Image.Resampling.LANCZOS)
            ez_atlas.paste(sprite, (region["x"], region["y"]))
            replaced += 1

        blob = (ROOT / ez_rel).read_bytes()
        rebuilt = repack_image(blob, ez_atlas)
        db = f"{key}_pattern_ez"
        dst = GAME / f"{db}.bin"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(rebuilt)

        chk = decode(dst)
        arm_new = chk["skeleton"]["armature"][0]
        arm_old = ez["skeleton"]["armature"][0]
        a_new = (arm_new.get("animation") or [{}])[0]
        a_old = (arm_old.get("animation") or [{}])[0]
        ok = (arm_new["name"] == arm_old["name"]
              and chk["atlas"].get("name") == ez["atlas"].get("name")
              and len(chk["atlas"]["SubTexture"]) == len(ez["atlas"]["SubTexture"])
              and a_new.get("duration") == a_old.get("duration")
              and chk["skeleton"].get("frameRate") == ez["skeleton"].get("frameRate")
              and not missing)
        row.update(status="built" if ok else "verify-failed",
                   db=db, path=dst.relative_to(ROOT).as_posix(),
                   sha256=hashlib.sha256(rebuilt).hexdigest(),
                   source=ez_rel, replaced=replaced, missing=missing,
                   regions=len(chk["atlas"]["SubTexture"]),
                   armature=arm_new["name"], atlas=chk["atlas"].get("name"),
                   duration=a_new.get("duration"), fps=chk["skeleton"].get("frameRate"))
        out_rows.append(row)

    out = {
        "keys": len(out_rows),
        "built": sum(r["status"] == "built" for r in out_rows),
        "missingEzSource": sum(r["status"] == "missing-ez-source" for r in out_rows),
        "verifyFailed": sum(r["status"] == "verify-failed" for r in out_rows),
        "rows": out_rows,
    }
    (PAT / "ez-build.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False))
    bad = [r for r in out_rows if r["status"] == "verify-failed"]
    if bad:
        print(json.dumps(bad[:3], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    build(args.limit)
