"""Ultimate-skill video matting, retiming and packaging.

Ports the local Greenscreen-Frame-Studio-Eraser keying algorithm byte-for-byte
(border-band background sampling + RGB-distance threshold + generic-green rule)
so the batch result equals what the local tool produces for a frame.

Pipeline per hero video:
  1. decode the 96-frame 24fps mp4 straight into numpy (no temp PNGs),
  2. chroma-key every frame with the local tool's algorithm,
  3. find the non-empty content window,
  4. resample that window to the ORIGINAL container's frame count,
  5. trim each frame to its alpha box and store WebP + box offsets,
  6. write meta JSON consumed by street-ultimate.js.

Usage:
  python tools/street_ultimate_mat.py plan                     # build plan
  python tools/street_ultimate_mat.py run [--ids 1,3] [--quality 90]
  python tools/street_ultimate_mat.py qa --ids 1,3             # contact sheets
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = ROOT / 'outputs/street-reskin/ultimate-keys-86/videos'
SPEC = ROOT / 'outputs/_ult86.json'
PACKED = ROOT / 'art-migration/packed-art.jsonl'
FX_PREVIEW = ROOT / 'local_game/fx-preview-data.js'
GAME = ROOT / 'local_game'
OUT = GAME / 'assets/street/ultimate'
PLAN = ROOT / 'outputs/street-reskin/ultimate-keys-86/ultimate_plan.json'
SIZE = 720
DEFAULT_THRESHOLD = 64  # local tool default (app.js project.keyThreshold)


# ---------------------------------------------------------------- plan ----

def load_spec() -> dict[int, dict]:
    rows = json.loads(SPEC.read_text('utf-8-sig'))
    return {int(r['id']): r for r in rows}


def load_fx_ult_keys() -> dict[int, list[str]]:
    text = FX_PREVIEW.read_text('utf8')
    rows = json.loads(text[text.find('['):text.rfind(']') + 1])
    out: dict[int, list[str]] = {}
    for row in rows:
        if row.get('slot') == '大招':
            out.setdefault(int(row['heroId']), []).append(row['key'])
    return out


def load_container_durations() -> dict[str, tuple[int, int]]:
    """container key -> (frames, fps) for the normal (non-EZ) payload."""
    dur: dict[str, tuple[int, int]] = {}
    for line in PACKED.open(encoding='utf8'):
        row = json.loads(line)
        key = Path(row['path']).name.rsplit('_', 1)[0]
        if key in dur:
            continue
        for arm in row['armatures']:
            for anim in arm['animations']:
                if anim.get('frames') is None:
                    continue
                dur[key] = (int(anim['frames']), int(arm['fps'] or 24))
    return dur


def build_plan() -> dict:
    spec = load_spec()
    ult_keys = load_fx_ult_keys()
    durations = load_container_durations()
    plan = {'videos': [], 'unmapped': []}
    for path in sorted(VIDEO_DIR.glob('*.mp4')):
        hid = int(path.name[:3])
        name = path.name[4:].replace('_720p.mp4', '')
        keys = ult_keys.get(hid, [])
        candidates = [(k, *durations[k]) for k in keys if k in durations]
        row = {
            'id': hid,
            'name': name,
            'video': path.relative_to(ROOT).as_posix(),
            'spec': spec.get(hid),
            'keys': keys,
            'mainKey': None,
            'origFrames': None,
            'origFps': None,
        }
        if candidates:
            # the main ultimate layer is the longest-running container layer
            key, frames, fps = max(candidates, key=lambda r: r[1] / r[2])
            row.update(mainKey=key, origFrames=frames, origFps=fps)
        elif hid in spec:
            row.update(mainKey=spec[hid]['model'], origFrames=int(spec[hid]['frames']), origFps=int(spec[hid]['fps']))
        if row['origFrames'] is None:
            plan['unmapped'].append(row)
        else:
            plan['videos'].append(row)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1), 'utf8')
    return plan


# --------------------------------------------------------------- matte ----

def _hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorised hue/saturation/value (all 0..1) for uint8 RGB."""
    px = rgb.astype(np.float32) / 255.0
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx = px.max(axis=2)
    mn = px.min(axis=2)
    diff = mx - mn
    hue = np.zeros_like(mx)
    safe = diff > 1e-6
    idx = safe & (mx == r)
    hue[idx] = ((g[idx] - b[idx]) / diff[idx]) % 6.0
    idx = safe & (mx == g)
    hue[idx] = (b[idx] - r[idx]) / diff[idx] + 2.0
    idx = safe & (mx == b)
    hue[idx] = (r[idx] - g[idx]) / diff[idx] + 4.0
    hue = (hue / 6.0) % 1.0
    sat = np.where(mx > 1e-6, diff / np.maximum(mx, 1e-6), 0.0)
    return hue, sat, mx


