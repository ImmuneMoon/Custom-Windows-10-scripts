import subprocess
import sys, os
import time
from pathlib import Path
import json
from colorama import Fore, Style, init
init(autoreset=True)

print("RUNNING build_and_deploy.py")

config_path = Path(__file__).parent / "Build_Deploy_Run" / "user_config.json"
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
    VCXSRV_PATH = Path(config.get("vcxsrv_path", "C:/Program Files/VcXsrv/vcxsrv.exe"))
    DOCKER_DESKTOP_PATH = Path(config.get("docker_path", "C:/Program Files/Docker/Docker Desktop.exe"))
    PROJECT_DIR = Path(config.get("project_dir", "."))
else:
    print("[X] user_config.json missing. Run configurator.")
    sys.exit(1)


# === CONFIGURATION ===
project_root = Path(__file__).parent.resolve()

# Look for .spec file used by PyInstaller
spec_file = next(project_root.glob("*.spec"), None)

# Dependency outputs
requirements_txt = project_root / "requirements.txt"
requirements_docker = project_root / "requirements-docker.txt"


# === FREEZE REQUIREMENTS ===
def freeze_requirements():
    print("[*] Freezing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Full requirements for local use
    with open(requirements_txt, "w") as f:
        subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=f)

    # Filtered requirements for Docker
    with open(requirements_txt, "r") as f:
        lines = f.readlines()
    with open(requirements_docker, "w") as f:
        f.writelines([line for line in lines if not line.lower().startswith("pywin32")])

    print("[✓] requirements.txt and requirements-docker.txt created.")

# === ENSURE DOCKER IS RUNNING OR LAUNCH IT ===
def ensure_docker_running():
    print("[*] Checking Docker availability...")
    docker_location = Path("C:/Program Files/Docker/Docker/Docker Desktop.exe")
    try:
        result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception()
        print(Fore.GREEN + "[✓] Docker is running.")
    except:
        print(Fore.YELLOW + "[!] Docker not responding. Launching Docker Desktop...")
        subprocess.run(["start", "docker"], shell=True)
        print(Fore.YELLOW + "[...] Waiting for Docker to become responsive...")
        for i in range(10):
            time.sleep(5)
            result = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{result}")
            if result.returncode == 0:
                print(Fore.GREEN + f"[✓] Docker became responsive after {5*(i+1)}s.")
                break
        else:
            print(Fore.RED + "[X] Docker still unreachable after waiting. Exiting.")
            sys.exit(1)

# === SET DOCKER CONTEXT TO DEFAULT IF NOT SET ===
def ensure_context_is_default():
    print(Fore.YELLOW + "[*] Checking Docker context...")
    result = subprocess.run(["docker", "context", "use", "default"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(Fore.RED + "[X] Failed to set Docker context to 'default'.")
        sys.exit(1)
    print(Fore.GREEN + "[✓] Docker context set to default.")

def run_vcxsrv():
    if VCXSRV_PATH.exists():
        print(Fore.YELLOW + "[*] Launching VcXsrv...")
        subprocess.Popen([
            str(VCXSRV_PATH), ":0", "-multiwindow", "-clipboard", "-wgl", "-ac"
        ])
        time.sleep(3)
    else:
        print(Fore.RED + f"[X] VcXsrv not found at {VCXSRV_PATH}")



# === COMPILE PYTHON TO EXE USING SPEC FILE ===
def run_pyinstaller():
    if not spec_file:
        print(Fore.RED + "[X] No .spec file found for PyInstaller.")
        sys.exit(1)
    print(Fore.YELLOW + f"[*] Building .exe with PyInstaller using {spec_file.name}...")
    subprocess.run(["pyinstaller", spec_file.name], check=True)
    print(Fore.GREEN + "[✓] Executable build complete.")

# === BUILD DOCKER IMAGE FROM LOCAL DIRECTORY ===
def build_docker_image():
    print(Fore.YELLOW + f"[*] Building Docker image '{docker_image}'...")
    subprocess.run(["docker", "build", "-t", docker_image, "."], check=True)
    print(Fore.GREEN + f"[✓] Docker image '{docker_image}' built.")

# PowerShell XWindows GUI minimizer
minimizer_script = project_root / "Build_Deploy_Run/minimize_xwindows.ps1"
# === RUN MINIMIZER POWERSHELL SCRIPT IF PRESENT ===
def run_minimize_XWindows():
    if minimizer_script.exists():
        print(Fore.YELLOW + "[*] Running minimize_xwindows.ps1...")
        subprocess.run([
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(minimizer_script)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(Fore.GREEN + "[✓] Minimized GUI windows.")
    else:
        print(Fore.RED + "[!] PowerShell minimizer script not found.")

# Normalize docker image name from folder name
docker_image = project_root.name.lower().replace(" ", "-")
# === EXECUTE THE BUILT DOCKER CONTAINER WITH DISPLAY FORWARDING ===
def run_docker_container():
    print(Fore.YELLOW + f"[*] Running Docker container '{docker_image}' with GUI support...")

    display = os.getenv("DISPLAY", "host.docker.internal:0")
    print(Fore.YELLOW + f"Docker display: {display}")

    docker_cmd = [
        "docker", "run", "--rm",
        "-e", f"DISPLAY={display}",
        "-e", "DISABLE_TRAY=1",
        docker_image
    ]

    try:
        subprocess.run(docker_cmd, check=True)
        print(Fore.GREEN + "[✓] Docker container executed.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[X] Docker failed to run: {e}")
        sys.exit(1)


# === MAIN EXECUTION ===
if __name__ == "__main__":
    freeze_requirements()
    run_vcxsrv()
    ensure_docker_running()
    ensure_context_is_default()
    run_pyinstaller()
    build_docker_image()
    run_docker_container()
    run_minimize_XWindows()

