# DLSS Studio 1.0.0 · 2026-10-30

[Español](es/ESTADO.md)

## Design

- Single dark/green screen for selecting technology/preset and copying a command.
- Automatic, discreet GPU display; no context forms, wiki, profiles or footer text.
- Explicit generation labels in the selector/card; no GENERATED COMMAND badge.
- Owner-supplied PNG icon used by the window and launchers.

## Distribution

- x86_64 AppImage and amd64 DEB with Python 3.10, Qt 6.8.3, libraries and fonts.
- Ubuntu 22.04 build base; glibc 2.35 minimum.
- Bundled catalog/icon; system Python/Qt not needed.
- Library license texts, build scripts, download hashes and self-test included.

## Recorded verification

37 logic/UI tests passed. AppImage verified on X11 and Wayland. Offline DEB installation and both formats executed in Ubuntu Base without Python/Qt. Shared-library audit found no missing dependencies; maximum glibc requirement 2.35.

Logic/UI checks cover commands, presets, generations, compatibility, existing parameters, clipboard, internal persistence and isolation of bundled libraries when querying the system's `nvidia-smi`. `--self-test` checks resources and select/copy interactions using simulated hardware; normal screenshots use actual detection.

## Limits

No in-game testing. No Steam changes, DLL replacement or driver installation. Universal distribution, ARM and musl compatibility are not claimed; see [BUILD.md](BUILD.md).
