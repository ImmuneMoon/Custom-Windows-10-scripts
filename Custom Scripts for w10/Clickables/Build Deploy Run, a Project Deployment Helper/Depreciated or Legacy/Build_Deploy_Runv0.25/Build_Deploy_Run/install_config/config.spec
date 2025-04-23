# config.spec
# Dynamic pathing to the current folder
import os
import glob
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the directory this spec is in
this_dir = Path(".").resolve()

# Define installer config_script
this_dir = Path(__file__).parent.resolve() if '__file__' in globals() else Path(".").resolve()
config_script = str(this_dir / 'install_config' / 'config.py')

# Include all .py files in ' assets/ ' and ' workers/ '
assert (this_dir / "assets").exists(), "Missing: assets/"
assert (this_dir / "workers").exists(), "Missing: workers/"

asset_files = [
    (str(path), "assets") for path in (this_dir / "assets").glob("*")
]
worker_files = [
    (str(path), "workers") for path in (this_dir / "workers").glob("*")
]


a = Analysis(
    [config_script],
    pathex=[str(this_dir)],
    binaries=[],
    datas=[
        (str(this_dir / 'build_and_deploy.py'), '.'),
        (str(this_dir / 'build_and_deploy_venv_locked.bat'), '.'),
        (str(this_dir / 'requirements.txt'), '.'),
        (str(this_dir / 'requirements-docker.txt'), '.'),
        (str(this_dir / 'install_config' / 'config.py'), 'install_config')
    ] + worker_files + asset_files,
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
