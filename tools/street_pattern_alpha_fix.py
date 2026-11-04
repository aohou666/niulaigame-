"""Re-normalise the alpha mass of the pattern containers to the original's, without regenerating.

The Qwen pass derives alpha from the generated luminance and then bounds it to the original footprint,
which trims a bit of coverage (median 0.84, p10 0.61). Scaling the alpha channel back to the original's
mass is a pure per-pixel operation on the packed atlas, so it needs no GPU time.

RGB stays untouched: it was already un-premultiplied, so alpha and colour are independent here.
"""
import io, json, sys
import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B

KIT = ROOT / "outputs" / "fx-handoff-20261102"
MAN = ROOT / "art-migration/generation/fx-qwen-pattern-20261103/manifest.jsonl"

plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
by_key = {}
for j in plan["jobs"]:
    by_key.setdefault(j["originalResourceKey"], j)

rows = [json.loads(l) for l in MAN.read_text("utf-8-sig").splitlines() if l.strip()]
fixed = 0
ratios = []
for rec in rows:
    if rec.get("status") != "built":
        continue
    job = by_key[rec["key"]]
    rel = job["normal"].get("path") or job["normal"]["candidates"][0]
    orig = decode(ROOT / rel)
    cur_path = ROOT / rec["path"]
    cur = decode(cur_path)
    oa = np.asarray(Image.open(io.BytesIO(orig["image"])).convert("RGBA"))[..., 3].astype(np.float64)
    atlas = Image.open(io.BytesIO(cur["image"])).convert("RGBA")
    arr = np.asarray(atlas).astype(np.float64)
    na = arr[..., 3]
    if na.sum() <= 0 or oa.sum() <= 0:
        continue
    scale = oa.sum() / na.sum()
    ratios.append(scale)
    if abs(scale - 1.0) < 0.02:
        continue
    arr[..., 3] = np.clip(na * scale, 0, 255)
    fixed_atlas = Image.fromarray(arr.astype(np.uint8), "RGBA")
    blob = cur_path.read_bytes()
    arm = cur["skeleton"]["armature"][0]["name"]
    rebuilt = B.rebuild(blob, fixed_atlas, arm, cur["atlas"].get("name"))
    cur_path.write_bytes(rebuilt)
    chk = decode(cur_path)
    rec["sha256"] = __import__("hashlib").sha256(rebuilt).hexdigest()
    rec["alphaMassScale"] = round(scale, 4)
    rec["alphaMassNormalised"] = True
    rec["armaturePreserved"] = chk["skeleton"]["armature"][0]["name"] == arm
    rec["regions"] = rec.get("regions", [])
    fixed += 1

MAN.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
if ratios:
    arr = np.array(ratios)
    print(json.dumps({"containers": len(rows), "adjusted": fixed,
                      "scaleMedian": round(float(np.median(arr)), 3),
                      "scaleMin": round(float(arr.min()), 3),
                      "scaleMax": round(float(arr.max()), 3)}, ensure_ascii=False))
else:
    print("nothing to do")
