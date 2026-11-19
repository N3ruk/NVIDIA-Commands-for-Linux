# Release 2.1.0 verification

[Home](../README.md) · [Español](../README_ES.md) · 2026-11-19

Results apply to the 2.1.0 sources and final DEB/AppImage, not merely to an earlier installed revision. [Machine-readable results and package hashes](release-2.1.0-verification.json) · [Changes from 2.0.0](../CHANGELOG.md).

## Verification scope

| Check | Observed result |
| --- | --- |
| Ubuntu 22.04 / Python 3.10 / PySide6 6.8.3 logic/UI suite | **108 tests passed** |
| Frozen-module identity | Core, UI and explanations match the compiled revised sources; **13 command-scope tests** also pass against the frozen core |
| Payload consistency | DEB payload files match the AppDir used to build the AppImage |
| AppImage with FUSE | Offscreen, X11 (`xcb`) and Wayland self-tests passed |
| Independent Ubuntu Base 22.04.5 without system Python/Qt | AppImage extract-and-run and DEB install/self-test/purge passed; network isolated |
| Upgrade from the published 2.0.0 DEB | Passed inside the clean base |
| Same-version 2.1.0 reinstall | Passed; package integrity checked |
| Installed payload mounted read-only | Self-tests passed in two separate processes |
| Existing profile preservation | Fixture file unchanged through upgrade, reinstall and purge |
| Removal | No application payload, executable or desktop entry remains in the clean base |
| ABI audit | **241 ELF files**, maximum required GLIBC symbol version **2.35** |
| Download integrity | Both package hashes checked in the clean base; hashes recorded in the JSON report |

The [GitHub build workflow](../.github/workflows/build-linux.yml) repeats the suite, builds both formats and checks installation/removal in a separate container without system Python/Qt. Publication is gated on a successful run for the exact main commit. The release notes link that run.

Build warnings concern the optional GTK appearance adapter, which is excluded from the final payload; the application uses Fusion. No GTK dependency is required by the distributed application.

## Boundaries

- Real GPU detection was checked on RTX 2060; RTX 5070/other families in UI fixtures are simulated. No physical RTX 40/50 verification is claimed.
- No game launches or FPS/visual/model-effect measurements were performed for these package checks. The audit records a separately observed SR/K command match, not general game certification.
- No authenticated Epic launch was tested. NVIDIA environment variables are not Epic game arguments; experimental launcher-wide inheritance remains unverified.
- Drivers, game integration, Proton/runtime components and compositor/display setup remain external requirements. glibc 2.35+/x86_64 is an ABI target, not universal Linux support.
- 2.1.0 was not installed on the host as part of publication. Host installation is not needed to reproduce the isolated checks.

Reproduce with `python3 tools/build_rootless.py` and `python3 tools/verify_portable.py`. The verification helper refuses an existing generated root. Public results and screenshots are in this repository; temporary build logs and generated root filesystems are not distribution artifacts.
