"""Requeue only this task's unstarted owned prompts; retain cancellation/requeue provenance."""
import argparse,json,time
from street_comfy import ROOT,request
p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--reason',required=True);a=p.parse_args()
for name in reversed(a.names):
 folder=ROOT/'art-migration/generation'/name;file=folder/'job.json';record=json.loads(file.read_text('utf8'));queue=request('/queue');pending={r[1] for r in queue['queue_pending']}
 if record['status']!='submitted' or record['promptId'] not in pending:print(name,'unchanged (already started/completed)');continue
 assert record['provider']=='local-comfyui';old=record['promptId'];request('/queue',{'delete':[old]});revision={'previousPromptId':old,'reason':a.reason,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};record.setdefault('queueRevisions',[]).append(revision)
 try:
  result=request('/prompt',{'prompt':json.loads((folder/'workflow.json').read_text('utf8')),'client_id':'oldniulai-street-reskin','front':True});record.update(promptId=result['prompt_id'],response=result);revision['newPromptId']=result['prompt_id']
 except Exception as e:record.update(status='queue-requeue-required',requeueError=str(e));file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');raise
 file.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');print(name,'reprioritized')
