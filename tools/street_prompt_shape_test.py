"""Fast still preview of the author's image stage (no H3 video), for prompt shape iteration.

Builds a minimal API graph from the parameters actually used in the author workflow
(UNET/CLIP/VAE -> QwenImage21Cache -> TextEncodeQwenImage21 -> KSamplerAdvanced -> VAEDecode -> SaveImage)
and runs one prompt per variant. Output lands in ComfyUI/output/FX/street_prompt_tests/.
"""
import json, time, urllib.request, sys
from pathlib import Path

API = "http://127.0.0.1:8188"
COMFY = Path(r"G:\comfyqiuye\ComfyUI-aki-v3.2\ComfyUI")
OUTDIR = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装\outputs\_handoff-verify\prompt-tests")

VARIANTS = {
    # A: directional blast cone - explicitly NOT a ring
    "a_directed": """A huge crimson-and-ivory elbow impact seen from the side, the moment the hit lands: one dense white-hot contact core slightly left of centre, a short thick cone of red-and-white force blasting out to the right, long thin sparks and torn ivory chips streaking backwards to the left, and one long bright horizontal streak passing through the core.

It is clearly an impact, not a halo: the shape is asymmetric, stretched along the strike direction, the left side is a ragged trail and the right side is a hard torn front. No ring, no circle, no donut, no symmetrical halo.

Glowing crimson body, ivory-white contact core, hard specular highlights, deep red rim light, crisp torn edges, no haze, no soft gradient mush.

The backdrop is pure black and completely unlit, with no floor, no horizon, no reflection and no fill light anywhere; the effect itself is the only source of light in the frame. At least eight percent of the frame is left empty black on all four sides.

Stylised game visual effect, ultra high contrast, crisp clean silhouette, hard-edged shards, bold readable volume. One single effect only. No person, no hand, no character, no weapon, no text, no logo, no watermark.""",

    # B: comic-style hit spark - irregular spikes, white core, red body
    "b_hitspark": """A huge cartoon impact spark at the instant of a punch landing: a small blinding white core, and from it a burst of long, uneven, needle-sharp spikes in deep crimson and bright ivory, some spikes long and some short, a few broken chips and embers flying off the tips.

The spikes are irregular and hard-edged, like a comic hit star, clearly radiating outward but not evenly, with big black gaps between adjacent spikes so the silhouette reads as sharp separate needles.

Glowing crimson and ivory spikes, white-hot core, hard specular highlights along each spike, no haze, no ring, no circle, no symmetrical halo.

The backdrop is pure black and completely unlit, with no floor, no horizon, no reflection and no fill light anywhere; the effect itself is the only source of light in the frame. At least eight percent of the frame is left empty black on all four sides.

Stylised game visual effect, ultra high contrast, crisp clean silhouette, hard-edged shards, bold readable volume. One single effect only. No person, no hand, no character, no weapon, no text, no logo, no watermark.""",

    # C: short thick crescent shock edge sweeping to the right (reads as a strike)
    "c_crescent": """A huge short thick crescent of crimson-and-ivory shock force sweeping to the right, seen from the side at the moment of a close-range elbow strike: the crescent is a hard torn blade of compressed air, thick at the middle and thinning into ragged tips, with a white-hot leading edge, red body, and torn ivory chips and embers trailing behind the concave side.

The shape is one asymmetric crescent, wide and blade-like, clearly sweeping in one direction; no ring, no circle, no halo, no symmetrical burst.

Glowing crimson body, white-hot leading edge, hard specular highlights, deep red rim light, crisp torn tips, no haze, no soft gradient mush.

The backdrop is pure black and completely unlit, with no floor, no horizon, no reflection and no fill light anywhere; the effect itself is the only source of light in the frame. At least eight percent of the frame is left empty black on all four sides.

Stylised game visual effect, ultra high contrast, crisp clean silhouette, hard-edged shards, bold readable volume. One single effect only. No person, no hand, no character, no weapon, no text, no logo, no watermark.""",

    # D: heavy pressure star - thicker, shorter spikes, dense body, less sparkler
    "d_heavy": """A huge heavy impact star at the instant a close-range elbow lands: a small blinding white core with a thick ring of compressed crimson force crushed against it, and from that ring short thick uneven ivory-and-crimson shards thrown outward, some blunt and some broken, heavier near the middle and splintering at the tips.

The silhouette is dense and heavy rather than sparkly: a solid crimson mass with white-hot cracks, thick hard-edged outer shards, and wide black gaps between them.

Glowing crimson body, white-hot compressed core, hard specular highlights on every facet, deep red rim light, crisp torn edges, no haze, no soft gradient mush, no thin needles.

The backdrop is pure black and completely unlit, with no floor, no horizon, no reflection and no fill light anywhere; the effect itself is the only source of light in the frame. At least eight percent of the frame is left empty black on all four sides.

Stylised game visual effect, ultra high contrast, crisp clean silhouette, hard-edged shards, bold readable volume. One single effect only. No person, no hand, no character, no weapon, no text, no logo, no watermark.""",

    # E: directional hit star - core offset, spikes swept to one side
    "e_swept": """A huge crimson-and-ivory impact star caught mid-strike, the contact core sitting left of centre and the whole burst swept to the right: a blinding white core, a dense crushed rim of crimson force around it, and long splintered ivory-and-crimson shards thrown out mostly to the right, with shorter torn stubs on the left and fine debris trailing back to the left.

The shape is clearly directional, longer on the right than on the left, the right tips raked forward as if driven by the hit, the left side friable and torn.

Glowing crimson body, white-hot contact core, hard specular highlights, deep red rim light, crisp torn edges, no haze, no ring, no circle, no symmetrical halo.

The backdrop is pure black and completely unlit, with no floor, no horizon, no reflection and no fill light anywhere; the effect itself is the only source of light in the frame. At least eight percent of the frame is left empty black on all four sides.

Stylised game visual effect, ultra high contrast, crisp clean silhouette, hard-edged shards, bold readable volume. One single effect only. No person, no hand, no character, no weapon, no text, no logo, no watermark.""",
}


