"""Batch material reskin for every planned skill-FX job.

For each job in the handoff plan: take the ORIGINAL packed container (normal + ez), remap every
texture's RGB through a per-character gradient LUT, keep the alpha channel byte-identical, repack the
bundle unchanged apart from the three name slots, and write a new container keyed for that hero.

Why recolour instead of regenerate: the alpha channel carries the attack's silhouette, its decay curve
and therefore the whole timing relationship with the character animation. Keeping it identical means
the reskin cannot drift in rhythm, which is exactly what a generated clip could not guarantee.

usage:
  py street_batch_recolor.py --limit 3            # sample, prints timing
  py street_batch_recolor.py                      # all jobs, resumable
"""
from __future__ import annotations
import argparse, hashlib, io, json, struct, sys, time, zlib
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
KIT = ROOT / "outputs" / "fx-handoff-20261102"
OUT = ROOT / "art-migration/generation/fx-batch-recolor-20261103"
GAME_FX = ROOT / "local_game/assets/street/fx/batch"

# ---------------------------------------------------------------- palette

HUE = {
    "红": (210, 34, 40), "橙": (240, 132, 40), "黄": (246, 206, 72), "金": (232, 186, 88),
    "绿": (72, 178, 96), "青": (84, 198, 204), "蓝": (56, 116, 224), "紫": (150, 92, 206),
    "粉": (244, 146, 178), "白": (246, 246, 240), "黑": (54, 50, 58), "灰": (126, 130, 138),
    "银": (198, 206, 216), "棕": (146, 96, 58), "米": (238, 224, 196), "玉": (196, 236, 214),
    "铜": (186, 124, 72), "钢": (150, 160, 172), "玫": (216, 72, 132), "橙": (240, 132, 40),
}
DARKEN = "墨暗深炭幽"
LIGHTEN = "浅淡柔奶骨米玉珠婚冷暖葱嫩粉白"
SATURATE = "电霓荧"

NEUTRAL = ("未锁定", (120, 140, 170))


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def parse_colour(word: str):
    """'球衣红' -> hue red; '奶白' -> warm white; '翡翠绿' -> saturated green."""
    word = str(word)
    hue = None
    for ch in reversed(word):
        if ch in HUE:
            hue = HUE[ch]
            break
    if hue is None:
        return None
    if any(ch in word for ch in DARKEN):
        hue = _mix(hue, (16, 14, 20), 0.45)
    if any(ch in word for ch in LIGHTEN) and word not in ("白",):
        hue = _mix(hue, (250, 246, 240), 0.38)
    if any(ch in word for ch in SATURATE):
        arr = np.array(hue, dtype=np.float32)
        m = arr.mean()
        arr = np.clip(m + (arr - m) * 1.35, 0, 255)
        hue = tuple(int(x) for x in arr)
    return hue


