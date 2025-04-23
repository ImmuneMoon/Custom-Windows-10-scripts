# install_config/install_workers/notify.py
import os
import subprocess
import sys
import logging
import queue # Added
from pathlib import Path
from install_config.install_workers.GUI.gui_utils import log_to_queue

logger = logging.getLogger(__name__)

# Internal log helper
def _log(log_q, message, level=logging.INFO):
    logger.log(level, message)
    if log_q and isinstance(log_q, queue.Queue):
        try: log_to_queue(f"[{logging.getLevelName(level)}] {message}")
        except Exception: pass

# Original function (slightly adapted naming)
def open_folder_and_readme(project_dir, open_project=True):
    """Opens Readme and optionally the project folder."""
    logger.debug(f"open_folder_and_readme called with project_dir={project_dir}, open_project={open_project}")
    # Use BDR-specific readme name
    readme = Path(project_dir) / "README_Build_Deploy_Run.md"
    if readme.is_file():
        try:
            logger.info(f"Opening readme: {readme}")
            if sys.platform == "win32": os.startfile(readme)
            elif sys.platform == "darwin": subprocess.call(['open', readme])
            else: subprocess.call(['xdg-open', readme])
        except Exception as e: logger.error(f"Failed to open readme {readme}: {e}")
    else:
        logger.warning(f"Readme file not found at {readme}")

    if open_project:
        try:
            logger.info(f"Opening project directory: {project_dir}")
            if sys.platform == "win32": os.startfile(project_dir)
            elif sys.platform == "darwin": subprocess.call(['open', project_dir])
            else: subprocess.call(['xdg-open', project_dir])
        except Exception as e: logger.error(f"Could not open project directory {project_dir}: {e}")

# New Orchestrator Function (moved from installer_steps)
def run_post_install_actions(log_q, project_dir, config, bdr_dest_dir, bdr_venv_path):
    
    # Runs post-install actions based on config. Logs via queue.
    # (Handles orchestrating calls based on config flags)
    
    _log(log_q, "Attempting post-install actions...", level=logging.INFO)
    should_open_project = config.get('open_project_folder', False)

    # --- Open Project Folder / Readme ---
    if should_open_project:
        _log(log_q, "Config indicates opening project folder/readme.", level=logging.INFO)
        try:
            open_folder_and_readme(str(project_dir), open_project=True) # Pass project_root
        except Exception as e:
            _log(log_q, f"Error during open_folder_and_readme: {e}", level=logging.WARNING)
    else:
        _log(log_q, "Skipping opening project folder/readme (not selected).", level=logging.INFO)

    # --- Add other actions based on config here ---
    # Example: VcXsrv launch (would need config['run_xlaunch'], config['vcxsrv_path'])
    # Example: Docker launch (would need config['run_docker'], config['docker_tag'], docker_helpers)

    _log(log_q, "Post-install actions finished.", level=logging.DEBUG)
    return True


# Allow running module directly for testing (optional)
if __name__ == '__main__':
    print("Testing notify.py...")
    test_dir = Path.cwd()
    print(f"Using test directory: {test_dir}")
    dummy_readme = test_dir / "README_Build_Deploy_Run.md"
    if not dummy_readme.exists():
        try: dummy_readme.write_text("# Dummy Readme")
        except Exception as e: print(f"Could not create dummy readme: {e}")

    logging.basicConfig(level=logging.DEBUG)
    print("\nTesting open_folder_and_readme:")
    open_folder_and_readme(str(test_dir), open_project=True)

    print("\nTesting run_post_install_actions:")
    dummy_q = queue.Queue()
    dummy_config = {'open_project_folder': True}
    dummy_bdr_dest = test_dir / "BUILD_DEPLOY_RUN_TEST"
    dummy_bdr_venv = dummy_bdr_dest / "venv"
    run_post_install_actions(dummy_q, test_dir, dummy_config, dummy_bdr_dest, dummy_bdr_venv)

    print("\nTest complete.")
    # if dummy_readme.exists(): os.remove(dummy_readme) # Clean up