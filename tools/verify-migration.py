import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'migration-manifest.json').read_text('utf-8'))
errors = []
for item in manifest['files']:
    path = root / item['path']
    if not path.is_file() or path.stat().st_size != item['size']:
        errors.append(item['path'])
        continue
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != item['sha256']:
        errors.append(item['path'])
print(f"Checked {len(manifest['files'])} files; errors={len(errors)}")
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
