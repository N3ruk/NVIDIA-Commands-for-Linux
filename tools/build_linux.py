#!/usr/bin/env python3
"""Build both Linux packages from the same frozen application (Ubuntu 22.04)."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dlss_studio import __version__ as VERSION
BUILD = ROOT / 'build/portable'
DIST = ROOT / 'dist'
APPDIR = BUILD / 'DLSS-Studio.AppDir'
RUNTIME_URL = 'https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-x86_64'
RUNTIME_SHA256 = '617aa77314d57c8b8e4fae9c3f0b35af7b30d5529cb69e98f64f92510ed98a46'


def run(*args, **kw):
    subprocess.run([str(a) for a in args], check=True, **kw)


def copy(source, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.chdir(ROOT)
    DIST.mkdir(exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    run(sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--distpath', BUILD / 'frozen', '--workpath', BUILD / 'pyinstaller',
        ROOT / 'packaging/dlss-studio.spec')
    if APPDIR.exists():
        shutil.rmtree(APPDIR)  # Generated package tree only.
    payload = APPDIR / 'usr/lib/dlss-studio'
    shutil.copytree(BUILD / 'frozen/dlss-studio', payload)
    copy(ROOT / 'packaging/AppRun', APPDIR / 'AppRun')
    copy(ROOT / 'packaging/dlss-studio.desktop', APPDIR / 'dlss-studio.desktop')
    copy(ROOT / 'packaging/dlss-studio.desktop', APPDIR / 'usr/share/applications/dlss-studio.desktop')
    icon = ROOT / 'dlss_studio/assets/dlss-studio.png'
    copy(icon, APPDIR / 'dlss-studio.png')
    copy(icon, APPDIR / 'usr/share/icons/hicolor/512x512/apps/dlss-studio.png')
    (APPDIR / '.DirIcon').symlink_to('dlss-studio.png')
    internal = payload / '_internal'
    # Fusion is the app's built-in style; this optional GTK adapter would
    # introduce an unnecessary system GTK dependency.
    (internal / 'PySide6/Qt/plugins/platformthemes/libqgtk3.so').unlink(missing_ok=True)
    fonts = Path('/usr/share/fonts/truetype/dejavu')
    for font in ['DejaVuSans.ttf', 'DejaVuSans-Bold.ttf', 'DejaVuSansMono.ttf']:
        copy(fonts / font, internal / 'fonts' / font)
    (internal / 'fonts.conf').write_text('''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig><dir prefix="relative">fonts</dir><dir>/usr/share/fonts</dir>
<dir>/usr/local/share/fonts</dir><dir prefix="xdg">fonts</dir>
<cachedir prefix="xdg">fontconfig</cachedir></fontconfig>
''')
    notices = payload / 'licenses'
    copy(ROOT / 'LICENSE', notices / 'DLSS-Studio-BSD-3-Clause.txt')
    copy(ROOT / 'THIRD_PARTY.md', notices / 'THIRD_PARTY.md')
    shutil.copytree(ROOT / 'packaging/licenses', notices / 'upstream', dirs_exist_ok=True)
    # Debian package copyright files include the redistribution conditions and
    # upstream source URLs for the shared libraries bundled by the freezer.
    qtroot = Path(sys.prefix) / 'lib/python3.10/site-packages/PySide6'
    if not qtroot.exists():
        import PySide6
        qtroot = Path(PySide6.__file__).parent
    for name in ['PySide6', 'shiboken6']:
        for license_dir in qtroot.parent.glob(name + '-*.dist-info/licenses'):
            shutil.copytree(license_dir, notices / name, dirs_exist_ok=True)
    for package in Path('/usr/share/doc').iterdir():
        if (package / 'copyright').is_file():
            copy(package / 'copyright', notices / 'debian' / (package.name + '.copyright'))
    run(APPDIR / 'AppRun', '--self-test', env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
    runtime = BUILD / 'downloads/runtime-x86_64'
    runtime.parent.mkdir(exist_ok=True)
    if not runtime.exists():
        urllib.request.urlretrieve(RUNTIME_URL, runtime)
    if digest(runtime) != RUNTIME_SHA256:
        raise SystemExit('AppImage runtime SHA256 mismatch; update the pinned URL/hash explicitly.')
    squash = BUILD / 'dlss-studio.squashfs'
    squash.unlink(missing_ok=True)
    run('mksquashfs', APPDIR, squash, '-noappend', '-comp', 'zstd', '-b', '1M',
        '-all-root', '-no-xattrs', '-processors', '2')
    appimage = DIST / f'DLSS-Studio-{VERSION}-x86_64.AppImage'
    with appimage.open('wb') as out:
        for part in [runtime, squash]:
            with part.open('rb') as source:
                shutil.copyfileobj(source, out)
    appimage.chmod(0o755)
    debroot = BUILD / 'debroot'
    if debroot.exists():
        shutil.rmtree(debroot)
    shutil.copytree(APPDIR, debroot / 'opt/dlss-studio', symlinks=True)
    copy(ROOT / 'packaging/dlss-studio.desktop', debroot / 'usr/share/applications/dlss-studio.desktop')
    copy(icon, debroot / 'usr/share/icons/hicolor/512x512/apps/dlss-studio.png')
    launcher = debroot / 'usr/bin/dlss-studio'
    launcher.parent.mkdir(parents=True)
    launcher.write_text('#!/bin/sh\nexec /opt/dlss-studio/AppRun "$@"\n')
    launcher.chmod(0o755)
    control = debroot / 'DEBIAN'
    control.mkdir()
    size = sum(f.stat().st_size for f in debroot.rglob('*') if f.is_file()) // 1024
    (control / 'control').write_text(f'''Package: dlss-studio
Version: {VERSION}
Section: games
Priority: optional
Architecture: amd64
Maintainer: N3ruk <264709581+N3ruk@users.noreply.github.com>
Homepage: https://github.com/N3ruk/DLSS-Studio
Depends: libc6 (>= 2.35)
Installed-Size: {size}
Description: Configurador de presets NVIDIA DLSS para Steam en Linux
 Interfaz en español para elegir presets y copiar parámetros de lanzamiento.
 Incluye Python, Qt, bibliotecas de escritorio y fuentes. No descarga
 dependencias al instalarse. Requiere sesión gráfica y controlador NVIDIA
 del sistema para detectar la GPU. No incluye Steam, Proton ni controladores.
''')
    checks = []
    for f in sorted(debroot.rglob('*')):
        if f.is_file() and not f.is_symlink() and control not in f.parents:
            checks.append(hashlib.md5(f.read_bytes()).hexdigest() + '  ' + str(f.relative_to(debroot)))
    (control / 'md5sums').write_text('\n'.join(checks) + '\n')
    deb = DIST / f'dlss-studio_{VERSION}_amd64.deb'
    run('dpkg-deb', '--root-owner-group', '-Zxz', '--build', debroot, deb)
    (DIST / 'SHA256SUMS').write_text(''.join(f'{digest(f)}  {f.name}\n' for f in [appimage, deb]))
    (DIST / 'build-info.json').write_text(json.dumps({
        'version': VERSION, 'architecture': 'x86_64', 'glibc_minimum': '2.35',
        'base': 'Ubuntu 22.04', 'python': sys.version.split()[0],
        'qt': '6.8.3', 'pyinstaller': '6.16.0', 'runtime_sha256': RUNTIME_SHA256,
        'bundled': 'Python, PySide6/Qt, desktop shared libraries, fonts, licenses',
        'external': 'glibc, Linux kernel, graphical session, NVIDIA driver, Steam/Proton for games',
    }, indent=2) + '\n')
    for f in [appimage, deb]:
        print(f'{f.name}: {f.stat().st_size / 1024 / 1024:.1f} MiB')


if __name__ == '__main__':
    main()
