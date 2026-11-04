"""Package the current local_game into an installable APK.

Reuses the compiled shell of the last debug build (dex + binary manifest +
resources.arsc) and replaces the whole `assets/` tree with the current
local_game contents; the caller aligns and signs it with apksigner.

Two payload modes:

  --slim (default)  drop content the engine can never request:
      * street/fx containers that are not registered in street-fx-table.js,
      * HD effect containers whose `_ez` twin is registered (DB_GLOBAL
        .ENABLE_AUTO_EZ resolves every effect through `_ez` first),
      * originals that StreetFXRedirect rewrites to a street container,
    and optionally re-encode street character/skin WebP and losslessly
    recompress large PNGs.

  --full            pack everything (previous 2.05 GiB build).

Always excluded: assets/character_idle (idle source frames, the atlas covers
the roster), assets/street/idle PNGs (legacy; atlas names .webp), tooling files.

Every asset is stored uncompressed: AssetHttpServer serves files through
AssetManager.openFd(), which only works on stored entries. zipalign cannot open
archives >= 2 GiB, so the 4-byte alignment is written here.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'local_game'
DEFAULT_BASE = ROOT / 'android_offline_shell/app/build/outputs/apk/debug/app-debug.apk'
DEFAULT_OUT = ROOT / 'outputs/apk-build/unsigned.apk'
SKIP_DIRS = {'__pycache__', 'server_data'}
SKIP_EXT = {'.py', '.ps1', '.bak'}
ALIGN_EXTRA_ID = 0xD935
EFFECT_AREAS = ('resource/assets/effect', 'resource/assets/ui_effect', 'assets/street/fx')


def align_extra(offset: int, name_len: int) -> bytes:
    """Padding extra field so the stored entry data starts on a 4-byte boundary."""
    base = (offset + 30 + name_len) % 4
    pad = (4 - base) % 4
    length = 4 + pad
    return struct.pack('<HH', ALIGN_EXTRA_ID, length - 4) + b'\0' * (length - 4)


def wanted(path: Path, rel: str) -> bool:
    if path.name == 'README.md' or path.suffix.lower() in SKIP_EXT:
        return False
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if rel.startswith('assets/character_idle/'):
        return False
    if rel.startswith('assets/street/idle/') and path.suffix.lower() == '.png':
        return False
    return True


def registered(game: Path) -> tuple[dict[str, str], dict[str, str]]:
    """name -> url from default.res.json plus the street FX table, plus redirects."""
    res = json.loads((game / 'resource/default.res_49784.json').read_text('utf8'))['resources']
    reg = {r['name']: r.get('url', '') for r in res if r.get('name')}
    table = (game / 'street-fx-table.js').read_text('utf8', errors='ignore')

    def block(var: str) -> dict:
        start = table.find(var)
        brace = table.find('{', table.find('=', start))
        depth = 0
        for pos in range(brace, len(table)):
            if table[pos] == '{':
                depth += 1
            elif table[pos] == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(table[brace:pos + 1])
        return {}

    start = table.find('window.StreetFXResources')
    arr_end = table.find(']', table.find('[', start))
    for row in json.loads(table[table.find('[', start):arr_end + 1]):
        reg.setdefault(row['name'], row['url'])
    return reg, block('window.StreetFXRedirect')


def url_path(game: Path, url: str) -> Path:
    return game / url.lstrip('/') if url.startswith('/') else game / 'resource' / url


def dead_assets(game: Path) -> dict[str, tuple[str, int]]:
    """rel path -> (category, bytes) for content the runtime cannot ask for."""
    reg, redirect = registered(game)
    reg_urls = {u.lstrip('/') for u in reg.values() if u}
    dead: dict[str, tuple[str, int]] = {}

    def add(category: str, path: Path) -> None:
        try:
            rel = path.relative_to(game).as_posix()
        except ValueError:
            return
        if path.is_file():
            dead.setdefault(rel, (category, path.stat().st_size))

    for path in (game / 'assets/street/fx').rglob('*'):
        if path.is_file() and path.relative_to(game).as_posix() not in reg_urls:
            add('unregistered-fx', path)
    for name, url in reg.items():
        if not name.endswith('_bin') or name.endswith('_ez_bin') or not url:
            continue
        if (name[:-4] + '_ez_bin') not in reg:
            continue
        path = url_path(game, url)
        if any(area in path.as_posix() for area in EFFECT_AREAS):
            add('hd-with-ez', path)
    for name, url in redirect.items():
        if url:
            add('redirected-original', url_path(game, url))
    return dead


def reencode_webp(path: Path, quality: int) -> bytes | None:
    try:
        from PIL import Image
        with Image.open(path) as im:
            buf = io.BytesIO()
            im.convert('RGBA').save(buf, 'WEBP', quality=quality, method=4, alpha_quality=100)
            return buf.getvalue()
    except Exception as exc:  # noqa: BLE001
        print(f'  webp skip {path.name}: {exc}', flush=True)
        return None


def recompress_png(path: Path) -> bytes | None:
    try:
        from PIL import Image
        with Image.open(path) as im:
            # Keep bit depth, palette and animation state intact: only plain
            # 8-bit still images are safe to rewrite losslessly.
            if im.mode not in ('RGBA', 'RGB', 'P', 'LA', 'L') or im.info.get('duration'):
                return None
            buf = io.BytesIO()
            im.save(buf, 'PNG', optimize=True, compress_level=9)
            return buf.getvalue()
    except Exception as exc:  # noqa: BLE001
        print(f'  png skip {path.name}: {exc}', flush=True)
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=str(DEFAULT_BASE))
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--game', default=str(GAME))
    ap.add_argument('--full', action='store_true', help='pack everything (no slim drops)')
    ap.add_argument('--webp-quality', type=int, default=0,
                    help='re-encode street characters/skins webp at this quality (0 = off)')
    ap.add_argument('--png-min-bytes', type=int, default=0,
                    help='losslessly recompress pngs above this size (0 = off)')
    args = ap.parse_args()
    base, out, game = Path(args.base), Path(args.out), Path(args.game)
    out.parent.mkdir(parents=True, exist_ok=True)

    dead = {} if args.full else dead_assets(game)
    files = []
    dropped = 0
    for path in game.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(game).as_posix()
        if not wanted(path, rel):
            continue
        if rel in dead:
            dropped += path.stat().st_size
            continue
        files.append((rel, path))
    files.sort(key=lambda r: r[0])
    total = sum(p.stat().st_size for _, p in files)
    from collections import Counter
    cats = Counter()
    sizes = Counter()
    for cat, size in dead.values():
        cats[cat] += 1
        sizes[cat] += size
    print(f'FILES {len(files)} rawGB={total / 1e9:.2f} droppedGB={dropped / 1e9:.2f}', flush=True)
    for cat, size in sizes.most_common():
        print(f'  drop {cat}: {size / 1e6:.1f} MB / {cats[cat]} files', flush=True)

    def transform(rel: str, path: Path) -> bytes:
        ext = path.suffix.lower()
        if ext == '.webp' and args.webp_quality and (
                rel.startswith('assets/street/characters/') or rel.startswith('assets/street/skins/')):
            data = reencode_webp(path, args.webp_quality)
            if data is not None:
                return data
        if ext == '.png' and args.png_min_bytes and path.stat().st_size >= args.png_min_bytes:
            data = recompress_png(path)
            if data is not None:
                return data
        return path.read_bytes()

    written = 0
    payload = 0
    with zipfile.ZipFile(base) as zin, zipfile.ZipFile(out, 'w', allowZip64=True) as zout:
        for info in zin.infolist():
            if info.filename.startswith('assets/') or info.filename.startswith('META-INF/'):
                continue
            data = zin.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_STORED if info.filename.endswith('.dex') or info.filename in (
                'resources.arsc', 'AndroidManifest.xml') else info.compress_type
            zi.external_attr = info.external_attr
            if zi.compress_type == zipfile.ZIP_STORED:
                zi.extra = align_extra(zout.fp.tell(), len(info.filename.encode('utf-8')))
            zout.writestr(zi, data)
        for rel, path in files:
            name = 'assets/' + rel
            data = transform(rel, path)
            payload += len(data)
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 4, 12, 0, 0))
            # AssetManager.openFd only works on uncompressed entries.
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o644 << 16
            zi.extra = align_extra(zout.fp.tell(), len(name.encode('utf-8')))
            zout.writestr(zi, data)
            written += 1
            if written % 1000 == 0:
                print(f'  packed {written}/{len(files)} files, payloadGB={payload / 1e9:.2f}', flush=True)

    size = out.stat().st_size
    print(f'PACKED {out} files={len(files)} payloadGB={payload / 1e9:.2f} apkGB={size / 1e9:.2f}')


if __name__ == '__main__':
    main()
