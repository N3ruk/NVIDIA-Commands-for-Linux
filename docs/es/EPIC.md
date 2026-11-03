# Epic Games Launcher oficial para Linux

[English / evidencia detallada](../EPIC.md) · [Inicio](../../README_ES.md) · 2026-11-03

La [página oficial](https://launcher.epicgames.com/) ofrece la Preview nativa de Linux. El AppImage inspeccionado se identifica como **0.109.0+ge564459**, usa Rust/Tauri y no se ha tratado como Electron ni como el launcher Windows bajo Wine.

El análisis estático localizó cuatro campos del esquema por juego: `autoUpdate`, `priorityDownload`, `additionalCommandsEnabled` y `additionalCommands`. No se estableció un editor de variables por juego. Las observaciones proceden de símbolos/desensamblado ordinarios; la búsqueda REA/Ghidra agotó su plazo y no produjo una descompilación. El informe inglés recoge hash, rangos y límites.

## Interfaz actual: solo argumentos del juego

**Comando Steam** y **Argumento Epic** aparecen en paralelo con copia independiente. Steam incluye variables, un único `%command%` y argumentos. Epic contiene **únicamente los argumentos reales del juego** posteriores a `%command%`.

1. En **Más opciones**, introduce los parámetros actuales, por ejemplo `%command% -dx12`.
2. Copia `-dx12` desde **Argumento Epic** y pégalo en los argumentos adicionales del juego en Epic. Usa solo parámetros que ese juego admita.
3. Las selecciones NVIDIA no se convierten en argumentos: si solo eliges DLSS, nitidez o Smooth Motion, la salida Epic queda vacía.

**Las variables NVIDIA no funcionan pegándolas en los argumentos del juego.** Tampoco pegues `%command%` ni wrappers Steam. La aplicación no inicia Epic ni ofrece perfiles de variables por juego.

## Entorno manual por sesión: experimental

Como técnica de terminal separada, no como salida de esta interfaz:

```sh
env VARIABLE=valor '/ruta/absoluta/EpicGamesLauncher.AppImage'
```

Sustituye el ejemplo por variables compatibles reales y la ruta de tu launcher, sin `%command%`. **Cierra Epic por completo antes de ejecutarlo** y abre el juego desde su biblioteca. Una segunda instancia puede reenviar la petición al proceso anterior y conservar su entorno antiguo.

Las variables afectan al launcher y potencialmente a todos los juegos de esa sesión. No es un perfil aislado por juego; para cambiar de configuración, cierra y reinicia el launcher.

## Límites

**No se ha verificado la herencia hasta un juego autenticado.** No se ha iniciado sesión ni accedido a configuraciones privadas. Las pruebas verifican extracción de argumentos, interfaz y portapapeles; no demuestran que el runtime de Epic implemente o conserve las variables de Steam/Proton.

Controladores, capas Vulkan, runtimes e integración del juego siguen siendo requisitos externos. No se escriben archivos internos de Epic ni se inventan identificadores o credenciales.
