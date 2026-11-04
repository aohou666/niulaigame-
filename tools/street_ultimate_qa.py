"""QA report for the matted ultimate assets.

Samples frames per hero and reports size, content window, frame boxes and a
key-colour fringe metric, so heroes that still show green/magenta spill can be
found without opening every contact sheet.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'local_game/assets/street/ultimate'
OUT = ROOT / 'outputs/street-reskin/ultimate-verify/qa-matte.json'


def main() -> dict:
    rows = []
    for meta_path in sorted(ASSETS.glob('*/meta.json')):
        meta = json.loads(meta_path.read_text('utf8'))
        d = meta_path.parent
        n = len(meta['files'])
        picks = sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1})
        fringe = 0
        visible = 0
        for i in picks:
            im = Image.open(d / meta['files'][i]).convert('RGBA')
            a = np.asarray(im).astype(np.int16)
            m = a[..., 3] > 0
            r, g, b = a[..., 0], a[..., 1], a[..., 2]
            if 'green' in meta.get('backdropFamilies', []):
                bad = m & (g - np.maximum(r, b) > 30) & (g > 80)
            else:
                bad = m & (np.minimum(r, b) - g > 30) & (np.minimum(r, b) > 80)
            fringe += int(bad.sum())
            visible += int(m.sum())
        rows.append({
            'id': meta['heroId'], 'name': meta['name'], 'frames': meta['frames'], 'fps': meta['fps'],
            'bytes': meta['bytes'], 'content': meta['contentWindow'],
            'families': meta.get('backdropFamilies'),
            'fringePermille': round(fringe / max(1, visible) * 1000, 2),
            'maxBox': max(meta['boxes'], key=lambda b: b[2] * b[3]),
        })
    total = sum(r['bytes'] for r in rows)
    report = {'heroes': len(rows), 'totalMB': round(total / 1e6, 1),
              'avgMB': round(total / max(1, len(rows)) / 1e6, 2),
              'fringeTop': sorted(rows, key=lambda r: -r['fringePermille'])[:10],
              'rows': rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf8')
    return {'heroes': report['heroes'], 'totalMB': report['totalMB'], 'avgMB': report['avgMB'],
            'fringeTop': [(r['id'], r['name'], r['fringePermille']) for r in report['fringeTop']]}


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False))
