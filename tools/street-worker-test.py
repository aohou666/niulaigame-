"""Exercise deadline isolation and candidate-QA failure with a fake queue in temp dirs."""
import json,runpy,sys,tempfile,types
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class EndIteration(Exception):pass
def scenario(past):
 with tempfile.TemporaryDirectory(prefix='street-worker-test-') as td:
  root=Path(td);base=root/'art-migration/generation';out=root/'outputs/street-reskin';out.mkdir(parents=True);base.mkdir(parents=True);calls=[]
  ids=['own-pending','own-running'] if past else ['own-pending']
  for i,id in enumerate(ids):
   folder=base/str(i);folder.mkdir();(folder/'job.json').write_text(json.dumps({'promptId':id,'status':'submitted'}));(folder/'design.json').write_text(json.dumps({'heroId':1,'action':'attack'}))
  def request(endpoint,data=None):
   calls.append([endpoint,data])
   if endpoint.startswith('/history'):return {'own-pending':{}}
   if endpoint=='/queue' and data is None:return {'queue_pending':[[0,'own-pending'],[1,'foreign-job']] if past else [],'queue_running':[[2,'own-running']] if past else []}
   return {}
  def collect(folder):
   assert not past,'deadline must precede collection';p=folder/'job.json';d=json.loads(p.read_text());d['status']='generated-unreviewed';p.write_text(json.dumps(d));return True
  def qa():raise KeyError('action')
  def stop(_):raise EndIteration()
  fakeComfy=types.SimpleNamespace(ROOT=root,request=request,collect=collect);fakeQA=types.SimpleNamespace(run=qa)
  with patch.dict(sys.modules,{'street_comfy':fakeComfy,'street_candidate_qa':fakeQA,'time':types.SimpleNamespace(sleep=stop)}),patch.object(sys,'argv',['worker','--until-utc','2000-01-01T00:00:00+00:00' if past else '2999-01-01T00:00:00+00:00']):
   try:runpy.run_path(str(ROOT/'tools/street_generation_worker.py'),run_name='__main__')
   except EndIteration:assert not past
  state=json.loads((out/'generation-worker.json').read_text())
  if past:
   assert state['status']=='deadline-stopped';assert ['/queue',{'delete':['own-pending']}] in calls;assert ['/interrupt',{}] in calls;assert 'foreign-job' not in state['cancelledPending'];assert not any(c[0].startswith('/history') for c in calls)
  else:assert state['status']=='active' and any(c[0]=='/queue' for c in calls),'candidate QA failure must not stop monitoring'
  return {'scenario':'deadline-before-collection-and-foreign-queue-isolation' if past else 'candidate-QA-exception-does-not-disable-deadline-monitor','pass':True,'calls':calls,'status':state['status']}
report={'pass':True,'tests':[scenario(True),scenario(False)]};out=ROOT/'art-migration/versions/0.37.0';out.mkdir(exist_ok=True);(out/'worker-runtime.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
