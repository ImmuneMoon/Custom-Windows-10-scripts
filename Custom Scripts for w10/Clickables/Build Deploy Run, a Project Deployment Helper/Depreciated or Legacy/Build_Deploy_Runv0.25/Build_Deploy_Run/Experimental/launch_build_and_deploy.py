import subprocess
import os
import sys

def run(cmd, cwd=None):
    print(f"[*] Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    venv_dir = os.path.join(project_root, "venv")
    is_windows = os.name == "nt"
    bin_dir = "Scripts" if is_windows else "bin"
    activate_path = os.path.join(venv_dir, bin_dir, "activate")

    print(f"[*] SCRIPT_DIR resolved to: {script_dir}")
    print(f"[*] Checking for build_and_deploy.py...")

    deploy_script = os.path.join(script_dir, "build_and_deploy.py")
    if not os.path.exists(deploy_script):
        print("[X] build_and_deploy.py not found.")
        sys.exit(1)

    print("[✓] build_and_deploy.py found.")

    if not os.path.exists(activate_path):
        print("[*] Creating virtual environment in root...")
        run(f"{sys.executable} -m venv {venv_dir}")

    pip_path = os.path.join(venv_dir, bin_dir, "pip")
    python_path = os.path.join(venv_dir, bin_dir, "python")

    print("[*] Installing bootstrap dependencies...")
    run(f'"{pip_path}" install -r Build_Deploy_Run/requirements-bootstrap.txt')

    print("[*] Virtual environment ready. Launching deploy script...")
    run(f'"{python_path}" "{deploy_script}"')

if __name__ == "__main__":
    main()

# Write the new launcher script to the Build_Deploy_Run directory
launcher_path = os.path.join(project_path, "launch_build_and_deploy.py")
with open(launcher_path, "w") as f:
    f.write(python_launcher_code)

launcher_path
