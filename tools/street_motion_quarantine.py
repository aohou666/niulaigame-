"""Separate installed mappings from continuous-motion approval after the audit."""
import json
from pathlib import Path
from street_atomic import atomic_write_text

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'outputs/street-reskin/resume-motion-continuity.json'
audit=json.loads(source.read_text('utf8'))
rows={r['heroId']:r for r in audit['rows'] if 'heroId' in r}
file=ROOT/'local_game/street-body-data.js'
data=json.loads(file.read_text('utf8').split('=',1)[1].strip().rstrip(';'))
quarantined=[];models=set()
for cfg in data['characters']:
    row=rows[cfg['id']]
    cfg['temporalQuality']='continuous-motion-revalidation-pending'
    if row['topFourDeltaShare']>.65:
        cfg['qualityQuarantineActions']=['gongji','jineng']
        cfg['qualityQuarantineReason']='More than65% of consecutive-frame RGB change concentrated in four jumps; conservative hold pending continuous-motion regeneration/review'
        quarantined.append(cfg['id'])
    models.update(cfg['models'])
data['version']='0.48.0'
atomic_write_text(file,'window.StreetBodyData='+json.dumps(data,separators=(',',':'))+';\n')
ledger=ROOT/'art-migration/packed-art.jsonl'
packed=[json.loads(line) for line in ledger.read_text('utf8').splitlines()]
for row in packed:
    if Path(row['path']).stem.rsplit('_',1)[0] not in models:continue
    old=row.get('verifiedAnimationReplacements',[])
    moved=[a for a in old if a in ['gongji','jineng']]
    row['verifiedAnimationReplacements']=[a for a in old if a not in moved]
    row['runtimeMappedAnimationReplacements']=sorted(set(row.get('runtimeMappedAnimationReplacements',[])+moved))
    row['continuousMotionReview']='pending; native timing and distinct image hashes do not prove complete animation'
atomic_write_text(ledger,'\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in packed)+'\n')
heroes=json.loads((ROOT/'local_game/character-art-data.js').read_text('utf8').split('=',1)[1].strip().rstrip(';'))['heroes']
report={'version':'0.48.0','all85ReviewedForBindingAndTemporalStatus':True,
        'installedTargetAttackSkillMappings':sum(c['id']!=13 for c in data['characters']),
        'continuousTargetAttackSkillApprovals':0,'quarantinedTargetAttackSkillMappings':sum(i!=13 for i in quarantined),
        'quarantinedIds':quarantined,'automaticScreeningIsNotManualApproval':True,
        'historicalReportsPreserved':True,'rows':[]}
for hid in sorted(map(int,heroes)):
    row=rows.get(hid)
    report['rows'].append({'heroId':hid,'installedAttackSkillMapping':row is not None,
        'temporallyApproved':False,'qualityStatus':'not-generated' if row is None else 'quarantined-pending-review' if hid in quarantined else 'continuous-motion-review-pending',
        'source':row['source'] if row else None,'screening':row})
out=ROOT/'art-migration/versions/0.48.0';out.mkdir(parents=True,exist_ok=True)
(out/'motion-quality-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
