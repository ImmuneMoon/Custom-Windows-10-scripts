import subprocess
import os
import shutil
import time
import ctypes
import ctypes.wintypes

# === Configuration Constants ===
spec_file = "Super_Power_Options.spec"
exe_name = "Super Power Options.exe"
dist_dir = "dist"
build_dir = "build"
docker_image_name = "super-power-options"

# === Win32 Constants and Functions ===
SW_MINIMIZE = 6
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowText = ctypes.windll.user32.GetWindowTextW
ShowWindow = ctypes.windll.user32.ShowWindow

# === Minimize Windows Matching Keywords ===
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

def run_fast_minimizer():
    targets = ["Docker", "VcXsrv", "Super Power Options"]
    hits = minimize_windows_by_title(targets)
    if hits:
        print("[✓] Minimized windows:", hits)
    else:
        print("[!] No matching windows to minimize")

def is_process_running(name):
    try:
        output = subprocess.check_output(["tasklist"], shell=True).decode()
        return name.lower() in output.lower()
    except Exception:
        return False

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
        launched = False
        custom_x_path = os.environ.get("XSERVER_PATH")
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
            matches = minimize_windows_by_title(keywords)
            if matches:
                print("[✓] X server window found")
                return
            time.sleep(1)
        print("[!] Timed out waiting for X server window")

def ensure_docker_running(timeout=90):
    print("[*] Checking Docker status...")

    def is_docker_ready():
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False

    if not is_docker_ready():
        print("[!] Docker not responding. Launching Docker Desktop...")
        subprocess.Popen(["start", "docker"], shell=True)

        print(f"[*] Waiting up to {timeout}s for Docker to become available...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if is_docker_ready():
                print("[✓] Docker is now running")
                return
            time.sleep(2)

        print("[X] Timed out waiting for Docker daemon")
    else:
        print("[✓] Docker is already running")

def clean_old_builds():
    print("[*] Cleaning old builds...")
    for path in [dist_dir, build_dir]:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[✓] Removed {path}")

def freeze_requirements():
    print("[*] Freezing environment to requirements.txt...")
    with open("requirements.txt", "w") as f:
        subprocess.run(["pip", "freeze"], stdout=f)
    print("[✓] Environment frozen")

def run_pyinstaller():
    print("[*] Running PyInstaller...")
    subprocess.run(["pyinstaller", spec_file], check=True)
    print("[✓] PyInstaller build complete")

def build_docker_image():
    print(f"[*] Building Docker image '{docker_image_name}'...")
    try:
        subprocess.run(["docker", "build", "-t", docker_image_name, "."], check=True)
        print(f"[✓] Docker image '{docker_image_name}' built")
    except subprocess.CalledProcessError as e:
        print("[X] Docker build failed")
        print(e)

if __name__ == "__main__":
    ensure_xlaunch_running()
    ensure_docker_running()
    run_fast_minimizer()
    clean_old_builds()
    freeze_requirements()
    run_pyinstaller()
    build_docker_image()
    run_fast_minimizer()