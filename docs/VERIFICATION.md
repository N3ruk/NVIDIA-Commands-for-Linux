# Release 2.0.0 verification

[Home](../README.md) · [Español](../README_ES.md) · 2026-11-03

## Verification scope

The checks below cover the current parallel Steam/Epic output interface, Reset, variable/value explanations and packaged resources. The release contains an offline command generator, not a game runtime.

| Check | Observed result |
| --- | --- |
| Host Python 3.14 / PyQt6 suite | **96 tests passed** |
| Ubuntu 22.04 Python 3.10 / PySide6 builder suite | **96 tests passed** |
| Packaged self-test | Presets, independent clipboards, Reset, explanations, resources and conflicts passed |
| AppImage normal execution / X11 / Wayland | Version and offscreen / `xcb` / `wayland` self-tests all returned 0 |
| Independent Ubuntu Base 22.04.5 without system Python/Qt | AppImage extract-and-run passed; no host directories, network unshared |
| DEB install / self-test / purge in isolated base | Passed; application directory, executable and desktop entry absent after purge |
| ABI audit | **241 ELF files**, maximum required GLIBC symbol version **2.35** |
| Package hashes | Both SHA256SUMS entries passed in the clean verification base |
| Installed host package | **2.0.0 installed**, packaged self-test and `dpkg -V` integrity check passed |
| GitHub CI | [Build and clean-base workflow](https://github.com/N3ruk/NVIDIA-Commands-for-Linux/actions/workflows/build-linux.yml) |

Real hardware detection was checked on **NVIDIA GeForce RTX 2060 / driver 595.99.02**. RTX 5070/RTX 40 and other GPU families in tests use simulated fixtures, not physical hardware. Real-GPU screenshots show parallel command outputs and the dark/green interface.

## What is checked

- DLSS SR/RR/FG/MFG presets, independent model/mode/custom 33–100% scale, dynamic MFG and generated-frame counts.
- GPU/driver/layer/API gates, Smooth Motion R580 per-generation baselines, R595 sharpening and FG conflict handling.
- Safe merging of DXVK/DRS settings and preserved launch parameters; conflicting/complex inputs rejected without execution.
- Valid POSIX environment-assignment grammar, exactly one Steam placeholder and extraction of game-only Epic arguments.
- Independent clipboard outputs, empty Reset even after conflicts, preserved GPU detection and value-by-value explanations, including unknown imported values.
- Packaged icon/catalog/licenses and Python/Qt independence from the clean verification base.

## Not established

- No physical RTX 5070/40 testing, game rendering, loaded model/DLL, visual quality, frame pacing or FPS gain.
- No authenticated Epic game launch. **Epic's game-argument field cannot apply NVIDIA environment variables.** Manual whole-launcher environments remain experimental/session-wide, with propagation unverified.
- No runtime certification of external launchers, Gamescope, MangoHud, PRIME or HDR; they are not controls in this interface.
- Native/Proton runtimes, anti-cheat, compositor/display support and game-integrated features remain external requirements.
- glibc 2.35+/x86_64 is an ABI target, not a claim to support every Linux distribution or compositor.

Reproduce with `python3 tools/build_rootless.py`, then `python3 tools/verify_portable.py`. The latter refuses to overwrite an existing generated verification root; archive that root before repeating. Detailed logs and private build evidence remain in ignored `.cache/` and `build/portable/`; no Epic binary or account data is published.
