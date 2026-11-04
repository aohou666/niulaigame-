"""Generate 86 character x 3 key-art variants with Qwen Image 2.1 reference-to-image.

Resumable: skips existing PNGs; appends one JSONL record per image.
Run with ComfyUI on 127.0.0.1:8188.
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
sys.path.insert(0, str(ROOT / "tools"))
from street_qwen_edit_min import edit

BRIEFS = json.loads((ROOT / "outputs/street-reskin/motifs-86-briefs.json").read_text("utf-8"))
OUT = ROOT / "outputs/street-reskin/keysart-86"
MANIFEST = ROOT / "art-migration/generation/keysart-86/manifest.jsonl"
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST.parent.mkdir(parents=True, exist_ok=True)

VARIANTS = {
    "v1": "Composition: dynamic three-quarter action pose, low-angle hero shot, the ultimate effect erupting behind and around the character, cinematic key art, character occupies 65% of frame.",
    "v2": "Composition: full-body character concept splash, standing confidently among their signature props, a huge subtle ultimate emblem glowing behind, clean dark backdrop, character occupies 80% of frame.",
    "v3": "Composition: close-up upper-body action shot, face and signature prop prominent, ultimate particles and effect cutting across the foreground, ink-brush energy, dramatic expression.",
}


def prompt_for(b: dict, variant: str) -> str:
    forbid = re.sub(r"人物|手指|头发|脸|身体|手", "", b["forbidden"]).strip("、， ")
    base = (
        f"Vertical 2D hand-painted mobile game character splash art. The character is {b['new']} "
        f"({b['camp']} {b['cls']}), a reincarnation of the old hero {b['old']}; use image 1 as the exact identity, "
        f"face, hair, outfit and body proportions. "
        "ANATOMY LOCK: every visible hand has exactly four digits — thumb, index, middle, ring; no pinky, no fifth finger; "
        "both hands use the same rule; the hand is a stylized bull/cow hand, not a human hand. "
        f"Outfit and signature props: {b['props']}. "
        f"Personality/role line: {b['role_quote']}. Story: {b['story']}. "
        f"Ultimate skill '{b['ult_name']}' ({b['fps']}fps, {b['frames']}-frame skill): {b['rage_desc']}. "
        f"Ultimate visual motif: {b['ult_motif']}. Non-human effect elements: {b['nonhuman']}. "
        f"Particles: {b['particles']}. Palette: {b['primary']} and {b['secondary']}. "
        "Thick dark ink outlines, flat cel shading, dramatic warm rim light, dark atmospheric game splash background, "
        "high contrast, crisp character silhouette, no text, no logo, no UI, no watermark, "
        f"do not include old {b['old']} elements: {forbid}."
    )
    return base + " " + VARIANTS[variant]


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = 0
    for hid, b in sorted(BRIEFS.items(), key=lambda kv: int(kv[0])):
        if limit and count >= limit:
            break
        d = OUT / f"{int(hid):03d}"
        d.mkdir(parents=True, exist_ok=True)
        portrait = ROOT / f"local_game/assets/street/characters/{int(hid):03d}/portrait.png"
        if not portrait.is_file():
            with MANIFEST.open("a", encoding="utf-8") as mf:
                mf.write(json.dumps({"id": int(hid), "status": "missing-portrait"}, ensure_ascii=False) + "\n")
            continue
        for variant in ("v1", "v2", "v3"):
            dst = d / f"{variant}.png"
            if dst.exists():
                continue
            t0 = time.time()
            rec = {"id": int(hid), "name": b["new"], "variant": variant, "status": "built"}
            try:
                sec = edit(portrait, prompt_for(b, variant), dst, (640, 896), 202611034000 + int(hid) * 100 + len(variant))
                rec["seconds"] = round(sec, 1)
                rec["path"] = dst.relative_to(ROOT).as_posix()
                count += 1
            except Exception as exc:
                rec = {"id": int(hid), "name": b["new"], "variant": variant,
                       "status": "failed", "error": str(exc)[:250]}
            with MANIFEST.open("a", encoding="utf-8") as mf:
                mf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                mf.flush()
            print(json.dumps({k: rec.get(k) for k in ("id", "name", "variant", "status", "seconds")},
                             ensure_ascii=False), flush=True)
    print(json.dumps({"generatedThisRun": count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
