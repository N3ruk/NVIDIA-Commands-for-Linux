# Third-party components

[Español](THIRD_PARTY_ES.md)

The project's BSD-3-Clause license applies to original code; bundled components retain their own licenses. Libraries are dynamic and replaceable under `usr/lib/dlss-studio/_internal` inside an extracted AppImage or `/opt/dlss-studio`.

- Python 3.10: PSF License; https://www.python.org/downloads/source/.
- PySide6 / Shiboken6 6.8.3 and Qt 6.8.3: LGPL-3.0/GPL depending on the component. Qt Core/Gui/Widgets and dynamic plugins are used, without static linking. Notices under `licenses/` and `_internal`. Corresponding sources: https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.8.3-src/ and https://download.qt.io/archive/qt/6.8/6.8.3/single/.
- PyInstaller 6.16.0: GPL-2.0 with executable-distribution exception; https://github.com/pyinstaller/pyinstaller/tree/v6.16.0.
- AppImage type2-runtime: MIT; https://github.com/AppImage/type2-runtime.
- DejaVu: Bitstream Vera/DejaVu license, bundled under `licenses/debian/`.
- Ubuntu 22.04 desktop libraries: license/source references in the package's `licenses/debian/*.copyright`. Corresponding source packages: https://archive.ubuntu.com/ubuntu/pool/.

Icon artwork was supplied by the project owner. NVIDIA, DLSS, Steam and Proton are trademarks of their owners; no affiliation is claimed.

Technical references in `docs/sources/` come from NVIDIA Streamline, NVIDIA DLSS and DXVK-NVAPI and are not relicensed under this project's BSD license. Refer to catalog links and upstream repositories for their terms.
