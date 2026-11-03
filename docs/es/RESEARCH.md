# Comparación NVIDIA App → Linux

[English / matriz completa](../RESEARCH.md) · [Inicio](../../README_ES.md) · Revisión: 2026-11-03

GPU de referencia: **GeForce RTX 5070 / Blackwell / RTX 50**. Una GPU compatible no demuestra que un juego, Proton, una biblioteca o un compositor acepten un ajuste. NVIDIA Commands for Linux sigue siendo un generador, no un port de NVIDIA App.

| Área | Resultado |
| --- | --- |
| DLSS SR/DLAA, RR y modelos | Conservados; escala personalizada 33–100 % añadida para SR/RR con DXVK-NVAPI |
| FG/MFG/dinámico | FG en RTX 40/50; MFG y dinámico en RTX 50; modo `dynamic` y conteo multiplicador−1 verificados |
| Actualizador DLSS | Solicitud al actualizador NGX de Proton; no se sustituyen bibliotecas nativas |
| Presets DLSS en juegos Linux nativos | Sin ruta documentada equivalente; se ocultan/reinician las selecciones exclusivas de Proton |
| Smooth Motion | Capa Vulkan del driver; bases revisadas RTX 50: 580.65.06, RTX 40: 580.95.05, x86_64. Bloqueos con FG y opción de cola gráfica para overlays |
| Reflex | Integración del juego; puente Vulkan opcional con su capa. No activa Reflex en juegos que no lo integran |
| Baja latencia y FPS | Alternativa `latencySleep` DXVK; limitadores DXVK/VKD3D, no sustitutos universales de NVIDIA ULL |
| VSync, anisotropía, LOD | Según API: DXVK/OpenGL; LOD solo DXVK. No se envían ajustes DXVK a DX12/Vulkan directo |
| Nitidez | Filtro OpenGL/Vulkan documentado en R595, intensidad y reducción de grano; no activa escalado NIS |
| NIS/FSR y supersampling | Fuera del generador; Gamescope ofrece alternativas separadas, no DLDSR/DSR del driver ni escalado temporal |
| AA | Permiso FXAA OpenGL para un perfil ya configurado. No se finge un forzado universal de MSAA/MFAA/AA temporal |
| Caché/multihilo | Variables del driver OpenGL; sin borrar cachés ni cambiar la precaché Steam |
| HDR | Fuera del generador; configuración externa de juego/runtime/pantalla/compositor. **No es RTX HDR ni conversión SDR→HDR** |
| G-SYNC/VRR | Permiso OpenGL; la pantalla y sesión deben estar configuradas previamente |
| Indicadores/estadísticas | Indicador del driver e indicadores DLSS. DXVK HUD/MangoHud quedan fuera de la interfaz; no incluye Reflex Analyzer |
| GPU híbrida | Detección real; sin simular GPU. PRIME es una configuración externa, no un control de la interfaz |
| Freestyle, RTX Dynamic Vibrance, RTX HDR, Ansel | Sin una ruta equivalente verificada para comandos Linux; no se ofrecen como si existiera |
| Optimización automática por juego | No se dispone de los perfiles/servicio de NVIDIA App; no se inventan ajustes óptimos |
| Drivers, overclock, voltajes, ventiladores y potencia | Tareas de sistema o herramientas separadas con restricciones; no variables de lanzamiento. Sin acciones globales/privilegiadas |
| Resolución física, refresco, color, varios monitores | Configuración del compositor/X11; Gamescope solo crea una superficie de juego anidada |
| Battery Boost, WhisperMode, FPS en segundo plano | Sin equivalente general verificado; el límite FPS normal no equivale a estas funciones |
| ShadowPlay/Highlights/Instant Replay | No portados; OBS/NVENC y captura del escritorio son alternativas separadas |
| RTX Video/Broadcast/cámara/audio | No incorporados como variables de juegos; soporte distinto según aplicación/SDK/plataforma |
| Cuenta/recompensas/descubrimiento de apps | Fuera del generador; sin acceso a credenciales |

Las fuentes oficiales, versiones revisadas y la matriz exhaustiva están en [RESEARCH.md](../RESEARCH.md); sus huellas están en el [manifiesto](../sources/linux-research-manifest.json). Los umbrales de Smooth Motion son **bases documentadas comprobadas**, no una afirmación de haber encontrado la primera versión de soporte.

DRS, variables nativas del driver, configuración de capas de traducción y wrappers son mecanismos distintos. No se equiparan. El programa comprueba los requisitos conocidos y no afirma que un juego haya aplicado los ajustes. Los ajustes anteriores ajenos se conservan con aviso, no se certifican. No es posible leer desde este generador el FG activado dentro del juego ni interpretar todos los IDs DRS numéricos o wrappers externos.
