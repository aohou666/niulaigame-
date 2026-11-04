"""Qwen Image 2.1 two-reference edit: image_1 = structure, image_2 = identity, one output image."""
import json, shutil, time
from pathlib import Path

from street_qwen_edit_min import req, COMFY


def edit_two(src1: Path, src2: Path, prompt: str, out: Path, size, seed: int = 20261103, negative: str = "", steps: int = 25) -> float:
    w, h = size
    w = max(64, round(w / 64) * 64)
    h = max(64, round(h / 64) * 64)
    n1 = "street_two_a_" + src1.stem[:32] + ".png"
    n2 = "street_two_b_" + src2.stem[:32] + ".png"
    shutil.copy2(src1, COMFY / "input" / n1)
    shutil.copy2(src2, COMFY / "input" / n2)
    g = {
        "42": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "43": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "44": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "45": {"class_type": "QwenImage21Cache", "inputs": {"device": "auto", "dtype": "default", "model": ["42", 0]}},
        "47": {"class_type": "TextEncodeQwenImage21",
               "inputs": {"prompt": prompt, "negative_prompt": negative, "resolution": max(w, h),
                          "clip": ["43", 0], "vae": ["44", 0],
                          "images.image_1": ["90", 0], "images.image_2": ["91", 0]}},
        "48": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "49": {"class_type": "KSamplerAdvanced",
               "inputs": {"add_noise": "enable", "noise_seed": seed, "steps": steps, "cfg": 1,
                          "sampler_name": "euler", "scheduler": "simple", "start_at_step": 0,
                          "end_at_step": 10000, "return_with_leftover_noise": "disable",
                          "model": ["45", 0], "positive": ["47", 0], "negative": ["47", 1],
                          "latent_image": ["48", 0]}},
        "50": {"class_type": "VAEDecode", "inputs": {"samples": ["49", 0], "vae": ["44", 0]}},
        "65": {"class_type": "SaveImage", "inputs": {"images": ["50", 0], "filename_prefix": "fx_qwen_edit/two_" + out.stem}},
        "90": {"class_type": "LoadImage", "inputs": {"image": n1}},
        "91": {"class_type": "LoadImage", "inputs": {"image": n2}},
    }
    q = req("/queue")
    while q.get("queue_running") or q.get("queue_pending"):
        time.sleep(3)
        q = req("/queue")
    t0 = time.time()
    pid = req("/prompt", {"prompt": g, "client_id": "qwen-two"})["prompt_id"]
    while time.time() - t0 < 600:
        hist = req("/history/" + pid)
        if pid in hist:
            entry = hist[pid]
            if entry.get("status", {}).get("status_str") != "success":
                raise RuntimeError(json.dumps(entry.get("status", {}).get("messages", []))[:500])
            for output in entry.get("outputs", {}).values():
                for item in output.get("images", []) or []:
                    src = COMFY / "output" / item.get("subfolder", "") / item["filename"]
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(src.read_bytes())
                    return round(time.time() - t0, 1)
        time.sleep(2)
    raise TimeoutError(pid)
