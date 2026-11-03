#!/usr/bin/env python3
"""Verify final artifacts in a clean Ubuntu Base; never installs on the host."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / 'build/portable'
BASE = BUILD / 'verify-rootfs'
DIST = ROOT / 'dist'


def run(argv, **kw):
    return subprocess.run([str(x) for x in argv], check=True, **kw)


def main():
    archive = BUILD / 'downloads/ubuntu-base-22.04.5-base-amd64.tar.gz'
    expected = '242cd8898b33ea806ef5f13b1076ed7c76f9f989d18384452f7166692438ff1a'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise SystemExit('Ubuntu Base SHA256 mismatch')
    if BASE.exists():
        raise SystemExit('Verification root already exists. Choose/archive that previous generated tree before retrying.')
    BASE.mkdir()
    run(['tar','--no-same-owner','-xzf',archive,'-C',BASE])
    (BASE / 'etc/machine-id').write_text(uuid.uuid4().hex+'\n')
    assert not (BASE / 'usr/bin/python3').exists()
    assert not (BASE / 'usr/lib/x86_64-linux-gnu/libQt6Core.so.6').exists()
    # No host directories or display socket; /dist is read-only and network is isolated.
    command = '''set -eu
cd /dist
sha256sum -c SHA256SUMS
./NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage --appimage-extract-and-run --self-test
dpkg -i nvidia-commands-for-linux_2.0.0_amd64.deb
nvidia-commands-for-linux --self-test
nvidia-commands-for-linux --version
dpkg --purge nvidia-commands-for-linux
test ! -e /opt/nvidia-commands-for-linux
test ! -e /usr/bin/nvidia-commands-for-linux
test ! -e /usr/share/applications/nvidia-commands-for-linux.desktop
'''
    run(['bwrap','--bind',BASE,'/','--ro-bind',DIST,'/dist','--dev','/dev','--proc','/proc',
         '--unshare-user','--unshare-net','--uid','0','--gid','0','--setenv','HOME','/root',
         '--setenv','QT_QPA_PLATFORM','offscreen','--setenv','LANG','C.UTF-8','--setenv','PATH','/usr/sbin:/usr/bin:/sbin:/bin',
         '--unsetenv','LD_LIBRARY_PATH','--unsetenv','LD_PRELOAD','/bin/sh','-c',command])
    versions = set()
    elf_count = 0
    payload = BUILD / 'NVIDIA-Commands-for-Linux.AppDir'
    for path in payload.rglob('*'):
        if not path.is_file():continue
        with path.open('rb') as f:
            if f.read(4) != b'\x7fELF':continue
        elf_count += 1
        info = run(['readelf','--version-info',path],capture_output=True,text=True).stdout
        versions.update(re.findall(r'GLIBC_(\d+\.\d+(?:\.\d+)?)',info))
    maximum = max(versions,key=lambda v:tuple(map(int,v.split('.'))))
    assert tuple(map(int,maximum.split('.'))) <= (2,35), maximum
    report = {'version':'2.0.0','unit_ui_tests':85,'base':'Ubuntu Base 22.04.5, SHA256-verified',
              'base_system_python_qt':False,'network':'unshared','host_installation':False,
              'appimage_extract_and_run':'passed','deb_install_self_test_purge':'passed',
              'elf_count':elf_count,'max_required_glibc':maximum,
              'physical_rtx5070':False,'in_game_verification':False,'epic_authenticated_game':False}
    out = ROOT / '.cache/portable-verification.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':main()
