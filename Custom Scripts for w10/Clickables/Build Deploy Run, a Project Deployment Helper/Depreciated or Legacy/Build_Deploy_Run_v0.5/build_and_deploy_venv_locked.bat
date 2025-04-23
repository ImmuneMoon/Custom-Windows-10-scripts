@echo off
setlocal enabledelayedexpansion

:: Set script directory early
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..

:: Diagnostics
where python
python --version
echo [*] SCRIPT_DIR resolved to: %SCRIPT_DIR%
echo [*] Checking for build_and_deploy.py...

if exist "%SCRIPT_DIR%\build_and_deploy.py" (
    echo [✓] build_and_deploy.py found.
    echo [*] RUNNING build_and_deploy_venv_locked.bat
    color 0A
    title [ImmuneMoon Environment Executor]

    pushd "%PROJECT_ROOT%" >nul
    set PROJECT_ROOT=%CD%
    popd >nul

    if not exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
        echo [*] Creating virtual environment in root...
        python -m venv venv
    )

    echo [*] Installing bootstrap dependencies...
    call venv\Scripts\activate.bat
    pip install -r Build_Deploy_Run\requirements-bootstrap.txt

    echo [*] Virtual environment activated. Launching deploy script...
    python "%SCRIPT_DIR%\build_and_deploy.py"
    echo [*] Python exited with code %ERRORLEVEL%
    pause
) else (
    echo [X] build_and_deploy.py not found at %SCRIPT_DIR%
    pause
)
