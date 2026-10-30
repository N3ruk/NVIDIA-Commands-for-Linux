# DLSS Studio

- Proyecto independiente de UGM, UpscaleStudio y Zafiro. No modificar esos proyectos para trabajar aquí.
- Interfaz y explicaciones en español. Mantener separadas tecnología, preset y modo de calidad.
- Lógica sin Qt en `dlss_studio/core.py`; UI en `dlss_studio/ui.py`.
- Qt: se prefiere PySide6, con PyQt6 como alternativa disponible en este equipo.
- Recursos instalables: `dlss_studio/data/catalog.json` y `dlss_studio/assets/`.
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

## Distribución 1.0.0

- Icono principal: `dlss_studio/assets/dlss-studio.png`, no sustituir por el SVG antiguo.
- Versiones sincronizadas en pyproject.toml y dlss_studio/__init__.py.
- Construcción: `python3 tools/build_rootless.py`; detalles en docs/BUILD.md.
- Validar AppImage y DEB en un sistema base sin Python/Qt; no confundir una prueba con bibliotecas del host con autonomía real.
