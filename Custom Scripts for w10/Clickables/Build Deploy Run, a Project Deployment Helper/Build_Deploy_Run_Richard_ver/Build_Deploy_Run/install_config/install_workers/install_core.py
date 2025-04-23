# install_config/install_workers/install_core.py
import logging, pyperclip, subprocess, shutil
from install_config.install_workers.venv_utils import write_bdr_config_file, create_venv
from pathlib import Path

logger = logging.getLogger(__name__)

# Master installation runner for GUI
def run_installation(
    xwindows_path,
    docker_path,
    project_path,
    open_paths=True,
    auto_confirm=False,
    create_user_env=True,
    force_overwrite_user_env=False
):
    try:
        logger.info("[INSTALL START] Preparing Build_Deploy_Run installation...")

        bdr_folder = Path(project_path) / "Build_Deploy_Run"
        bdr_venv_path = bdr_folder / ".venv"
        requirements_path = bdr_folder / "requirements.txt"

        # Step 0: Warn and optionally clean up root-level venv if found
        root_venv = Path(project_path) / ".venv"
        if root_venv.exists():
            logger.warning(f"[PRECHECK] Found existing root-level .venv: {root_venv}")
            if force_overwrite_user_env:
                logger.info("[PRECHECK] force_overwrite_user_env is True, removing root-level .venv...")
                shutil.rmtree(root_venv)

        # Step 0.5: Check for legacy build/deploy artifacts
        dist_path = Path(project_path) / "dist"
        dockerfile_path = Path(project_path) / "Dockerfile"
        if dist_path.exists():
            logger.warning("[PRECHECK] Legacy 'dist' folder found. Possible EXE remnants.")
        if dockerfile_path.exists():
            logger.warning("[PRECHECK] Dockerfile found in project root.")

        # Step 1: Ensure BDR venv is created if requested
        if create_user_env:
            logger.info("[INSTALL INIT] Creating virtual environment for BDR...")
            create_venv(bdr_venv_path, force_delete=force_overwrite_user_env)
        else:
            logger.info("[INSTALL INIT] Skipping venv creation (create_user_env=False)")

        # Step 2: Sanity check for pip
        pip_path = bdr_venv_path / "Scripts" / "pip.exe"
        if not pip_path.exists():
            logger.critical(f"[VENV ERROR] pip.exe missing in venv: {pip_path}")
            return False

        # Step 3: Activate venv and run deploy script
        logger.info("[INSTALL EXEC] Launching deployment in BDR venv...")
        try:
            deploy_cmd = [
                str(bdr_venv_path / "Scripts" / "python.exe"),
                str(bdr_folder / "internal" / "deploy_fusion_runner.py"),
                "--entrypoint", "main.py"
            ]
            if auto_confirm:
                deploy_cmd.append("--auto-confirm")

            subprocess.run(deploy_cmd, check=True)
        except subprocess.CalledProcessError as deploy_error:
            logger.error(f"[DEPLOY ERROR] Deployment failed with: {deploy_error}")
            return False

        # Step 4: Freeze requirements post-deploy
        logger.info("[INSTALL EXEC] Freezing updated requirements to requirements.txt...")
        try:
            with open(requirements_path, "w", encoding="utf-8") as f:
                subprocess.run([
                    str(bdr_venv_path / "Scripts" / "python.exe"),
                    "-m", "pip", "freeze"
                ], check=True, stdout=f)
        except Exception as freeze_err:
            logger.error(f"[REQUIREMENTS ERROR] Failed to write requirements.txt: {freeze_err}")
            return False

        # Step 5: Save deploy metadata and clipboard launch
        write_bdr_config_file(bdr_folder, xwindows_path=xwindows_path, docker_path=docker_path, open_paths=open_paths)
        bat_cmd = f".\\Build_Deploy_Run\\build_and_deploy_venv_locked.bat"
        pyperclip.copy(bat_cmd)
        logger.info("[CLIPBOARD] Launch command copied to clipboard.")
        logger.info("[INSTALL COMPLETE] Installation finished successfully. Venv exited.")

        return True

    except Exception as e:
        logger.exception("[INSTALL ERROR] Fatal error during installation:", exc_info=e)
        return False
