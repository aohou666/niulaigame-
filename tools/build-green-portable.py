"""Package the standalone green frame workbench, including its Node runtime."""
from pathlib import Path
import hashlib
import zipfile

root = Path(__file__).resolve().parent.parent
source = root / "workbenches" / "greenscreen-frame-studio"
target = root / "migration-packages" / "Greenscreen-Frame-Studio-Eraser-Portable-Windows-x64.zip"
target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for item in sorted(source.rglob("*")):
        if item.is_file():
            archive.write(item, "Greenscreen-Frame-Studio-Eraser-Portable/" + item.relative_to(source).as_posix())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
digest = hashlib.file_digest(target.open("rb"), "sha256").hexdigest()
target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
print(f"{target.name}: {target.stat().st_size} bytes; SHA256 {digest}")
