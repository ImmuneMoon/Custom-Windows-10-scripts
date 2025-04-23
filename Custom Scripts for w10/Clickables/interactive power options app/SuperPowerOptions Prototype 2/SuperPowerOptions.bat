# Create a Windows batch file to launch the app with venv activation

bat_file_content = """
@echo off
REM Activate virtual environment and launch the app
SET VENV_DIR=venv

IF NOT EXIST %VENV_DIR% (
    echo [!] Virtual environment not found. Creating one...
    python -m venv venv
)

CALL %VENV_DIR%\\Scripts\\activate.bat

echo [*] Launching Super Power Options...
python main.py

deactivate
"""

bat_file_path = "/mnt/data/launch_super_power_options.bat"
with open(bat_file_path, "w") as f:
    f.write(bat_file_content)

bat_file_path
