# NVIDIA App → Linux capability audit

**2.1.0 capability matrix.** Changes and new-key findings: [2026-11-19 audit](AUDIT-2026-11-19.md). General tuning controls from 2.0.0 have been removed.

[Español](es/RESEARCH.md) · [Home](../README.md) · Reviewed 2026-11-19

Reference GPU: GeForce RTX 5070 (Blackwell, RTX 50). Hardware eligibility is not evidence that a particular game, component version or compositor accepts an override. NVIDIA App itself is a Windows application; this project is a command composer, not a port of that application.

## Coverage matrix

| NVIDIA App / graphics feature | Linux route / outcome in 2.1.0 |
| --- | --- |
| DLSS SR / model presets / DLAA | DXVK-NVAPI DRS, Proton games with DLSS integration; retained and extended with custom 33–100% scale |
| Ray Reconstruction | Independent RR DRS models/modes/scaling; integration required, not a general RT enable switch |
| Frame Generation | RTX 40/50 plus game/runtime support; hardware gate retained |
| Multi Frame Generation / dynamic MFG | RTX 50, recent components; fixed 2–6× / dynamic up to 6×; mode and generated-frame counts validated |
| DLSS component updates | Required with preset/model requests; optional update-only `PROTON_ENABLE_NGX_UPDATER=1`. Downloads handled by Proton; no native library replacement |
| Native Linux DLSS preset overrides | Not supported by the documented native route; Proton-only controls hidden/reset for native games |
| Smooth Motion | `NVPRESENT_ENABLE_SMOOTH_MOTION=1`; Vulkan layer, RTX 50 documented at 580.65.06, RTX 40 at 580.95.05; x86_64 baseline |
| Smooth Motion overlay workaround | Optional `NVPRESENT_QUEUE_FAMILY=1`, with a performance caveat |
| Reflex | DXVK-NVAPI forwards integrated DirectX Reflex; optional Vulkan bridge requires its layer. Does not add Reflex to games without it. Modern winevulkan can offer a separate direct-extension route |
| Low Latency Mode | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Max Frame Rate | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Vertical sync | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Adaptive sync / G-SYNC | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Anisotropic filtering | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Texture LOD bias | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Image sharpening | R595 documented `__GL_SHARPEN_ENABLE`, value and film-grain control, OpenGL/Vulkan |
| NVIDIA Image Scaling | Not offered by this generator; Gamescope NIS v1.0.3 is a separate spatial-upscaling alternative, not the Windows driver UI feature |
| DSR / DLDSR | No verified equivalent driver launch setting; Gamescope supersampling is a separate alternative, not offered here and explicitly not DLDSR |
| FSR spatial scaling | Not offered here; Gamescope FSR 1 is a separate spatial-scaling alternative, distinct from DLSS, FSR 2/3 and frame generation |
| FXAA / MSAA / MFAA | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Threaded optimization | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Shader disk cache | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| HDR game output | Not offered by this generator; native HDR requires game/runtime/display/compositor setup, separate from RTX HDR |
| RTX HDR / SDR-to-HDR | Not implemented; native HDR signaling is not RTX HDR |
| Freestyle / RTX Dynamic Vibrance / Ansel / Photo Mode | No verified interchangeable Linux driver launch-variable route; not exposed as equivalent |
| FPS/performance overlay | Removed from the interface in 2.1.0; historical internal composition retained for compatibility. |
| Actual DLSS model indicator | Wine NGX registry indicators (persistent, explicit disable); native Vulkan SR indicator via `__NGX_SHOW_INDICATOR` (temporary) |
| Preferred GPU / hybrid systems | Real GPU detection, no GPU spoofing; PRIME offload is external and not offered as a control |
| Optimal settings / cloud game optimization | No access to NVIDIA App's Windows profiles/cloud optimization; no invented recommendations per game |
| Driver download / Game Ready vs Studio | Distribution/package-manager responsibility, not generated as game launch options |
| Automatic GPU tuning / overclock / voltage / power / fans | Linux has separate NVML/NV-CONTROL tooling and hardware/session restrictions; not per-game launch variables. No global tuning or privileged writes in this app |
| Display resolution / refresh / multi-monitor / color / rotation / scaling | OS compositor/X11 settings; Gamescope changes nested game surface dimensions only, not physical display settings |
| Background FPS / laptop Battery Boost / WhisperMode | No verified general Linux equivalent exposed; foreground FPS limiter is not those features |
| ShadowPlay / Instant Replay / Highlights / recording / screenshots | Not ported. OBS with NVENC / desktop capture are separate Linux alternatives, not the NVIDIA App feature |
| RTX Video Super Resolution / Video HDR / Broadcast / webcam/audio effects | Not implemented as game launch variables; applications and SDK/platform support differ |
| System information / GPU discovery | Real `nvidia-smi` query; newest known GeForce RTX family selected on multi-NVIDIA systems with a notice; this does not prove the game uses that GPU |
| NVIDIA application discovery / rewards / account services | Out of scope; no NVIDIA/Epic/Steam account integration |

## Evidence and boundaries

Primary sources (download fingerprints: [research manifest](sources/linux-research-manifest.json)):

- [NVIDIA App features](https://www.nvidia.com/en-us/software/nvidia-app/).
- [NVIDIA Linux gaming guide: DLSS / Smooth Motion / Reflex](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html).
- NVIDIA Linux Smooth Motion manuals: [580.65.06](https://download.nvidia.com/XFree86/Linux-x86_64/580.65.06/README/nvpresent.html), [580.95.05](https://download.nvidia.com/XFree86/Linux-x86_64/580.95.05/README/nvpresent.html), [590.48.01](https://download.nvidia.com/XFree86/Linux-x86_64/590.48.01/README/nvpresent.html). These establish reviewed baselines, not a claim to have located the first release supporting each GPU.
- [NVIDIA R595 OpenGL environment documentation](https://download.nvidia.com/XFree86/Linux-x86_64/595.71.05/README/openglenvvariables.html), including explicit OpenGL/Vulkan scope for sharpening and API OSD.
- [DXVK-NVAPI README](https://github.com/jp7677/dxvk-nvapi) and [driver settings](https://github.com/jp7677/dxvk-nvapi/wiki/Passing-driver-settings); [NVAPI setting enums](https://github.com/NVIDIA/nvapi/blob/main/NvApiDriverSettings.h).
- [DXVK configuration](https://github.com/doitsujin/dxvk/blob/master/dxvk.conf), [VKD3D-Proton runtime options](https://github.com/HansKristian-Work/vkd3d-proton), [Proton](https://github.com/ValveSoftware/Proton).
- [Gamescope](https://github.com/ValveSoftware/gamescope), [official Epic launcher](https://launcher.epicgames.com/) and [release notes](https://launcher.epicgames.com/release-notes).

DRS, native driver environment, translation-layer configuration and optional wrappers are different mechanisms. They are not interchangeable or universally enforceable. Native libraries/runtime versions and game integration cannot be inferred from the GPU name. The application validates known hardware/API/driver/layer constraints, preserves unmodified inputs where possible and never asserts in-game success.

NVIDIA documents that Smooth Motion and native FG should not be combined. Inherited named/numeric FG-on settings and selected FG/MFG modes are checked. The generator cannot inspect in-game FG, unknown numeric DRS IDs or every external wrapper; warnings remain necessary. Existing user-supplied overrides not controlled by this selection are preserved with a warning, not certified.

NVIDIA's cloud optimizer, Windows-only integrations and separate system-management tasks are intentionally distinguished from missing implementations. "No verified route" means the cited scope did not establish a reliable launch-command implementation; it is not proof that no third-party experiment exists.
