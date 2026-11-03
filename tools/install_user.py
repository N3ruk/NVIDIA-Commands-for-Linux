#!/usr/bin/env python3
"""Install only a per-user desktop entry; no system modifications or elevation."""
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parent.parent
entry_dir = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "applications"
entry_dir.mkdir(parents=True, exist_ok=True)
target = entry_dir / "nvidia-commands-for-linux.desktop"
if target.exists() and "X-NVIDIA-Commands-for-Linux-Managed=true" not in target.read_text():
    raise SystemExit("Ya existe un acceso nvidia-commands-for-linux.desktop no gestionado por este proyecto; no se sobrescribe.")
root.joinpath("run.sh").chmod(0o755)
escaped_root = str(root).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
text = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=NVIDIA Commands for Linux
GenericName=Configurador DLSS para Linux
Comment=DLSS, Smooth Motion y comandos gráficos para Steam y Epic
Exec="{escaped_root}/run.sh"
Icon={root}/nvidia_commands/assets/nvidia-commands-for-linux.png
Terminal=false
Categories=Game;Utility;
Keywords=DLSS;NVIDIA;Proton;Steam;Epic;Ray Reconstruction;Frame Generation;
StartupNotify=true
StartupWMClass=nvidia-commands-for-linux
X-NVIDIA-Commands-for-Linux-Managed=true
"""
target.write_text(text, encoding="utf-8")
target.chmod(0o644)
try:
    result = subprocess.run(["desktop-file-validate", str(target)], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stdout + result.stderr)
except FileNotFoundError:
    print("desktop-file-validate no disponible; acceso creado sin esa validación.")
try:
    subprocess.run(["update-desktop-database", str(entry_dir)], check=True, capture_output=True)
except (FileNotFoundError, subprocess.SubprocessError):
    print("Índice de aplicaciones no actualizado; el archivo .desktop sí está creado.")
print("Acceso instalado:", target)
