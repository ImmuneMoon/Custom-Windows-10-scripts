# install_config/install_workers/venv_utils.py
import logging, subprocess, traceback, shutil, os
from pathlib import Path

logger = logging.getLogger(__name__)

def find_system_python():
    """Tries to find python.exe/python on the system PATH."""
    logger.debug("Searching for system Python executable...")
    # Use shutil.which to find python - requires Python 3.3+
    python_exe = shutil.which("python")
    if python_exe:
        logger.info(f"Found system Python at: {python_exe}")
        # Optional: Add version check? subprocess.run([python_exe, "--version"])
        return python_exe
    else:
        logger.error("System Python executable not found in PATH.")
        # Raising an error might be better than returning None if Python is essential
        raise RuntimeError("System Python executable not found in PATH.")

# --- Venv Creator (Revised Strategy) ---
def create_venv(path: Path, force_delete: bool = False):
    """
    Creates a virtual environment at the specified path using the system Python.
    Optionally deletes an existing environment first if force_delete is True.
    """
    if not isinstance(path, Path):
        path = Path(path) # Ensure path is a Path object

    # Handle existing directory
    if path.exists():
        if force_delete:
            logger.warning(f"[VENV] Removing existing venv at: {path}")
            try:
                shutil.rmtree(path)
                logger.debug(f"[VENV] Successfully removed existing venv: {path}")
            except OSError as e:
                logger.error(f"[VENV ERROR] Failed to remove existing venv {path}: {e}")
                raise RuntimeError(f"Failed to remove existing venv: {e}") from e
        else:
            # If it exists and force_delete is False, assume it's okay and do nothing.
            logger.info(f"[VENV] Environment already exists at {path} and force_delete is False. Skipping creation.")
            # Check if it's usable?
            scripts_subdir = "Scripts" if os.name == 'nt' else "bin"
            venv_python_exe = path / scripts_subdir / "python.exe" if os.name == 'nt' else path / scripts_subdir / "python"
            if venv_python_exe.is_file():
                logger.info(f"[VENV] Existing environment at {path} seems valid (found python).")
                return # Successfully "created" by finding existing valid one
            else:
                logger.error(f"[VENV ERROR] Existing directory at {path} is not a valid venv (python missing). Cannot proceed without force_delete=True.")
                raise RuntimeError(f"Existing directory at {path} is not a valid venv and force_delete is False.")

    logger.info(f"[VENV] Attempting to create virtual environment at {path} using system Python...")

    # 1. Find system Python
    system_python_exe = find_system_python()
    # find_system_python now raises error if not found

    # 2. Construct the command to run system Python's venv module
    cmd = [system_python_exe, "-m", "venv", str(path)]
    logger.info(f"Executing command: {' '.join(cmd)}")

    try:
        # 3. Run the command using subprocess
        result = subprocess.run(
            cmd,
            check=True, # Raise exception on failure
            capture_output=True, # Capture output
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        logger.info(f"[VENV] System Python created virtual environment successfully at {path}.")
        if result.stdout: logger.debug(f"[VENV] Creation STDOUT:\n{result.stdout}")
        if result.stderr: logger.warning(f"[VENV] Creation STDERR:\n{result.stderr}")

        # --- Verification ---
        scripts_subdir = "Scripts" if os.name == 'nt' else "bin"
        venv_python_exe = path / scripts_subdir / "python.exe" if os.name == 'nt' else path / scripts_subdir / "python"
        pip_exe = path / scripts_subdir / "pip.exe" if os.name == 'nt' else path / scripts_subdir / "pip"

        if not venv_python_exe.is_file():
             logger.error(f"[VENV ERROR] Venv created but python executable is missing in {venv_python_exe.parent}!")
             raise RuntimeError("Venv creation seemed successful, but python executable is missing.")
        if not pip_exe.is_file():
             logger.warning(f"[VENV WARNING] Venv created but pip executable is missing in {pip_exe.parent}. Requirement installation might fail.")
             # Decide whether to raise an error or just warn
             # raise RuntimeError("Venv creation seemed successful, but pip executable is missing.")
        else:
            logger.info(f"[VENV] python and pip executables verified successfully in new venv at {path}.")

    except subprocess.CalledProcessError as venv_error:
        logger.critical(f"[VENV CRITICAL] System Python failed to create venv (Exit Code {venv_error.returncode}): {venv_error}")
        stderr_output = venv_error.stderr if hasattr(venv_error, 'stderr') and venv_error.stderr else "N/A"
        stdout_output = venv_error.stdout if hasattr(venv_error, 'stdout') and venv_error.stdout else "N/A"
        logger.error(f"[VENV] Creation Fallback STDERR:\n{stderr_output}")
        logger.error(f"[VENV] Creation Fallback STDOUT:\n{stdout_output}")
        raise RuntimeError(f"System Python failed to create virtual environment: {venv_error}") from venv_error
    except Exception as final_e:
        logger.critical(f"[VENV CRITICAL] Unexpected error during venv creation: {final_e}", exc_info=True)
        raise RuntimeError(f"Unexpected error creating venv via system Python: {final_e}") from final_e


# --- PIP Installer ---
def install_requirements(venv_path: Path, requirements_file: Path):
    """Installs packages from a requirements file into the specified venv."""
    if not isinstance(venv_path, Path): venv_path = Path(venv_path)
    if not isinstance(requirements_file, Path): requirements_file = Path(requirements_file)

    scripts_subdir = "Scripts" if os.name == 'nt' else "bin"
    python_exe = venv_path / scripts_subdir / "python.exe" if os.name == 'nt' else venv_path / scripts_subdir / "python"
    pip_exe = venv_path / scripts_subdir / "pip.exe" if os.name == 'nt' else venv_path / scripts_subdir / "pip"

    if not python_exe.is_file():
        raise FileNotFoundError(f"Python executable not found in venv: {python_exe}")
    if not pip_exe.is_file():
        # If pip is missing, we likely can't install. Error out.
        logger.error(f"[PIP INSTALL ERROR] pip executable missing in venv {venv_path} before installing requirements.")
        raise FileNotFoundError(f"pip executable not found in venv: {pip_exe}")

    # Check if requirements file exists *before* trying to install
    if not requirements_file.is_file():
         logger.warning(f"[PIP INSTALL] Requirements file not found, skipping installation: {requirements_file}")
         # If the requirements file is optional, returning here is okay.
         # If it's mandatory for this step, consider raising an error.
         return

    logger.info(f"[PIP INSTALL] Preparing to install requirements from: {requirements_file} into {venv_path}")

    try:
        # Prepare a cleaned environment for subprocess to avoid conflicts
        clean_env_pip = os.environ.copy()
        clean_env_pip.pop('PYTHONHOME', None)
        clean_env_pip.pop('PYTHONPATH', None)
        # Ensure the venv's script directory is on the PATH for this subprocess
        venv_scripts_dir_str = str(python_exe.parent)
        original_path = clean_env_pip.get('PATH', '')
        clean_env_pip['PATH'] = f"{venv_scripts_dir_str}{os.pathsep}{original_path}"

        # Optionally upgrade pip first (can sometimes help with complex packages)
        logger.info(f"[PIP INSTALL] Upgrading pip in: {python_exe}")
        pip_upgrade_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check"]
        pip_upgrade_result = subprocess.run(
            pip_upgrade_cmd,
            check=False, # Don't fail install if pip upgrade fails, just log
            capture_output=True, text=True, encoding='utf-8', errors='replace', env=clean_env_pip
        )
        if pip_upgrade_result.returncode != 0:
            logger.warning(f"[PIP INSTALL WARNING] Failed to upgrade pip (Exit code {pip_upgrade_result.returncode}). Continuing installation...")
            if pip_upgrade_result.stderr: logger.warning(f"Pip upgrade stderr:\n{pip_upgrade_result.stderr}")

        # Install requirements
        logger.info(f"[PIP INSTALL] Installing requirements from: {requirements_file}")
        req_install_cmd = [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)]
        req_install_result = subprocess.run(
            req_install_cmd,
            check=True, # Fail the step if requirements installation fails
            capture_output=True, text=True, encoding='utf-8', errors='replace', env=clean_env_pip
        )
        logger.info("[PIP INSTALL] Requirements installation completed successfully.")
        if req_install_result.stdout: logger.debug(f"Pip install stdout:\n{req_install_result.stdout}")
        if req_install_result.stderr: logger.warning(f"Pip install stderr:\n{req_install_result.stderr}") # Log stderr even on success

    except subprocess.CalledProcessError as e:
        logger.error(f"[PIP INSTALL ERROR] Command failed with exit code {e.returncode}: {' '.join(e.cmd)}")
        stderr_output = e.stderr if hasattr(e, 'stderr') and e.stderr else "N/A"
        stdout_output = e.stdout if hasattr(e, 'stdout') and e.stdout else "N/A"
        logger.error(f"[PIP INSTALL] STDERR:\n{stderr_output}")
        logger.error(f"[PIP INSTALL] STDOUT:\n{stdout_output}")
        # Re-raise to signal failure to the calling step
        raise RuntimeError(f"Failed to install requirements from {requirements_file}") from e
    except Exception as e_final:
        logger.error(f"[PIP INSTALL ERROR] Unexpected error during requirement installation: {e_final}", exc_info=True)
        raise RuntimeError(f"Unexpected error installing requirements: {e_final}") from e_final


