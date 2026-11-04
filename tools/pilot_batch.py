"""Batch motif reskin: per display region, old frame + hero portrait as two Qwen references.
Frame count, slot rects, armature and clock are preserved. Resumable.

usage:
  py pilot_batch.py --jobs H016-ULT-V01-L01-S01,H054-ULT-V01-L01-S01
  py pilot_batch.py --all --limit 10
"""
from __future__ import annotations
import argparse, io, json, sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B
from qwen_edit_two import edit_two
from street_qwen_edit_min import edit as edit_one

PLAN = json.loads((ROOT / "outputs/fx-handoff-20261102/plan.json").read_text("utf-8-sig"))
JOB_BY_ID = {j["jobId"]: j for j in PLAN["jobs"]}
SPEC_PATH = ROOT / "outputs/street-reskin/motifs/角色母题规格_86.json"
SPEC = {}
if SPEC_PATH.exists():
    SPEC = {int(k): v for k, v in json.loads(SPEC_PATH.read_text("utf-8")).items()}
MANIFEST = ROOT / "art-migration/generation/fx-motif-batch/manifest.jsonl"
CAND = ROOT / "local_game/assets/street/fx/pilot/batch"
WORK = ROOT / "outputs/street-reskin/pilot/batch"
MANIFEST.parent.mkdir(parents=True, exist_ok=True)
CAND.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

# Only these keys have real character frames; every other key is treated as effect-only.
CHAR_KEYS = {"common_skill_pangtong_02"}
# Effect-only motifs must not contain body/pose words, otherwise the model paints a person into the old silhouette.
FX_MOTIF = {
    (1, "普攻"): "红领带鞭、金色指向光、金发丝光，金/白/红",
    (1, "大招"): "领带风暴、巨型宣言光纹、金色指向光、金发丝光，金/红/黑",
    (2, "普攻"): "棕色坨状爆点、炭火油花、金链碎屑，暖橙/炭黑",
    (2, "大招"): "金链旋涡、炭火油花、夜市摊灯影，暖橙/炭黑",
    (11, "普攻"): "游戏机砸击、红色星芒、哨声波，红/白",
    (11, "大招"): "游戏机键位符号、上下左右指示灯、红色冲刺光、哨声波，红/白",
}


