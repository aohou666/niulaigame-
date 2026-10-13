"""Build a complete game ZIP from tracked source plus release-only assets."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'migration-packages'
out.mkdir(exist_ok=True)
bundle = out / 'game-history.bundle'
subprocess.run(['git', 'bundle', 'create', str(bundle), '--all'], cwd=root, check=True)
paths = {}
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode('utf-8').split('\0')
for name in tracked:
    if name and not name.startswith('workbenches/'):
        paths[name] = root / name
for folder in ['local_game/resource', '.tools/python']:
    for path in (root / folder).rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts or 'site-packages' in path.parts:
            continue
        paths[path.relative_to(root).as_posix()] = path
for name in ['offline-replica-save.json', 'offline-replica-config.json', 'offline-runtime-catalog.json']:
    path = root / 'pc_server_data' / name
    if path.is_file():
        paths[path.relative_to(root).as_posix()] = path
paths['game-history.bundle'] = bundle
manifest = {'date': '2026-10-13', 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(), 'files': []}
archive = out / 'game-development-20261013.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as package:
    for index, (name, source) in enumerate(sorted(paths.items()), 1):
        digest = hashlib.sha256()
        size = 0
        with source.open('rb') as stream, package.open('OfflineGame/' + name, 'w', force_zip64=True) as target:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
                size += len(chunk)
                target.write(chunk)
        manifest['files'].append({'path': name, 'size': size, 'sha256': digest.hexdigest()})
        if index % 3000 == 0:
            print(f'Packed {index}/{len(paths)} files', flush=True)
    payload = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
    package.writestr('OfflineGame/migration-manifest.json', payload)
(out / 'game-development-manifest.json').write_bytes(payload)
with zipfile.ZipFile(archive) as package:
    if package.testzip() is not None:
        raise SystemExit('ZIP CRC verification failed')
digest = hashlib.sha256()
with archive.open('rb') as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(chunk)
(out / (archive.name + '.sha256')).write_text(digest.hexdigest() + '  ' + archive.name + '\n', encoding='ascii')
print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'files': len(paths), 'sha256': digest.hexdigest()}), flush=True)
