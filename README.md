<img src="nvidia_commands/assets/nvidia-commands-for-linux.png" width="100" align="right" alt="NVIDIA Commands for Linux">

# NVIDIA Commands for Linux · 2.0.0

**English** | [Español](README_ES.md)

**Compose NVIDIA graphics launch commands for Linux. Previously DLSS Studio.**

Choose DLSS models and supported Linux graphics options, then copy a command. The dark/green Spanish-language interface detects your GPU and filters controls by GPU generation and graphics API. **Not NVIDIA App, and not affiliated with NVIDIA, Valve or Epic Games.**

![Interface with real GPU detection](docs/screenshot.png)

## Download

[Release 2.0.0](https://github.com/N3ruk/NVIDIA-Commands-for-Linux/releases/tag/v2.0.0):

| Format | Download |
| --- | --- |
| Portable x86_64 AppImage | [NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage](https://github.com/N3ruk/NVIDIA-Commands-for-Linux/releases/download/v2.0.0/NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage) |
| Self-contained amd64 DEB | [nvidia-commands-for-linux_2.0.0_amd64.deb](https://github.com/N3ruk/NVIDIA-Commands-for-Linux/releases/download/v2.0.0/nvidia-commands-for-linux_2.0.0_amd64.deb) |

Both include Python, Qt, desktop libraries, fonts and licenses. Requires x86_64 GNU/Linux, **glibc 2.35+**, and an X11/Wayland desktop (Ubuntu 22.04+, Debian 12+, Mint 21+). Not ARM, 32-bit, musl or a universal Linux binary. Drivers and game runtimes are not bundled. Optional Gamescope/MangoHud must be installed separately.

```sh
chmod +x NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage
./NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage
# Without FUSE:
./NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage --appimage-extract-and-run
```

Open the DEB in your package installer. It installs under `/opt/nvidia-commands-for-linux`; package metadata declares replacement of `dlss-studio`. Old saved profile files are not deleted. The new application-menu entry is **NVIDIA Commands for Linux**. Verify downloads with the release's `SHA256SUMS`.

## Graphics controls

- **DLSS SR / DLAA:** J/K (4.0), L/M (4.5), recommended/historical presets, independent quality mode, custom 33–100% internal scale.
- **Ray Reconstruction:** independent model, mode and custom scale; requires game integration.
- **FG / MFG:** RTX 40 FG 2×; RTX 50 fixed up to 6× and dynamic MFG. Dynamic mode uses the actual `dynamic` DRS value.
- **Smooth Motion:** driver interpolation through `VK_LAYER_NV_present`; documented baselines RTX 50 **580.65.06+**, RTX 40 **580.95.05+**, Vulkan x86_64. Conflicts with game FG are blocked/reported.
- **NVIDIA sharpening:** OpenGL/Vulkan driver filter, strength and film-grain suppression; documented R595+ baseline. Not NIS scaling.
- **Latency / pacing:** optional Vulkan Reflex bridge, DXVK latency-sleep control, DXVK/VKD3D FPS limits and API-specific VSync.
- **Textures / display:** DXVK/OpenGL anisotropy, DXVK LOD bias, DXVK native-HDR signaling, OpenGL VRR, threaded optimizations, shader cache and FXAA permission.
- **Overlays:** DXVK HUD, optional MangoHud, driver graphics indicator and DLSS indicators with an explicit disable option.
- **Hybrid graphics:** optional NVIDIA PRIME render offload.
- **Optional Gamescope:** spatial NIS/FSR 1 upscaling and supersampling for Steam commands. Not driver DSR/DLDSR or temporal DLSS. Automatic Smooth Motion/Gamescope combination is blocked to avoid applying the layer to the compositor.

Native Linux and Wine/Proton are distinct: **native Linux DLSS preset overrides are not supported** by this implementation. Selecting a native API resets Proton-only selections to game-controlled. Native Vulkan can use the temporary SR indicator, Smooth Motion and compatible driver options.

![Linux options filtered for the detected GPU](docs/linux-options.png)

## Steam

1. Keep **Steam · por juego** selected and choose the game's actual graphics API.
2. Select compatible options. Existing simple launch parameters can be merged under **Más opciones**.
3. Copy into Steam → game Properties → General → Launch Options.
4. Enable integrated technologies in the game. Disable in-game FG when using Smooth Motion.

Exactly one `%command%` is generated. Existing wrappers, arguments and unrelated settings are preserved when safely mergeable; conflicting/complex input is rejected rather than executed.

## Official Epic Linux Preview — session-level, experimental

The official native Linux launcher exists; the inspected public build is **0.109.0+ge564459**. Its per-game additional-command field is **not a Steam launch-command field**.

1. Select **Epic oficial · sesión del launcher** and the absolute path to its official AppImage/binary.
2. Optionally paste a `com.epicgames.launcher://apps/…` game link.
3. Fully exit Epic, copy the generated **terminal command**, and run it. It starts the launcher with environment variables for **that whole session**, not an isolated per-game profile.
4. Copy any game arguments separately using **Copiar argumentos Epic** into the game's additional arguments setting.

No `%command%` is sent to Epic. Steam wrappers are rejected, not applied to the launcher as though it were the game. **Environment propagation through Epic's runtime to an authenticated game has not been verified.** Proton-specific settings only work if the actual runtime implements them. See [Epic investigation and limitations](docs/EPIC.md).

## Scope and verification

This is an offline command generator: no game launch, Steam/Epic edits, DLL replacement, driver installation or credential access. NGX updates can be requested; Proton may download components when you subsequently launch a game. DLSS debug indicators under Wine persist in the game prefix: run a generated disable-indicator command once to clear them.

No physical RTX 5070 or in-game model/FPS verification was available. Tests using RTX 5070/other generations are simulations; real detection was checked on an RTX 2060. Claims are separated in the [verification report](docs/VERIFICATION.md).

[Full NVIDIA App comparison and sources](docs/RESEARCH.md): RTX HDR/Dynamic Vibrance, Freestyle, DLDSR, automatic game optimization, ShadowPlay, driver management, display calibration and GPU tuning are **not** silently presented as Linux launch-variable equivalents. Alternatives and configuration outside this generator are documented.

## Development

Python 3.10+ and PySide6/PyQt6:

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[pyside]'
./run.sh
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

[Build AppImage/DEB](docs/BUILD.md) · [Research](docs/RESEARCH.md) · [Epic](docs/EPIC.md) · [Verification](docs/VERIFICATION.md) · [Third-party licenses](THIRD_PARTY.md).

Original code: [BSD-3-Clause](LICENSE). Owner-supplied icon and dark/green visual identity retained. Existing DLSS Studio 1.0.0 release/history remain available.
