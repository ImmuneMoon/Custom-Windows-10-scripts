# install_config/install_workers/installer_steps.py
import logging, queue, threading, traceback, os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Make sure these imports are correct based on your project structure
# Assuming manage_user_project_venv will be added to venv_utils.py
from .venv_utils import setup_user_virtualenv
from .deploy_config import copy_deploy_config
from .install_utils import (
    copy_bdr_scripts,
    copy_venv_bootstrap,
    run_entrypoint_script,
    validate_docker_setup,
    copy_xlaunch_config,
)
from .post_copy import copy_additional_files  # New import

def build_steps(
    source_dir: Path,
    user_project_dir: Path,
    entrypoint_script: str,
    force_replace_venv: bool,
    skip_docker: bool,
) -> List[dict]:
    steps = [
        {
            "name": "Copy BDR Scripts",
            "func": copy_bdr_scripts,
            "args": [source_dir, user_project_dir],
            "kwargs": {"overwrite": True},
            "test": lambda: (user_project_dir / "Build_Deploy_Run").exists()
        },
        {
            "name": "Copy Venv Bootstrap",
            "func": copy_venv_bootstrap,
            "args": [source_dir, user_project_dir],
            "kwargs": {},
            "test": lambda: (user_project_dir / "Build_Deploy_Run" / "venv_bootstrap.py").exists()
        },
        {
            "name": "Copy Deploy Config",
            "func": copy_deploy_config,
            "args": [user_project_dir],
            "kwargs": {},
            "test": lambda: (user_project_dir / "Build_Deploy_Run" / "deploy_config.json").exists()
        },
        {
            "name": "Setup User Virtualenv",
            "func": setup_user_virtualenv,
            "args": [user_project_dir],
            "kwargs": {"force": force_replace_venv},
            "test": lambda: (user_project_dir / "Build_Deploy_Run" / ".venv").exists()
        },
        {
            "name": "Validate Docker Setup",
            "func": validate_docker_setup,
            "args": [user_project_dir],
            "kwargs": {},
            "test": lambda: True,
            "skip": skip_docker
        },
        {
            "name": "Copy XLaunch Config",
            "func": copy_xlaunch_config,
            "args": [source_dir, user_project_dir],
            "kwargs": {},
            "test": lambda: (user_project_dir / "Build_Deploy_Run" / "config.xlaunch").exists()
        },
        {
            "name": "Post-Copy Additional Files",
            "func": copy_additional_files,
            "args": [user_project_dir],
            "kwargs": {},
            "test": lambda: (user_project_dir / "Build_Deploy_Run" / "build_and_deploy_venv_locked.bat").exists()
        }
    ]
    return steps