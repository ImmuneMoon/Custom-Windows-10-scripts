@echo off

:: ./build_and_deploy_venv_locked.bat

REM === Build & Deploy VENV Locked Script ===
SETLOCAL ENABLEEXTENSIONS
TITLE Build and Deploy - Locked Venv

REM --- Paths ---
SET VENV_DIR=%~dp0.venv
SET PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
SET PROJECT_DIR=%~dp0..
SET CONFIG_FILE=%~dp0.deploy_config

REM --- Banner ---
echo -------------------------------------------------
echo  BUILD AND DEPLOY SCRIPT STARTED
echo  Using virtual environment: %VENV_DIR%
echo -------------------------------------------------
echo.

REM --- Check venv existence ---
IF NOT EXIST "%PYTHON_EXE%" (
    echo [FATAL] Python executable not found at: %PYTHON_EXE%
    echo         It’s likely your venv creation failed or is missing pip.
    echo         Try manually running:
    echo         python -m venv "%VENV_DIR%"
    echo         followed by:
    echo         "%VENV_DIR%\Scripts\python.exe" -m ensurepip
    where python
    pause
    exit /b 1
)

REM --- Debug global Python paths ---
echo [DEBUG] Checking global python paths:
where python

REM --- Activate Environment ---
call "%VENV_DIR%\Scripts\activate.bat"

REM --- Load Config if Exists ---
SET ENTRYPOINT_ARG=
SET SKIP_DOCKER_ARG=

IF EXIST "%CONFIG_FILE%" (
    FOR /F "tokens=1,2 delims==" %%A IN (%CONFIG_FILE%) DO (
        IF /I "%%A"=="entrypoint" SET ENTRYPOINT_ARG=--entrypoint %%B
        IF /I "%%A"=="skip_docker" IF /I "%%B"=="true" SET SKIP_DOCKER_ARG=--skip-docker
    )
)

REM --- Confirm Python being used ---
echo [DEBUG] Running sys.executable check:
"%PYTHON_EXE%" -c "import sys; print('[DEBUG] sys.executable:', sys.executable)"

REM --- Run Deployment ---
echo [INFO] Launching deployment...
"%PYTHON_EXE%" -c "import runpy; runpy.run_path(r'%~dp0internal\\deploy_fusion_runner.py', run_name='__main__')" %ENTRYPOINT_ARG% %SKIP_DOCKER_ARG%

REM --- Freeze Dependencies ---
echo [INFO] Freezing requirements.txt to project root
"%PYTHON_EXE%" -m pip freeze > "%PROJECT_DIR%\requirements.txt"

echo.
echo [SUCCESS] Build and deploy process complete.
pause
exit /b 0
