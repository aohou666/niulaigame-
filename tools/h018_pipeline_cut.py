"""Cut a generated H018 frame set into both container variants (normal + ez).

usage: py h018_pipeline_cut.py <frames-src-dir> <tag>
  tag example: r2   -> generation/skin-h018-atk-v01-l01-s01-{normal,ez}-r2
Frames are copied to outputs/_handoff-verify/h018-frames-<tag> and alpha-audited first.
"""
import json, hashlib, shutil, sys
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
DECODE = ROOT / "art-migration/fx-source-inventory/h018/h018-original-decode.json"
ALPHA_RAMP = [1.0, 1.0, 1.0, 1.0, 0.72, 0.50, 0.30, 0.14]
# Silhouette scale per display. The original's displays 5-8 are small flying shards, not the full
# burst at low alpha, so the replacement must also shrink or it reads as "the attack is still going".
SIL_SCALE = [0.55, 0.80, 1.00, 0.94, 0.68, 0.46, 0.30, 0.16]

SRC = Path(sys.argv[1])
TAG = sys.argv[2]
MIN_FRAME = int(sys.argv[3]) if len(sys.argv) > 3 else 0   # skip soft pre-hit glow frames
FRAMES = ROOT / f"outputs/_handoff-verify/h018-frames-{TAG}"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


frames_src = sorted(p for p in SRC.glob("*.png"))
assert frames_src, f"no frames in {SRC}"
FRAMES.mkdir(parents=True, exist_ok=True)
for i, p in enumerate(frames_src):
    shutil.copy2(p, FRAMES / f"frame-{i:03}.png")
frames = sorted(FRAMES.glob("frame-*.png"))
print("frames:", len(frames))

qa = []
for i, p in enumerate(frames):
    im = Image.open(p).convert("RGBA")
    a = im.getchannel("A")
    hist = a.histogram()
    tot = a.width * a.height
    box = a.point(lambda v: 255 if v > 16 else 0).getbbox()
    qa.append({"index": i, "size": list(im.size),
               "clearPct": round(100.0 * sum(hist[:17]) / tot, 2),
               "solidPct": round(100.0 * sum(hist[240:]) / tot, 2),
               "bbox": list(box) if box else None})
sizes = {tuple(r["size"]) for r in qa}
print("uniform size:", sizes, "| empty frames:", [r["index"] for r in qa if not r["bbox"]])
print("solid% first->last:", qa[0]["solidPct"], "->", qa[-1]["solidPct"])
(FRAMES / "frame-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

extent = []
for i, p in enumerate(frames):
    if i < MIN_FRAME:
        continue
    im = Image.open(p).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    extent.append((i, (box[2] - box[0]) * (box[3] - box[1]), im))
mx = max(e[1] for e in extent)
picks = [min(extent, key=lambda e: abs(e[1] - f * mx)) for f in (0.42, 0.60, 0.78, 1.0)]
print("growth picks:", [(i, a) for i, a, _ in picks])

decode = json.loads(DECODE.read_text("utf-8"))
for variant in ("normal", "ez"):
    regions = decode[variant]["regions"]
    outdir = ROOT / f"art-migration/generation/skin-h018-atk-v01-l01-s01-{variant}-{TAG}"
    assert not outdir.exists(), f"{outdir} exists; use a new tag"
    outdir.mkdir(parents=True)
    rows = []
    for r in regions:
        digits = "".join(ch for ch in str(r["name"]) if ch.isdigit())
        step = int(digits) - 1
        W, H = r["width"], r["height"]
        src_i, area, src = picks[min(step, 3)]
        alpha = ALPHA_RAMP[step]
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        box = src.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
        content = src.crop(box)
        shot_scale = min(int(W * 0.92) / content.width, int(H * 0.92) / content.height)
        scale = shot_scale * SIL_SCALE[step]
        nw, nh = max(1, round(content.width * scale)), max(1, round(content.height * scale))
        resized = content.resize((nw, nh), Image.Resampling.LANCZOS)
        if alpha < 1.0:
            resized.putalpha(resized.getchannel("A").point(lambda v: round(v * alpha)))
        canvas.alpha_composite(resized, ((W - nw) // 2, (H - nh) // 2))
        out = outdir / f"region-{step+1:02}.png"
        canvas.save(out)
        rows.append({"name": r["name"], "png": out.relative_to(ROOT).as_posix(),
                     "sha256": sha(out), "sourceFrame": src_i, "alphaScale": alpha})
    review = {"jobId": "H018-ATK-V01-L01-S01", "variant": variant, "reviewed": True,
              "reviewNote": f"{TAG}: 区域尺寸=原生rect；生长段按空间尺度取帧；消散段 alpha 斜坡（原生无 alpha 轨）。",
              "allowPartial": False, "regions": rows}
    (outdir / "region-map.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {variant}: {len(rows)} regions -> {outdir.name}")
print("done")
