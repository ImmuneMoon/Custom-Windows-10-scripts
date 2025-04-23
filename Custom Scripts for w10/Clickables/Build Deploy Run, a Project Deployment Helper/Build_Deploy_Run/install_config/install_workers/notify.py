# notify.py — Installer execution pipeline
import os
from pathlib import Path


def post_install_actions(project_dir, open_project=True):
    # Open readme
    readme = Path(project_dir) / "README_Build_Deploy_Run.md"
    if readme.exists():
        try:
            os.startfile(readme)
        except Exception:
            print(f"[!] Failed to open: {readme if readme.exists() else project_dir}")


    # Optional project folder
    if open_project:
        try:
            os.startfile(project_dir)
        except Exception:
            print("[!] Could not open project directory.")
