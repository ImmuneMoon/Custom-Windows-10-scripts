import subprocess
import os
import shutil

# === CONFIG SETTINGS ===
spec_file = "Super_Power_Options.spec"          # Your PyInstaller .spec file
exe_name = "Super Power Options.exe"            # Name of the EXE to terminate if running
dist_dir = "dist"                               # Where PyInstaller drops the final build
build_dir = "build"                             # PyInstaller's temp build files
docker_image_name = "super-power-options"       # Docker image tag for this app

# === CLEAN PREVIOUS BUILD FILES ===
def clean_old_builds():
    print("[*] Cleaning old builds...")
    for path in [dist_dir, build_dir]:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[✓] Removed {path}")

# === KILL RUNNING EXE IF ACTIVE ===
def kill_running_exe():
    print(f"[*] Killing any running '{exe_name}' processes...")
    try:
        # Force-terminate the EXE using Windows taskkill
        subprocess.run(f'taskkill /f /im "{exe_name}"', shell=True, check=True)
        print(f"[✓] Killed {exe_name}")
    except subprocess.CalledProcessError:
        print("[✓] No running instances found")

# === SNAPSHOT ENVIRONMENT DEPENDENCIES ===
def freeze_requirements():
    print("[*] Freezing current environment to requirements.txt...")
    with open("requirements.txt", "w") as f:
        subprocess.run(["pip", "freeze"], stdout=f)
    print("[✓] requirements.txt updated")

# === COMPILE PYTHON TO .EXE ===
def run_pyinstaller():
    print("[*] Running PyInstaller...")
    subprocess.run(["pyinstaller", spec_file], check=True)
    print("[✓] PyInstaller build complete!")

# === PACKAGE TO DOCKER IMAGE ===
def build_docker_image():
    print(f"[*] Building Docker image '{docker_image_name}'...")
    try:
        subprocess.run(["docker", "build", "-t", docker_image_name, "."], check=True)
        print(f"[✓] Docker image '{docker_image_name}' built successfully")
    except subprocess.CalledProcessError:
        print("[X] Docker build failed")

# === EXECUTION ENTRY POINT ===
if __name__ == "__main__":
    clean_old_builds()
    kill_running_exe()
    freeze_requirements()
    run_pyinstaller()
    build_docker_image()
