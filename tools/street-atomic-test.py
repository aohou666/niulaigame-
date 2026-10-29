"""Verify hot-reader publication never observes partial JSON; exercise transient sharing-lock retry."""
import json,sys,tempfile,threading,hashlib,importlib.util,urllib.request
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent));from street_atomic import atomic_write_text
spec=importlib.util.spec_from_file_location('street_server_io',Path(__file__).resolve().parents[1]/'local_game/offline_server.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
errors=[];reads=[0];stop=threading.Event()
with tempfile.TemporaryDirectory(prefix='street-atomic-test-') as td:
 path=Path(td)/'data.js';atomic_write_text(path,json.dumps({'version':0,'padding':'x'*131072}))
 def reader():
  while not stop.is_set():
   try:
    with module.open_static_file(path) as stream:r=json.loads(stream.read().decode('utf8'))
    assert len(r['padding'])==131072;reads[0]+=1
   except Exception as e:errors.append(repr(e));stop.set()
 t=threading.Thread(target=reader);t.start()
 try:
  for i in range(1,21):atomic_write_text(path,json.dumps({'version':i,'padding':'x'*131072}))
 finally:stop.set();t.join()
 assert not errors and reads[0]>0,(errors,reads)
 import street_atomic
 original=street_atomic.os.replace;calls=[0]
 def transient(source,target):
  calls[0]+=1
  if calls[0]<3:raise OSError(22,'simulated temporary sharing lock')
  return original(source,target)
 with patch.object(street_atomic.os,'replace',transient):atomic_write_text(path,json.dumps({'version':21,'padding':'x'*131072}))
 assert calls[0]==3 and json.loads(path.read_text('utf8'))['version']==21
 originalOpen=Path.open;openCalls=[0]
 def temporary_busy(self,*args,**kwargs):
  openCalls[0]+=1
  if openCalls[0]<3:raise PermissionError(13,'simulated transient reader sharing lock')
  return originalOpen(self,*args,**kwargs)
 with patch.object(Path,'open',temporary_busy):
  with module.open_static_file(path) as stream:assert json.loads(stream.read())['version']==21
 assert openCalls[0]==3
 module.ROOT=Path(td);hot=Path(td)/'assets/street/hot-data.js';hot.parent.mkdir(parents=True);atomic_write_text(hot,json.dumps({'version':0,'padding':'x'*131072}))
 class QuietHandler(module.OfflineHandler):
  def log_message(self,*args):pass
 server=module.ThreadingHTTPServer(('127.0.0.1',0),QuietHandler);serverThread=threading.Thread(target=server.serve_forever);serverThread.start();httpReads=[]
 try:
  for i in range(10):
   atomic_write_text(hot,json.dumps({'version':i,'padding':'x'*131072}))
   with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/assets/street/hot-data.js') as response:
    value=json.loads(response.read());assert response.status==200 and len(value['padding'])==131072;httpReads.append(value['version'])
 finally:server.shutdown();serverThread.join();server.server_close()
 report={'pass':True,'httpReads':httpReads,'readerRetryAttempts':openCalls[0],'concurrentReaderParses':reads[0],'publications':20,'partialReads':errors,'injectedTransientFailures':2,'replaceAttempts':calls[0],'temporaryFilesRemain':len(list(Path(td).glob('*.tmp')))};assert report['temporaryFilesRemain']==0
Path('art-migration/versions/0.42.0/atomic-runtime.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
