# Build and verify Linux packages

[Español](es/BUILD.md) · [Home](../README.md)

## Release 2.0.0 packages

- `NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage`: portable, Python and Qt included.
- `nvidia-commands-for-linux_2.0.0_amd64.deb`: self-contained installation under `/opt/nvidia-commands-for-linux`.
- `SHA256SUMS`: package hashes.
- `build-info.json`: builder versions and system requirements.

Targets x86_64/amd64 GNU/Linux with **glibc 2.35+**, including Ubuntu 22.04+, Debian 12+ and Linux Mint 21+. Not native ARM, 32-bit or Alpine/musl. DEB requires a DEB-compatible distribution.

Includes Python, PySide6/Qt, desktop support libraries, fonts and licenses. Installation does not run pip or download components. glibc, kernel, desktop, NVIDIA driver, Steam and Proton remain system/game components. Real GPU detection needs the system driver's `nvidia-smi`.

## From a modern Linux host, without sudo

Requires `bwrap`, `tar`, Python 3 and Internet:

```sh
python3 tools/build_rootless.py
```

Downloads and SHA256-verifies Ubuntu Base 22.04.5 and builds inside a user namespace. UID 0 exists only inside that environment; it has no host privileges. Work stays under `build/portable`, outputs under `dist`.

## On Ubuntu 22.04 or an equivalent container

Install the build packages listed in `PACKAGES` in `tools/build_rootless.py`, then:

```sh
python3 -m venv .venv-build
.venv-build/bin/pip install -r packaging/requirements-build.txt
QT_QPA_PLATFORM=offscreen .venv-build/bin/python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen .venv-build/bin/python tools/build_linux.py
```

The AppImage runtime is SHA256-pinned. Changes to the `continuous` download stop the build until the hash is reviewed and explicitly updated. Major Python/Qt/freezer versions are recorded in `build-info.json`; APT repositories/transitive dependencies may evolve. Builds on different dates are not promised to be byte-identical.

## Checks

```sh
QT_QPA_PLATFORM=offscreen ./dist/NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage --self-test
./dist/NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage --version
(cd dist && sha256sum -c SHA256SUMS)
```

The self-test uses a simulated GPU to check presets and clipboard only; it does not certify real hardware or an in-game model. For real detection and a screenshot:

```sh
./dist/NVIDIA-Commands-for-Linux-2.0.0-x86_64.AppImage --screenshot artifacts/preview.png
```

Without FUSE, add `--appimage-extract-and-run`. Offline DEB testing can use another clean Ubuntu Base with `QT_QPA_PLATFORM=offscreen nvidia-commands-for-linux --self-test`, without installing Python/Qt. X11 and Wayland plugins are included; the GTK appearance adapter is omitted because the application uses its own Fusion style.

## Independent clean-base verification

```sh
python3 tools/verify_portable.py
```

Uses a separate generated Ubuntu Base without Python/Qt, isolated network and no host directories. Installs/purges the DEB only there. The helper refuses an existing verification root; preserve/archive that generated tree before a repeat. See [verification](../docs/VERIFICATION.md) for actual results and remaining unknowns.
