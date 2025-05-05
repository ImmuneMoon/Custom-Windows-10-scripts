# ./ BuildDeployInstaller.spec

import sys
import os


from PyInstaller.utils.hooks import collect_data_files

block_cipher = None


datas=[('assets', 'assets')],
 

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Dynamically collect all files inside 'assets' folder
assets_datas = collect_data_files('assets', includes=["*.ico", "*.png"], excludes=[])

a = Analysis(
    ['install_config/install_workers/GUI/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'plyer',
        'plyer.platforms.win.notification',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BuildDeployInstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=get_resource_path('assets/icon.ico')
)
