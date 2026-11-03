# Release 2.0.0 verification

[Home](../README.md) · [Español](../README_ES.md) · 2026-11-03

## Completed locally

| Check | Observed result |
| --- | --- |
| Python logic/UI regression suite | **85 tests passed** on host Python 3.14/PyQt6 and Ubuntu 22.04 builder Python 3.10/PySide6 6.8.3 |
| Hardware detection | Real NVIDIA GeForce RTX 2060, driver 595.99.02; also verified from frozen AppImage screenshot |
| Other GPU families | Unit/UI fixtures, including RTX 5070/RTX 40, driver versions and layer presence; **simulated, not physical hardware** |
| AppImage, normal execution | `--self-test`, `--version` and real-detection screenshot passed on the host; no host installation |
| Host graphical backends | Packaged self-test passed with `QT_QPA_PLATFORM=xcb` and `wayland`; test processes exited (a transient executor cleanup warning was checked against the process table) |
| GitHub CI | [Run 41613508866](https://github.com/N3ruk/NVIDIA-Commands-for-Linux/actions/runs/41613508866): build and independent clean-base install/purge jobs both passed for code commit `680e850381275040c59417ffce793c2552e3e815` |
| AppImage without FUSE | Extract-and-run self-test passed in separate clean Ubuntu Base 22.04.5 |
| DEB | Installed, self-tested, version-checked and purged **inside an isolated Ubuntu Base**, not on the host |
| Base independence | No `/usr/bin/python3` or system Qt6 in the verification base before installing/running; host directories not mounted; network namespace unshared |
| Package hashes | Both SHA256SUMS entries verified in the clean base |
| ABI audit | **241 ELF files**, maximum required GLIBC symbol version **2.35** |
| DEB cleanup | `/opt/nvidia-commands-for-linux`, binary and desktop entry absent after purge |
| Resources / clipboard | Bundled icon/catalog, preset selection, Steam/Epic composition, conflict rejection and clipboard passed packaged self-test |
| UI review | Dark/green theme retained; real GPU screenshot and Linux-options view inspected; incompatible controls hidden/blocked and resettable |
| Source completeness | Missing original `core.py` recovered by reimplementation against existing regression contracts; broad `core.*` ignore fixed; new core is tracked under `nvidia_commands/core.py` |

The rootless build initially failed because the fresh base lacked a D-Bus machine ID. The build helper now initializes an ID only in its generated base. The successful isolated portability run emitted a non-fatal locale fallback warning; the helper now explicitly sets `C.UTF-8`. No change to the host's machine ID, packages, drivers or launchers was made.

## What the tests establish

- Existing DLSS SR/RR/FG/MFG behavior and presets; reserved preset rejection and independent model/mode/scale semantics.
- Actual dynamic-mode setting and generated-frame counts; custom scale constrained to the documented 33–100% interval.
- GPU/driver/layer/API gates, including Smooth Motion R580 per-generation baselines and R595 sharpening route.
- Smooth Motion/FG conflicts from selected and known inherited named/numeric settings; automatic Smooth Motion/Gamescope combination blocked.
- DXVK settings merging without discarding unrelated settings; VSync/anisotropy/LOD controls rejected outside their API scope.
- Correct POSIX assignment grammar, verified by an isolated fixed-fixture `/bin/sh` environment check. The application itself never executes launch text.
- Safe separation of Epic's terminal command and additional game arguments; no Steam placeholder/wrapper sent as an Epic game argument.
- Recovery after GPU/API changes, including an explicitly disabled anisotropy value, without leaving hidden incompatible selections impossible to reset.

## Not established

- No physical RTX 5070/40 testing, game rendering, model/DLL loading, visual quality, frame-generation pacing or FPS gain was observed.
- No authenticated Epic game was launched. **Epic environment propagation remains experimental/session-wide**, not verified per-game profiles.
- Optional Gamescope/MangoHud were not installed or runtime-certified; commands and published requirements were checked.
- The native/Proton game runtime, anti-cheat, compositor HDR/VRR support and game-integrated features remain external requirements.
- The host X11/Wayland self-tests are not a claim that every compositor or Linux distribution was tested. glibc 2.35+/x86_64 is an ABI target, not universal distro support.

Reproduce with `python3 tools/build_rootless.py`, then `python3 tools/verify_portable.py` (requires a fresh generated verification-root path; the helper refuses to overwrite an existing one). Detailed local evidence stays in ignored `.cache/` and `build/portable/`; no Epic binary, account data or build root is published.
