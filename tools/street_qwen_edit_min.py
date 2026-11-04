"""Minimal Qwen Image 2.1 edit call: one reference image + one prompt -> one PNG.

Same model trio as the user's '文生/图像编辑一体化' workflow (qwen_image_2.1 + qwen3vl_8b + vae_bf16) and the
same reference-image mechanism (TextEncodeQwenImage21 with `images.image_1`), but expressed as a small
API graph so it can be driven in a loop.

usage: py street_qwen_edit_min.py <input.png> <prompt> <out.png> [size] [seed]
"""
import json, shutil, sys, time, urllib.request
from pathlib import Path

API = "http://127.0.0.1:8188"
COMFY = Path(r"G:\comfyqiuye\ComfyUI-aki-v3.2\ComfyUI")


def req(path, data=None, timeout=180):
    body = None if data is None else json.dumps(data).encode()
    r = urllib.request.Request(API + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def edit(src_png: Path, prompt: str, out_png: Path, size=1024, seed=20261103):
    """size: int (square) or (width, height). Both are rounded to multiples of 64."""
    if isinstance(size, (tuple, list)):
        w, h = int(size[0]), int(size[1])
    else:
        w = h = int(size)
    w = max(64, round(w / 64) * 64)
    h = max(64, round(h / 64) * 64)
    name = "street_edit_" + src_png.stem[:40].replace(" ", "_") + ".png"
    shutil.copy2(src_png, COMFY / "input" / name)
    g = {
        "42": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "43": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "44": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "45": {"class_type": "QwenImage21Cache", "inputs": {"device": "auto", "dtype": "default", "model": ["42", 0]}},
        "47": {"class_type": "TextEncodeQwenImage21",
               "inputs": {"prompt": prompt, "negative_prompt": "", "resolution": max(w, h),
                          "clip": ["43", 0], "vae": ["44", 0], "images.image_1": ["90", 0]}},
        "48": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "49": {"class_type": "KSamplerAdvanced",
               "inputs": {"add_noise": "enable", "noise_seed": seed, "steps": 25, "cfg": 1,
                          "sampler_name": "euler", "scheduler": "simple", "start_at_step": 0,
                          "end_at_step": 10000, "return_with_leftover_noise": "disable",
                          "model": ["45", 0], "positive": ["47", 0], "negative": ["47", 1], "latent_image": ["48", 0]}},
        "50": {"class_type": "VAEDecode", "inputs": {"samples": ["49", 0], "vae": ["44", 0]}},
        "65": {"class_type": "SaveImage", "inputs": {"images": ["50", 0], "filename_prefix": f"fx_qwen_edit/{out_png.stem}"}},
        "90": {"class_type": "LoadImage", "inputs": {"image": name}},
    }
    q = req("/queue")
    while q.get("queue_running") or q.get("queue_pending"):
        time.sleep(3); q = req("/queue")
    t0 = time.time()
    resp = req("/prompt", {"prompt": g, "client_id": "qwen-edit-min"})
    pid = resp["prompt_id"]
    while time.time() - t0 < 600:
        h = req("/history/" + pid)
        if pid in h:
            e = h[pid]
            if e.get("status", {}).get("status_str") != "success":
                raise RuntimeError(json.dumps(e.get("status", {}).get("messages", []))[:500])
            for out in e.get("outputs", {}).values():
                for it in out.get("images", []) or []:
                    src = COMFY / "output" / it.get("subfolder", "") / it["filename"]
                    out_png.parent.mkdir(parents=True, exist_ok=True)
                    out_png.write_bytes(src.read_bytes())
                    return round(time.time() - t0, 1)
        time.sleep(2)
    raise TimeoutError(pid)


if __name__ == "__main__":
    src = Path(sys.argv[1]); prompt = sys.argv[2]; dst = Path(sys.argv[3])
    size = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20261103
    print("seconds:", edit(src, prompt, dst, size, seed), "->", dst)
