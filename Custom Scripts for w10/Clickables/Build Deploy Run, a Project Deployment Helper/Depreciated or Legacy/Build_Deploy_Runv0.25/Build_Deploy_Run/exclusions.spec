# Write the cleaned, flexible spec file as project_template.spec
project_template_spec_path = os.path.join(project_path, "project_template.spec")

with open(project_template_spec_path, "w", encoding="utf-8") as f:
    f.write("""\
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# Dynamically resolve project root
spec_dir = Path(__file__).resolve().parent
project_root = spec_dir.parent

# Recursively include all files EXCEPT Build_Deploy_Run/
datas = [
    (str(path), str(path.parent.relative_to(project_root)))
    for path in project_root.rglob("*")
    if "Build_Deploy_Run" not in str(path)
       and not path.name.endswith(".pyc")
       and not path.name.startswith(".")
]

a = Analysis(
    [str(project_root / "main.py")],  # Fallback; will be overwritten by config at runtime
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["Build_Deploy_Run"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="YourApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon="assets/icon.ico",
)
""")

project_template_spec_path
