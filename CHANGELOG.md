# Changelog

## 2.1.0 — 2026-11-19

Changes relative to 2.0.0 only.

### Changed

- Neutral startup: no preselected SR/K or unrelated overrides when selecting another technology.
- Smooth Motion, Reflex and NVIDIA sharpening moved out of the removed general panel into independent technology cards; they are not new technologies in this release.
- NGX update-only selection is independent of model/quality selection. DLSS indicators are explicit opt-in diagnostics under More options.

### Fixed

- DLSS preset/model requests always include their NGX updater dependency, including after Reset and for recognized imported overrides. Selecting SR/K does not implicitly select RR, FG, DLAA or a quality mode.
- Smooth Motion conflicts now include imported numeric FG-on values and simultaneous application to Gamescope and the game. Explicit FG-off remains compatible.
- Reflex bridge activation is rejected when imported parameters disable its required layer.

### Removed

- **Ajustes NVIDIA / Linux** general settings panel and its FPS limits, VSync, anisotropy/texture LOD, VRR, shader cache, threaded optimization, DXVK latency, FXAA and driver OSD controls. Historical internal composition remains for compatibility, but these controls are no longer exposed.

## Español

### 2.1.0 — 2026-11-19

Solo diferencias respecto a 2.0.0.

#### Cambios

- Inicio neutro: sin SR/K preseleccionado ni ajustes ajenos al seleccionar otra tecnología.
- Smooth Motion, Reflex y nitidez NVIDIA pasan del panel general retirado a fichas independientes; no son tecnologías nuevas de esta versión.
- Selección de solo actualización NGX independiente del modelo y la calidad. Indicadores DLSS como diagnóstico explícito en Más opciones.

#### Arreglos

- Las solicitudes de presets/modelos DLSS incluyen siempre su dependencia NGX, también después de Reset y para overrides importados reconocidos. Elegir SR/K no selecciona implícitamente RR, FG, DLAA ni un modo de calidad.
- Los conflictos de Smooth Motion incluyen valores numéricos FG-on importados y la aplicación simultánea a Gamescope y al juego. FG-off explícito sigue siendo compatible.
- Se rechaza activar el puente Reflex si los parámetros importados deshabilitan la capa necesaria.

#### Eliminado

- Panel **Ajustes NVIDIA / Linux** y controles generales de límite FPS, VSync, anisotropía/LOD de texturas, VRR, caché de shaders, multihilo, latencia DXVK, FXAA y OSD del driver. La composición interna histórica se conserva por compatibilidad, pero ya no se ofrecen esos controles.
