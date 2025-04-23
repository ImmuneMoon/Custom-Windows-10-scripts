# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

try:
    import venv
except ImportError:
    print("ERROR: Cannot import 'venv' module.")
    venv = None

block_cipher = None

# More reliable root resolution
bdr_root = Path(__file__).resolve().parent.parent
assets_dir = bdr_root / "assets"
workers_dir = bdr_root / "workers"
install_config_dir = bdr_root / "install_config"
install_workers_dir = install_config_dir / "install_workers"

# Entry script: thin launcher at top level
entry_script = bdr_root / "launch_gui.py"

def recursive_datas(src_dir, prefix):
    datas = []
    src_dir = Path(src_dir)
    if not src_dir.exists():
        print(f"[WARN] Folder not found: {src_dir}")
        return datas
    for file in src_dir.rglob("*"):
        if file.is_file():
            rel_path = file.relative_to(src_dir)
            target = Path(prefix) / rel_path.parent
            datas.append((str(file), str(target)))
    return datas

# Utility: Collect and append files to be copied later into user's project
# Output goes to Build_Deploy_Run folder post-install via a .bat or installer step
external_deployables = [
    (bdr_root / "workers", "Build_Deploy_Run/workers"),
    (bdr_root / "build_and_deploy_venv_locked.bat", "Build_Deploy_Run"),
    (bdr_root / "deploy_fusion_runner.py", "Build_Deploy_Run"),
    (bdr_root / "requirements.txt", "Build_Deploy_Run")
]

# Bundle all relevant data folders
datas = []
datas += recursive_datas(workers_dir, "workers")
datas += recursive_datas(install_workers_dir, "install_config/install_workers")
datas += recursive_datas(install_config_dir, "install_config")
datas += recursive_datas(assets_dir, "assets")

# Add venv support files
if venv:
    try:
        venv_pkg_path = Path(os.path.dirname(venv.__file__))
        datas += recursive_datas(venv_pkg_path, "venv")
    except Exception as e:
        print(f"Failed to bundle venv package: {e}")

# Add deployable files to root or subfolder for later copying
for file, target in external_deployables:
    if Path(file).exists():
        datas.append((str(file), str(target)))

# Add icon
icon_path = assets_dir / "icon.ico"
icon_file = str(icon_path) if icon_path.is_file() else None
if icon_file:
    datas.append((icon_file, '.'))

# Declare missing platform packages that may be required by pyperclip
additional_hiddenimports = [
    'PyQt5', 'PyQt5.QtWidgets', 'qtpy', 'qtpy.QtWidgets', 'Foundation', 'AppKit'
]

hiddenimports = [
    'queue', 'logging', 'threading', 'shutil', 'tkinter',
    'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    'tkinter.scrolledtext', 'pyperclip',
    'PIL', 'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageTk', 'PIL.PngImagePlugin',
    'install_config.install_workers.installer_steps',
    'install_config.install_workers.venv_utils',
    'install_config.install_workers.deploy_config',
    'install_config.install_workers.install_utils',
    'install_config.install_workers.GUI.main_view',
    'install_config.install_workers.GUI.gui_setup',
    'install_config.install_workers.GUI.gui_state',
    'install_config.install_workers.GUI.gui_utils',
    'install_config.install_workers.GUI.widgets',
    'install_config.install_workers.GUI.queue_handler',
] + additional_hiddenimports

a = Analysis(
    [str(entry_script)],
    pathex=[str(bdr_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    disable_windowed_traceback=False,
    argv_emulation=False,
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
