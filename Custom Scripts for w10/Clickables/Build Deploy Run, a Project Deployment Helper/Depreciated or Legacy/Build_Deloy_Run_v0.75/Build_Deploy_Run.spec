# -*- mode: python ; coding: utf-8 -*-

# Imports needed for the spec file itself
import os
import sys
from pathlib import Path

block_cipher = None

# --- Configuration ---
# Project root IS the directory containing this spec file
HERE = Path(__file__).resolve().parent
# Define paths relative to the project root (HERE)
ASSETS_DIR = HERE / "assets"
WORKERS_DIR = HERE / "workers"
ENTRY_SCRIPT = HERE / "launch_gui.py" # Correct entry script
DEPLOY_RUNNER_SCRIPT = HERE / "deploy_fusion_runner.py" # File to be copied by installer
BDR_REQUIREMENTS = HERE / "requirements.txt" # File to be copied by installer

# --- Optional Checks (recommended) ---
if not ENTRY_SCRIPT.is_file(): raise FileNotFoundError(f"Entry script not found: {ENTRY_SCRIPT}")
if not ASSETS_DIR.is_dir(): print(f"[WARN] Assets directory not found: {ASSETS_DIR}") # Warn only
if not WORKERS_DIR.is_dir(): raise FileNotFoundError(f"Workers directory not found: {WORKERS_DIR}") # Error if missing
if not DEPLOY_RUNNER_SCRIPT.is_file(): raise FileNotFoundError(f"Deploy runner script not found: {DEPLOY_RUNNER_SCRIPT}")
if not BDR_REQUIREMENTS.is_file(): raise FileNotFoundError(f"BDR requirements file not found: {BDR_REQUIREMENTS}")

# --- PyInstaller Data Files (`datas`) ---
# Bundle necessary non-code files/folders needed AT RUNTIME by the EXE,
# or needed BY THE INSTALLER LOGIC to copy later.
# Format: ('source_path_on_disk', 'destination_path_in_bundle')
datas = []

# 1. Bundle 'assets' (for GUI icons)
if ASSETS_DIR.is_dir():
    datas.append((str(ASSETS_DIR), 'assets'))

# 2. Bundle 'workers' (so installer can copy it)
if WORKERS_DIR.is_dir():
    datas.append((str(WORKERS_DIR), 'workers'))

# 3. Bundle other files (so installer can copy them)
if DEPLOY_RUNNER_SCRIPT.is_file():
    datas.append((str(DEPLOY_RUNNER_SCRIPT), '.')) # Copies to bundle root
if BDR_REQUIREMENTS.is_file():
    datas.append((str(BDR_REQUIREMENTS), '.')) # Copies to bundle root

# --- Icon ---
icon_path = ASSETS_DIR / "icon.ico"
# Use relative path for the icon argument in EXE()
icon_file_arg = str(icon_path.relative_to(HERE)) if icon_path.is_file() else None

# --- Hidden Imports ---
# Modules PyInstaller might miss
additional_hiddenimports = [ # For pyperclip platform specifics
    'PyQt5', 'PyQt5.QtWidgets', 'qtpy', 'qtpy.QtWidgets', 'Foundation', 'AppKit'
]
hiddenimports = [
    'queue', 'logging', 'threading', 'shutil', 'tkinter', 'os', 'traceback',
    'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    'tkinter.scrolledtext', 'pyperclip',
    'PIL', 'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageTk', 'PIL.PngImagePlugin', 'PIL.IcoImagePlugin',
    # List main project modules needed - ensures they are bundled
    'install_config.constants',
    'install_config.install_workers.GUI.main_view',
    'install_config.install_workers.GUI.gui_setup',
    'install_config.install_workers.GUI.gui_state',
    'install_config.install_workers.GUI.gui_utils',
    'install_config.install_workers.GUI.widgets',
    'install_config.install_workers.GUI.callbacks',
    'install_config.install_workers.installer_steps',
    'install_config.install_workers.venv_utils',
    'install_config.install_workers.deploy_config',
    'install_config.install_workers.install_utils',
    'install_config.install_workers.notify',
] + additional_hiddenimports

# --- Analysis ---
a = Analysis(
    [str(ENTRY_SCRIPT)],  # Use the correct GUI launch script
    pathex=[str(HERE)],   # Search path is the project root
    binaries=[],
    datas=datas,          # Use the corrected datas list
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],          # Remove the incorrect excludes
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# --- PYZ (Python Archive) ---
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- EXE ---
exe = EXE(
    pyz,
    a.scripts,
    [],                 # No scripts needed here usually if entry is in Analysis
    exclude_binaries=True,
    name='BuildDeployInstaller', # Use a suitable name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Set to False for final GUI release
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=icon_file_arg # Use relative path variable for icon
)

# --- COLLECT (Bundle into Folder) ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas, # Include data files specified in Analysis.datas
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BuildDeployInstaller' # Name of the output folder in 'dist'
)