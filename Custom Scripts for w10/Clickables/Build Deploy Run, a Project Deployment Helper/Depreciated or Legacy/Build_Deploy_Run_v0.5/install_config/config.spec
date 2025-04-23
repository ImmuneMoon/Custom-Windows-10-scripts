# config.spec
# Dynamic pathing to the current folder
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the directory this spec is in
this_dir = Path(".").resolve()

# Define your main script
main_script = str(this_dir / "config.py")

a = Analysis(
    [main_script],
    pathex=[str(this_dir)],
    binaries=[],
    datas = [
    ('build_and_deploy.py', '.'),
    ('build_and_deploy_venv_locked.bat', '.'),
    ('minimize_xwindows.ps1', '.'),
    ('assets/icon.ico', 'assets'),
    ('assets/icon.png', 'assets'),
    ('requirements.txt', '.'), 
    ('requirements-docker.txt', '.'),
    ('requirements-bootstrap.txt', '.')
    ],
    hiddenimports=[],
    hookspath=[],
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
    name="Build_Deploy_Run",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=str(this_dir / "assets" / "icon.ico") if (this_dir / "assets" / "icon.ico").exists() else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="Build_Deploy_Run",
)
