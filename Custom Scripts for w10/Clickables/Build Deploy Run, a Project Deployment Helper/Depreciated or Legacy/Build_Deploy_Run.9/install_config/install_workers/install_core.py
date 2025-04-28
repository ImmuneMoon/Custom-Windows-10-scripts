from pathlib import Path
import os, sys, subprocess, json, shutil, time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "install_workers")))
from install_workers.utils import resource_path

def run_installer(vcxsrv_path, docker_path, project_dir, entrypoint,
                  open_project=False, run_xlaunch=False, run_docker=False):
    print("[*] Starting installation...")

    # === Validate Inputs ===
    if not Path(project_dir).exists():
        print(f"[X] Project directory not found: {project_dir}")
        return

    entrypoint_path = Path(project_dir) / entrypoint
    if not entrypoint_path.exists():
        print(f"[X] Entrypoint script not found: {entrypoint_path}")
        return

    # === Install Tools ===
    if vcxsrv_path and Path(vcxsrv_path).exists():
        print("[*] Installing VcXsrv...")
        subprocess.run([vcxsrv_path, "/silent"], shell=True)
    else:
        print("[!] VcXsrv path invalid or not provided.")

    if docker_path and Path(docker_path).exists():
        print("[*] Installing Docker Desktop...")
        subprocess.run([docker_path, "install", "--quiet"], shell=True)
    else:
        print("[!] Docker path invalid or not provided.")

    # === Copy Build_Deploy_Run folder ===
    bdr_src = Path(__file__).parent.parent.resolve()
    bdr_dest = Path(project_dir) / "Build_Deploy_Run"

    print("[*] Copying Build_Deploy_Run folder to project...")
    if bdr_dest.exists():
        shutil.rmtree(bdr_dest)
    shutil.copytree(bdr_src, bdr_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # === Create user_config.json ===
    user_config_path = bdr_dest / "user_config.json"
    config = {
        "vcxsrv_path": str(Path(vcxsrv_path).resolve()) if vcxsrv_path else "",
        "docker_path": str(Path(docker_path).resolve()) if docker_path else "",
        "project_dir": str(Path(project_dir).resolve()),
        "entrypoint": str(Path(entrypoint).name)
    }

    try:
        with open(user_config_path, "w") as f:
            json.dump(config, f, indent=4)
        print("[✓] user_config.json updated.")
    except Exception as e:
        print(f"[X] Failed to write user_config.json: {e}")
        return

    # === Create Virtual Environment ===
    venv_path = bdr_dest / "venv"
    if venv_path.exists():
        confirm = input("[!] Existing virtual environment detected. Delete it? (y/n): ")
        if confirm.lower() == "y":
            shutil.rmtree(venv_path)
            print("[*] Old virtual environment deleted.")
        else:
            print("[*] Skipping virtual environment creation.")
            return
    else:
        print("[*] Creating new virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)])

    # === Wait for python.exe to show up
    python_exe = venv_path / "Scripts" / "python.exe"
    for _ in range(20):
        if python_exe.exists():
            break
        time.sleep(0.5)
    else:
        print(f"[X] Timed out waiting for {python_exe}")
        return

    # === Install requirements
    req_file = bdr_dest / "requirements.txt"
    subprocess.run([str(python_exe), "-m", "ensurepip", "--upgrade"])
    subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(req_file)])

    # === Post Actions ===
    if open_project:
        print("[*] Opening project folder...")
        os.startfile(project_dir)

    print("[✓] Installation complete. No deployment triggered.")
