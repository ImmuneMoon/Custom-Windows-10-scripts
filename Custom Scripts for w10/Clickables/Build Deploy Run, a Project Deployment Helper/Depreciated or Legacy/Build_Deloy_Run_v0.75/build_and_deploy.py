from pathlib import Path
import sys
import json
import subprocess
import os
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, attr): return ''
    Fore = Style = Dummy()
    def init(*args, **kwargs): pass


# === Init CLI colors ===
init(autoreset=True)
print(Fore.CYAN + ">>> RUNNING build_and_deploy.py")

# === Load config ===
config_path = Path(__file__).parent / "user_config.json"
if not config_path.exists():
    print(Fore.RED + "[X] user_config.json missing. Run the configurator.")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

# === Import helpers ===
from workers.freeze import freeze_requirements
from workers.docker_helpers import (
    patch_dockerfile,
    ensure_dockerignore,
    ensure_docker_running,
    ensure_context_is_default,
    build_docker_image,
    run_docker_container,
)
from workers.display_forwarding import launch_vcxsrv, minimize_x_windows
from pyinstaller_runner import run_pyinstaller

# === Setup project details ===
project_root = Path(config.get("project_dir", ".")).resolve()
entrypoint = config.get("entrypoint", "main.py")
spec_path = config.get("spec_file", None)
spec_file = Path(spec_path) if spec_path else None
docker_image = project_root.name.lower().replace(" ", "-")

# === Smoke test BEFORE any heavy lifting ===
print(Fore.YELLOW + "[*] Running smoke test...")
smoke_test = Path(__file__).parent / "workers" / "smoke_test.bat"

if not smoke_test.is_file():
    print(Fore.RED + f"[!] Missing smoke test: {smoke_test}")
    sys.exit(1)

try:
    subprocess.run([str(smoke_test)], check=True)
except subprocess.CalledProcessError as e:
    print(Fore.RED + f"[X] Smoke test failed with exit code {e.returncode}")
    sys.exit(e.returncode)

# === Run PyInstaller ===
if spec_file:
    print(Fore.YELLOW + "[*] Building EXE via PyInstaller...")
    if not run_pyinstaller(spec_file):
        sys.exit(1)
if not spec_file:
    spec_file = Path(__file__).parent / "Super_Power_Options.spec"

deploy_script_path = os.path.join(project_root , "build_and_deploy.py")
# === Start X Server and prep windows ===
vcxsrv_path = config.get("vcxsrv_path")
if vcxsrv_path:
    launch_vcxsrv(Path(vcxsrv_path))
minimize_x_windows(project_root)

# === Freeze + Docker Build Sequence ===
freeze_requirements(project_root)
patch_dockerfile(project_root, entrypoint)
ensure_dockerignore(project_root)
ensure_docker_running()
ensure_context_is_default()
build_docker_image(docker_image)
run_docker_container(docker_image)
minimize_x_windows(project_root)
