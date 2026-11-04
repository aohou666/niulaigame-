from pathlib import Path
from zipfile import ZipFile,ZIP_STORED
import hashlib,json,argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--build-dir');args=parser.parse_args()
build=Path(args.build_dir) if args.build_dir else root/'outputs/reskin-v020/build'
files=[]
with ZipFile(build/'unsigned.apk','w',ZIP_STORED) as target:
    with ZipFile(build/'shell.apk') as source:
        for info in source.infolist():target.writestr(info,source.read(info.filename))
    for dex in (build/'dex').glob('*.dex'):target.write(dex,dex.name)
    for p in (root/'local_game').rglob('*'):
        if not p.is_file() or p.suffix.lower() in ('.py','.ps1') or p.name=='README.md' or '__pycache__' in p.parts or 'server_data' in p.parts:continue
        relative=p.relative_to(root/'local_game').as_posix()
        target.write(p,'assets/'+relative)
        files.append(relative)
assert len([f for f in files if f.startswith('reskin/') and f.endswith('.png')])==81
assert 'character-reskin-data.js' in files and 'character-reskin.js' in files
print(json.dumps({'assetFiles':len(files),'reskinPortraits':81,'bytes':(build/'unsigned.apk').stat().st_size}))
