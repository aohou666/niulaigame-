"""Reject single-gesture generation for authored multiple positive hit markers."""
import json
from pathlib import Path

def check_single_gesture(hero_ids, audit_path):
    audit = json.loads(Path(audit_path).read_text('utf8'))
    if not audit.get('complete'):
        raise ValueError('Complete frozen native-event audit required')
    failures = []
    for row in audit['records']:
        if not any(row['model'].startswith(f'hero_{hid:03}_') for hid in hero_ids):
            continue
        hits = sorted(set(e['frame0'] for e in row['events']
                          if e['name'] in ('pia', 'zd') and e['frame0'] > 0))
        if len(hits) > 1:
            failures.append(f"{row['model']}/{row['action']}: {hits}")
    if failures:
        raise ValueError('Single-gesture template cannot represent multiple native hits; '
                         'prepare and review explicit multi-hit choreography first: '
                         + '; '.join(failures))
