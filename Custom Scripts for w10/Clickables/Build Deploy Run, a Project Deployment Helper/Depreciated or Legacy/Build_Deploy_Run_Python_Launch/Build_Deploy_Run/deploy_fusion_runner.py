import os
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, env=None):
    subprocess.run(cmd, shell=True, check=True, env=env)

def venv_exists(path):
    return (Path(path) / "Scripts" / "activate").exists()

def create_venv(path):
    print(f"[+] Creating venv at {path}")
    run_command(f'python -m venv "{path}"')

def install_requirements(req_path, venv_path):
    pip = Path(venv_path) / "Scripts" / "pip.exe"
    run_command(f'"{pip}" install -r "{req_path}"')

def prompt_user(question):
    print(question + " [y/N]: ", end="")
    return input().strip().lower() == "y"

def delete_venv(path):
    print(f"[!] Deleting existing venv at {path}...")
    shutil.rmtree(path)

def generate_clean_requirements(project_dir, output_path):
    print("[*] Generating clean requirements.txt from user project...")
    ignore_paths = ["Build_Deploy_Run", "venv"]
    temp_req = Path(project_dir) / "temp_reqs.txt"
    run_command(f'pip freeze > "{temp_req}"')

    with open(temp_req, "r") as src, open(output_path, "w") as dst:
        for line in src:
            if not any(ig in line.lower() for ig in ignore_paths):
                dst.write(line)
    temp_req.unlink()

def generate_exe(project_dir):
    print("[*] Building EXE...")
    run_command(f'pyinstaller "{project_dir}/Super_Power_Options.spec"')

def build_docker_image(project_dir, tag="super_power_options"):
    print("[*] Building Docker image...")
    run_command(f'docker build -t {tag} "{project_dir}"')

def main():
    base = Path.cwd()
    bdr_dir = base / "Build_Deploy_Run"
    proj_dir = base

    # Step 1: Ensure Build_Deploy_Run is in place
    if not bdr_dir.exists():
        print("[X] Build_Deploy_Run folder not found.")
        return

    # Step 2: Setup BDR venv
    bdr_venv = bdr_dir / "venv"
    if not venv_exists(bdr_venv):
        create_venv(bdr_venv)
        install_requirements(bdr_dir / "requirements.txt", bdr_venv)

    # Step 3: EXE / Docker pre-check
    exe_path = proj_dir / "dist"
    docker_image_name = "super_power_options"
    if exe_path.exists():
        print("[i] Existing EXE found — will be overwritten.")
    if shutil.which("docker"):
        print("[i] Docker available — continuing.")

    # Step 4: Handle project venv
    proj_venv = proj_dir / "venv"
    if venv_exists(proj_venv):
        if prompt_user("Replace existing project venv?"):
            delete_venv(proj_venv)
        else:
            print("Aborted by user.")
            return

    # Step 5: Create clean project venv
    create_venv(proj_venv)
    req_out = proj_dir / "requirements.txt"
    generate_clean_requirements(proj_dir, req_out)
    install_requirements(req_out, proj_venv)

    # Step 6: Build EXE and Docker
    generate_exe(proj_dir)
    build_docker_image(proj_dir)

    print("[✓] Deploy complete. All systems go.")

if __name__ == "__main__":
    main()
