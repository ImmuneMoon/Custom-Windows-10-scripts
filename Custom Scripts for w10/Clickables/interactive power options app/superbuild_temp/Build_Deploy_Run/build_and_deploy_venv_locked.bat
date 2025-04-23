@echo off
setlocal enabledelayedexpansion

echo [*] RUNNING build_and_deploy_venv_locked.bat
color 0A
title [ImmuneMoon Environment Executor]

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..

pushd "%PROJECT_ROOT%" >nul
set PROJECT_ROOT=%CD%
popd >nul

if not exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment in root...
    python -m venv "%PROJECT_ROOT%\venv"
)

call "%PROJECT_ROOT%.\venv\Scripts\activate.bat"

echo [*] Installing required base packages...
pip install -r "%SCRIPT_DIR%requirements-bootstrap.txt"

echo [*] Virtual environment activated. Launching deploy script...
python "%SCRIPT_DIR%.\build_and_deploy.py"
pause
