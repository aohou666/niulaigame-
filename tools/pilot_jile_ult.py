"""鸡·大招 common_skill_pangtong_02: frame-by-frame Qwen edit using (old frame + new portrait) as one
composite reference, then repack into the original 54 display rects (same names/clock/fps).

usage: py pilot_jile_ult.py generate
       py pilot_jile_ult.py pack
"""
from __future__ import annotations
import io, json, sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B
from qwen_edit_two import edit_two

KEY = "common_skill_pangtong_02"
PLAN = json.loads((ROOT / "outputs/fx-handoff-20261102/plan.json").read_text("utf-8-sig"))
JOB = next(j for j in PLAN["jobs"] if j["originalResourceKey"] == KEY)
SRC = ROOT / JOB["normal"]["path"]
OUT = ROOT / "outputs/street-reskin/pilot/jile-ult"
GAME = ROOT / "local_game/assets/street/fx/pilot"
PORTRAIT = ROOT / "local_game/assets/street/characters/024/portrait.png"

IDENTITY = ("the new character from the right reference: a plump yellow bull wearing a chicken hood "
            "(red comb, white feather ruff, black curved horns, black tail feathers), purple gloves, "
            "holding a golden corn cob in one hand and a small neon phone in the other")

CHAR_PROMPT = (
    "Output exactly ONE single image. Image 1 is the old animation frame: keep its exact pose, camera angle, "
    "arm positions, full-body framing and empty black margin. Image 2 is the new character identity only. "
    "Replace the cartoon chicken in image 1 completely with " + IDENTITY + ". Keep the same body pose and "
    "gesture, but face, hood, horns, feathers, gloves and props must be the new character. Do not reproduce "
    "image 2 as a separate figure, do not draw two characters, no split panel, no reference border. Pure black "
    "background, hard-edged stylised game art, no text, no logo, no watermark."
)


def prompt_for(idx: int) -> str:
    if 0 <= idx <= 7:
        return CHAR_PROMPT
    if idx in (8, 9):
        return (
            "Output exactly ONE image. Image 1 is the old effect frame: keep its placement and footprint. Replace "
            "the white egg/eye shape with a golden corn cob and a small purple phone-screen fragment. Image 2 is "
            "the new character identity/palette reference only; do not draw it. No split panel, no border. Pure "
            "black background, hard-edged game VFX, no text.")
    if 10 <= idx <= 19:
        return (
            "Output exactly ONE image. Image 1 is the old explosion frame: keep its exact layout, growth direction "
            "and coverage. Replace it with a neon-violet phone-screen shockwave, cyan equalizer bars and golden corn "
            "kernels bursting outward; white-hot core, purple/cyan rim light, corn-gold debris. Image 2 is the new "
            "character palette/identity reference only; do not draw it. No split panel, no border. Pure black "
            "background, hard-edged game VFX, no text.")
    if idx == 20:
        return ("Output exactly ONE image. Image 1 is the old highlight: keep position and size. Replace it with one "
                "glowing golden corn kernel with a violet phone-screen rim. Image 2 is palette reference only; do not "
                "draw it. No panels/borders, pure black background.")
    if idx == 21:
        return ("Output exactly ONE image. Image 1 is the old hand: keep the same gesture and placement. Replace it "
                "with a purple-gloved bull hand holding a corn cob / phone edge, same angle. Image 2 is identity "
                "reference only; do not draw it. No panels/borders, pure black background, no text.")
    if 22 <= idx <= 33:
        return ("Output exactly ONE image. Image 1 is the old debris frame: keep the same flying directions, density "
                "and coverage. Replace the shards with golden corn kernels, black-and-orange feather blades and cyan "
                "neon signal bars. Image 2 is palette reference only; do not draw it. No panels/borders, pure black "
                "background, no text.")
    if 34 <= idx <= 44:
        return ("Output exactly ONE image. Image 1 is the old compressed pre-impact frame: keep the same shape and "
                "coverage. Replace it with a compressed ring of neon-violet phone light and corn-gold energy, cracked "
                "glass edge. Image 2 is palette reference only; do not draw it. No panels/borders, pure black "
                "background, no text.")
    if idx == 45:
        return ("Output exactly ONE image. Image 1 is the old thin ring: keep the same ring size and placement. Replace "
                "it with a thin cyan phone-screen ring with faint equalizer ticks. Image 2 is palette reference only; "
                "do not draw it. No panels/borders, pure black background, no text.")
    return ("Output exactly ONE image. Image 1 is the old impact frame: keep the same layout and coverage. Replace it "
            "with a white-hot golden corn impact core, violet phone-screen shards and cyan electric arcs. Image 2 is "
            "palette reference only; do not draw it. No panels/borders, pure black background, no text.")


