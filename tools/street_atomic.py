"""Publish data files atomically, with bounded retries for transient Windows sharing locks."""
import os,tempfile,time
from pathlib import Path

def atomic_write_text(path,text,encoding='utf8'):
 path=Path(path);descriptor,temporary=tempfile.mkstemp(prefix=path.name+'.codex-',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(descriptor,'w',encoding=encoding,newline='\n') as stream:
   stream.write(text);stream.flush();os.fsync(stream.fileno())
  for attempt in range(32):
   try:os.replace(temporary,path);return
   except OSError:
    if attempt==31:raise
    time.sleep(.05)
 finally:
  Path(temporary).unlink(missing_ok=True)
