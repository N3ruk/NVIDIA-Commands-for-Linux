# Auditoría de comandos y tecnologías NVIDIA — 2026-11-19

[English](../AUDIT-2026-11-19.md) · [Inicio](../../README_ES.md)

## Estado y alcance

Auditoría de los cambios respecto a la versión pública 2.0.0, commit `685984ec104d81599545ad43bcf528f73d304d12`, incorporados a la release **2.1.0**. La [verificación de la release](../VERIFICATION.md) documenta las comprobaciones de los paquetes.

## Hallazgos y correcciones

1. **El comando inicial de K de la release ya era correcto.** No sería riguroso atribuir el fallo a todos los comandos anteriores. El problema reproducido era `Reset → elegir K`: Reset desmarcaba el actualizador NGX y elegir un preset no lo restauraba. También se podía desmarcar manualmente. La configuración DRS por sí sola no actualiza una DLL antigua.
2. **K venía preseleccionado.** Seleccionar únicamente Smooth Motion añadía también SR/K y NGX, aunque no se hubieran solicitado. Ahora todas las tecnologías empiezan sin override y la salida está vacía hasta elegir algo.
3. **NGX es una dependencia del preset**, no una casilla opcional que pueda quedar desactivada tras Reset. Las solicitudes de modelos reconocidas que se importan reciben también esa dependencia. La casilla adicional permite solicitar *solo* actualización NGX, sin elegir modelo ni calidad. Desactivar FG sin elegir un preset no solicita actualización.
4. **Retirado «Ajustes NVIDIA / Linux»**, su clase de interfaz y sus conexiones. Los controles generales de FPS, VSync, texturas, VRR, caché, multihilo, FXAA y OSD ya no se ofrecen. Smooth Motion, Reflex y nitidez se conservan como tecnologías independientes, con ficha y requisitos; no son funciones nuevas inventadas para esta revisión. La composición interna histórica de otras opciones se conserva por compatibilidad, según AGENTS.md, pero no se puede activar desde la interfaz.
5. **Alcance explícito:** un preset SR no selecciona RR, FG, DLAA, modo de calidad, nitidez, overlays ni ajustes generales. Las opciones actuales pegadas voluntariamente por el usuario se conservan y se advierte sobre overrides ajenos; no se consideran selecciones implícitas del programa. Reset permite empezar sin ellas.
6. **Conflictos:** se detectan valores FG importados tanto nominales como numéricos (incluido `NGX_DLSS_FG_OVERRIDE=1/0x1`). Un `FG off` explícito permite Smooth Motion. Se bloquea aplicar la capa Smooth Motion simultáneamente al wrapper Gamescope y al juego; se rechaza activar el puente Reflex si los parámetros importados deshabilitan su capa.

## Comandos mínimos comprobados

Solo SR/K, sin importar otros parámetros y dejando la calidad controlada por el juego:

```text
PROTON_ENABLE_NGX_UPDATER=1 DXVK_NVAPI_DRS_SETTINGS=NGX_DLSS_SR_OVERRIDE=on,NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_k %command%
```

Solo actualizar componentes DLSS:

```text
PROTON_ENABLE_NGX_UPDATER=1 %command%
```

Solo Smooth Motion:

```text
NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command%
```

NGX permite descargar componentes compatibles a la caché del prefijo; **no fija una versión comercial ni una versión de DLL**, no sustituye la DLL del juego ni verifica el preset efectivo. Elegir K tampoco modifica la resolución ni el modo Calidad/Rendimiento.

## Auditoría de funciones: Steam / Linux

