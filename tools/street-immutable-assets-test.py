"""A client retaining an old manifest must still receive its exact binary atlas."""
import hashlib,importlib.util,json,sys,tempfile,threading,urllib.request
from pathlib import Path
from street_atomic import atomic_write_bytes,atomic_write_text

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('street_server_io',ROOT/'local_game/offline_server.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='street-immutable-test-') as temp:
    root=Path(temp);assets=root/'assets/street';assets.mkdir(parents=True)
    module.ROOT=root
    class QuietHandler(module.OfflineHandler):
        def log_message(self,*args):pass
    server=module.OfflineHTTPServer(('127.0.0.1',0),QuietHandler)
    thread=threading.Thread(target=server.serve_forever);thread.start()
    base=f'http://127.0.0.1:{server.server_port}/assets/street/'
    manifests=[];reads=0
    try:
        for i in range(6):
            payload=bytes([i])+bytes(range(256))*8192
            digest=hashlib.sha256(payload).hexdigest();name=f'body-{digest[:16]}.webp'
            atomic_write_bytes(assets/name,payload)
            atomic_write_text(assets/'manifest-data.js',json.dumps({'atlas':name,'sha256':digest}))
            with urllib.request.urlopen(base+'manifest-data.js') as response:current=json.loads(response.read())
            manifests.append(current)
            # Current and every already-held old manifest are exercised after publication.
            for manifest in manifests:
                with urllib.request.urlopen(base+manifest['atlas']) as response:
                    actual=response.read();assert response.status==200
                assert hashlib.sha256(actual).hexdigest()==manifest['sha256'];reads+=1
        assert len(list(assets.glob('body-*.webp')))==6
        assert not list(assets.glob('*.tmp'))
    finally:server.shutdown();thread.join();server.server_close()
report={'pass':True,'realHttpBinaryReads':reads,'heldManifestVersions':len(manifests),'bytesPerAtlas':len(payload),'allHeldManifestsRetainedExactAtlas':True,'temporaryFilesRemain':0}
version=next((a.split('=',1)[1] for a in sys.argv[1:] if a.startswith('--version=')),'0.51.0')
out=ROOT/'art-migration/versions'/version;out.mkdir(parents=True,exist_ok=True)
(out/'immutable-binary-runtime.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
