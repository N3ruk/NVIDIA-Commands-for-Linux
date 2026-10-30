# DLSS Studio 1.0.0 · 2026-10-30

## Diseño

- Pantalla única oscura y verde: elegir tecnología/preset y copiar comando.
- GPU automática y discreta; sin contexto, wiki, perfiles ni textos al pie.
- Generación explícita en selector/ficha; sin insignia superior «COMANDO GENERADO».
- Nuevo icono PNG suministrado por el propietario, aplicado a ventana y lanzadores.

## Distribución

- AppImage x86_64 y DEB amd64 con Python 3.10, Qt 6.8.3, bibliotecas y fuentes.
- Base de construcción: Ubuntu 22.04; requisito mínimo glibc 2.35.
- Catálogo e icono incluidos; no se necesita Python/Qt del sistema.
- Licencias y condiciones de las bibliotecas acompañan a los paquetes.
- Scripts de construcción, hashes de descarga y autocomprobación incluidos.

## Comprobación

37 pruebas de lógica/UI superadas. AppImage verificado en X11 y Wayland.
Instalación DEB offline y ejecución de ambos formatos en Ubuntu Base sin Python/Qt.
Auditoría de bibliotecas compartidas sin dependencias ausentes; glibc máxima 2.35.

Las pruebas de lógica/UI cubren comandos, presets, generaciones, compatibilidad,
parámetros existentes, portapapeles, persistencia interna y aislamiento de las
bibliotecas del ejecutable al consultar `nvidia-smi` del sistema.
`--self-test` comprueba recursos e interacción de selección/copia con hardware
simulado. La captura normal utiliza la detección real.

## Límites

No se ha probado dentro de un juego. No se modifica Steam, no se sustituyen DLL
ni se instalan controladores. No se garantiza compatibilidad con todas las
distribuciones, ARM ni musl; véase BUILD.md.
