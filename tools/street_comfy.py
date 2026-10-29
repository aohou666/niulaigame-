"""Reproducible local Qwen Image 2.1 generation; preserve prompt graph and provenance."""
from __future__ import annotations
import argparse, hashlib, json, time, urllib.request, urllib.error, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMFY=Path(r'G:\comfylight\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI')
API='http://127.0.0.1:8188'

def request(endpoint,data=None):
    body=None if data is None else json.dumps(data).encode()
    req=urllib.request.Request(API+endpoint,data=body,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=45) as r:
            payload=r.read();return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()) from e

def qwen(prompt,reference=None,resolution=768,steps=28,seed=2026102901):
    graph={
      '1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_int8_convrot.safetensors','weight_dtype':'default'}},
      '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
      '3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
      '4':{'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'negative_prompt':'blurry, cropped body, duplicate character, watermark, unreadable text, medieval armor, ancient Chinese costume','resolution':resolution}},
      '5':{'class_type':'KSampler','inputs':{'model':['1',0],'seed':seed,'steps':steps,'cfg':4,'sampler_name':'euler','scheduler':'simple','positive':['4',0],'negative':['4',1],'latent_image':['4',2],'denoise':1}},
      '6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['3',0]}},
      '7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':'street-reskin/qwen'}}}
    if reference:
        source=Path(reference).resolve(); name='street_'+hashlib.sha256(source.read_bytes()).hexdigest()[:16]+source.suffix
        shutil.copy2(source,COMFY/'input'/name)
        graph['8']={'class_type':'LoadImage','inputs':{'image':name}}
        graph['4']['inputs']['images.image_1']=['8',0]
    return graph

def submit(graph,name,front=False):
    folder=ROOT/'art-migration/generation'/name;folder.mkdir(parents=True,exist_ok=False)
    (folder/'workflow.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2),'utf8')
    result=request('/prompt',{'prompt':graph,'client_id':'oldniulai-street-reskin','front':front})
    record={'promptId':result['prompt_id'],'submittedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'submitted','provider':'local-comfyui','workflowSha256':hashlib.sha256((folder/'workflow.json').read_bytes()).hexdigest(),'response':result}
    (folder/'job.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps({'job':str(folder),'result':result},ensure_ascii=False),flush=True)
    return folder

def collect(folder):
    folder=Path(folder).resolve();record=json.loads((folder/'job.json').read_text('utf8'))
    history=request('/history/'+record['promptId']).get(record['promptId'])
    if history is None:print('PENDING',record['promptId']);return False
    (folder/'history.json').write_text(json.dumps(history,ensure_ascii=False,indent=2),'utf8')
    record['comfyStatus']=history.get('status')
    if history.get('status',{}).get('status_str')!='success':
        record['status']='failed';(folder/'job.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
        error=next((v for k,v in history['status'].get('messages',[]) if k=='execution_error'),{})
        print(json.dumps({'job':str(folder),'status':'failed','node':error.get('node_type'),'error':error.get('exception_message','')[:500]}));return False
    files=[]
    for node,out in history['outputs'].items():
        for item in out.get('images',[]):
            source=COMFY/('temp' if item.get('type')=='temp' else 'output')/item.get('subfolder','')/item['filename']
            dest=folder/item['filename'];shutil.copy2(source,dest)
            files.append({'path':str(dest.relative_to(ROOT).as_posix()),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    record.update(status='generated-unreviewed',outputs=files)
    (folder/'job.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'job':str(folder),'status':record['status'],'files':len(files)},ensure_ascii=False));return True

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    g=sub.add_parser('qwen');g.add_argument('--name',required=True);g.add_argument('--prompt-file',type=Path,required=True);g.add_argument('--reference',type=Path);g.add_argument('--resolution',type=int,default=768);g.add_argument('--steps',type=int,default=28)
    c=sub.add_parser('collect');c.add_argument('folder',type=Path)
    a=p.parse_args()
    if a.mode=='collect':collect(a.folder)
    else:submit(qwen(a.prompt_file.read_text('utf8'),a.reference,a.resolution,a.steps),a.name)

if __name__=='__main__':main()
