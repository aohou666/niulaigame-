"""Reject single-gesture generation for authored multiple positive hit markers."""
import hashlib,json
from pathlib import Path

def check_single_gesture(hero_ids, audit_path):
    audit = json.loads(Path(audit_path).read_text('utf8'))
    if not audit.get('complete'):
        raise ValueError('Complete frozen native-event audit required')
    failures = []
    root=Path(__file__).resolve().parents[1]
    review_path=root/'art-migration/choreography/hero002-adjacent-markers-review.json'
    review=json.loads(review_path.read_text('utf8')) if review_path.exists() else None
    def reviewed_cluster(row):
        if not review or review.get('status')!='reviewed-single-gesture-event-cluster':return False
        if row['model'] not in review.get('modelsVisuallyReviewed',[]) or row['action']!=review.get('action'):return False
        if review.get('nativeAuditSha256')!=hashlib.sha256(Path(audit_path).read_bytes()).hexdigest():return False
        actual=[{'name':e['name'],'frame0':e['frame0']} for e in row['events'] if e['name'] in ('pia','zd')]
        if actual!=review.get('events') or review.get('runtimeEventsMayBeRemoved') is not False:return False
        if not review.get('evidenceFiles'):return False
        for evidence in review['evidenceFiles']:
            file=root/evidence['path']
            if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=evidence['sha256']:return False
        return True
    for row in audit['records']:
        if not any(row['model'].startswith(f'hero_{hid:03}_') for hid in hero_ids):
            continue
        hits = sorted(set(e['frame0'] for e in row['events']
                          if e['name'] in ('pia', 'zd') and e['frame0'] > 0))
        if len(hits) > 1 and not reviewed_cluster(row):
            failures.append(f"{row['model']}/{row['action']}: {hits}")
    if failures:
        raise ValueError('Single-gesture template cannot represent multiple native hits; '
                         'prepare and review explicit multi-hit choreography first: '
                         + '; '.join(failures))
