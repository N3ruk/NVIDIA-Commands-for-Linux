# Construir y verificar Linux

## Paquetes de la versión 1.0.0

- `DLSS-Studio-1.0.0-x86_64.AppImage`: portable, Python y Qt incluidos.
- `dlss-studio_1.0.0_amd64.deb`: instalación autónoma en `/opt/dlss-studio`.
- `SHA256SUMS`: huellas de ambos paquetes.
- `build-info.json`: versiones del constructor y requisitos del sistema.

Arquitectura **x86_64/amd64**, GNU/Linux con **glibc 2.35 o posterior**:
Ubuntu 22.04+, Debian 12+, Linux Mint 21+ y otras distribuciones compatibles.
No funciona de forma nativa en ARM, Linux de 32 bits ni Alpine/musl.
El DEB solo es para distribuciones que utilicen ese formato.

Se incluyen el intérprete Python, PySide6/Qt, las bibliotecas gráficas auxiliares,
fuentes y licencias. No se ejecuta pip ni se descargan componentes al instalar.
No se incluyen glibc, el kernel, la sesión gráfica, controladores NVIDIA,
Steam ni Proton. Esos componentes pertenecen al sistema o al juego.
La detección real necesita `nvidia-smi` del controlador del sistema.

## Desde un Linux moderno, sin sudo

Necesitas `bwrap`, `tar`, Python 3 y acceso a Internet en la máquina de construcción:

```sh
python3 tools/build_rootless.py
```

Descarga Ubuntu Base 22.04.5, verifica SHA256 y construye en un user namespace.
El UID 0 solo existe dentro del entorno aislado: no obtiene privilegios del host.
Todo se conserva en `build/portable`; los paquetes terminados aparecen en `dist`.

## En Ubuntu 22.04 o un contenedor equivalente

Instala los paquetes de construcción indicados en `PACKAGES` de
`tools/build_rootless.py` y después:

```sh
python3 -m venv .venv-build
.venv-build/bin/pip install -r packaging/requirements-build.txt
QT_QPA_PLATFORM=offscreen .venv-build/bin/python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen .venv-build/bin/python tools/build_linux.py
```

El runtime AppImage está fijado por SHA256. Si cambia la descarga `continuous`,
la construcción se detiene hasta revisar y actualizar explícitamente su hash.
Las versiones principales de Python/Qt/freezer se guardan en `build-info.json`;
los repositorios apt y dependencias transitivas pueden evolucionar. No se promete
que dos compilaciones diferentes sean idénticas byte a byte.

## Comprobaciones

```sh
QT_QPA_PLATFORM=offscreen ./dist/DLSS-Studio-1.0.0-x86_64.AppImage --self-test
./dist/DLSS-Studio-1.0.0-x86_64.AppImage --version
(cd dist && sha256sum -c SHA256SUMS)
```

La autocomprobación usa una GPU simulada únicamente para probar presets y
portapapeles: no certifica la GPU real ni un modelo cargado dentro de un juego.
Para comprobar detección real e interfaz:

```sh
./dist/DLSS-Studio-1.0.0-x86_64.AppImage --screenshot artifacts/preview.png
```

Si FUSE no está disponible, el runtime admite `--appimage-extract-and-run`.
Para pruebas offline del DEB, se puede instalar dentro de otro Ubuntu Base limpio
y ejecutar `QT_QPA_PLATFORM=offscreen dlss-studio --self-test` sin instalar Python/Qt.
Los plugins X11 y Wayland están incluidos; el adaptador de apariencia GTK no es
necesario porque la app usa su propio estilo Fusion y no se distribuye.
