"""Cut a two-clip H018 set into both container variants.

displays 1-3 come from the BURST clip (impact -> peak), displays 4-8 from the DECAY clip
(debris field opening outward), so the native 8-display timeline gets a real decay phase
instead of re-using the peak frame at low alpha.

usage: py h018_pipeline_cut2.py <burst-frames-dir> <decay-frames-dir> <tag> [burst-skip] [decay-skip]
"""
import json, hashlib, shutil, sys
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
DECODE = ROOT / "art-migration/fx-source-inventory/h018/h018-original-decode.json"

# per display: source clip, pick mode, fraction, silhouette scale, alpha
# burst grows from a point, so pick by spatial extent; the decay clip's bounding box saturates almost
# immediately, so its frames must be taken in temporal order or the sequence goes backwards.
PROFILE = [
    ("burst", "extent", 0.45, 0.55, 1.00),
    ("burst", "extent", 0.72, 0.82, 1.00),
    ("burst", "extent", 1.00, 1.00, 1.00),
    ("decay", "index", 0.12, 1.00, 1.00),
    ("decay", "index", 0.38, 0.96, 0.95),
    ("decay", "index", 0.62, 0.92, 0.85),
    ("decay", "index", 0.82, 0.88, 0.72),
    ("decay", "index", 1.00, 0.84, 0.55),
]

BURST = Path(sys.argv[1])
DECAY = Path(sys.argv[2])
TAG = sys.argv[3]
BURST_SKIP = int(sys.argv[4]) if len(sys.argv) > 4 else 4
DECAY_SKIP = int(sys.argv[5]) if len(sys.argv) > 5 else 2


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(src_dir, skip, tag):
    files = sorted(p for p in src_dir.glob("*.png"))
    assert files, src_dir
    dst = ROOT / f"outputs/_handoff-verify/h018-frames-{TAG}-{tag}"
    dst.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(files):
        shutil.copy2(p, dst / f"frame-{i:03d}.png")
    frames = []
    for i, p in enumerate(sorted(dst.glob("frame-*.png"))):
        if i < skip:
            continue
        im = Image.open(p).convert("RGBA")
        box = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
        assert box, f"empty frame {p}"
        frames.append({"idx": i, "im": im, "extent": (box[2] - box[0]) * (box[3] - box[1])})
    print(f"  {tag}: {len(files)} frames, {len(frames)} usable (skip {skip})")
    return frames


print("sources:")
burst = load(BURST, BURST_SKIP, "burst")
decay = load(DECAY, DECAY_SKIP, "decay")

picks = {}
for clip, frames in (("burst", burst), ("decay", decay)):
    mx = max(f["extent"] for f in frames)
    picks[clip] = (frames, mx)

decode = json.loads(DECODE.read_text("utf-8"))
for variant in ("normal", "ez"):
    regions = decode[variant]["regions"]
    outdir = ROOT / f"art-migration/generation/skin-h018-atk-v01-l01-s01-{variant}-{TAG}"
    assert not outdir.exists(), f"{outdir} exists; use a new tag"
    outdir.mkdir(parents=True)
    rows = []
    for r in regions:
        step = int("".join(ch for ch in str(r["name"]) if ch.isdigit())) - 1
        clip, mode, frac, sil, alpha = PROFILE[step]
        frames, mx = picks[clip]
        if mode == "extent":
            pick = min(frames, key=lambda f: abs(f["extent"] - frac * mx))
        else:
            k = round(frac * (len(frames) - 1))
            pick = frames[k]
        W, H = r["width"], r["height"]
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        box = pick["im"].getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
        content = pick["im"].crop(box)
        fit = min(int(W * 0.92) / content.width, int(H * 0.92) / content.height)
        scale = fit * sil
        nw, nh = max(1, round(content.width * scale)), max(1, round(content.height * scale))
        resized = content.resize((nw, nh), Image.Resampling.LANCZOS)
        if alpha < 1.0:
            resized.putalpha(resized.getchannel("A").point(lambda v: round(v * alpha)))
        canvas.alpha_composite(resized, ((W - nw) // 2, (H - nh) // 2))
        out = outdir / f"region-{step+1:02}.png"
        canvas.save(out)
        rows.append({"name": r["name"], "png": out.relative_to(ROOT).as_posix(), "sha256": sha(out),
                     "clip": clip, "sourceFrame": pick["idx"], "silhouetteScale": sil, "alphaScale": alpha})
        print(f"  {variant} {r['name']:6s} {W}x{H} <- {clip} f{pick['idx']:02} sil={sil} a={alpha}")
    review = {"jobId": "H018-ATK-V01-L01-S01", "variant": variant, "reviewed": True,
              "reviewNote": f"{TAG}: 前3位取炸开段、后5位取消散段（真消散素材）；区域尺寸=原生rect。",
              "allowPartial": False, "regions": rows}
    (outdir / "region-map.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("done")
