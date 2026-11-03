# Official Epic Games Launcher for Linux

[Español](es/EPIC.md) · [Home](../README.md) · Inspected 2026-11-03

## Verified observations

- Epic's [official page](https://launcher.epicgames.com/) offers a native Linux **Preview**, with Ubuntu 22.04+, Fedora 43+ and Debian 12+ listed. Windows-only games may still need a compatibility layer. This does not imply that every game or anti-cheat is compatible.
- The current [release notes](https://launcher.epicgames.com/release-notes) list **0.109.0**, November 2, 2026.
- The public AppImage was downloaded from the page's official installer endpoint. Its extracted ELF identifies **0.109.0+ge564459**; SHA-256 `b84b4ea982ee7b5017e465dff0a3234ac3e5b23979902323bd96074a2ae3a7cd`. It is a native Rust/Tauri application, not assumed to be Electron or the Wine Windows launcher.
- Offline symbol/disassembly inspection located `PerGameSettings`' field visitor at `0x29cfde0`–`0x29cfe85`. It compares four fields: `autoUpdate`, `priorityDownload`, `additionalCommandsEnabled`, `additionalCommands`. No per-game environment-variable field was established in that inspected schema.
- The binary includes separate Proton acquisition/wrapping paths and child-environment scrubbing. Presence of a Proton runtime is **not** proof it honors Steam's current configuration variables or forwards every inherited variable.
- Ghidra/REA accepted artifact identity, but native function search timed out before analysis results were available. The 32 MiB standalone layout tool could not accept this 197 MiB ELF. The field observations above are from ordinary offline `nm`/`objdump`/byte-range inspection, **not** a successful REA decompilation. Split DWARF files were absent, so GDB type recovery did not establish additional fields. The analysis session was closed.

## Current interface: game arguments only

**Comando Steam** and **Argumento Epic** appear side by side with independent copy buttons. Steam contains environment assignments, any safely preserved wrappers, exactly one `%command%`, then game arguments. Epic contains **only game arguments** after that placeholder.

For example, enter `%command% -dx12` in **Más opciones**, then copy `-dx12` from **Argumento Epic** to the game's additional-command setting. Only use arguments actually supported by that game. The application never invents arguments from NVIDIA selections.

**NVIDIA variables are not Epic game arguments.** If you only select DLSS, Smooth Motion or sharpening, the Epic box remains empty. Do not paste environment assignments, `%command%` or Steam wrappers into Epic's game-argument field. This interface does not launch Epic or provide per-game environment profiles.

## Experimental manual session environment

A separate Unix terminal technique can set environment variables when starting the whole launcher. It is **not a generated output of this interface**:

```sh
env VARIABLE=value '/absolute/path/to/EpicGamesLauncher.AppImage'
```

Replace the placeholder assignment with actual supported variables and the path with your launcher executable. Do not include `%command%`. Open the game from the launcher library.

**Fully exit the launcher first**: a second instance can hand off to an existing process with its old environment. Variables apply to the launcher and potentially all games in that session, not isolated per-game profiles. Fully close and restart to change the session environment.

No authenticated game has verified this propagation. A correct Unix startup environment does not prove that Epic's runtime retains or implements a variable.

## Remaining unknowns

No Epic login, account/private game configuration, authenticated game launch or actual child-game environment was accessed. **Argument extraction and clipboard behavior are verified by parser/UI tests, not by a real Epic game.** Compatibility/runtime propagation remains experimental. No per-game variable editor or undocumented config-file write is implemented. Future launcher versions may change the schema and must be reviewed independently.

DXVK-NVAPI and `PROTON_ENABLE_NGX_UPDATER` require corresponding runtime implementations. The generic Unix environment-startup route does not guarantee those implementations exist in Epic. NVIDIA driver variables likewise require the game's process to retain/load the corresponding driver/layer.
