import subprocess
from pathlib import Path
import json
import os
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, attr): return ''
    Fore = Style = Dummy()
    def init(*args, **kwargs): pass


# Root project directory
project_path = "/mnt/data/Build_Deploy_Run/Build_Deploy_Run"
runner_path = os.path.join(project_path, "workers", "pyinstaller_runner.py")
runner_path

def run_pyinstaller(spec_file: Path = None, project_root: Path = None):
    """Run PyInstaller with a dynamically generated or provided spec file."""

    # Load config
    config_path = Path(__file__).resolve().parents[1] / "user_config.json"
    if not config_path.exists():
        print(Fore.RED + "[X] user_config.json missing. Cannot proceed with PyInstaller.")
        return False

    with open(config_path) as f:
        config = json.load(f)

    # Resolve key paths from config
    project_root = Path(config.get("project_dir", ".")).resolve()
    entrypoint = config.get("entrypoint", "main.py")
    entrypoint_path = project_root / entrypoint
    app_name = project_root.name.replace(" ", "_")
    icon_path = project_root / "assets" / "icon.ico"
    icon_line = f"    icon=r'{icon_path}'," if icon_path.exists() else ""

    if not spec_file:
        spec_file = project_root / "Build_Deploy_Run.spec"

        # Collect data files to include (excluding Build_Deploy_Run and other trash)
        datas_entries = []
        for path in project_root.rglob("*"):
            if "Build_Deploy_Run" in str(path):
                continue
            if path.name.endswith(".pyc") or path.name.startswith("."):
                continue
            rel_path = path.parent.relative_to(project_root)
            datas_entries.append(f"    (r'{str(path)}', r'{str(rel_path)}'),")

        datas_block = "\\n".join(datas_entries)

        # Generate the .spec file content
        spec_content = f'''
            # -*- mode: python ; coding: utf-8 -*-
            from pathlib import Path

            block_cipher = None
            project_root = Path(r"{project_root}")

            datas = [
            {datas_block}
            ]

            a = Analysis(
                [r'{entrypoint_path}'],
                pathex=[r'{project_root}'],
                binaries=[],
                datas=datas,
                hiddenimports=[],
                hookspath=[],
                runtime_hooks=[],
                excludes=['Build_Deploy_Run'],
                noarchive=False,
            )

            pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

            exe = EXE(
                pyz,
                a.scripts,
                a.binaries,
                a.datas,
                [],
                name='{app_name}',
                debug=False,
                bootloader_ignore_signals=False,
                strip=False,
                upx=True,
                upx_exclude=[],
                runtime_tmpdir=None,
                console=True,
            {icon_line}
            )
            '''

        # Write the actual spec file to disk
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(spec_content)
        
    print(Fore.YELLOW + f"[*] Building .exe with PyInstaller using {spec_file.name}...")
    try:
        subprocess.run(["pyinstaller", str(spec_file)], check=True)
        print(Fore.GREEN + "[✓] Executable build complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[X] PyInstaller failed: {e}")
        return False

runner_path