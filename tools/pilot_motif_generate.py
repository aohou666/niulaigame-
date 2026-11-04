"""Pilot: per-region character-motif generation (Qwen Image 2.1 text-to-image), then pack into the
original container's atlas rects so the armature / slot timeline / fps stay untouched.

usage:
  py pilot_motif_generate.py generate <key>
  py pilot_motif_generate.py pack <key>
"""
from __future__ import annotations
import io, json, sys, time, urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode
import street_batch_recolor as B

API = "http://127.0.0.1:8188"
COMFY = Path(r"C:\Users\dongdong\..\..\..\G:\comfyqiuye")  # unused; kept out of paths
PLAN = json.loads((ROOT / "outputs/fx-handoff-20261102/plan.json").read_text("utf-8-sig"))
BY_KEY = {}
for _j in PLAN["jobs"]:
    BY_KEY.setdefault(_j["originalResourceKey"], _j)

OUT = ROOT / "outputs/street-reskin/pilot"
GAME = ROOT / "local_game/assets/street/fx/pilot"

# ---------------------------------------------------------------- motifs

MOTIFS = {
    "common_skill_pangtong_01_1": {
        "name": "鸡 · 手机节拍",
        "palette": "neon violet, electric cyan, hot white core",
        "stages": [
            "one tiny neon equalizer tick with a cyan spark",
            "one small broken phone-glass shard with violet edge light",
            "one thin electric arc curling around a glass splinter",
            "one small holographic screen fragment showing three equalizer bars",
            "one short neon signal bar with a white hot tip",
            "one small cracked camera-lens flare with magenta ring",
            "a wide holographic phone-screen shock ring with cyan equalizer bars",
            "a dense neon-violet impact ring with cracked glass edges",
            "a thin outer shockwave ring with signal dots",
            "an outer ring of broken neon glass and equalizer debris",
            "a wide expanding neon equalizer wave with violet sparks",
        ],
    },
    "common_skill_pangde_02": {
        "name": "锤王 · 铁锤重压",
        "palette": "forged iron grey, hammered copper orange, white hot sparks",
        "stages": [
            "one small copper rivet with a spark",
            "one forged-iron chip with an orange edge",
            "a hammer-face shaped iron mass with rivets and white hot contact point",
            "a cracked iron plate ring with copper seams",
            "a heavy circular shockwave of iron dust and orange sparks",
            "thick broken iron plates flying outward with rivets",
            "a low ring of iron dust and dying orange embers",
        ],
    },
    "common_skill_zhangjiao_baguazhen": {
        "name": "驱鬼道长 · 符阵",
        "palette": "cinnabar red, talisman yellow, ink black, gold seal",
        "stages": [
            "eight narrow yellow paper talisman strips with cinnabar seals arranged in a perfect ring, "
            "each strip slightly curled, a red-gold seal at the centre (NO yin-yang disc, no trigram lines), "
            "ink-black gaps between the strips, crisp paper edges",
        ],
    },
}


