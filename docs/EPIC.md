# Official Epic Games Launcher for Linux

[Español](es/EPIC.md) · [Home](../README.md) · Inspected 2026-11-03

## Verified observations

- Epic's [official page](https://launcher.epicgames.com/) offers a native Linux **Preview**, with Ubuntu 22.04+, Fedora 43+ and Debian 12+ listed. Windows-only games may still need a compatibility layer. This does not imply that every game or anti-cheat is compatible.
- The current [release notes](https://launcher.epicgames.com/release-notes) list **0.109.0**, November 2, 2026.
- The public AppImage was downloaded from the page's official installer endpoint. Its extracted ELF identifies **0.109.0+ge564459**; SHA-256 `b84b4ea982ee7b5017e465dff0a3234ac3e5b23979902323bd96074a2ae3a7cd`. It is a native Rust/Tauri application, not assumed to be Electron or the Wine Windows launcher.
- Offline symbol/disassembly inspection located `PerGameSettings`' field visitor at `0x29cfde0`–`0x29cfe85`. It compares four fields: `autoUpdate`, `priorityDownload`, `additionalCommandsEnabled`, `additionalCommands`. No per-game environment-variable field was established in that inspected schema.
- The binary includes separate Proton acquisition/wrapping paths and child-environment scrubbing. Presence of a Proton runtime is **not** proof it honors Steam's current configuration variables or forwards every inherited variable.
- Ghidra/REA accepted artifact identity, but native function search timed out before analysis results were available. The 32 MiB standalone layout tool could not accept this 197 MiB ELF. The field observations above are from ordinary offline `nm`/`objdump`/byte-range inspection, **not** a successful REA decompilation. Split DWARF files were absent, so GDB type recovery did not establish additional fields. The analysis session was closed.

## Implemented output contract

Steam emits environment assignments, wrappers, exactly one `%command%`, then game arguments. Epic Preview has **no assumed equivalent Steam parser**:

```text
env VARIABLE=value '/absolute/path/to/EpicGamesLauncher.AppImage' 'com.epicgames.launcher://apps/…'
```

The URI is optional and must be copied from an actual official game shortcut/link; the application does not invent identifiers, authentication tokens or entitlements. The executable path and URI are quoted independently. Without a URI, open the game from the launcher library.

**Fully exit the launcher first**: starting a second instance can hand off to an already-running process with the old environment. Settings apply to all games started by that launcher session, and to the launcher itself where relevant. To isolate another configuration, fully close and start a new session. This is not per-game profile storage.

Game arguments such as `-dx12` are emitted separately, with a separate copy button. Enable/paste them in that game's additional-command setting. Environment assignments and `%command%` do not belong there. Steam wrappers/Gamescope are rejected for this route rather than wrapped around the launcher.

## Remaining unknowns

No Epic login, account/private game configuration, authenticated game launch or actual child-game environment was accessed. **The generated startup environment is verified by parser/UI tests, not by a real Epic game.** Compatibility/runtime propagation remains experimental. No per-game variable editor or undocumented config-file write is implemented. Future launcher versions may change the schema and must be reviewed independently.

DXVK-NVAPI and `PROTON_ENABLE_NGX_UPDATER` require corresponding runtime implementations. The generic Unix environment-startup route does not guarantee those implementations exist in Epic. NVIDIA driver variables likewise require the game's process to retain/load the corresponding driver/layer.
