#!/usr/bin/env python3
"""Install only a per-user desktop entry; no system modifications or elevation."""
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parent.parent
entry_dir = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "applications"
entry_dir.mkdir(parents=True, exist_ok=True)
target = entry_dir / "dlss-studio.desktop"
if target.exists() and "X-DLSS-Studio-Managed=true" not in target.read_text():
    raise SystemExit("Ya existe un acceso dlss-studio.desktop no gestionado por este proyecto; no se sobrescribe.")
root.joinpath("run.sh").chmod(0o755)
escaped_root = str(root).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
text = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=DLSS Studio
GenericName=Configurador DLSS para Linux
Comment=Presets, compatibilidad y parámetros de Steam para NVIDIA DLSS
Exec="{escaped_root}/run.sh"
Icon={root}/dlss_studio/assets/dlss-studio.png
Terminal=false
Categories=Game;Utility;
Keywords=DLSS;NVIDIA;Proton;Steam;Ray Reconstruction;Frame Generation;
StartupNotify=true
StartupWMClass=dlss-studio
X-DLSS-Studio-Managed=true
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