# <<< NEW FUNCTION ADDED HERE >>>
def manage_user_project_venv(user_project_dir: Path, force_delete: bool):
    """
    Checks for a venv in the user project root. If found, deletes
    it only if force_delete is True (determined by GUI checkbox).
    Creates a new venv if it doesn't exist or was deleted.
    Relies on the create_venv function defined above.
    """
    if not isinstance(user_project_dir, Path): user_project_dir = Path(user_project_dir)
    user_venv_path = user_project_dir / ".venv" # Standard venv name
    logger.info(f"[USER VENV] Managing environment at: {user_venv_path}")

    venv_existed = False
    if user_venv_path.exists() and user_venv_path.is_dir():
        venv_existed = True
        logger.warning(f"[USER VENV] Found existing environment at {user_venv_path}")
        if force_delete:
            logger.warning("[USER VENV] force_delete is True (user confirmed via GUI). Removing existing environment...")
            try:
                shutil.rmtree(user_venv_path)
                logger.info("[USER VENV] Successfully removed existing environment.")
                # Proceed to create fresh one below
            except OSError as e:
                logger.error(f"[USER VENV ERROR] Failed to remove {user_venv_path}: {e}")
                raise RuntimeError(f"Failed removing user venv: {e}") from e
        else:
            logger.info("[USER VENV] force_delete is False (user did not check replace option). Skipping deletion and creation.")
            # If we didn't delete it, assume it's wanted as-is and do nothing further.
            return # Exit the function
    elif user_venv_path.exists() and not user_venv_path.is_dir():
        # Handle case where .venv exists but is a file, not a directory
        logger.error(f"[USER VENV ERROR] Path exists but is not a directory: {user_venv_path}. Attempting removal.")
        try:
            user_venv_path.unlink() # Try removing the file
            logger.info(f"[USER VENV] Removed existing file at {user_venv_path}.")
        except OSError as e:
             logger.error(f"[USER VENV ERROR] Failed to remove existing file {user_venv_path}: {e}")
             raise RuntimeError(f"Failed removing existing file blocking user venv: {e}") from e
        # Proceed to create venv below

    else:
        logger.info(f"[USER VENV] No environment found at {user_venv_path}. Will create one.")
        # Proceed to create one below

    # --- Create venv ---
    # This block runs if:
    # 1. The venv directory didn't exist initially.
    # 2. The venv directory existed and force_delete was True (it was deleted above).
    # 3. The .venv path existed but was a file (it was deleted above).

    logger.info(f"[USER VENV] Creating new environment at {user_venv_path}...")
    try:
        # Call create_venv from this same file.
        # Pass force_delete=False because we explicitly handled deletion above based on the flag.
        create_venv(user_venv_path, force_delete=False)
        logger.info(f"[USER VENV] Successfully created environment at {user_venv_path}.")
    except Exception as e:
         # Catch errors specifically from create_venv
         logger.error(f"[USER VENV ERROR] create_venv failed for {user_venv_path}: {e}", exc_info=True)
         # Re-raise or handle as appropriate for the installer step
         raise # Propagate error to stop installation


