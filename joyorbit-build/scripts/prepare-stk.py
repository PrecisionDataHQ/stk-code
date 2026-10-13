"""Prepare pinned STK source, dependencies and unchanged official Android data."""
from pathlib import Path
import hashlib
import os
import subprocess
import tarfile
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
cache=ROOT/'build/downloads';cache.mkdir(parents=True,exist_ok=True)
items=[
 ('SuperTuxKart-1.5-src.tar.gz','https://github.com/supertuxkart/stk-code/releases/download/1.5/SuperTuxKart-1.5-src.tar.gz','33cf8841e4ff4082d80b9248014295bbbea61d14683e86dff100e3ab8f7b27cb'),
 ('stk-dependencies-android-src.tar.xz','https://github.com/supertuxkart/dependencies/releases/download/preview/dependencies-android-src.tar.xz','f87a54743eebd1d776a490a5b9b978706e48820fa28bb501f29a2b2788a9c279'),
 ('SuperTuxKart-1.5.apk','https://github.com/supertuxkart/stk-code/releases/download/1.5/SuperTuxKart-1.5.apk','e1f2f49152abfb8f3ed0ced47981e84096758bff9758563aa3b917111a2a3cbd')]
for name,url,digest in items:
    target=cache/name
    if not target.exists():urllib.request.urlretrieve(url,target)
    if hashlib.file_digest(target.open('rb'),'sha256').hexdigest()!=digest:
        raise SystemExit('Checksum mismatch: '+name+'; no source updated.')
source=Path(os.environ.get('JOYORBIT_STK_SOURCE',str(ROOT/'.sources/stk/SuperTuxKart-1.5-src')))
if source.exists():raise SystemExit('STK source exists; preserve it and choose a fresh JOYORBIT_STK_SOURCE.')
source.parent.mkdir(parents=True,exist_ok=True)
with tarfile.open(cache/items[0][0]) as archive:archive.extractall(source.parent,filter='data')
if not source.exists():raise SystemExit('Use the release directory name SuperTuxKart-1.5-src.')
with tarfile.open(cache/items[1][0]) as archive:archive.extractall(source/'lib',filter='data')
with zipfile.ZipFile(cache/items[2][0]) as archive:
    for entry in archive.infolist():
        if entry.filename.startswith('assets/') and not entry.is_dir():
            target=source/'android'/entry.filename
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(entry))
subprocess.run(['patch','-p1','-i',str(ROOT/'android/stk-macos.patch')],cwd=source,check=True)
print('Prepared '+str(source)+'; run build-stk.sh with this JOYORBIT_STK_SOURCE.')
