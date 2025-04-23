import sys
# install_config/install_workers/install_utils.py
from pathlib import Path
import shutil, logging, subprocess, traceback, os # os Needed for os.pathsep and os.name
from typing import Union, List, Optional

logger = logging.getLogger(__name__)


def run_command(cmd: Union[str, List[str]], env: Optional[dict] = None, cwd: Optional[Union[str, Path]] = None) -> None:
    """
    Executes a command using subprocess.run with optional environment variables and working directory.
    Raises CalledProcessError on failure. Logs output.
    """
    if not cmd:
        raise ValueError("Command is empty or None.")
    if isinstance(cmd, str):
        cmd = [cmd] # Convert single string command to list
    elif not isinstance(cmd, (list, tuple)):
        raise TypeError("Command must be a string or list of strings.")

    # Ensure all parts of the command list are strings
    cmd_str_list = []
    for i, part in enumerate(cmd):
        if not isinstance(part, str):
             # Attempt conversion if Path object, otherwise raise error
             if isinstance(part, Path):
                 cmd_str_list.append(str(part))
             else:
                 raise TypeError(f"Command part at index {i} is not string/Path: {repr(part)}")
        else:
             cmd_str_list.append(part)
    cmd = cmd_str_list # Use the validated/converted list

    # Avoid logging overly long commands if necessary, maybe truncate?
    log_cmd = ' '.join(cmd)
    logger.info(f"[CMD] Running: {log_cmd}")
    try:
        # Use check=True to automatically raise CalledProcessError on non-zero exit
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True,
            encoding='utf-8', errors='replace', env=env, cwd=cwd
        )
        # Log stdout only if it contains non-whitespace characters
        stdout_strip = result.stdout.strip()
        if stdout_strip: logger.info(f"[CMD STDOUT]\n{stdout_strip}")
        # Log stderr as warning even if successful
        stderr_strip = result.stderr.strip()
        if stderr_strip: logger.warning(f"[CMD STDERR]\n{stderr_strip}")

    except subprocess.CalledProcessError as e:
        # Log details from the exception object
        logger.error(f"[ERROR] Command failed with exit code {e.returncode}: {log_cmd}")
        stdout_output = e.stdout.strip() if hasattr(e, 'stdout') and e.stdout else "N/A"
        stderr_output = e.stderr.strip() if hasattr(e, 'stderr') and e.stderr else "N/A"
        logger.error(f"[FAILED CMD STDOUT]\n{stdout_output}")
        logger.error(f"[FAILED CMD STDERR]\n{stderr_output}")
        raise # Re-raise the exception after logging
    except FileNotFoundError:
        logger.error(f"[ERROR] Command not found: {cmd[0]}. Check PATH and spelling.")
        raise # Re-raise
    except Exception as e:
        logger.error(f"[FATAL] Unexpected error running command {log_cmd}: {e}", exc_info=True)
        raise


def copy_entire_bdr_folder(source_dir: Path, target_dir: Path, confirm_overwrite: bool = True) -> Path:
    """Copies the entire Build_Deploy_Run folder structure (Potentially Legacy)."""
    logger.warning("copy_entire_bdr_folder called - may be legacy, prefer copy_bdr_scripts.")
    # Ensure Path objects
    if not isinstance(source_dir, Path): source_dir = Path(source_dir)
    if not isinstance(target_dir, Path): target_dir = Path(target_dir)

    # Assuming source_dir *is* the BDR source folder
    src_folder = source_dir
    if not src_folder.is_dir():
        raise FileNotFoundError(f"[BDR] Expected BDR source folder missing: {src_folder}")

    # Define target BDR folder within the user's project dir
    bdr_target_folder = target_dir / "Build_Deploy_Run"

    if bdr_target_folder.exists():
        if confirm_overwrite:
            logger.warning(f"[BDR] Overwriting existing directory: {bdr_target_folder}")
            try:
                shutil.rmtree(bdr_target_folder)
            except OSError as e:
                 logger.error(f"[BDR ERROR] Failed to remove existing directory {bdr_target_folder}: {e}")
                 raise RuntimeError(f"Failed to remove existing BDR directory: {e}") from e
        else:
            logger.info(f"[BDR] Skipping copy (folder exists, overwrite not confirmed): {bdr_target_folder}")
            return bdr_target_folder # Return existing path

    try:
        # Copy the source directory content into the target BDR folder
        shutil.copytree(src_folder, bdr_target_folder, dirs_exist_ok=True)
        logger.info(f"[BDR] Folder copied from {src_folder} to: {bdr_target_folder}")
    except Exception as e:
         logger.error(f"[BDR ERROR] Failed during copytree from {src_folder} to {bdr_target_folder}: {e}")
         raise RuntimeError(f"Failed to copy BDR folder: {e}") from e

    return bdr_target_folder


# Detect PyInstaller path if frozen
if getattr(sys, 'frozen', False):
    bdr_root = Path(getattr(sys, '_MEIPASS'))
else:
    bdr_root = Path(__file__).resolve().parent

