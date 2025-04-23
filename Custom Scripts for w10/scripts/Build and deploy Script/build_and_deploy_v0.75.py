import subprocess
import os
import shutil
import time
import ctypes
import ctypes.wintypes

# === Configuration Constants ===
spec_file = "Super_Power_Options.spec"       # PyInstaller spec file
exe_name = "Super Power Options.exe"         # Executable name to kill before rebuild
dist_dir = "dist"                            # Output folder for PyInstaller
build_dir = "build"                          # Intermediate folder for PyInstaller
docker_image_name = "super-power-options"    # Docker image tag

# === Win32 Constants and Functions for Minimizing Windows ===
SW_MINIMIZE = 6
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowText = ctypes.windll.user32.GetWindowTextW
ShowWindow = ctypes.windll.user32.ShowWindow

# === Minimize Windows Matching Given Keywords ===
def minimize_windows_by_title(keywords):
    matched = []

    def foreach_window(hwnd, lParam):
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLength(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buffer, length + 1)
        title = buffer.value
        for keyword in keywords:
            if keyword.lower() in title.lower():
                ShowWindow(hwnd, SW_MINIMIZE)
                matched.append(title)
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return matched

# === Wrapper for Minimizer Function ===
def run_fast_minimizer():
    targets = ["Docker", "VcXsrv", "Super Power Options"]
    hits = minimize_windows_by_title(targets)
    if hits:
        print("[✓] Minimized windows:", hits)
    else:
        print("[!] No matching windows to minimize")

# === Check if a Process is Running via Tasklist ===
def is_process_running(name):
    try:
        output = subprocess.check_output(["tasklist"], shell=True).decode()
        return name.lower() in output.lower()
    except Exception:
        return False

# === Start Docker if Not Already Running ===
def ensure_docker_running():
    print("[*] Checking Docker status...")
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("[✓] Docker is running")
    except subprocess.CalledProcessError:
        print("[!] Docker not running. Starting Docker Desktop...")
        subprocess.Popen(["start", "docker"], shell=True)
        time.sleep(10)

# === Start X Server if Not Already Running ===
def ensure_xlaunch_running(wait_for_window=True, timeout=30):
    print("[*] Checking for X server...")

    known_servers = {
        "VcXsrv": r"C:\Program Files\VcXsrv\vcxsrv.exe",
        "Xming": r"C:\Program Files (x86)\Xming\Xming.exe"
    }

    for proc in ["vcxsrv.exe", "xming.exe"]:
        if is_process_running(proc):
            print(f"[✓] {proc} already running")
            break
    else:
        custom_x_path = os.environ.get("XSERVER_PATH")
        launched = False

        if custom_x_path and os.path.exists(custom_x_path):
            subprocess.Popen([custom_x_path])
            print(f"[✓] X server launched from env var: {custom_x_path}")
            launched = True
        else:
            for name, path in known_servers.items():
                if os.path.exists(path):
                    subprocess.Popen([path])
                    print(f"[✓] {name} launched from {path}")
                    launched = True
                    break

        if not launched:
            print("[X] No known X server found. Install VcXsrv or Xming.")
            return

    if wait_for_window:
        print("[*] Waiting for X server window to appear...")
        keywords = ["VcXsrv", "Xming"]
        start_time = time.time()

        while time.time() - start_time < timeout:
            matches = minimize_windows_by_title(keywords)  # Checks if it's visible
            if matches:
                print("[✓] X server window found")
                return
            time.sleep(1)

        print("[!] Timed out waiting for X server window")


# === Remove Old Build Folders ===
def clean_old_builds():
    print("[*] Cleaning old builds...")
    for path in [dist_dir, build_dir]:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[✓] Removed {path}")

# === Freeze Python Environment to requirements.txt ===
def freeze_requirements():
    print("[*] Freezing environment to requirements.txt...")
    with open("requirements.txt", "w") as f:
        subprocess.run(["pip", "freeze"], stdout=f)
    print("[✓] Environment frozen")

# === Build Executable with PyInstaller ===
def run_pyinstaller():
    print("[*] Running PyInstaller...")
    subprocess.run(["pyinstaller", spec_file], check=True)
    print("[✓] PyInstaller build complete")

# === Build Docker Image from Current Directory ===
def build_docker_image():
    print(f"[*] Building Docker image '{docker_image_name}'...")
    try:
        subprocess.run(["docker", "build", "-t", docker_image_name, "."], check=True)
        print(f"[✓] Docker image '{docker_image_name}' built")
    except subprocess.CalledProcessError:
        print("[X] Docker build failed")

# === Master Execution Chain ===
if __name__ == "__main__":
    ensure_xlaunch_running()       # Start and wait for X server
    ensure_docker_running()        # THEN start Docker
    run_fast_minimizer()           # Minimize windows
    clean_old_builds()
    freeze_requirements()
    run_pyinstaller()
    build_docker_image()
    run_fast_minimizer()
