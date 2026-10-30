#!/usr/bin/env python3
"""Build on a newer Linux host without sudo, using bubblewrap + Ubuntu 22.04."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / 'build/portable'
BASE = WORK / 'rootfs'
URL = 'https://cdimage.ubuntu.com/ubuntu-base/releases/22.04/release/ubuntu-base-22.04.5-base-amd64.tar.gz'
SHA256 = '242cd8898b33ea806ef5f13b1076ed7c76f9f989d18384452f7166692438ff1a'
PACKAGES = '''python3 python3-venv python3-pip libpython3.10 binutils patchelf squashfs-tools
libglib2.0-0 libwayland-client0 libwayland-cursor0 libwayland-egl1 libdrm2 libgbm1 libgl1 libegl1 libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0
libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0
libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1
libxcb-util1 libdbus-1-3 libfontconfig1 libfreetype6 libnss3 libx11-xcb1
libxrender1 libxi6 libsm6 libice6 fonts-dejavu-core'''.split()


def main():
    if not shutil.which('bwrap'):
        raise SystemExit('Se necesita bubblewrap (bwrap) y user namespaces habilitados.')
    archive = WORK / 'downloads/ubuntu-base-22.04.5-base-amd64.tar.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise SystemExit('Ubuntu base SHA256 incorrecto')
    if not (BASE / 'bin/bash').exists():
        BASE.mkdir(parents=True, exist_ok=True)
        # Official archive, verified above; preserve its absolute symlinks.
        subprocess.run(['tar', '--no-same-owner', '-xzf', str(archive), '-C', str(BASE)], check=True)
    resolver = BASE / 'etc/resolv.conf'
    if resolver.is_symlink():
        resolver.unlink()
    resolver.write_bytes(Path('/etc/resolv.conf').read_bytes())
    certificates = BASE / 'etc/ssl/certs/ca-certificates.crt'
    certificates.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile('/etc/ssl/certs/ca-certificates.crt', certificates)
    sources = BASE / 'etc/apt/sources.list'
    sources.write_text(sources.read_text().replace('http://', 'https://'))
    (BASE / 'etc/apt/apt.conf.d/00rootless').write_text('APT::Sandbox::User "root";\n')
    # Avoid a postinst chown to an unmapped group inside the user namespace.
    (BASE / 'usr/local/share/fonts').mkdir(parents=True, exist_ok=True)
    setup = ('set -eu; export DEBIAN_FRONTEND=noninteractive; '
             'apt-get update; apt-get install -y --no-install-recommends ' + ' '.join(PACKAGES) + '; '
             'test -x /opt/build-venv/bin/python || python3 -m venv /opt/build-venv; '
             'python -m pip install -r packaging/requirements-build.txt; '
             'QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v; '
             'QT_QPA_PLATFORM=offscreen python tools/build_linux.py')
    subprocess.run(['bwrap', '--bind', str(BASE), '/', '--bind', str(ROOT), '/src',
                    '--dev', '/dev', '--proc', '/proc', '--unshare-user', '--uid', '0', '--gid', '0',
                    '--chdir', '/src', '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'HOME', '/root',
                    '--setenv', 'PATH', '/opt/build-venv/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                    '/bin/bash', '-c', setup], check=True)


if __name__ == '__main__':
    main()
