"""Package the current local_game into an installable APK.

Reuses the compiled shell of the last debug build (dex + binary manifest +
resources.arsc) and replaces the whole `assets/` tree with the current
local_game contents, then the caller aligns and signs it with apksigner.

Excluded on purpose:
  * assets/character_idle/   full-resolution idle source frames; the 85 roster
                             heroes are served by character-idle-atlas-data.js
                             (85 atlas packs, 0 png references),
  * assets/street/idle/**/*.png  legacy frames; the atlas only names .webp,
  * tooling files (*.py, *.ps1, README.md, __pycache__, server_data).
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'local_game'
DEFAULT_BASE = ROOT / 'android_offline_shell/app/build/outputs/apk/debug/app-debug.apk'
DEFAULT_OUT = ROOT / 'outputs/apk-build/unsigned.apk'
STORE = {'png', 'jpg', 'jpeg', 'webp', 'bin', 'dbbin', 'mp3', 'ogg', 'wav', 'ttf', 'fnt', 'zip', 'apk', 'db', 'q'}
SKIP_DIRS = {'__pycache__', 'server_data'}
SKIP_EXT = {'.py', '.ps1', '.bak'}
ALIGN_EXTRA_ID = 0xD935


def align_extra(offset: int, name_len: int) -> bytes:
    """Padding extra field so the stored entry data starts on a 4-byte boundary.

    build-tools zipalign refuses archives of 2 GiB or more, and this APK is over
    that, so the alignment zipalign would have added is written here instead.
    """
    base = (offset + 30 + name_len) % 4
    pad = (4 - base) % 4
    length = 4 + pad
    return struct.pack('<HH', ALIGN_EXTRA_ID, length - 4) + b'\0' * (length - 4)


def wanted(path: Path, rel: str) -> bool:
    if path.name == 'README.md':
        return False
    if path.suffix.lower() in SKIP_EXT:
        return False
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if rel.startswith('assets/character_idle/'):
        return False
    if rel.startswith('assets/street/idle/') and path.suffix.lower() == '.png':
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=str(DEFAULT_BASE))
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--game', default=str(GAME))
    args = ap.parse_args()
    base, out, game = Path(args.base), Path(args.out), Path(args.game)
    out.parent.mkdir(parents=True, exist_ok=True)

    files = []
    for path in game.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(game).as_posix()
        if wanted(path, rel):
            files.append((rel, path))
    files.sort(key=lambda r: r[0])
    total = sum(p.stat().st_size for _, p in files)

    written = 0
    stored = 0
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
            ext = path.suffix.lower().lstrip('.')
            # The app's HTTP server has assets/ as its web root, and the game
            # requests /assets/street/... for the reskin tree, so the ZIP layout
            # must mirror local_game exactly: local_game/<rel> -> assets/<rel>.
            name = 'assets/' + rel
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 4, 12, 0, 0))
            # AssetHttpServer serves every file through AssetManager.openFd(),
            # which only works on uncompressed (STORED) assets - the Gradle build
            # used noCompress for exactly this reason.
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o644 << 16
            zi.extra = align_extra(zout.fp.tell(), len(name.encode('utf-8')))
            zout.writestr(zi, path.read_bytes())
            written += 1
            if zi.compress_type == zipfile.ZIP_STORED:
                stored += path.stat().st_size
            if written % 500 == 0:
                print(f'  packed {written}/{len(files)} files...', flush=True)

    size = out.stat().st_size
    print(f'PACKED {out} files={len(files)} rawGB={total / 1e9:.2f} apkGB={size / 1e9:.2f} storedGB={stored / 1e9:.2f}')


if __name__ == '__main__':
    main()
