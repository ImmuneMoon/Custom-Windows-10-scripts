import subprocess
import time
import sys
from pathlib import Path
from colorama import Fore


def ensure_docker_running():
    print(Fore.YELLOW + "[*] Checking Docker availability...")
    try:
        result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(Fore.GREEN + "[✓] Docker is running.")
            return
    except Exception:
        pass

    print(Fore.YELLOW + "[!] Docker not responding. Attempting to launch Docker Desktop...")

    # Attempt to start Docker Desktop
    try:
        subprocess.run(["start", "docker"], shell=True)
    except Exception as e:
        print(Fore.RED + f"[X] Failed to launch Docker: {e}")
        sys.exit(1)

    for i in range(12):
        time.sleep(5)
        result = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            print(Fore.GREEN + f"[✓] Docker became responsive after {(i+1)*5}s.")
            return

    print(Fore.RED + "[X] Docker did not become responsive in time. Exiting.")
    sys.exit(1)


def ensure_context_is_default():
    print(Fore.YELLOW + "[*] Setting Docker context to 'default'...")
    result = subprocess.run(["docker", "context", "use", "default"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(Fore.RED + "[X] Failed to set Docker context to 'default'.")
        sys.exit(1)
    print(Fore.GREEN + "[✓] Docker context set to 'default'.")


def build_dockerfile_if_missing(project_root: Path, entrypoint="main.py"):
    dockerfile = project_root / "Dockerfile"
    if dockerfile.exists():
        print(Fore.GREEN + "[✓] Dockerfile already exists.")
        return

    print(Fore.YELLOW + "[*] Dockerfile not found. Creating default Dockerfile...")
    dockerfile.write_text(f"""\
FROM python:3.11-slim

WORKDIR /app
COPY . /app/
RUN rm -rf /app/Build_Deploy_Run
RUN pip install --no-cache-dir -r requirements-docker.txt

CMD ["python", "{entrypoint}"]
""")
    print(Fore.GREEN + "[✓] Dockerfile created.")


def patch_dockerfile(project_root: Path):
    dockerfile = project_root / "Dockerfile"
    if not dockerfile.exists():
        return

    with open(dockerfile, "r", encoding="utf-8") as f:
        content = f.read()

    line_to_inject = "RUN rm -rf /app/Build_Deploy_Run"
    if line_to_inject in content:
        print(Fore.GREEN + "[✓] Dockerfile already excludes Build_Deploy_Run.")
        return

    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "COPY" in line.upper():
            lines.insert(i + 1, line_to_inject)
            break
    else:
        lines.append(line_to_inject)

    dockerfile.write_text("\n".join(lines))
    print(Fore.GREEN + "[✓] Dockerfile patched to exclude Build_Deploy_Run.")


def ensure_dockerignore(project_root: Path):
    dockerignore = project_root / ".dockerignore"
    if dockerignore.exists():
        print(Fore.GREEN + "[✓] .dockerignore already exists.")
        return

    dockerignore.write_text(
        "Build_Deploy_Run/\n"
        "__pycache__/\n"
        "*.pyc\n"
        "*.spec\n"
        "*.bat\n"
        "*.ps1\n"
        "venv/\n"
    )
    print(Fore.GREEN + "[+] .dockerignore created.")


def build_docker_image(project_root: Path, image_name: str):
    print(Fore.YELLOW + f"[*] Building Docker image '{image_name}'...")
    subprocess.run(["docker", "build", "-t", image_name, "."], cwd=project_root, check=True)
    print(Fore.GREEN + f"[✓] Docker image '{image_name}' built.")


def run_docker_container(image_name: str, display="host.docker.internal:0"):
    print(Fore.YELLOW + f"[*] Running Docker container '{image_name}' with GUI support...")

    docker_cmd = [
        "docker", "run", "--rm",
        "-e", f"DISPLAY={display}",
        "-e", "DISABLE_TRAY=1",
        image_name
    ]

    try:
        subprocess.run(docker_cmd, check=True)
        print(Fore.GREEN + "[✓] Docker container executed.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[X] Docker failed to run: {e}")
        sys.exit(1)
