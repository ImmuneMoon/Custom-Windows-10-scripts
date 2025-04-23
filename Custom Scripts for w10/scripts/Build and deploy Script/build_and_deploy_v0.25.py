import subprocess
import os
import shutil
import time

# === Configuration Constants ===
spec_file = "Super_Power_Options.spec"       # PyInstaller specification file
exe_name = "Super Power Options.exe"         # Name of compiled binary to terminate if running
dist_dir = "dist"                            # PyInstaller output directory
build_dir = "build"                          # PyInstaller intermediate build directory
docker_image_name = "super-power-options"    # Tag for the Docker image
vcxsrv_path = r"C:\Program Files\VcXsrv\vcxsrv.exe"  # Default install path for VcXsrv (X11 server)

# === Utility: Check if a Windows process is active ===
def is_process_running(name):
    try:
        output = subprocess.check_output(["tasklist"], shell=True).decode()
        return name.lower() in output.lower()
    except Exception:
        return False

# === Ensure Docker is running; start it if not ===
def ensure_docker_running():
    print("[*] Checking Docker status...")
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("[✓] Docker is running")
    except subprocess.CalledProcessError:
        print("[!] Docker is not running. Attempting to launch Docker Desktop...")
        subprocess.Popen(["start", "docker"], shell=True)
        time.sleep(10)  # Static wait; assumes Docker starts within 10 seconds

# === Ensure VcXsrv is active; start it if not ===
def ensure_xlaunch_running():
    print("[*] Checking for X server...")

    known_servers = {
        "VcXsrv": r"C:\Program Files\VcXsrv\vcxsrv.exe",
        "Xming": r"C:\Program Files (x86)\Xming\Xming.exe"
    }

    # Check if any known X server is running
    for proc in ["vcxsrv.exe", "xming.exe"]:
        if is_process_running(proc):
            print(f"[✓] {proc} is already running")
            return
        
    custom_x_path = os.environ.get("XSERVER_PATH")
    if custom_x_path and os.path.exists(custom_x_path):
        subprocess.Popen([custom_x_path])
        print(f"[✓] X server launched from custom path: {custom_x_path}")
        return

    # Try launching a known server
    for name, path in known_servers.items():
        if os.path.exists(path):
            subprocess.Popen([path])
            print(f"[✓] {name} launched from {path}")
            return

    print("[X] No known X server found or running.")
    print("    ➤ Install VcXsrv or Xming.")
    print("    ➤ Or set XSERVER_PATH env var if using a custom server.")


# === Delete old build and dist directories ===
def clean_old_builds():
    print("[*] Cleaning old builds...")
    for path in [dist_dir, build_dir]:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[✓] Removed {path}")

# === Force-terminate the app if currently running ===
def kill_running_exe():
    print(f"[*] Killing any running '{exe_name}' processes...")
    try:
        subprocess.run(f'taskkill /f /im "{exe_name}"', shell=True, check=True)
        print(f"[✓] Killed {exe_name}")
    except subprocess.CalledProcessError:
        print("[✓] No running instances found")

# === Write current environment packages to requirements.txt ===
def freeze_requirements():
    print("[*] Freezing current environment to requirements.txt...")
    with open("requirements.txt", "w") as f:
        subprocess.run(["pip", "freeze"], stdout=f)
    print("[✓] requirements.txt updated")

# === Run PyInstaller with specified .spec file ===
def run_pyinstaller():
    print("[*] Running PyInstaller...")
    subprocess.run(["pyinstaller", spec_file], check=True)
    print("[✓] PyInstaller build complete")

# === Build a Docker image from current directory ===
def build_docker_image():
    print(f"[*] Building Docker image '{docker_image_name}'...")
    try:
        subprocess.run(["docker", "build", "-t", docker_image_name, "."], check=True)
        print(f"[✓] Docker image '{docker_image_name}' built successfully")
    except subprocess.CalledProcessError:
        print("[X] Docker build failed")

# === Execution entry point ===

def run_powershell_minimizer():
    script_path = os.path.abspath("minimize_xwindows.ps1")
    if not os.path.exists(script_path):
        print(f"[X] PowerShell minimizer script not found at {script_path}")
        return
    print("[*] Executing PowerShell minimizer script...")
    try:
        subprocess.run([
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", script_path
        ], check=True)
        print("[✓] PowerShell minimizer executed")
    except subprocess.CalledProcessError:
        print("[X] PowerShell minimizer failed to execute")

# Call the functions at the end of your script execution
if __name__ == "__main__":
    ensure_docker_running()
    ensure_xlaunch_running()
    clean_old_builds()
    kill_running_exe()
    freeze_requirements()
    run_pyinstaller()
    build_docker_image()
    run_powershell_minimizer()
