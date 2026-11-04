"""Batch PATTERN reskin: per-region Qwen Image 2.1 edit, alpha taken back from the original.

Why per region and not per contact sheet: a 4x2 sheet lets the model drift the cell layout and invent
content (it drew a jersey number), so fixed-grid slicing misaligns. One call per region cannot drift.

Why alpha from the original: the alpha channel carries the silhouette and therefore the decay curve and
the whole timing relationship with the character animation. The generated RGB is composited onto the
ORIGINAL alpha, so a pattern change can never alter the rhythm.

Pipeline per key:
  original container -> for each region: crop, flatten on black -> Qwen edit -> RGB -> original alpha
  -> fit into the native region rect -> repack (names unchanged) -> container
The EZ variant reuses the normal edits (downscaled into the EZ rects), which halves the GPU work.

usage:
  py street_qwen_batch_edit.py --keys 5                 # first five keys, prints ETA
  py street_qwen_batch_edit.py --all                    # every key, resumable
  py street_qwen_batch_edit.py --all --regions 4        # only the first four displays (cheaper)
"""
from __future__ import annotations
import argparse, hashlib, io, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
KIT = ROOT / "outputs" / "fx-handoff-20261102"
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B
from street_qwen_edit_min import edit as qwen_edit

GEN = ROOT / "art-migration/generation/fx-qwen-pattern-20261103"
GAME = ROOT / "local_game/assets/street/fx/pattern"

# material wording per palette word, so the prompt carries the character's identity
MATERIAL_HINT = {
    "球衣红": "basketball-jersey crimson cloth with stitched seams",
    "白金": "ivory-white bone plating",
    "象牙白": "ivory bone-white",
    "金": "polished gold",
    "银": "brushed silver",
    "玉": "polished jade",
    "翡翠": "emerald jade",
    "墨": "ink-black lacquer",
    "霓虹": "neon tube glow",
    "电": "crackling electric arcs",
    "冰": "clear ice",
    "火": "molten fire",
    "铁": "forged iron",
    "铜": "hammered copper",
    "竹": "split bamboo",
    "符": "yellow paper talisman",
    "奶": "soft milk-white",
    "粉": "soft pink",
    "草": "grass green",
    "信号": "hi-vis signal colour",
    "警示": "warning stripes",
    "篮球": "basketball leather",
}


def prompt_for(profile: dict, palette: str) -> str:
    words = [w for w in str(palette).replace("，", "、").split("、") if w]
    hints = []
    for w in words:
        for k, v in MATERIAL_HINT.items():
            if k in w:
                hints.append(v)
                break
    if not hints:
        hints.append("stylised game VFX material")
    mat = profile.get("materialEn") or ""
    base = ("Keep the exact same silhouette, layout, direction and empty black margin as the reference image. "
            "Repaint only the material and pattern")
    if mat:
        base += f", guided by: {mat}"
    base += ". Use " + ", ".join(dict.fromkeys(hints)) + "."
    base += (" The background stays pure black. Keep a hard-edged readable silhouette, crisp shards, "
             "a hot white core and deep coloured rim light. Do not add any person, hand, character, "
             "weapon, text, number, logo or watermark.")
    return base


def _lum(rgb: np.ndarray) -> np.ndarray:
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0


