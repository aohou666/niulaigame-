"""Exercise startup connection bursts and byte integrity through the actual HTTP handler."""
import concurrent.futures,hashlib,importlib.util,json,socket,threading,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('street_server',ROOT/'local_game/offline_server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class QuietHandler(m.OfflineHandler):
 def log_message(self,*args):pass
server=m.OfflineHTTPServer(('127.0.0.1',0),QuietHandler);thread=threading.Thread(target=server.serve_forever);thread.start()
path=ROOT/'local_game/assets/street/environments/noodle-plaza-battle.jpg';expected=hashlib.sha256(path.read_bytes()).hexdigest();results=[]
try:
 def get(_):
  start=time.monotonic()
  with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/assets/street/environments/noodle-plaza-battle.jpg',timeout=15) as response:
   data=response.read();assert response.status==200 and hashlib.sha256(data).hexdigest()==expected
  return (time.monotonic()-start)*1000
 with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:results=list(pool.map(get,range(128)))
finally:server.shutdown();thread.join();server.server_close()
report={'pass':len(results)==128,'requests':len(results),'concurrentClients':64,'listenBacklog':server.request_queue_size,'identicalResponseSha256':expected,'maxLatencyMs':max(results),'scope':'Real128 HTTP image responses with64 clients; does not establish origin of all historical RES errors.'}
(ROOT/'art-migration/versions/0.45.0/server-burst.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
