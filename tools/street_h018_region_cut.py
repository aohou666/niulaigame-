"""Cut generated RGBA frames into a container variant's exact region sizes.

Mapping rationale (native impact burst): the original 8 textures play impact -> peak -> decay.
The author workflow only grows to the final shape, so the first four regions take growth frames
picked by spatial extent and the last four re-use the peak with an explicit alpha ramp, which is
the only way to reproduce the native decay (the container has no alpha track).

usage: street_h018_region_cut.py <normal|ez>
"""
import json, hashlib, sys
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
FRAMES = ROOT / "outputs/_handoff-verify/h018-frames"
DECODE = ROOT / "art-migration/fx-source-inventory/h018/h018-original-decode.json"

VARIANT = sys.argv[1] if len(sys.argv) > 1 else "normal"
assert VARIANT in ("normal", "ez"), VARIANT
OUT = ROOT / f"art-migration/generation/skin-h018-atk-v01-l01-s01-{VARIANT}-r1"
ALPHA_RAMP = [1.0, 1.0, 1.0, 1.0, 0.72, 0.50, 0.30, 0.14]


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


frames = sorted(FRAMES.glob("frame-*.png"))
assert len(frames) == 36, len(frames)

extent = []
for i, p in enumerate(frames):
    im = Image.open(p).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    extent.append((i, (box[2] - box[0]) * (box[3] - box[1]), p, im))
mx = max(e[1] for e in extent)
print(f"max bbox area {mx}")

picks = []
for frac in (0.42, 0.60, 0.78, 1.0):
    pick = min(extent, key=lambda e: abs(e[1] - frac * mx))
    picks.append(pick)
print("growth picks:", [(i, area) for i, area, _, _ in picks])

regions = json.loads(DECODE.read_text("utf-8"))[VARIANT]["regions"]
assert len(regions) == 8, len(regions)

OUT.mkdir(parents=True, exist_ok=False)
def step_of(name):
    """元件 N -> N-1. Atlas array order differs between normal and ez, so key by name."""
    digits = "".join(ch for ch in str(name) if ch.isdigit())
    assert digits, name
    n = int(digits) - 1
    assert 0 <= n < 8, name
    return n


rows = []
for r in regions:
    i = step_of(r["name"])
    W, H = r["width"], r["height"]
    src_i, area, path, src = picks[min(i, 3)]
    alpha = ALPHA_RAMP[i]
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    box = src.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    content = src.crop(box)
    maxw, maxh = int(W * 0.92), int(H * 0.92)
    scale = min(maxw / content.width, maxh / content.height)
    nw, nh = max(1, round(content.width * scale)), max(1, round(content.height * scale))
    resized = content.resize((nw, nh), Image.Resampling.LANCZOS)
    if alpha < 1.0:
        resized.putalpha(resized.getchannel("A").point(lambda v: round(v * alpha)))
    canvas.alpha_composite(resized, ((W - nw) // 2, (H - nh) // 2))
    out = OUT / f"region-{i+1:02}.png"
    canvas.save(out)
    rows.append({"name": r["name"], "index": i, "size": [W, H], "scale": round(scale, 4),
                 "sourceFrame": src_i, "alphaScale": alpha,
                 "png": out.relative_to(ROOT).as_posix(), "sha256": sha(out)})
    print(f"  {r['name']:6s} {W}x{H} <- frame{src_i:02} scale={scale:.3f} alpha={alpha}")

review = {
    "jobId": "H018-ATK-V01-L01-S01",
    "variant": VARIANT,
    "reviewed": False,
    "reviewNote": "",
    "allowPartial": False,
    "regions": [{"name": x["name"], "png": x["png"], "sha256": x["sha256"],
                 "sourceFrame": x["sourceFrame"], "alphaScale": x["alphaScale"]} for x in rows],
    "note": "Draft: growth frames by spatial extent for impact/peak; explicit alpha ramp for decay.",
}
(OUT / "region-map.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "selection.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
