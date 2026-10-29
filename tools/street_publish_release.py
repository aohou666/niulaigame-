"""Publish explicit game-resource assets with existing Git credential-helper authentication.

Credentials remain in process memory and are never logged or saved.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO='aohou666/oldniulai';TAG='street-v0.23.0';out=ROOT/'release-manifest'
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never')
result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,cwd=ROOT,env=env)
credentials=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
token=credentials.get('password')
if not token:raise RuntimeError('Existing GitHub credential helper did not provide authentication')
headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'oldniulai-art-migration'}
def api(path,data=None,method=None):
 req=urllib.request.Request('https://api.github.com'+path,data=None if data is None else json.dumps(data).encode('utf8'),headers={**headers,'Content-Type':'application/json'},method=method or ('GET' if data is None else 'POST'))
 try:
  with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as e:
  if e.code==404:return None
  raise RuntimeError('GitHub API '+str(e.code)+' '+e.read().decode('utf8')[:300]) from None

release=api(f'/repos/{REPO}/releases/tags/{TAG}')
if release is None:
 release=api(f'/repos/{REPO}/releases',{'tag_name':TAG,'target_commitish':'ba58f3405eefebe48ddfbd570bfcf315f071ae04','name':'离谱街区换皮 v0.23.0 · 阶段性开发版','prerelease':True,'draft':False,'body':'前三个实质版本（v0.21、v0.22、v0.23）的阶段性同步。\n\n已接入85名角色的841处头像/立绘引用；85/85角色详情与技能栏复查通过。待机5201帧使用共享图集，六名固定我方角色估算解码纹理存储下降84.34%。官方生成的街区广场已进入实战。\n\n全量换皮尚未完成：原攻击、受击等动作以及大部分UI、建筑、道具和特效仍在逐项替换，未宣称零bug或所有设备永不卡顿。详见 art-migration/WORKLOG.md 及版本 review.json。\n\n恢复运行环境：克隆 main，再将 original-game-resources.zip 解压到仓库根目录。新生成的待机图集已纳入Git。运行 python local_game/offline_server.py，再访问 http://127.0.0.1:8787/offline-launcher.html。本资源包不含存档、凭据或无关个人文件；重建原始待机图集所需的3.15GB原PNG源序列将单独保存，不是运行依赖。'} )
status={'releaseUrl':release['html_url'],'releaseId':release['id'],'assets':[]}
(out/'github-release.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n','utf8')

class ProgressFile:
 def __init__(self,file):self.file=file;self.sent=0;self.last=0
 def read(self,n=-1):
  chunk=self.file.read(n);self.sent+=len(chunk)
  if self.sent-self.last>=16*1024*1024:
   self.last=self.sent
   (ROOT/'outputs/street-reskin/release-upload-progress.json').write_text(json.dumps({'bytesReadForUpload':self.sent,'totalBytes':self.file_size,'releaseUrl':release['html_url'],'updatedUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}),'utf8')
  return chunk

for name in ['original-game-resources.zip','original-game-resources.manifest.json']:
 path=out/name;assets=api(f'/repos/{REPO}/releases/{release["id"]}/assets')
 existing=next((item for item in assets if item['name']==name),None)
 if existing is not None:
  if existing['size']!=path.stat().st_size:raise RuntimeError('Existing release asset has a different size: '+name)
 else:
  url=release['upload_url'].split('{',1)[0]+'?name='+name
  with path.open('rb') as stream:
   body=ProgressFile(stream);body.file_size=path.stat().st_size
   req=urllib.request.Request(url,data=body,headers={**headers,'Content-Type':'application/zip' if name.endswith('.zip') else 'application/json','Content-Length':str(path.stat().st_size)},method='POST')
   with urllib.request.urlopen(req,timeout=180) as response:existing=json.load(response)
 verified=api(f'/repos/{REPO}/releases/assets/{existing["id"]}')
 if verified['name']!=name or verified['size']!=path.stat().st_size or verified['state']!='uploaded':raise RuntimeError('Remote asset verification failed: '+name)
 local_hash=hashlib.sha256(path.read_bytes()).hexdigest()
 if verified.get('digest') and verified['digest']!='sha256:'+local_hash:raise RuntimeError('Remote SHA-256 does not match: '+name)
 status['assets'].append({'name':name,'bytes':verified['size'],'url':verified['browser_download_url'],'localSha256':local_hash,'remoteDigest':verified.get('digest'),'verifiedNameAndSize':True})
 (out/'github-release.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps(status['assets'][-1],ensure_ascii=False),flush=True)
print('Release uploaded and verified:',status['releaseUrl'])
