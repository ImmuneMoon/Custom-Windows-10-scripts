# freeze.py
import subprocess
from pathlib import Path

EXCLUDE_MODULES = ["pyinstaller", "colorama", "altgraph", "pywin32-ctypes", "pefile"]

# === FREEZE REQUIREMENTS ===
def freeze_requirements(project_root: Path):
    print("[*] Freezing requirements...")

    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to freeze requirements")

    lines = result.stdout.splitlines()

    # Filter out bootstrap/internal tools
    clean_lines = [
        line for line in lines
        if not any(bad in line.lower() for bad in EXCLUDE_MODULES)
    ]

    for filename in ["requirements.txt", "requirements-docker.txt"]:
        out_path = project_root / filename
        with out_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(clean_lines) + "\n")
        print(f"[✓] Wrote {filename}")