# --- Optional: Save Additional Config ---
# This function seems specific to BDR config, not directly related to venv creation
# Keep it as is unless its logic needs changing
def write_bdr_config_file(target_dir: Path, xwindows_path: str = '', docker_path: str = '', open_paths: bool = False):
    """Writes user-selected paths (Docker, XWindows) to a config file."""
    if not isinstance(target_dir, Path): target_dir = Path(target_dir)
    # Assuming this config file belongs inside the Build_Deploy_Run folder
    config_file = target_dir / ".deploy_config" # Changed filename slightly, adjust if needed
    try:
        # Create target directory if it doesn't exist (should exist after copy step)
        target_dir.mkdir(parents=True, exist_ok=True)

        lines_to_write = []
        if xwindows_path:
            lines_to_write.append(f"xwindows_path={xwindows_path}")
        if docker_path:
            lines_to_write.append(f"docker_path={docker_path}")
        # Add other config settings if needed from GUI
        lines_to_write.append(f"open_paths={'true' if open_paths else 'false'}") # Example

        with config_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines_to_write) + "\n")
        logger.info(f"[CONFIG] Wrote BDR config to: {config_file}")

    except Exception as e:
        logger.error(f"[CONFIG ERROR] Failed to write BDR config to {config_file}: {e}", exc_info=True)
        # Decide if this is fatal - if batch script relies on it, maybe raise
        # raise RuntimeError(f"Failed to write BDR config: {e}") from e