def req(path, data=None, timeout=90):
    body = None if data is None else json.dumps(data).encode()
    r = urllib.request.Request(API + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def graph(prompt, tag, width, height, seed):
    return {
        "42": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "43": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "44": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "45": {"class_type": "QwenImage21Cache", "inputs": {"device": "auto", "dtype": "default", "model": ["42", 0]}},
        "47": {"class_type": "TextEncodeQwenImage21", "inputs": {"prompt": prompt, "negative_prompt": "", "resolution": 1088, "clip": ["43", 0], "vae": ["44", 0]}},
        "48": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "49": {"class_type": "KSamplerAdvanced", "inputs": {"add_noise": "enable", "noise_seed": seed, "steps": 25, "cfg": 1,
                                                           "sampler_name": "euler", "scheduler": "simple",
                                                           "start_at_step": 0, "end_at_step": 10000,
                                                           "return_with_leftover_noise": "disable",
                                                           "model": ["45", 0], "positive": ["47", 0],
                                                           "negative": ["47", 1], "latent_image": ["48", 0]}},
        "50": {"class_type": "VAEDecode", "inputs": {"samples": ["49", 0], "vae": ["44", 0]}},
        "65": {"class_type": "SaveImage", "inputs": {"images": ["50", 0], "filename_prefix": f"FX/street_pilot/{tag}"}},
    }


def prompt_for(key: str, idx: int, stage: str) -> str:
    m = MOTIFS[key]
    return (f"Stylised game visual effect sprite on a pure black unlit backdrop: {stage}. "
            f"Character motif palette: {m['palette']}. The effect is the only light source, centered, "
            "with at least 8% empty black margin on every side. Crisp hard-edged silhouette, high contrast, "
            "readable bold volume, no haze, no soft gradient mush. One single effect only. "
            "No person, no hand, no character, no weapon, no text, no logo, no watermark.")


def size_for(w, h, max_side=640, min_side=256):
    scale = max_side / max(w, h)
    nw, nh = max(min_side, round(w * scale)), max(min_side, round(h * scale))
    nw, nh = (nw // 8) * 8, (nh // 8) * 8
    return max(8, nw), max(8, nh)


def generate(key):
    m = MOTIFS[key]
    job = BY_KEY[key]
    d = decode(ROOT / job["normal"]["path"])
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    regions = d["atlas"]["SubTexture"]
    outdir = OUT / key
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, r in enumerate(regions):
        stage = m["stages"][min(idx, len(m["stages"]) - 1)]
        box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
        sprite = atlas.crop(box)
        arr = np.asarray(sprite)[..., 3].astype(np.float32) / 255.0
        mass = float(arr.sum())
        w, h = size_for(r["width"], r["height"])
        prompt = prompt_for(key, idx, stage)
        tag = f"{key}/{idx:02d}"
        g = graph(prompt, tag, w, h, 2026110312 + idx)
        q = req("/queue")
        while q.get("queue_running") or q.get("queue_pending"):
            time.sleep(5); q = req("/queue")
        pid = req("/prompt", {"prompt": g, "client_id": "street-pilot"})["prompt_id"]
        print(f"[{key}] {idx+1}/{len(regions)} queued {pid}", flush=True)
        t0 = time.time()
        while time.time() - t0 < 900:
            hst = req("/history/" + pid)
            if pid in hst:
                entry = hst[pid]
                st = entry.get("status", {})
                if st.get("status_str") != "success":
                    raise RuntimeError(f"generation failed: {st.get('messages')}")
                images = [it for out in entry.get("outputs", {}).values() for it in (out.get("images") or [])]
                if not images:
                    raise RuntimeError("no output image")
                it = images[0]
                src = Path(r"G:\comfyqiuye\ComfyUI-aki-v3.2\ComfyUI") / "output" / it.get("subfolder", "") / it["filename"]
                dst = outdir / f"{r['name'].replace('/', '_')}.png"
                dst.write_bytes(src.read_bytes())
                rows.append({"index": idx, "region": r["name"], "rect": [r["width"], r["height"]],
                             "alphaMass": mass, "prompt": prompt, "image": dst.relative_to(ROOT).as_posix()})
                print(f"[{key}] {idx+1}/{len(regions)} done {time.time()-t0:.0f}s", flush=True)
                break
            time.sleep(4)
        else:
            raise RuntimeError("generation timeout")
    (outdir / "manifest.json").write_text(json.dumps({"key": key, "motif": m, "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def edit_alpha(rgb_img: Image.Image, target_mass: float) -> Image.Image:
    """Qwen renders on black; derive a matte from luminance and normalise the mass to the original slot."""
    rgb = np.asarray(rgb_img.convert("RGB")).astype(np.float32)
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    a = np.clip((lum - 0.035) / 0.965, 0.0, 1.0) ** 0.85
    s = float(a.sum())
    if s > 1e-3 and target_mass > 0:
        a = np.clip(a * (target_mass / s), 0.0, 1.0)
    # un-premultiply against the black backdrop
    rgb = np.clip(rgb / np.maximum(a[..., None], 0.35), 0.0, 255.0)
    return Image.fromarray(np.dstack([rgb, a * 255.0]).astype(np.uint8), "RGBA")


def pack(key):
    manifest = json.loads((OUT / key / "manifest.json").read_text("utf-8"))
    job = BY_KEY[key]
    src_path = ROOT / job["normal"]["path"]
    blob = src_path.read_bytes()
    d = decode(src_path)
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    new_atlas = atlas.copy()
    for row in manifest["rows"]:
        sprite = Image.open(ROOT / row["image"]).convert("RGB")
        rgba = edit_alpha(sprite, row["alphaMass"])
        # Qwen leaves a lot of black margin; crop to the visible matte so the motif fills the slot
        arr = np.asarray(rgba)
        mask = arr[..., 3] > 8
        ys, xs = np.where(mask)
        if len(xs):
            pad = 4
            box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
                   min(arr.shape[1], xs.max() + 1 + pad), min(arr.shape[0], ys.max() + 1 + pad))
            rgba = rgba.crop(box)
        rgba = rgba.resize((row["rect"][0], row["rect"][1]), Image.Resampling.LANCZOS)
        # normalise the mass AFTER the resize, so the slot keeps the original visual weight
        a = np.asarray(rgba)[..., 3].astype(np.float32)
        s = float(a.sum())
        if s > 1e-3 and row["alphaMass"] > 0:
            a = np.clip(a * (row["alphaMass"] * 255.0 / s), 0.0, 255.0)
            rgb = np.asarray(rgba)[..., :3]
            rgba = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA")
        region = next(r for r in d["atlas"]["SubTexture"] if r["name"] == row["region"])
        new_atlas.paste(rgba, (region["x"], region["y"]))
    arm = d["skeleton"]["armature"][0]
    rebuilt = B.rebuild(blob, new_atlas, arm["name"], d["atlas"].get("name"))
    GAME.mkdir(parents=True, exist_ok=True)
    dst = GAME / f"{key}_motif.bin"
    dst.write_bytes(rebuilt)
    chk = decode(dst)
    a_new = (chk["skeleton"]["armature"][0].get("animation") or [{}])[0]
    a_old = (arm.get("animation") or [{}])[0]
    ok = (chk["skeleton"]["armature"][0]["name"] == arm["name"]
          and chk["atlas"].get("name") == d["atlas"].get("name")
          and len(chk["atlas"]["SubTexture"]) == len(d["atlas"]["SubTexture"])
          and a_new.get("duration") == a_old.get("duration")
          and chk["skeleton"].get("frameRate") == d["skeleton"].get("frameRate"))
    print(json.dumps({"key": key, "out": dst.relative_to(ROOT).as_posix(), "namesAndClockPreserved": ok,
                      "regions": len(chk["atlas"]["SubTexture"]), "duration": a_new.get("duration"),
                      "fps": chk["skeleton"].get("frameRate")}, ensure_ascii=False))


if __name__ == "__main__":
    mode, key = sys.argv[1], sys.argv[2]
    generate(key) if mode == "generate" else pack(key)
