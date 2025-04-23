from pathlib import Path
import sys
import json
from colorama import Fore, init
from display_forwarding import launch_vcxsrv, minimize_x_windows
from pyinstaller_runner import run_pyinstaller



init(autoreset=True)

from freeze import freeze_requirements
from pyinstaller_runner import run_pyinstaller
from docker_helpers import (
    ensure_dockerfile_clean,
    ensure_dockerignore_exists,
    ensure_docker_running,
    ensure_context_is_default,
    build_docker_image,
    run_docker_container,
)

print(Fore.CYAN + ">>> RUNNING build_and_deploy.py")

# === Load config ===
config_path = Path(__file__).parent / "Build_Deploy_Run" / "user_config.json"
if not config_path.exists():
    print(Fore.RED + "[X] user_config.json missing. Run the configurator.")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

project_root = Path(config.get("project_dir", ".")).resolve()
entrypoint = config.get("entrypoint", "main.py")
spec_path = config.get("spec_file", None)
spec_file = Path(spec_path) if spec_path else None

# === run pyinstaller if spec file exists
success = run_pyinstaller(spec_file)
if not success:
    sys.exit(1)

# Run VcXsrv
launch_vcxsrv(Path(config["vcxsrv_path"]))
minimize_x_windows(project_root)



# Later on, after Docker launches maybe
minimize_x_windows(project_root / "Build_Deploy_Run/minimize_xwindows.ps1")
# === Docker image name ===
docker_image = project_root.name.lower().replace(" ", "-")

# === Main deployment sequence ===
freeze_requirements(project_root)
ensure_dockerfile_clean(project_root, entrypoint)
ensure_dockerignore_exists(project_root)
launch_vcxsrv(config)
ensure_docker_running()
ensure_context_is_default()
run_pyinstaller(spec_file, project_root)
build_docker_image(docker_image)
run_docker_container(docker_image)
minimize_x_windows(project_root)
