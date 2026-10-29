"""Revise only this task's unstarted Qwen workflows after validating RGBA matting compatibility."""
import json,shutil
from pathlib import Path
from street_comfy import ROOT,request,submit
base=ROOT/'art-migration/generation';queue=request('/queue');pending={row[1] for row in queue['queue_pending']};running={row[1] for row in queue['queue_running']};candidates=[]
for folder in sorted(base.iterdir()):
 jobfile=folder/'job.json';workflowfile=folder/'workflow.json'
 if not jobfile.exists():continue
 job=json.loads(jobfile.read_text('utf8'));graph=json.loads(workflowfile.read_text('utf8'))
 if graph.get('9',{}).get('class_type')!='easy imageRemBg' or '11' in graph:continue
 if job['status'] not in ['submitted','failed']:continue
 if job.get('supersededBy'):continue
 candidates.append((folder,job,graph))
delete=[job['promptId'] for _,job,_ in candidates if job['promptId'] in pending]
if delete:request('/queue',{'delete':delete})
for folder,job,graph in candidates:
 graph['11']={'class_type':'SplitImageWithAlpha','inputs':{'image':['6',0]}}
 graph['9']['inputs']['images']=['11',0]
 target=submit(graph,folder.name.removesuffix('-v1')+'-v2')
 if (folder/'design.json').exists():shutil.copy2(folder/'design.json',target/'design.json')
 job['supersededBy']=target.relative_to(ROOT).as_posix()
 if job['status']=='submitted' and job['promptId'] not in running:job['status']='superseded'
 (folder/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),'utf8')
print('Revised distinct workflow jobs:',len(candidates))