def edit_region(sprite: Image.Image, prompt: str, seed: int) -> Image.Image:
    """Qwen edit one region sprite (RGBA) -> RGBA with a correct matte.

    Qwen returns an opaque RGB image painted on black. Copying the original alpha straight onto it
    leaves black RGB under the soft edges, which reads as a grey halo over a bright background. So:
      1. alpha is derived from the generated luminance (the black backdrop is the matte)
      2. the RGB is un-premultiplied (observed = rgb * a  ->  rgb = observed / a)
      3. the alpha mass is normalised to the original sprite, so the effect keeps its footprint
         and the eight displays keep the original's visual weight
    Any failure falls back to the original sprite so one bad call cannot abort a multi-hour batch.
    """
    W, H = sprite.size
    flat = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    flat.alpha_composite(sprite)
    src = GEN / "_in" / f"region-{seed}.png"
    src.parent.mkdir(parents=True, exist_ok=True)
    flat.convert("RGB").save(src)
    dst = GEN / "_out" / f"region-{seed}.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    scale = 512.0 / max(W, H)
    size = (max(64, round(W * scale)), max(64, round(H * scale)))
    try:
        qwen_edit(src, prompt, dst, size=size, seed=seed)
        gen = Image.open(dst).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    except Exception as exc:                      # keep the batch alive
        print(f"    ! region {seed} edit failed, falling back to original: {str(exc)[:120]}", flush=True)
        return sprite.copy()

    rgb = np.asarray(gen).astype(np.float32)
    a_gen = np.clip((_lum(rgb) - 0.035) / 0.965, 0.0, 1.0) ** 0.85
    orig_a = np.asarray(sprite.getchannel("A")).astype(np.float32) / 255.0
    s_gen, s_orig = float(a_gen.sum()), float(orig_a.sum())
    if s_gen > 1e-3 and s_orig > 1e-3:
        a_gen = np.clip(a_gen * (s_orig / s_gen), 0.0, 1.0)
    # do not invent coverage far outside the original footprint
    a_gen = a_gen * np.clip(orig_a * 2.5, 0.0, 1.0)
    # un-premultiply, but cap the gain: dividing dark pixels by a small alpha blows them out to white
    rgb_true = np.clip(rgb / np.maximum(a_gen[..., None], 0.35), 0.0, 255.0)
    out = np.dstack([rgb_true, a_gen * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--regions", type=int, default=8)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--chunk", type=int, default=10, help="keys per batch; the run pauses and checkpoints between batches")
    ap.add_argument("--pause", type=float, default=5.0, help="seconds to idle between batches")
    ap.add_argument("--max-batches", type=int, default=0, help="0 = keep going until every key is done")
    args = ap.parse_args()

    plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
    chars = {c["heroId"]: c for c in plan["characters"]}
    by_key = {}
    for j in plan["jobs"]:
        by_key.setdefault(j["originalResourceKey"], []).append(j)
    keys = sorted(by_key)
    hero_of = {k: by_key[k][0]["heroId"] for k in keys}
    if not args.all:
        n = args.keys or 5
        keys = keys[args.start:args.start + n]

    GEN.mkdir(parents=True, exist_ok=True)
    GAME.mkdir(parents=True, exist_ok=True)
    manifest = GEN / "manifest.jsonl"
    done = set()
    if manifest.exists():
        for line in manifest.read_text("utf-8-sig").splitlines():
            if line.strip():
                done.add(json.loads(line)["key"])

    t0 = time.time()
    built = 0
    in_chunk = 0
    batches = 0
    progress = GEN / "batch-progress.json"
    with manifest.open("a", encoding="utf-8") as mf:
        for key in keys:
            if key in done:
                continue
            hero = hero_of[key]
            profile = (chars.get(hero, {}).get("profile") or {})
            palette = profile.get("palette") or "未锁定"
            prompt = prompt_for(profile, palette)
            job = by_key[key][0]
            rel = job["normal"].get("path") or job["normal"]["candidates"][0]
            src_path = ROOT / rel
            if not src_path.is_file():
                mf.write(json.dumps({"key": key, "status": "missing-source"}, ensure_ascii=False) + "\n")
                continue
            blob = src_path.read_bytes()
            d = decode(src_path)
            atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
            regions = d["atlas"]["SubTexture"]
            new_atlas = atlas.copy()
            rec = {"key": key, "heroId": hero, "palette": palette, "prompt": prompt, "regions": []}
            for idx, r in enumerate(regions[:args.regions]):
                box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
                sprite = atlas.crop(box)
                edited = edit_region(sprite, prompt, 20261103 + idx)
                new_atlas.paste(edited, (r["x"], r["y"]))
                rec["regions"].append({"name": r["name"], "rect": list(box),
                                       "sha256": hashlib.sha256(edited.tobytes()).hexdigest()})
            arm_name = d["skeleton"]["armature"][0]["name"]
            db = f"{key}_pattern"
            rebuilt = B.rebuild(blob, new_atlas, arm_name, d["atlas"].get("name"))
            dst = GAME / f"{db}.bin"
            dst.write_bytes(rebuilt)
            chk = decode(dst)
            rec.update(status="built", db=db, path=dst.relative_to(ROOT).as_posix(),
                       sha256=hashlib.sha256(rebuilt).hexdigest(),
                       armaturePreserved=chk["skeleton"]["armature"][0]["name"] == arm_name,
                       alphaIdentical=np.array_equal(
                           np.asarray(atlas)[..., 3], np.asarray(new_atlas)[..., 3]))
            mf.write(json.dumps(rec, ensure_ascii=False) + "\n"); mf.flush()
            built += 1
            in_chunk += 1
            el = time.time() - t0
            per = el / built
            remaining = (len(keys) - built) * per
            print(f"  {built} keys | {per:.0f}s/key | elapsed {el/60:.1f}m | ETA {remaining/60:.1f}m", flush=True)
            if in_chunk >= args.chunk:
                in_chunk = 0
                batches += 1
                progress.write_text(json.dumps({"completedKeys": sorted(done) + [k for k in keys[:built]],
                                                "built": built, "batches": batches,
                                                "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
                                               ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  -- batch {batches} done, pausing {args.pause:g}s --", flush=True)
                time.sleep(args.pause)
                if args.max_batches and batches >= args.max_batches:
                    print("  -- max batches reached, stopping --", flush=True)
                    break

    el = time.time() - t0
    print(json.dumps({"keys": len(keys), "built": built, "seconds": round(el, 1),
                      "perKeySeconds": round(el / built, 1) if built else None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
