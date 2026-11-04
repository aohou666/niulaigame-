"""Restyle the ORIGINAL effect's eight textures into a new material palette, keeping alpha exactly.

The original art already reads as an attack, so its silhouette, motion and timing are kept byte-for-byte
in the alpha channel; only RGB is remapped through a luminance->gradient LUT so the effect changes
material (blue-white energy -> jersey-crimson / ivory pressure) without redrawing the shape.

usage: py street_fx_recolor_regions.py <variant> <tag>
  variant: 'grad'  (smooth gradient map)
           'hard'  (gradient map + posterised, hard-edged bands)
"""
import json, hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode

VARIANT = sys.argv[1]
TAG = sys.argv[2]

# luminance stops -> colour. 0 = darkest, 1 = white-hot core.
PALETTES = {
    # jersey crimson body, ivory-white blast front, warm gold in the mid-tones
    "grad": [(0.00, (18, 0, 6)), (0.18, (74, 6, 16)), (0.40, (156, 16, 28)),
             (0.62, (214, 44, 40)), (0.80, (255, 150, 96)), (0.92, (255, 236, 214)),
             (1.00, (255, 255, 255))],
    # same ramp but with hard-edged banding, closer to flat game-VFX shading
    "hard": [(0.00, (16, 0, 4)), (0.22, (92, 6, 16)), (0.46, (176, 18, 30)),
             (0.66, (226, 58, 46)), (0.84, (255, 178, 120)), (1.00, (255, 250, 240))],
}


def lut(palette):
    xs = np.array([p[0] for p in palette], dtype=np.float32)
    cols = np.array([p[1] for p in palette], dtype=np.float32)
    lum = np.linspace(0, 1, 256, dtype=np.float32)
    out = np.stack([np.interp(lum, xs, cols[:, c]) for c in range(3)], axis=1)
    return out.astype(np.uint8)


def remap(im: Image.Image, table: np.ndarray, hard: bool) -> Image.Image:
    arr = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, a = arr[..., :3], arr[..., 3]
    # luminance weighted toward the bright core so the ramp follows perceived energy
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    lum = np.clip(lum, 0, 1)
    if hard:
        lum = np.round(lum * 6) / 6.0           # seven flat bands
    idx = (lum * 255).astype(np.uint8)
    out = table[idx]
    res = np.dstack([out, a]).astype(np.uint8)
    return Image.fromarray(res, "RGBA")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


table = lut(PALETTES[VARIANT])
hard = VARIANT == "hard"

src_variants = {
    "normal": ROOT / "local_game/resource/assets/effect/common_skill_zhaoyun_01_3bee13d0.bin",
    "ez": ROOT / "local_game/resource/assets/effect/common_skill_zhaoyun_01_ez_77cda8df.bin",
}

for variant_name, path in src_variants.items():
    d = decode(path)
    atlas = Image.open(__import__("io").BytesIO(d["image"])).convert("RGBA")
    outdir = ROOT / f"art-migration/generation/skin-h018-atk-v01-l01-s01-{variant_name}-{TAG}"
    assert not outdir.exists(), f"{outdir} exists; use a new tag"
    outdir.mkdir(parents=True)
    rows = []
    for r in d["atlas"]["SubTexture"]:
        box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
        sprite = atlas.crop(box)
        styled = remap(sprite, table, hard)
        out = outdir / f"region-{r['name'].split()[-1]:>2}.png".replace(" ", "")
        styled.save(out)
        # alpha must be untouched
        assert np.array_equal(np.asarray(sprite)[..., 3], np.asarray(styled)[..., 3]), "alpha changed"
        rows.append({"name": r["name"], "png": out.relative_to(ROOT).as_posix(), "sha256": sha(out)})
    review = {"jobId": "H018-ATK-V01-L01-S01", "variant": variant_name, "reviewed": True,
              "reviewNote": f"{TAG}: 原纹理逐张材质重映射（亮度→渐变 LUT），alpha 与原图逐像素相同。",
              "allowPartial": False, "regions": rows}
    (outdir / "region-map.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{variant_name}: {len(rows)} regions -> {outdir.name}")
print("done")