def graph(prompt, tag, width=1152, height=640, seed=2026110201):
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
        "65": {"class_type": "SaveImage", "inputs": {"images": ["50", 0], "filename_prefix": f"FX/street_prompt_tests/{tag}"}},
    }


def req(path, data=None, timeout=60):
    body = None if data is None else json.dumps(data).encode()
    r = urllib.request.Request(API + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def main():
    only = sys.argv[1:] or list(VARIANTS)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for tag in only:
        prompt = VARIANTS[tag]
        g = graph(prompt, tag)
        q = req("/queue")
        while q.get("queue_running") or q.get("queue_pending"):
            time.sleep(5)
            q = req("/queue")
        resp = req("/prompt", {"prompt": g, "client_id": "h018-prompt-test"})
        pid = resp["prompt_id"]
        print(f"[{tag}] queued {pid}", flush=True)
        t0 = time.time()
        files = []
        while time.time() - t0 < 1800:
            h = req("/history/" + pid)
            if pid in h:
                entry = h[pid]
                st = entry.get("status", {})
                if st.get("status_str") != "success":
                    print(f"[{tag}] FAILED", st.get("messages")[:2], flush=True)
                    break
                for out in entry.get("outputs", {}).values():
                    for item in out.get("images", []) or []:
                        src = COMFY / "output" / item.get("subfolder", "") / item["filename"]
                        dst = OUTDIR / f"{tag}.png"
                        dst.write_bytes(src.read_bytes())
                        files.append(str(dst))
                break
            time.sleep(5)
        dur = time.time() - t0
        results[tag] = {"promptId": pid, "seconds": round(dur, 1), "files": files}
        print(f"[{tag}] done in {dur:.0f}s -> {files}", flush=True)
    (OUTDIR / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