def build_lut(palette: str):
    """palette string -> 256x3 uint8 LUT (luminance ramp)."""
    words = [w for w in str(palette).replace("，", "、").replace(" ", "、").split("、") if w]
    cols = [c for c in (parse_colour(w) for w in words) if c]
    if not cols:
        cols = [NEUTRAL[1]]
    primary = cols[0]
    accent = cols[1] if len(cols) > 1 else _mix(primary, (255, 255, 255), 0.55)
    stops = [
        (0.00, _mix((10, 8, 12), primary, 0.18)),
        (0.18, _mix((12, 10, 14), primary, 0.45)),
        (0.40, _mix(primary, (0, 0, 0), 0.18)),
        (0.62, primary),
        (0.80, accent),
        (0.92, _mix(accent, (255, 252, 246), 0.62)),
        (1.00, (255, 255, 255)),
    ]
    xs = np.array([s[0] for s in stops], dtype=np.float32)
    arr = np.array([s[1] for s in stops], dtype=np.float32)
    lum = np.linspace(0, 1, 256, dtype=np.float32)
    lut = np.stack([np.interp(lum, xs, arr[:, c]) for c in range(3)], axis=1)
    return np.clip(lut, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- bundle helpers

def split(blob):
    assert blob[:3] == bytes([219, 189, 30]) and blob[6] == 0, "not an audited PNG bundle"
    parts, pos = [], 12
    for _ in range(3):
        n = struct.unpack_from("<I", blob, pos)[0]; pos += 4
        parts.append(blob[pos:pos + n]); pos += n
    assert pos == len(blob), "trailing data"
    return parts


def raw(blob, part):
    return zlib.decompress(part, -15) if blob[4] else part


def pack(blob, part):
    if not blob[4]:
        return part
    c = zlib.compressobj(6, zlib.DEFLATED, -15)
    return c.compress(part) + c.flush()


def rebuild(src_blob: bytes, atlas: Image.Image, new_name: str, atlas_name: str):
    parts = split(src_blob)
    skel = raw(src_blob, parts[0])
    assert skel[:4] == b"DBDT"
    size = struct.unpack_from("<I", skel, 8)[0]
    prefix, payload, tail = skel[:12], skel[12:12 + size], skel[12 + size:]
    old = json.loads(payload)["armature"][0]["name"].encode()
    tokens = [old + b"_ez", old]
    text = payload
    for tok in tokens:
        if tok in text:
            text = text.replace(tok, new_name.encode())
    pad = (-(12 + len(text))) % 8
    if pad:
        text += b" " * pad
    new_skel = prefix[:8] + struct.pack("<I", len(text)) + text + tail

    atlas_json = json.loads(raw(src_blob, parts[1]))
    atlas_json["name"] = atlas_name
    if "imagePath" in atlas_json:
        atlas_json["imagePath"] = atlas_name + "_tex.png"
    atlas_bytes = json.dumps(atlas_json, ensure_ascii=False, separators=(",", ":")).encode()

    buf = io.BytesIO(); atlas.save(buf, format="PNG")
    return src_blob[:12] + b"".join(struct.pack("<I", len(p)) + p
                                    for p in [pack(src_blob, new_skel), pack(src_blob, atlas_bytes),
                                              pack(src_blob, buf.getvalue())])


def recolour(container, lut):
    """-> (new atlas image, regions count, alpha-identical flag)"""
    atlas = Image.open(io.BytesIO(container["image"])).convert("RGBA")
    src = np.asarray(atlas).copy()
    rgb = src[..., :3].astype(np.float32)
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    idx = np.clip(lum, 0, 1) * 255
    uint = idx.astype(np.uint8)
    out = lut[uint]
    result = np.dstack([out, src[..., 3]]).astype(np.uint8)
    same_alpha = np.array_equal(result[..., 3], src[..., 3])
    return Image.fromarray(result, "RGBA"), same_alpha


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-existing", action="store_true", default=True)
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "tools"))
    from street_packed_inventory import decode

    plan = json.loads((KIT / "plan.json").read_text("utf-8-sig"))
    jobs = plan["jobs"]
    chars = {c["heroId"]: c for c in plan["characters"]}
    if args.limit:
        jobs = jobs[: args.limit]

    OUT.mkdir(parents=True, exist_ok=True)
    GAME_FX.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.jsonl"
    done = set()
    if manifest_path.exists():
        for line in manifest_path.read_text("utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["jobId"])

    t0 = time.time()
    built = skipped = 0
    rows = []
    with manifest_path.open("a", encoding="utf-8") as mf:
        for k, job in enumerate(jobs):
            if job["jobId"] in done:
                skipped += 1
                continue
            char = chars.get(job["heroId"], {})
            profile = char.get("profile") or {}
            palette = profile.get("palette") or "未锁定"
            lut = build_lut(palette)
            rec = {"jobId": job["jobId"], "heroId": job["heroId"], "palette": palette,
                   "shared": bool(job.get("sharedAcrossHeroes")), "variants": {}}
            for variant, key_field in (("normal", "targetResourceKey"), ("ez", "targetEzResourceKey")):
                spec = job.get(variant) or {}
                rel = spec.get("path") or next(iter(spec.get("candidates") or []), None)
                if not rel:
                    rec["variants"][variant] = {"status": "missing-source"}
                    continue
                src = ROOT / rel
                if not src.is_file():
                    rec["variants"][variant] = {"status": "missing-source", "path": rel}
                    continue
                blob = src.read_bytes()
                d = decode(src)
                atlas, same_alpha = recolour(d, lut)
                db = job[key_field]
                new = rebuild(blob, atlas, job["targetResourceKey"], db)
                dst = GAME_FX / f"{db}.bin"
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(new)
                chk = decode(dst)
                arm = chk["skeleton"]["armature"][0]
                old_arm = d["skeleton"]["armature"][0]
                a_new = (arm.get("animation") or [{}])[0]
                a_old = (old_arm.get("animation") or [{}])[0]
                clock_ok = (a_new.get("duration") == a_old.get("duration")
                            and chk["skeleton"].get("frameRate") == d["skeleton"].get("frameRate"))
                # The engine only needs the ARMATURE to carry the key (getArmature(db, src)); the
                # animation name is looked up by DragonBones and several originals do not match it
                # either (e.g. armature "shouji" with animation "common_skill_caozhi_02"), so it is
                # recorded but not required to equal the new key.
                ok = (arm["name"] == job["targetResourceKey"]
                      and chk["atlas"]["name"] == db
                      and len(chk["atlas"]["SubTexture"]) == len(d["atlas"]["SubTexture"])
                      and clock_ok)
                rec["variants"][variant] = {
                    "status": "built" if ok else "verify-failed",
                    "db": db, "path": dst.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(new).hexdigest(),
                    "sourceSha256": hashlib.sha256(blob).hexdigest(),
                    "regions": len(chk["atlas"]["SubTexture"]),
                    "frames": a_new.get("duration"),
                    "fps": chk["skeleton"].get("frameRate"),
                    "alphaIdentical": same_alpha,
                    "nameAndClockVerified": ok,
                }
            mf.write(json.dumps(rec, ensure_ascii=False) + "\n"); mf.flush()
            rows.append(rec)
            built += 1
            if built % 10 == 0 or k == len(jobs) - 1:
                el = time.time() - t0
                rate = built / el if el else 0
                print(f"  {built}/{len(jobs)} jobs | {el:.1f}s | {rate:.2f} job/s", flush=True)

    el = time.time() - t0
    summary = {"jobs": len(jobs), "built": built, "skipped": skipped, "seconds": round(el, 1),
               "perJobSeconds": round(el / built, 2) if built else None,
               "out": str(OUT), "containers": str(GAME_FX)}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