| Función | Ruta documentada y requisitos | Decisión |
| --- | --- | --- |
| DLSS SR/DLAA, RR, FG/MFG | DRS de DXVK-NVAPI + NGX en Proton; integración en el juego. RTX 20+ para SR/RR; RTX 40+ FG; RTX 50 para MFG/dinámico | Conservadas, dependencias y alcance corregidos |
| Smooth Motion | `NVPRESENT_ENABLE_SMOOTH_MOTION=1`; Vulkan incluido DXVK/VKD3D; `VK_LAYER_NV_present`; bases RTX 50 580.65.06+, RTX 40 580.95.05+ | Ya existía; ficha independiente. Sin FG simultáneo ni activación automática |
| Compatibilidad Smooth Motion/overlays | `NVPRESENT_QUEUE_FAMILY=1`, presenta desde cola gráfica con posible coste | Ya existía; solo se añade al marcarlo expresamente |
| Reflex DirectX | El juego integra Reflex y DXVK-NVAPI lo enruta | No requiere un interruptor universal ni un comando añadido |
| Reflex Windows/Vulkan, puente | `DXVK_NVAPI_VKREFLEX=1` y capa `VK_LAYER_DXVK_NVAPI_reflex`, además de integración del juego | Ya existía; ficha específica, sin suplantarlo por una opción DXVK de baja latencia |
| Reflex Windows/Vulkan, ruta directa moderna | winevulkan 1.4.357+ y revisión 2 de `VK_NV_low_latency`; la aplicación debe habilitar la extensión | Documentada. No necesita activar el puente; no se ofrece como función forzada en cualquier juego |
| Nitidez NVIDIA | `__GL_SHARPEN_ENABLE`, `__GL_SHARPEN_VALUE`, `__GL_SHARPEN_IGNORE_FILM_GRAIN`; OpenGL/Vulkan, base R595 | Ya existía; ficha independiente, solo variables propias |
| Indicadores DLSS | Wine: `DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS`, **persistente**. Vulkan nativo: `__NGX_SHOW_INDICATOR`, temporal y solo SR | Diagnóstico opcional en Más opciones; nunca se añade por elegir un preset |
| DLSS NR, NR SL y override Streamline | La wiki actual añade `NGX_DLSS_NR_OVERRIDE`, preset NR, `NGX_DLSS_NR_SL_OVERRIDE` y `SL_DLSS_OVERRIDE` | Novedades de sintaxis identificadas, **no expuestas como tecnología utilizable**: las fuentes revisadas no acreditan una matriz de GPU/juegos/modelos ni una finalidad fiable que presentar al usuario. Reconocer un enum no demuestra una función aplicada |
| RTX HDR, Dynamic Vibrance, Freestyle, DLDSR, optimización automática, ShadowPlay | No se ha acreditado una variable Steam/Linux equivalente en las fuentes revisadas | No se inventan controles. HDR nativo, Gamescope, grabación NVENC y configuración global son mecanismos distintos |
| FPS/VSync/texturas/VRR/caché y otros ajustes generales | Algunos tienen rutas DXVK u OpenGL específicas, pero no son funciones universales NVIDIA | Retirados del panel solicitado; no se reintroducen con otro nombre |

No se han encontrado otras tecnologías NVIDIA ausentes con requisitos y un comando de usuario suficientemente acreditados para incorporarlas en esta revisión. La búsqueda no demuestra que no existan experimentos de terceros.

## Fuentes primarias

Consultadas el 2026-11-19; URLs y SHA256 en [manifiesto](../sources/launch-audit-2026-11-19.json). Las copias descargadas quedan en `.cache/audit-2026-11-19/`.

- [DXVK-NVAPI: NGX y presets](https://github.com/jp7677/dxvk-nvapi/wiki/Passing-driver-settings#ngx-snippet-updates-and-preset-overrides).
- [DXVK-NVAPI: requisitos y Reflex Vulkan](https://github.com/jp7677/dxvk-nvapi#requirements).
- [NVIDIA 595.99.02: NGX](https://download.nvidia.com/XFree86/Linux-x86_64/595.99.02/README/ngx.html), [Smooth Motion](https://download.nvidia.com/XFree86/Linux-x86_64/595.99.02/README/nvpresent.html), [variables OpenGL/Vulkan](https://download.nvidia.com/XFree86/Linux-x86_64/595.99.02/README/openglenvvariables.html).
- [Enumeraciones NVIDIA NVAPI](https://github.com/NVIDIA/nvapi/blob/main/NvApiDriverSettings.h): FG override on=1; modo on=2, auto=3, dynamic=4, off=1.

## Verificación de esta revisión

- Suite de lógica/UI: **108 pruebas**, con comandos exactos, aislamiento entre tecnologías, copia, Reset y restricciones de GPU/API/driver/capa. Log final en `.cache/audit-2026-11-19/tests-final.log`.
- Autocomprobación de la aplicación desde las fuentes, recursos y portapapeles; capturas de la GPU real RTX 2060 y de Smooth Motion con RTX 5070 **simulada**. Diseño oscuro/verde y salidas Steam/Epic conservados.
- Capturas en `artifacts/audit-2026-11-19/`; comparación reproducida antes/después en `.cache/audit-2026-11-19/before-after.json`.
- El comando SR/K coincide exactamente con el que se verificó por separado en Rise of the Tomb Raider el 2026-11-19: indicador oficial K y DLSS 310.9.16 en dos arranques. Esa evidencia previa no certifica otros juegos ni otros presets. **Esta revisión no ha vuelto a iniciar juegos**, medir FPS ni probar físicamente RTX 40/50.
- No se han modificado Steam, DLL, controladores ni el prefijo del juego. El empaquetado y la publicación 2.1.0 se documentan por separado en [VERIFICATION.md](../VERIFICATION.md).
