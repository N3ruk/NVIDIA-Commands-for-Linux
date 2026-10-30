# Componentes de terceros

La licencia BSD-3-Clause del proyecto se aplica al código propio; los componentes
incluidos conservan sus licencias. Las bibliotecas son dinámicas y reemplazables
en `usr/lib/dlss-studio/_internal` (dentro de AppImage extraído o `/opt/dlss-studio`).

- Python 3.10: PSF License. Fuente: https://www.python.org/downloads/source/
- PySide6 / Shiboken6 6.8.3 y Qt 6.8.3: LGPL-3.0/GPL según componente;
  se utilizan Qt Core, Gui, Widgets y sus plugins dinámicos, sin enlace estático.
  Licencias y avisos distribuidos en `licenses/` y `_internal`.
  Fuentes correspondientes: https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.8.3-src/
  y https://download.qt.io/archive/qt/6.8/6.8.3/single/.
- PyInstaller 6.16.0: GPL-2.0 con excepción para distribuir ejecutables;
  https://github.com/pyinstaller/pyinstaller/tree/v6.16.0.
- AppImage type2-runtime: MIT; https://github.com/AppImage/type2-runtime.
- DejaVu: licencia Bitstream Vera/DejaVu. Incluida en `licenses/debian/`.
- Bibliotecas de escritorio procedentes de Ubuntu 22.04: licencias y enlaces a
  código fuente en `licenses/debian/*.copyright` del paquete. Paquetes fuente:
  https://archive.ubuntu.com/ubuntu/pool/.

La iconografía fue proporcionada por el propietario del proyecto. NVIDIA, DLSS,
Steam y Proton son marcas de sus respectivos titulares; no hay afiliación.

Las referencias técnicas en `docs/sources/` proceden de NVIDIA Streamline,
NVIDIA DLSS y DXVK-NVAPI; no están sujetas a la licencia BSD de este proyecto.
Consulte los enlaces del catálogo y los repositorios originales para sus términos.
