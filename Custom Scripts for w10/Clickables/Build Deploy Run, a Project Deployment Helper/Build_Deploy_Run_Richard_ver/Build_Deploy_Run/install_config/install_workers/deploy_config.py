
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_deploy_config(
    target_dir: Path,
    entrypoint: str = "main.py",
    skip_docker: bool = False,
    docker_path: str = "",    
    xwindows_path: str = ""   
) -> bool:
    """Generates the .deploy_config file in a hybrid format (plain + JSON-friendly)."""
    try:
        config_path = Path(target_dir) / ".deploy_config"
        lines = [
            "format=kv",  # Format marker for future extensibility
            f"entrypoint={entrypoint}",
            f"skip_docker={str(skip_docker).lower()}"
        ]
        if docker_path:
            lines.append(f"docker_path={docker_path}")
        if xwindows_path:
            lines.append(f"xwindows_path={xwindows_path}")

        config_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
        logger.info(f"[DEPLOY CONFIG] Generated config at: {config_path}")
        return True
    except Exception as e:
        logger.error(f"[DEPLOY CONFIG] Failed to write .deploy_config: {e}", exc_info=True)
        return False