def copy_bdr_scripts(src_bdr_root: Path, target_bdr_dir: Path, confirm_overwrite: bool = True):
    """
    Copies required files/folders from BDR source to target BDR directory.
    Overwrites target contents if confirm_overwrite is True.
    """
    logger.debug(f"copy_bdr_scripts(): copying from '{src_bdr_root}' to '{target_bdr_dir}' (Overwrite: {confirm_overwrite})")

    if not isinstance(src_bdr_root, Path): src_bdr_root = Path(src_bdr_root)
    if not isinstance(target_bdr_dir, Path): target_bdr_dir = Path(target_bdr_dir)

    if not src_bdr_root.is_dir():
        logger.error(f"[BDR] BDR source directory missing: {src_bdr_root}")
        raise FileNotFoundError(f"[BDR] BDR source directory missing: {src_bdr_root}")

    if target_bdr_dir.exists() and confirm_overwrite:
         logger.warning(f"[BDR] Overwriting existing contents of: {target_bdr_dir}")
         # Overwrite implies removing old content might be safest if structure changes
         # For simplicity, let copytree/copy2 overwrite files, ensure target dir exists.
    elif target_bdr_dir.exists() and not confirm_overwrite:
         logger.info(f"Target dir {target_bdr_dir} exists, overwrite=False. Skipping copy.")
         return # Don't copy if overwrite not allowed

    # Ensure target directory exists
    try:
        target_bdr_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
         logger.error(f"[BDR ERROR] Cannot create target directory {target_bdr_dir}: {e}")
         raise RuntimeError(f"Failed to create target BDR directory: {e}") from e

    # --- Define what to copy ---
    dirs_to_copy = ["workers"]
    # It's generated later by generate_batch_script, so don't copy it here.
    files_to_copy = ["deploy_fusion_runner.py", "requirements.txt"] # BDR's requirements

    # --- Copy folders ---
    for folder_name in dirs_to_copy:
        src_dir = src_bdr_root / folder_name
        dest_dir = target_bdr_dir / folder_name
        if src_dir.is_dir():
            try:
                # Remove destination first if it exists to ensure clean copy
                if dest_dir.exists():
                    logger.debug(f"Removing existing target directory before copy: {dest_dir}")
                    shutil.rmtree(dest_dir)
                shutil.copytree(src_dir, dest_dir) # No dirs_exist_ok needed after removal
                logger.debug(f"[BDR] Copied directory {src_dir} to {dest_dir}")
            except Exception as e:
                 logger.error(f"[BDR ERROR] Failed copying directory {src_dir} to {dest_dir}: {e}")
                 raise RuntimeError(f"Failed to copy directory '{folder_name}': {e}") from e
        else:
            if folder_name == "workers": # Treat 'workers' as required
                 logger.error(f"[BDR] Required source directory missing: {src_dir}")
                 raise FileNotFoundError(f"[BDR] Required directory missing: {src_dir}")
            else:
                 logger.warning(f"[BDR] Source directory '{folder_name}' not found at {src_dir}, skipping.")

    # --- Copy files ---
    for file_name in files_to_copy:
        src_file = src_bdr_root / file_name
        dest_file = target_bdr_dir / file_name
        if src_file.is_file():
             try:
                shutil.copy2(src_file, dest_file) # copy2 overwrites existing files
                logger.debug(f"[BDR] Copied file {src_file} to {dest_file}")
             except Exception as e:
                 logger.error(f"[BDR ERROR] Failed copying file {src_file} to {dest_file}: {e}")
                 raise RuntimeError(f"Failed to copy required file '{file_name}': {e}") from e
        else:
            # Raise error if required files are missing
            logger.error(f"[BDR] Required source file missing: {src_file}")
            raise FileNotFoundError(f"[BDR] Required file missing: {src_file}")

    logger.info(f"[BDR] Selected content copied to: {target_bdr_dir}")


