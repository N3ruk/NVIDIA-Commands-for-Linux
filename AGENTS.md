# NVIDIA Commands for Linux

- Proyecto independiente de UGM, UpscaleStudio y Zafiro. No modificar esos proyectos para trabajar aquí.
- Interfaz y explicaciones en español. Mantener separadas tecnología, preset y modo de calidad.
- Lógica sin Qt en `nvidia_commands/core.py`; UI en `nvidia_commands/ui.py`.
- Qt: se prefiere PySide6, con PyQt6 como alternativa disponible en este equipo.
- Recursos instalables: `nvidia_commands/data/catalog.json` y `nvidia_commands/assets/`.
- Actualizar el catálogo desde `tools/build_catalog.py`, con fuentes y fecha. No inventar equivalencias entre letras SR/RR/FG ni soporte Linux a partir de Windows.
- Prohibido ejecutar parámetros introducidos por el usuario. El generador solo compone y valida cadenas.
- Preservar los parámetros previos soportados; bloquear entradas que no puedan combinarse y explicar el motivo. Un único `%command%`.
- No modificar Steam ni sustituir DLL. No realizar pruebas de juegos o instalaciones privilegiadas sin que formen parte del encargo.
- Pruebas: `python3 -m unittest discover -s tests -v`.
- Vista verificable: `QT_QPA_PLATFORM=offscreen ./run.sh --screenshot artifacts/preview.png`.
- Acceso de usuario: `python3 tools/install_user.py`, sin sudo.
- Empaquetado: `python3 -m pip wheel --no-deps --no-build-isolation --no-index . -w dist`.
- Nunca afirmar que un modelo se aplicó en un juego sin evidencia del runtime. La aplicación no realiza esa verificación.

## Diseño acordado (2026-10-29)

- Mantener la estética oscura y verde. Una sola pantalla orientada a elegir preset y copiar.
- GPU automática y discreta en la barra lateral; sin formulario de Proton, resolución u objetivo ni simulación de GPU.
- Sin secciones «Entender DLSS» / «Fuentes y datos», pestañas solo informativas ni confirmaciones manuales de integración.
- Generación explícita en selector y ficha: J/K = 4.0; L/M = 4.5; CNN = 2.x/3.x sin versión exacta atribuida. RR transformer = familia 4.0+, no una versión exacta por letra.
- Conservar referencias técnicas en el catálogo/docs, no convertir la UI en una wiki.
- Barra lateral limpia bajo la GPU: sin «Tus perfiles», textos inferiores ni versión. Sin insignia superior «COMANDO GENERADO». Mantener el área del comando y su botón de copia.
- Compatibilidad FG/MFG se sigue validando. Los perfiles guardados anteriormente no se borran, pero ya no se ofrecen en la interfaz.

## Distribución 2.0.0

- Icono principal: `nvidia_commands/assets/nvidia-commands-for-linux.png`, no sustituir por el SVG antiguo.
- Versiones sincronizadas en pyproject.toml y nvidia_commands/__init__.py.
- Construcción: `python3 tools/build_rootless.py`; detalles en docs/BUILD.md.
- Validar AppImage y DEB en un sistema base sin Python/Qt; no confundir una prueba con bibliotecas del host con autonomía real.

## Ampliación autorizada 2026-11-03

- Nombre público y paquete: NVIDIA Commands for Linux / nvidia-commands-for-linux. Módulo: nvidia_commands.
- Mantener Steam por juego separado de Epic por sesión; Epic es experimental hasta verificar un juego autenticado. No afirmar perfiles de variables por juego.
- Filtro adicional por API; opciones DXVK/OpenGL no son universales. Juegos nativos no admiten estos presets DLSS de Proton.
- Comillas de variables Steam: NOMBRE=valor_entrecomillado, no entrecomillar toda la asignación (eso intentaría ejecutar un nombre de comando).
- Smooth Motion y FG/MFG no se combinan. No activar automáticamente Smooth Motion sobre Gamescope y el juego a la vez.
- Escalas DLSS personalizadas: 33–100 %. MFG dinámico: NGX_DLSSG_MODE=dynamic. Conteo DRS: multiplicador menos uno.
- Investigación, fuentes, límites y verificación en docs/RESEARCH.md, docs/EPIC.md y docs/VERIFICATION.md.
