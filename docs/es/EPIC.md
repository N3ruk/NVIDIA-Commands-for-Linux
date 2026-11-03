# Epic Games Launcher oficial para Linux

[English / evidencia detallada](../EPIC.md) · [Inicio](../../README_ES.md) · 2026-11-03

Se confirmó en la [página oficial](https://launcher.epicgames.com/) la Preview nativa de Linux y en las [notas](https://launcher.epicgames.com/release-notes) la versión 0.109.0. El AppImage público inspeccionado se identifica como **0.109.0+ge564459** y usa Rust/Tauri; no se ha tratado como Electron ni como el launcher Windows bajo Wine.

El análisis estático ordinario localizó cuatro campos en el esquema por juego: `autoUpdate`, `priorityDownload`, `additionalCommandsEnabled` y `additionalCommands`. No se estableció un editor de variables por juego en ese esquema. La búsqueda nativa de REA/Ghidra agotó su plazo; las observaciones de campos proceden de símbolos/desensamblado con herramientas ordinarias, no de una descompilación REA completada. El informe inglés recoge hash, rangos y límites.

## Cómo usar la salida

1. Elige **Epic oficial · sesión del launcher** y la ruta absoluta de su AppImage/binario.
2. Puedes añadir un enlace real `com.epicgames.launcher://apps/…` copiado de un acceso del juego; sin enlace, ábrelo desde la biblioteca.
3. **Cierra Epic por completo** y ejecuta el comando copiado en una terminal. Una segunda instancia puede reenviar la petición a la anterior, que conserva su entorno antiguo.
4. El comando inicia Epic con variables para **toda esa sesión**. No es un perfil aislado por juego y también puede afectar al launcher. Cierra y reinicia con otra configuración para cambiar de entorno.
5. Usa **Copiar argumentos Epic** para copiar argumentos como `-dx12` por separado y habilitarlos en los ajustes del juego.

No pegues variables de entorno ni `%command%` en el campo de argumentos del juego. Los wrappers de Steam/Gamescope se bloquean en este destino: envolver el launcher no equivale a envolver el juego.

## Límite importante

**No se ha verificado la herencia hasta un juego real con cuenta.** No se ha iniciado sesión ni accedido a configuraciones privadas. Las pruebas verifican composición, comillas, interfaz y portapapeles; la propagación al runtime/juego sigue siendo experimental. Las rutas de adquisición de Proton presentes en el binario no demuestran que ese Proton implemente las variables de Steam.

Los controladores, runtimes, bibliotecas y compatibilidad de cada juego siguen siendo requisitos externos. No se escriben archivos internos de Epic ni se inventan identificadores, tokens o parámetros privados.
