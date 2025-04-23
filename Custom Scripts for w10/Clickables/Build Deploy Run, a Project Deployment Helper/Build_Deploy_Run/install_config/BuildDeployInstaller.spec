# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import time
from pathlib import Path

block_cipher = None

print(">>> LAUNCHED INSTALLER SPEC")

# === Directory structure ===
this_dir = Path(os.path.abspath(".")).resolve()
assets_dir = this_dir / "assets"
install_config = this_dir / "install_config"
install_workers = install_config / "install_workers"

# Ensure install_workers is importable during build
sys.path.insert(0, str(install_workers))

# === Utility: Collect files recursively ===
def recursive_datas(src, target):
    return [
        (str(p), str(Path(target) / p.relative_to(src).parent))
        for p in src.rglob("*") if p.is_file()
    ]

worker_files = recursive_datas(install_workers, "install_workers")

# === Optional icon ===
icon_path = assets_dir / "icon.ico"
icon_file = str(icon_path) if icon_path.exists() else None

# === Batch deploy script ===
deploy_script = this_dir / "Build_Deploy_Run" / "build_and_deploy_venv_locked.bat"
deploy_script_file = [(str(deploy_script), ".")] if deploy_script.exists() else []

# === Wait for files if needed (sync hook)
try:
    time.sleep(1)
except:
    pass

# === Analysis ===
a = Analysis(
    [str(install_config / "config.py")],
    pathex=[
        str(this_dir),
        str(install_config),
        str(install_workers),
    ],
    binaries=[],
    datas=[
        *worker_files,
        *([(str(icon_path), "assets")] if icon_path.exists() else []),
        *([(str(assets_dir / "icon.png"), "assets")] if (assets_dir / "icon.png").exists() else []),
        *deploy_script_file,
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BuildDeployInstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=icon_file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BuildDeployInstaller'
)
