"""Collect this task's real ComfyUI results until the authorized local-day deadline."""
from __future__ import annotations
import argparse,datetime,json,time,traceback
from pathlib import Path
from street_comfy import ROOT,request,collect
from street_candidate_qa import run as candidate_qa
p=argparse.ArgumentParser();p.add_argument('--until-utc',required=True);a=p.parse_args()
deadline=datetime.datetime.fromisoformat(a.until_utc);base=ROOT/'art-migration/generation';out=ROOT/'outputs/street-reskin'
while True:
 try:
  records={}
  for folder in base.iterdir():
   f=folder/'job.json'
   if f.exists():records[json.loads(f.read_text('utf8'))['promptId']]=(folder,json.loads(f.read_text('utf8')))
  history=request('/history?max_items=1000')
  for prompt,(folder,job) in records.items():
   if job['status']=='submitted' and prompt in history:collect(folder)
  candidate_qa()
  q=request('/queue');now=datetime.datetime.now(datetime.timezone.utc)
  counts={}
  for folder,job in records.values():
   current=json.loads((folder/'job.json').read_text('utf8'));counts[current['status']]=counts.get(current['status'],0)+1
  status={'checkedUtc':now.isoformat(),'deadlineUtc':deadline.isoformat(),'jobs':counts,'running':[r[1] for r in q['queue_running']],'pending':len(q['queue_pending']),'status':'active'}
  if now>=deadline:
   ours=[r[1] for r in q['queue_pending'] if r[1] in records]
   if ours:request('/queue',{'delete':ours})
   if any(r[1] in records for r in q['queue_running']):request('/interrupt',{})
   status.update(status='deadline-stopped',cancelledPending=ours)
  (out/'generation-worker.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n','utf8')
  if status['status']=='deadline-stopped':break
 except Exception as e:
  print(type(e).__name__,str(e)[:500],flush=True)
 time.sleep(45)
