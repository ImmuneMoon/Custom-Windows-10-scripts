import os
import shutil
import subprocess
import sys
import json
from pathlib import Path

def copy_project(src_dir: Path, dest_dir: Path):
    if dest_dir.exists():
        raise FileExistsError(f"Target directory already exists: {dest_dir}")
    shutil.copytree(src_dir, dest_dir)
    print(f"[✓] Project copied to: {dest_dir}")

def generate_config(dest_dir: Path):
    config_path = dest_dir / "user_config.json"
    config = {
        "project_name": "MyApp",
        "author": "user",
        "entry_point": "main.py"
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"[✓] user_config.json generated at {config_path}")

def create_venv(dest_dir: Path):
    venv_path = dest_dir / "venv"
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
    print(f"[✓] Virtual environment created at {venv_path}")

def install_requirements(dest_dir: Path):
    venv_python = dest_dir / "venv" / "Scripts" / "python.exe"
    req_file = dest_dir / "requirements.txt"
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", str(req_file)])
    print(f"[✓] Requirements installed from {req_file}")

def main():
    src_dir = Path(__file__).parent.resolve()
    print("[?] Where do you want to install Build_Deploy_Run?")
    dest_input = input("Enter target directory: ").strip()
    dest_dir = Path(dest_input) / "Build_Deploy_Run"

    try:
        copy_project(src_dir, dest_dir)
        generate_config(dest_dir)
        create_venv(dest_dir)
        install_requirements(dest_dir)
        print("\n[✔] Setup complete! You can now run `build_and_deploy_venv_locked.bat` when ready.")
    except Exception as e:
        print(f"[!] Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