# --- Batch Script Generation (Using Temp File for pip freeze) ---
def generate_batch_script(target_dir: Path):
    """
    Generates the build_and_deploy_venv_locked.bat file inside the target_dir.
    Uses temp file for pip freeze to avoid redirection issues and adds error checks.
    """
    if not isinstance(target_dir, Path): target_dir = Path(target_dir)

    # Use temp file method for pip freeze
    batch_content = r"""@echo off
REM === Build & Deploy VENV Locked Script ===
SETLOCAL ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS

TITLE Build and Deploy - Locked Venv

REM --- Paths ---
SET "SCRIPT_DIR=%~dp0"
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
SET "VENV_DIR=%SCRIPT_DIR%\.venv"
SET "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
SET "PROJECT_DIR=%SCRIPT_DIR%\.."
SET "CONFIG_FILE=%SCRIPT_DIR%\.deploy_config"
SET "TARGET_SCRIPT=%SCRIPT_DIR%\deploy_fusion_runner.py"

REM --- Banner ---
echo -------------------------------------------------
echo  BUILD AND DEPLOY SCRIPT STARTED
echo  Using virtual environment: %VENV_DIR%
echo -------------------------------------------------
echo.

REM --- Check venv existence ---
IF NOT EXIST "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found in venv: "%PYTHON_EXE%". Aborting.
    goto :eof_error
)

REM --- Check target script existence ---
IF NOT EXIST "%TARGET_SCRIPT%" (
    echo [ERROR] Target deployment script not found: "%TARGET_SCRIPT%". Aborting.
    goto :eof_error
)

REM --- Load Config if Exists ---
SET "ENTRYPOINT_ARG="
SET "SKIP_DOCKER_ARG="
IF EXIST "%CONFIG_FILE%" (
    echo [INFO] Loading config from "%CONFIG_FILE%"
    FOR /F "usebackq tokens=1,* delims==" %%A IN ("%CONFIG_FILE%") DO (
        set "VAR_NAME=%%A" & set "VAR_VALUE=%%B"
        for /f "tokens=* delims= " %%W in ("!VAR_NAME!") do set "VAR_NAME=%%W"
        for /f "tokens=* delims= " %%X in ("!VAR_VALUE!") do set "VAR_VALUE=%%X"
        REM Pass args correctly quoted for deploy_fusion_runner.py
        IF /I "!VAR_NAME!"=="entrypoint" SET "ENTRYPOINT_ARG=--entrypoint \"!VAR_VALUE!\""
        IF /I "!VAR_NAME!"=="skip_docker" IF /I "!VAR_VALUE!"=="true" SET "SKIP_DOCKER_ARG=--skip-docker"
        REM Add lines here to parse docker_path, xwindows_path if needed by script later
        REM IF /I "!VAR_NAME!"=="docker_path" SET "DOCKER_PATH_ARG=--docker-path \"!VAR_VALUE!\""
        REM IF /I "!VAR_NAME!"=="xwindows_path" SET "XWIN_PATH_ARG=--xwindows-path \"!VAR_VALUE!\""
    )
) ELSE ( echo [INFO] No .deploy_config file found at "%CONFIG_FILE%". Assuming defaults if applicable. )

REM --- Run Deployment (Python Script) ---
echo [INFO] Launching deployment: "%PYTHON_EXE%" "%TARGET_SCRIPT%" %ENTRYPOINT_ARG% %SKIP_DOCKER_ARG%
REM Pass only the args parsed above
"%PYTHON_EXE%" "%TARGET_SCRIPT%" %ENTRYPOINT_ARG% %SKIP_DOCKER_ARG%
SET "DEPLOY_EXIT_CODE=%ERRORLEVEL%"

IF NOT !DEPLOY_EXIT_CODE! == 0 (
  echo [ERROR] Deployment script '%TARGET_SCRIPT%' failed with exit code !DEPLOY_EXIT_CODE!. See output above.
  goto :eof_error
) ELSE ( echo [INFO] Deployment script finished successfully. )

REM --- Freeze Dependencies (Using Temp File) ---
echo [INFO] Freezing requirements.txt to project root: "%PROJECT_DIR%\requirements.txt"
REM Use %TEMP% for temporary file location
SET "REQ_TEMP_FILE=%TEMP%\bdr_reqs_%RANDOM%_%TIME::=.%.txt"
"%PYTHON_EXE%" -m pip freeze > "!REQ_TEMP_FILE!"
SET "FREEZE_EXIT_CODE=%ERRORLEVEL%"

IF !FREEZE_EXIT_CODE! == 0 (
    REM Use COPY /Y for robust overwrite, redirect output to NUL
    COPY /Y "!REQ_TEMP_FILE!" "%PROJECT_DIR%\requirements.txt" > NUL
    SET "COPY_EXIT_CODE=%ERRORLEVEL%"
    IF !COPY_EXIT_CODE! == 0 (
        echo [INFO] Successfully froze requirements.txt.
    ) ELSE (
        echo [WARNING] Failed to copy temp requirements file to "%PROJECT_DIR%\requirements.txt" (Exit Code: !COPY_EXIT_CODE!). Check permissions.
    )
    REM Delete temp file regardless of copy success if freeze worked
    IF EXIST "!REQ_TEMP_FILE!" DEL "!REQ_TEMP_FILE!" > NUL
) ELSE (
    echo [WARNING] 'pip freeze' command failed (Exit Code: !FREEZE_EXIT_CODE!). requirements.txt not updated.
    REM Delete temp file if freeze failed
    IF EXIST "!REQ_TEMP_FILE!" DEL "!REQ_TEMP_FILE!" > NUL
)

echo.
echo [SUCCESS] Build and deploy process complete.
goto :eof_success

:eof_error
echo.
echo [SCRIPT FAILED]
pause
exit /b 1

:eof_success
echo.
pause
exit /b 0

ENDLOCAL
""" # End of batch_content raw string

    batch_path = target_dir / "build_and_deploy_venv_locked.bat"
    try:
        # Ensure target directory exists (should have been created by copy step)
        target_dir.mkdir(parents=True, exist_ok=True)
        # Write batch file with UTF-8 encoding and Windows line endings
        with open(batch_path, "w", encoding="utf-8", newline='\r\n') as f:
            f.write(batch_content)
        logger.info(f"[GEN] Batch script generated at: {batch_path}")
    except Exception as e:
        logger.error(f"[GEN] Failed to generate batch script: {e}", exc_info=True)
        raise RuntimeError(f"Failed to generate batch script: {e}") from e