def size_for(w, h, max_side=512, min_side=192):
    scale = max_side / max(w, h)
    nw, nh = max(min_side, round(w * scale)), max(min_side, round(h * scale))
    return max(64, (nw // 64) * 64), max(64, (nh // 64) * 64)


def is_character_frame(w: int, h: int) -> bool:
    # Thin tall strips are slashes/beams, not characters: require a real body-sized rect.
    return h > w * 1.5 and w * h >= 5000


def strip_border_bg(im: Image.Image) -> Image.Image:
    """If a character frame came back on a solid coloured backdrop, key it out before alpha."""
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    h, w = arr.shape[:2]
    border = np.concatenate([arr[0, :], arr[-1, :], arr[:, 0], arr[:, -1]], axis=0)
    bg = np.median(border, axis=0)
    if float(bg.max()) < 35:  # already black/transparent
        return im
    dist = np.sqrt(((arr - bg) ** 2).sum(axis=2))
    arr[dist < 42] = 0
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def prompt_for(job: dict, idx: int, region: dict) -> str:
    prof = job.get("profile") or {}
    hero = job.get("name") or job["jobId"]
    spec = SPEC.get(int(job["heroId"]), {})
    motif = spec.get("ult" if job.get("slot") == "大招" else "atk") or prof.get("theme") or "character VFX"
    look = spec.get("props") or ""
    elements = spec.get("nonhuman") or FX_MOTIF.get((int(job["heroId"]), job.get("slot")), motif)
    particles = spec.get("particles") or "光尘、火星"
    colors = f"{spec.get('primary', '')}/{spec.get('secondary', '')}".strip("/")
    forbidden = spec.get("forbidden") or f"old {job.get('originalName', '')} props and palette"
    is_character = job["originalResourceKey"] in CHAR_KEYS and is_character_frame(region["width"], region["height"])
    if is_character:
        return (
            "Output exactly ONE single image. Image 1 is the old animation frame: keep its exact pose, camera, arm "
            "positions and full-body framing. Image 2 is the new character identity: use its outfit, props, materials "
            f"and colours. Replace the old character with {hero} in the same pose. New-asset look: {look}. "
            f"Concrete motif: {motif}. Palette: {colors}. Avoid these old elements: {forbidden}. "
            "2D hand-painted game art, thick dark ink outlines, flat cel shading, warm saturated palette, "
            "yellow-green rim glow. One character only, no split panel, no text, no old character, no background.")
    return (
        "Output exactly ONE single image: an EFFECT-ONLY texture replacement. Image 1 is the old effect frame. "
        "Keep its exact silhouette, layout, scale, position, number of objects and empty black margin; do not add, "
        f"remove or move any shape. Only replace the material/colour/details with these non-human elements: "
        f"{elements}. Particles: {particles}. "
        f"Palette lock: use only {colors} plus white/black highlights; no other hues. Avoid these old elements: {forbidden}. "
        "DO NOT draw any character, person, face, body, hand, finger, hair, costume or portrait. No new object outside "
        "the old silhouette. 2D hand-painted game VFX, thick dark edges, flat cel colours. One image only, no split "
        "panel, no text, no background, no old logo.")


def load_progress():
    done = {}
    if MANIFEST.exists():
        for line in MANIFEST.read_text("utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("status") == "built":
                    done[r["jobId"]] = r
    return done


def run_job(job: dict):
    key = job["originalResourceKey"]
    target = job["targetResourceKey"]
    hero = int(job["heroId"])
    portrait = ROOT / f"local_game/assets/street/characters/{hero:03d}/portrait.png"
    if not portrait.is_file():
        return {"jobId": job["jobId"], "status": "missing-portrait"}
    src = ROOT / job["normal"]["path"]
    d = decode(src)
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    outdir = WORK / target
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, r in enumerate(d["atlas"]["SubTexture"]):
        old_path = outdir / f"old{idx:02d}.png"
        if not old_path.exists():
            im = atlas.crop((r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"]))
            bg = Image.new("RGBA", im.size, (16, 20, 26, 255)); bg.alpha_composite(im)
            bg.convert("RGB").save(old_path)
        w, h = size_for(r["width"], r["height"])
        out = outdir / f"{idx:02d}.png"
        is_character = job["originalResourceKey"] in CHAR_KEYS and is_character_frame(r["width"], r["height"])
        neg = ("3D render, photoreal, old character, human, text, watermark, background, scenery, split panel, border, "
               "multiple characters" if is_character else
               "character, person, face, body, hand, costume, portrait, human, 3D render, photoreal, text, watermark, "
               "background, scenery, split panel, border")
        if not out.exists():
            if is_character:
                sec = edit_two(old_path, portrait, prompt_for(job, idx, r), out, (w, h),
                               202611032200 + idx, negative=neg, steps=22)
            else:
                # No portrait reference for effect frames: otherwise the model draws the character.
                sec = edit_one(old_path, prompt_for(job, idx, r), out, (w, h), 202611032200 + idx)
        else:
            sec = 0
        rows.append({"index": idx, "region": r["name"], "rect": [r["width"], r["height"]], "char": is_character,
                     "image": out.relative_to(ROOT).as_posix(), "seconds": sec,
                     "alphaMass": float((np.asarray(atlas.crop((r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])))[..., 3].astype(np.float32) / 255.0).sum())})
    # pack
    blob = src.read_bytes()
    new_atlas = atlas.copy()
    for row in rows:
        rgb = Image.open(ROOT / row["image"]).convert("RGB")
        reg = d["atlas"]["SubTexture"][row["index"]]
        if not row["char"]:
            # Effect slots must keep the original silhouette/composition: use the OLD alpha verbatim.
            w, h = row["rect"]
            old_a = atlas.crop((reg["x"], reg["y"], reg["x"] + reg["width"], reg["y"] + reg["height"])) \
                         .getchannel("A").resize((w, h), Image.Resampling.LANCZOS)
            rgba = Image.merge("RGBA", (*rgb.resize((w, h), Image.Resampling.LANCZOS).split(), old_a))
            new_atlas.paste(rgba, (reg["x"], reg["y"]))
            continue
        rgb = strip_border_bg(rgb)
        arr = np.asarray(rgb).astype(np.float32)
        lum = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]) / 255.0
        a = np.clip((lum - 0.06) / 0.94, 0.0, 1.0) ** 0.85
        ai = Image.fromarray((a * 255).astype(np.uint8), "L")
        ys, xs = np.where(np.asarray(ai) > 8)
        if len(xs):
            pad = 4
            box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
                   min(ai.width, xs.max() + 1 + pad), min(ai.height, ys.max() + 1 + pad))
            rgb = rgb.crop(box); ai = ai.crop(box)
        rgba = Image.merge("RGBA", (*rgb.split(), ai)).resize((row["rect"][0], row["rect"][1]), Image.Resampling.LANCZOS)
        a2 = np.asarray(rgba)[..., 3].astype(np.float32); s = float(a2.sum())
        if s > 1e-3:
            a2 = np.clip(a2 * (row["alphaMass"] * 255.0 / s), 0.0, 255.0)
            rgba = Image.merge("RGBA", (*rgba.split()[:3], Image.fromarray(a2.astype(np.uint8), "L")))
        new_atlas.paste(rgba, (reg["x"], reg["y"]))
    arm = d["skeleton"]["armature"][0]
    rebuilt = B.rebuild(blob, new_atlas, arm["name"], d["atlas"].get("name"))
    dst = CAND / f"{target}.bin"
    dst.write_bytes(rebuilt)
    chk = decode(dst)
    a_new = (chk["skeleton"]["armature"][0].get("animation") or [{}])[0]
    a_old = (arm.get("animation") or [{}])[0]
    ok = (chk["skeleton"]["armature"][0]["name"] == arm["name"]
          and chk["atlas"].get("name") == d["atlas"].get("name")
          and len(chk["atlas"]["SubTexture"]) == len(d["atlas"]["SubTexture"])
          and a_new.get("duration") == a_old.get("duration")
          and chk["skeleton"].get("frameRate") == d["skeleton"].get("frameRate"))
    return {"jobId": job["jobId"], "status": "built" if ok else "verify-failed", "key": key, "target": target,
            "heroId": hero, "regions": len(rows), "duration": a_new.get("duration"),
            "fps": chk["skeleton"].get("frameRate"), "out": dst.relative_to(ROOT).as_posix(),
            "namesAndClockPreserved": ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    done = load_progress()
    if args.force:
        done = {}
    if args.jobs:
        jobs = [JOB_BY_ID[x.strip()] for x in args.jobs.split(",") if x.strip()]
    else:
        jobs = PLAN["jobs"]
    if args.limit:
        jobs = jobs[: args.limit]
    built = 0
    with MANIFEST.open("a", encoding="utf-8") as mf:
        for job in jobs:
            if job["jobId"] in done:
                continue
            try:
                rec = run_job(job)
            except Exception as exc:
                rec = {"jobId": job["jobId"], "status": "failed", "error": str(exc)[:300]}
            mf.write(json.dumps(rec, ensure_ascii=False) + "\n"); mf.flush()
            print(json.dumps({k: rec.get(k) for k in ("jobId", "status", "regions", "duration", "fps")}, ensure_ascii=False), flush=True)
            if rec.get("status") == "built":
                built += 1
    print(json.dumps({"builtThisRun": built, "totalJobs": len(jobs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
