# install_config/install_workers/post_copy.py
from pathlib import Path
import shutil
import logging

def deploy_to_project_root(installer_dir: Path, target_root: Path):
    """
    Copies deployment-ready assets like workers/, .bat scripts, etc.
    from installer_dir to target_root/Build_Deploy_Run
    """
    deployables = [
        (installer_dir / "workers", target_root / "Build_Deploy_Run" / "workers"),
        (installer_dir / "build_and_deploy_venv_locked.bat", target_root / "Build_Deploy_Run" / "build_and_deploy_venv_locked.bat"),
        (installer_dir / "deploy_fusion_runner.py", target_root / "Build_Deploy_Run" / "deploy_fusion_runner.py"),
        (installer_dir / "requirements.txt", target_root / "Build_Deploy_Run" / "requirements.txt")
    ]

    for src, dst in deployables:
        try:
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            logging.info(f"[Deploy] Copied {src} -> {dst}")
        except Exception as e:
            logging.error(f"[Deploy] Failed to copy {src} to {dst}: {e}")