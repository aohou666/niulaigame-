"""Flag pose jumps from real source frames; numerical flags never approve animation."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def measure(folder):
    folder=folder.resolve()
    job = json.loads((folder / 'job.json').read_text('utf8'))
    files = [ROOT / row['path'] for row in job.get('outputs', [])]
    arrays = []
    for file in files:
        with Image.open(file) as im:
            arrays.append(np.asarray(im.convert('RGB').resize((128, 128)), dtype=np.float32))
    delta = [float(np.abs(y-x).mean()) for x, y in zip(arrays, arrays[1:])]
    total = sum(delta)
    top = sum(sorted(delta, reverse=True)[:4]) / max(total, 1e-9)
    median = float(np.median(delta)) if delta else 0
    jumps = [i+1 for i, value in enumerate(delta) if value > max(2, median*12)]
    # Deliberate anticipation/recovery holds lower the median even in fluid clips.
    # Count meaningful transition frames rather than rejecting a low median itself.
    significant = sum(value > max(.5, max(delta, default=0)*.1) for value in delta)
    flag = len(files) < 20 or top > .65 or significant < 10
    return {'source': folder.relative_to(ROOT).as_posix(), 'frames': len(files),
            'sourceSignature': hashlib.sha256(''.join(row['sha256'] for row in job.get('outputs', [])).encode()).hexdigest(),
            'meanAbsoluteRgbDelta128': [round(x, 5) for x in delta],
            'medianDelta': round(median, 5), 'topFourDeltaShare': round(top, 5),
            'jumpFrames': jumps, 'significantTransitionFrames': significant,
            'algorithmVersion':'0.49.0', 'requiresTemporalReview': flag,
            'interpretation': 'screening only; no automatic animation approval or rejection'}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('names', nargs='*')
    p.add_argument('--runtime', action='store_true')
    p.add_argument('--report', required=True)
    a = p.parse_args()
    rows = []
    if a.runtime:
        data = json.loads((ROOT/'local_game/street-body-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))
        for hero in data['characters']:
            design = json.loads((ROOT/hero['source']/'body-design.json').read_text('utf8'))
            row = measure(ROOT/design['sourceBodyJob'])
            row['heroId'] = hero['id']
            rows.append(row)
    rows.extend(measure(ROOT/'art-migration/generation'/name) for name in a.names)
    report = {'method': '128x128 RGB consecutive-frame absolute delta; four-jump concentration and static-hold screening',
              'manualReviewRequired': True, 'rows': rows, 'flagged': sum(row['requiresTemporalReview'] for row in rows)}
    target = ROOT/a.report
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n','utf8')
    print(json.dumps({'rows': len(rows), 'flagged': report['flagged'], 'report': str(target)}))

if __name__ == '__main__':
    main()
