<img src="dlss_studio/assets/dlss-studio.png" width="100" align="right" alt="DLSS Studio">

# DLSS Studio · 1.0.0

**Facilita configurar presets DLSS y copiar comandos para tus juegos.**

Aplicación de escritorio en español para Steam/Linux/Proton. Elige tecnología,
preset y modo de calidad; copia el comando y pégalo en los parámetros de Steam.
No modifica Steam ni sustituye DLL. No afiliada a NVIDIA ni a Valve.

![Interfaz de DLSS Studio](docs/screenshot.png)

## Descargar

**[Descargas de la versión 1.0.0](https://github.com/N3ruk/DLSS-Studio/releases/tag/v1.0.0)**

| Formato | Uso |
| --- | --- |
| [AppImage x86_64](https://github.com/N3ruk/DLSS-Studio/releases/download/v1.0.0/DLSS-Studio-1.0.0-x86_64.AppImage) | Portable, sin instalación |
| [DEB amd64](https://github.com/N3ruk/DLSS-Studio/releases/download/v1.0.0/dlss-studio_1.0.0_amd64.deb) | Debian, Ubuntu, Linux Mint y derivados compatibles |

Ambos incluyen **Python, Qt, bibliotecas auxiliares y fuentes**. No necesitan
instalar Python/PySide6 ni descargar dependencias de la aplicación.

**Requisitos:** Linux x86_64 con **glibc 2.35+** y sesión gráfica X11/Wayland;
por ejemplo Ubuntu 22.04+, Debian 12+ o Linux Mint 21+. No son paquetes para ARM,
32 bits ni Alpine/musl. El DEB requiere un sistema compatible con Debian.
El controlador NVIDIA y `nvidia-smi`, Steam y Proton no están incluidos.

### AppImage

```sh
chmod +x DLSS-Studio-1.0.0-x86_64.AppImage
./DLSS-Studio-1.0.0-x86_64.AppImage
```

Si tu distribución no permite FUSE:

```sh
./DLSS-Studio-1.0.0-x86_64.AppImage --appimage-extract-and-run
```

### DEB

Abre el archivo con el instalador de paquetes de tu distribución. Se instala en
`/opt/dlss-studio` y añade **DLSS Studio** al menú de aplicaciones.
El paquete solo declara glibc como dependencia del sistema; las dependencias
propias de la aplicación ya están dentro. No instala controladores ni usa pip.

Puedes verificar la descarga con `SHA256SUMS`, disponible en la misma publicación:

```sh
sha256sum -c SHA256SUMS
```

## Uso

1. La GPU se detecta automáticamente y aparece discretamente en la barra lateral.
2. Elige tecnología y preset: **J/K · DLSS 4.0**, **L/M · DLSS 4.5**.
3. Ajusta opcionalmente Calidad/Rendimiento, independientemente del modelo.
4. En **Más opciones**, conserva tus parámetros actuales o desactiva el actualizador NGX.
5. Pulsa **Copiar para Steam** y pega en Propiedades → General → Parámetros de lanzamiento.
6. Activa la tecnología dentro del juego cuando corresponda.

Una sola pantalla, sin perfiles, formularios de contexto ni páginas de wiki.
La compatibilidad FG/MFG se valida automáticamente según la familia de GPU.

## Incluido

- Super Resolution/DLAA: modelos J/K, L/M, automático e históricos.
- Ray Reconstruction: modelos y generación identificados independientemente de SR.
- Frame Generation: FG, MFG y modo dinámico según hardware compatible.
- FG de NVIDIA bloqueado en RTX 20/30; MFG y dinámico requieren RTX 50.
- Conservación de parámetros existentes, combinación de ajustes DRS y detección de conflictos.
- Catálogo offline con referencias; la app no ejecuta el comando que genera.

## Alcance

La generación indicada es la del modelo/función solicitados, no una certificación
de la DLL o modelo cargado dentro del juego. La aplicación del preset depende
del juego, Proton, NGX, DXVK-NVAPI y el controlador. No se ha verificado dentro de un juego.

Las letras históricas CNN se muestran como **DLSS 2.x / 3.x**, sin atribuirles una
versión exacta. En RR transformer se indica **familia DLSS 4.0+**, sin equiparar
las letras de tecnologías diferentes. Automático no fija una generación concreta.

El actualizador NGX de Proton puede descargar componentes al iniciar el juego;
se puede desactivar en **Más opciones**. La app en sí no instala esos componentes.
Las cadenas complejas de shell no se ejecutan ni se reinterpretan silenciosamente.
En equipos multi-GPU se muestra la primera fila de `nvidia-smi` y se avisa.

## Desarrollo

Python 3.10+ y PySide6 o PyQt6:

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[pyside]'
./run.sh
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

Acceso al menú para desarrollo, sin sudo: `python3 tools/install_user.py`.

- [Construcción de AppImage y DEB, requisitos y comprobaciones](docs/BUILD.md).
- `dlss_studio/core.py`: hardware, validación y generación del comando.
- `dlss_studio/ui.py`: interfaz Qt.
- `tools/build_catalog.py`: generador del catálogo; revisar las fuentes antes de modificarlo.
- `docs/sources/`: referencias técnicas y evidencia del catálogo.

## Licencia

Código propio: [BSD-3-Clause](LICENSE). Dependencias y referencias técnicas:
[componentes de terceros](THIRD_PARTY.md). Las marcas pertenecen a sus titulares.
