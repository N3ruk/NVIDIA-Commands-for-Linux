from pathlib import Path
import glob

root = Path(SPECPATH).parent
# Include the desktop integration libraries even when PyInstaller considers
# them system libraries. Do not ship libc or vendor GPU drivers.
patterns = [
    'libxcb*.so.*', 'libX11*.so.*', 'libXau.so.*', 'libXdmcp.so.*',
    'libXrender.so.*', 'libXext.so.*', 'libXi.so.*', 'libXfixes.so.*',
    'libSM.so.*', 'libICE.so.*', 'libxkbcommon*.so.*', 'libfontconfig.so.*',
    'libfreetype.so.*', 'libpng16.so.*', 'libexpat.so.*', 'libbrotli*.so.*',
    'libdbus-1.so.*', 'libwayland-*.so.*', 'libdrm.so.*', 'libgbm.so.*', 'libGL.so.*', 'libEGL.so.*', 'libGLX.so.*',
    'libGLdispatch.so.*', 'libOpenGL.so.*', 'libstdc++.so.*', 'libgcc_s.so.*',
]
extra = {}
for pattern in patterns:
    for item in glob.glob('/usr/lib/x86_64-linux-gnu/' + pattern):
        extra[Path(item).name] = (item, '.')
a = Analysis(
    [str(root / 'packaging/entry.py')], pathex=[str(root)],
    binaries=list(extra.values()),
    datas=[(str(root / 'dlss_studio/data'), 'dlss_studio/data'),
           (str(root / 'dlss_studio/assets'), 'dlss_studio/assets')],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['PyQt6', 'PyQt5', 'PySide2', 'tkinter', 'unittest', 'pytest'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='dlss-studio',
          debug=False, bootloader_ignore_signals=False, strip=False,
          upx=False, console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='dlss-studio')
