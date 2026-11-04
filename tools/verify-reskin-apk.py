import hashlib,json,zlib
from pathlib import Path
from zipfile import ZipFile
root=Path(__file__).resolve().parents[1];out=root/'outputs/reskin-v020'
apk=out/'原创角色换皮-v0.20-预览测试版.apk'
with ZipFile(apk) as z:
    for file in ['character-reskin.js','character-reskin-data.js','index_bh_lite3zbtest_andr.html']:
        assert z.read('assets/'+file)==(root/'local_game'/file).read_bytes(),file
    imgs=[n for n in z.namelist() if n.startswith('assets/reskin/hero_') and n.endswith('.png')]
    assert len(imgs)==81
    for n in imgs:assert z.read(n)==(root/'local_game'/n.removeprefix('assets/')).read_bytes(),n
    assert z.read('classes.dex') and z.read('AndroidManifest.xml')
    original_count=0
    for info in z.infolist():
        if not info.filename.startswith('assets/resource/'):continue
        p=root/'local_game'/info.filename.removeprefix('assets/')
        assert p.is_file() and p.stat().st_size==info.file_size,info.filename
        assert zlib.crc32(p.read_bytes())==info.CRC,info.filename
        original_count+=1
report={'apkSha256':hashlib.file_digest(apk.open('rb'),'sha256').hexdigest(),'apkBytes':apk.stat().st_size,'packagedPortraits':81,'runtimeScriptsMatchWorkspace':True,'originalAssetFilesCompared':original_count,'originalAssetsPreserved':True}
(out/'package-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