def _background(rgb: np.ndarray) -> np.ndarray:
    """Exact port of app.js sampleBackground()."""
    h, w = rgb.shape[:2]
    band = max(1, min(16, w // 2, h // 2))
    sub = rgb[..., :3]
    border = np.concatenate([
        sub[:band, :, :].reshape(-1, 3),
        sub[h - band:, :, :].reshape(-1, 3),
        sub[band:h - band, :band, :].reshape(-1, 3),
        sub[band:h - band, w - band:, :].reshape(-1, 3),
    ]).astype(np.int32)
    greenish = (border[:, 1] > border[:, 0] + 20) & (border[:, 1] > border[:, 2] + 20)
    source = border[greenish] if greenish.any() else border
    if len(source) == 0:
        return np.array([0, 255, 0], np.int32)
    return np.median(source, axis=0).astype(np.int32)


def _family(bg: np.ndarray) -> str | None:
    h, s, v = _hsv(bg.reshape(1, 1, 3).astype(np.uint8))
    hue, sat, val = float(h[0, 0]), float(s[0, 0]), float(v[0, 0])
    if val < 0.2 or sat < 0.3:
        return None
    if 0.18 <= hue <= 0.48:
        return 'green'
    # Magenta/pink key colours land around 300 deg (0.83); pure red 0 deg also
    # appears when the backdrop is keyed from a compressed frame.
    if hue >= 0.72 or hue <= 0.10:
        return 'magenta'
    return None


def matte_frame(rgb: np.ndarray, threshold: int) -> tuple[np.ndarray, str | None]:
    """Local tool keying (exact port) plus backdrop-family removal and despill.

    The studio tool removes pixels within an RGB distance of the sampled border
    colour plus a bright-green rule. MiniMax output sometimes paints a darker
    green (or magenta) card behind the effect, which that rule leaves as a solid
    block. On top of the ported rules this adds a hue-family removal limited to
    darker shades of the sampled backdrop and a despill of remaining edges; both
    use the sampled backdrop family only, so the opposite-colour art is intact.
    """
    h, w = rgb.shape[:2]
    sub = rgb[..., :3]
    bg = _background(rgb)
    px = sub.astype(np.int32)
    dist = np.sqrt(((px - bg) ** 2).sum(axis=2))
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    generic_green = (g >= 110) & (g - r >= 40) & (g - b >= 40)
    bg_mask = rgb[..., 3] < 8 if rgb.shape[2] == 4 else np.zeros((h, w), bool)
    mask = (dist <= threshold) | generic_green | bg_mask
    family = _family(bg)
    if family:
        bh, bs, bv = _hsv(bg.reshape(1, 1, 3).astype(np.uint8))
        bh, bv = float(bh[0, 0]), float(bv[0, 0])
        hue, sat, val = _hsv(sub)
        dh = np.abs(hue - bh)
        dh = np.minimum(dh, 1.0 - dh)
        mask |= (dh <= 0.055) & (sat >= 0.30) & (val <= bv * 0.78)
        # Model output sometimes paints a flat card of the key colour behind the
        # effect. Its shade can sit just outside the border colour's distance
        # (e.g. a brighter magenta), so it is also keyed from the dominant flat
        # colour inside the frame.
        family_pixels = (dh <= 0.06) & (sat >= 0.35)
        if family_pixels.sum() > 0.02 * h * w:
            key2 = np.median(sub[family_pixels].astype(np.int32), axis=0)
            dist2 = np.sqrt(((px - key2) ** 2).sum(axis=2))
            mask |= dist2 <= threshold

    out = rgb.copy()
    visible = ~mask
    if family == 'green':
        excess = np.clip(g - np.maximum(r, b), 0, 255)
        out[..., 1] = np.where(visible, g - excess * 0.75, g).astype(np.uint8)
    elif family == 'magenta':
        excess = np.clip(np.minimum(r, b) - g, 0, 255)
        out[..., 0] = np.where(visible, r - excess * 0.75, r).astype(np.uint8)
        out[..., 2] = np.where(visible, b - excess * 0.75, b).astype(np.uint8)
    out[..., 3] = np.where(mask, 0, 255).astype(np.uint8)
    return out, family


def decode_frames(video: Path) -> list[np.ndarray]:
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
           '-f', 'rawvideo', '-pix_fmt', 'rgba', '-fps_mode', 'passthrough', '-']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    raw = np.frombuffer(proc.stdout, np.uint8)
    frame_bytes = SIZE * SIZE * 4
    n = raw.size // frame_bytes
    frames = raw[:n * frame_bytes].reshape(n, SIZE, SIZE, 4)
    return [frames[i] for i in range(n)]


def content_window(alpha_list: list[np.ndarray], min_ratio: float = 0.0015) -> tuple[int, int]:
    cover = [float((a > 0).mean()) for a in alpha_list]
    idx = [i for i, c in enumerate(cover) if c >= min_ratio]
    if not idx:
        return 0, len(alpha_list) - 1
    return idx[0], idx[-1]


def pick_indices(first: int, last: int, count: int) -> list[int]:
    if count <= 1:
        return [first]
    span = last - first
    return [first + round(span * i / (count - 1)) for i in range(count)]


def process(row: dict, threshold: int, quality: int, out_root: Path) -> dict:
    video = ROOT / row['video']
    frames = decode_frames(video)
    mattes = [matte_frame(f, threshold) for f in frames]
    alphas = [m[0][..., 3] for m in mattes]
    families = sorted({m[1] for m in mattes if m[1]})
    first, last = content_window(alphas)
    picks = pick_indices(first, last, int(row['origFrames']))
    hero_dir = out_root / f"{row['id']:03d}"
    hero_dir.mkdir(parents=True, exist_ok=True)
    boxes, files, bytes_total = [], [], 0
    for i, src in enumerate(picks):
        img = Image.fromarray(mattes[src][0], 'RGBA')
        box = img.getchannel('A').getbbox()
        if box:
            x0, y0, x1, y1 = box
            crop = img.crop(box)
        else:
            x0 = y0 = x1 = y1 = 0
            crop = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        name = f'f{i:03d}.webp'
        target = hero_dir / name
        crop.save(target, 'WEBP', quality=quality, method=4, alpha_quality=100)
        bytes_total += target.stat().st_size
        boxes.append([int(x0), int(y0), int(x1 - x0), int(y1 - y0)])
        files.append(name)
    meta = {
        'heroId': row['id'],
        'name': row['name'],
        'model': row['mainKey'],
        'keys': row['keys'],
        'mainKey': row['mainKey'],
        'sourceFrames': len(frames),
        'sourceFps': 24,
        'contentWindow': [first, last],
        'frames': len(picks),
        'fps': int(row['origFps']),
        'duration': round(len(picks) / int(row['origFps']), 4),
        'canvas': SIZE,
        'files': files,
        'boxes': boxes,
        'keyThreshold': threshold,
        'backdropFamilies': families,
        'webpQuality': quality,
        'bytes': bytes_total,
    }
    (hero_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf8')
    return {'id': row['id'], 'name': row['name'], 'frames': len(picks), 'fps': meta['fps'],
            'content': [first, last], 'bytes': bytes_total, 'path': hero_dir.relative_to(ROOT).as_posix()}


# ------------------------------------------------------------------ qa ----

def contact_sheet(hero_meta: Path, dst: Path, step: int = 8) -> None:
    meta = json.loads(hero_meta.read_text('utf8'))
    d = hero_meta.parent
    picks = range(0, meta['frames'], step)
    cols = 6
    rows = (len(list(picks)) + cols - 1) // cols
    cell = 240
    sheet = Image.new('RGB', (cols * cell, rows * cell), (18, 20, 24))
    for n, i in enumerate(range(0, meta['frames'], step)):
        frame = Image.open(d / meta['files'][i]).convert('RGBA')
        x, y, w, h = meta['boxes'][i]
        big = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        big.alpha_composite(frame, (x, y))
        tile = Image.new('RGB', (SIZE, SIZE), (24, 60, 90))
        tile.paste(big, (0, 0), big)
        tile = tile.resize((cell, cell), Image.LANCZOS)
        sheet.paste(tile, ((n % cols) * cell, (n // cols) * cell))
    dst.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dst)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['plan', 'run', 'qa'])
    ap.add_argument('--ids', default='')
    ap.add_argument('--quality', type=int, default=90)
    ap.add_argument('--threshold', type=int, default=DEFAULT_THRESHOLD)
    ap.add_argument('--out', default=str(OUT))
    args = ap.parse_args()
    if args.mode == 'plan':
        plan = build_plan()
        print(json.dumps({'mapped': len(plan['videos']), 'unmapped': [r['id'] for r in plan['unmapped']]}, ensure_ascii=False))
        return
    plan = json.loads(PLAN.read_text('utf8'))
    wanted = {int(x) for x in args.ids.split(',') if x.strip()} if args.ids else None
    rows = [r for r in plan['videos'] if wanted is None or r['id'] in wanted]
    out_root = Path(args.out)
    results = []
    for row in rows:
        try:
            results.append(process(row, args.threshold, args.quality, out_root))
            print(json.dumps(results[-1], ensure_ascii=False), flush=True)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({'id': row['id'], 'error': str(exc)}, ensure_ascii=False), flush=True)
    if args.mode == 'run':
        total = sum(r.get('bytes', 0) for r in results)
        report = {'heroes': len(results), 'totalMB': round(total / 1e6, 1),
                  'errors': [r for r in results if 'error' in r], 'rows': results}
        (ROOT / 'outputs/street-reskin/ultimate-verify/matte-report.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=1), 'utf8')
        print(json.dumps({'heroes': len(results), 'totalMB': report['totalMB']}, ensure_ascii=False))
    if args.mode == 'qa':
        for r in rows:
            meta = out_root / f"{r['id']:03d}" / 'meta.json'
            if meta.exists():
                contact_sheet(meta, ROOT / f"outputs/street-reskin/ultimate-verify/contact-{r['id']:03d}.png")
        print(json.dumps({'qa': [r['id'] for r in rows]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