def make_reference(old: Image.Image, portrait: Image.Image, path: Path, tall: bool):
    canvas_w, canvas_h = (768, 512) if tall else (1024, 512)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (16, 20, 26, 255))
    side = canvas_w // 2
    old = old.copy(); old.thumbnail((side - 24, canvas_h - 24), Image.LANCZOS)
    portrait = portrait.copy(); portrait.thumbnail((side - 24, canvas_h - 24), Image.LANCZOS)
    def paste_center(im, x0):
        bg = Image.new("RGBA", im.size, (16, 20, 26, 255)); bg.alpha_composite(im)
        canvas.alpha_composite(bg, (x0 + (side - im.width) // 2, (canvas_h - im.height) // 2))
    paste_center(old, 0); paste_center(portrait, side)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(path)


def size_for(w, h, max_side=640, min_side=256):
    scale = max_side / max(w, h)
    nw, nh = max(min_side, round(w * scale)), max(min_side, round(h * scale))
    return max(64, (nw // 64) * 64), max(64, (nh // 64) * 64)


def generate():
    d = decode(SRC)
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    portrait = Image.open(PORTRAIT).convert("RGBA")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, r in enumerate(d["atlas"]["SubTexture"]):
        box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
        old = atlas.crop(box)
        old_path = OUT / "refs" / f"old{idx:02d}.png"
        if not old_path.exists():
            old_path.parent.mkdir(parents=True, exist_ok=True)
            bg = Image.new("RGBA", old.size, (16, 20, 26, 255)); bg.alpha_composite(old)
            bg.convert("RGB").save(old_path)
        w, h = size_for(r["width"], r["height"])
        out = OUT / f"{idx:02d}.png"
        sec = edit_two(old_path, PORTRAIT, prompt_for(idx), out, (w, h), 202611031500 + idx)
        print(f"[{idx+1}/54] {r['name']} {w}x{h} {sec}s", flush=True)
        rows.append({"index": idx, "region": r["name"], "rect": [r["width"], r["height"]],
                     "alphaMass": None, "image": out.relative_to(ROOT).as_posix(), "seconds": sec})
    # record old alpha masses for packing (computed here so pack is independent)
    for row in rows:
        r = d["atlas"]["SubTexture"][row["index"]]
        a = np.asarray(atlas.crop((r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])))[..., 3].astype(np.float32) / 255.0
        row["alphaMass"] = float(a.sum())
    (OUT / "manifest.json").write_text(json.dumps({"key": KEY, "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def pack():
    manifest = json.loads((OUT / "manifest.json").read_text("utf-8"))
    blob = SRC.read_bytes()
    d = decode(SRC)
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    new_atlas = atlas.copy()
    for row in manifest["rows"]:
        rgb = Image.open(ROOT / row["image"]).convert("RGB")
        # alpha from luminance, crop, resize, normalise mass to the old display
        arr = np.asarray(rgb).astype(np.float32)
        lum = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]) / 255.0
        floor = 0.10 if row["index"] < 8 else 0.035
        a = np.clip((lum - floor) / (1.0 - floor), 0.0, 1.0) ** 0.85
        a_img = Image.fromarray((a * 255).astype(np.uint8), "L")
        mask = np.asarray(a_img) > 8
        ys, xs = np.where(mask)
        if len(xs):
            pad = 4
            box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
                   min(a_img.width, xs.max() + 1 + pad), min(a_img.height, ys.max() + 1 + pad))
            rgb = rgb.crop(box); a_img = a_img.crop(box)
        rgba = Image.merge("RGBA", (*rgb.split(), a_img)).resize((row["rect"][0], row["rect"][1]), Image.Resampling.LANCZOS)
        a2 = np.asarray(rgba)[..., 3].astype(np.float32)
        s = float(a2.sum())
        if s > 1e-3:
            a2 = np.clip(a2 * (row["alphaMass"] * 255.0 / s), 0.0, 255.0)
            rgba = Image.merge("RGBA", (*rgba.split()[:3], Image.fromarray(a2.astype(np.uint8), "L")))
        r = d["atlas"]["SubTexture"][row["index"]]
        new_atlas.paste(rgba, (r["x"], r["y"]))
    arm = d["skeleton"]["armature"][0]
    rebuilt = B.rebuild(blob, new_atlas, arm["name"], d["atlas"].get("name"))
    GAME.mkdir(parents=True, exist_ok=True)
    dst = GAME / f"{KEY}_motif.bin"
    dst.write_bytes(rebuilt)
    chk = decode(dst)
    a_new = (chk["skeleton"]["armature"][0].get("animation") or [{}])[0]
    a_old = (arm.get("animation") or [{}])[0]
    ok = (chk["skeleton"]["armature"][0]["name"] == arm["name"]
          and chk["atlas"].get("name") == d["atlas"].get("name")
          and len(chk["atlas"]["SubTexture"]) == len(d["atlas"]["SubTexture"])
          and a_new.get("duration") == a_old.get("duration")
          and chk["skeleton"].get("frameRate") == d["skeleton"].get("frameRate"))
    print(json.dumps({"key": KEY, "out": dst.relative_to(ROOT).as_posix(), "namesAndClockPreserved": ok,
                      "regions": len(chk["atlas"]["SubTexture"]), "duration": a_new.get("duration"),
                      "fps": chk["skeleton"].get("frameRate")}, ensure_ascii=False))


if __name__ == "__main__":
    generate() if sys.argv[1] == "generate" else pack()
