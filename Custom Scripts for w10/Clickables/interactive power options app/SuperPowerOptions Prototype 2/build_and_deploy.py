import subprocess
import os
from pathlib import Path

# Define paths
project_root = Path(__file__).parent.resolve()
req_file = project_root / "requirements.txt"
docker_req_file = project_root / "requirements-docker.txt"
docker_image = "super-power-options"

print("[+] Ensuring dependencies are frozen correctly...")
# Ensure necessary packages are installed before freezing
subprocess.run(["pip", "install", "pystray", "pillow", "pyinstaller"])

# Generate a fresh requirements.txt
with open(req_file, "w") as f:
    subprocess.run(["pip", "freeze"], stdout=f)

# Filter out Windows-only packages (e.g., pywin32) for Docker
print("[+] Creating Docker-compatible requirements-docker.txt...")
if req_file.exists():
    with open(req_file, "r") as f:
        lines = f.readlines()
    with open(docker_req_file, "w") as f:
        f.writelines([line for line in lines if "pywin32" not in line])
else:
    docker_req_file.write_text("")

# Build Docker image
print(f"[+] Building Docker image '{docker_image}'...")
subprocess.run(["docker", "build", "-t", docker_image, "."], check=True)

# Run Docker container
print(f"[*] Running Docker container '{docker_image}'...")
subprocess.run(["docker", "run", "--rm", docker_image], check=True)

print("[✓] Done!")