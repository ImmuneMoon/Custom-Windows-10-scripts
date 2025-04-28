@echo off
setlocal enabledelayedexpansion

echo [*] Build Deploy Run - Stage 2 Execution [*]
echo.

:: Determine paths assuming this script is in BUILD_DEPLOY_RUN_RICHARD_VER folder
set "BDR_FOLDER_NAME=BUILD_DEPLOY_RUN_RICHARD_VER"
set "SCRIPT_DIR=%~dp0"
:: Go one level up from the script's dir to get the project root
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"
popd
echo Project Root: %PROJECT_ROOT%

:: Define the target Python build script path (relative to PROJECT_ROOT)
set "BUILD_SCRIPT_PATH=%PROJECT_ROOT%\%BDR_FOLDER_NAME%\workers\build_fusion.py"

:: Check if the designated build script exists
if not exist "!BUILD_SCRIPT_PATH!" (
    echo [X] ERROR: Build script not found at: !BUILD_SCRIPT_PATH!
    echo     Please ensure the build logic exists in this file or update BUILD_SCRIPT_PATH in the .bat file.
    pause
    exit /b 1
)

:: Check if the project virtual environment exists (created by Stage 1)
set "VENV_ACTIVATE_PATH=%PROJECT_ROOT%\venv\Scripts\activate.bat"
if not exist "!VENV_ACTIVATE_PATH!" (
    echo [X] ERROR: Project virtual environment not found at: %PROJECT_ROOT%\venv
    echo     Please run the Stage 1 Installer (BuildDeployInstaller.exe) first.
    pause
    exit /b 1
)

echo [*] Activating project virtual environment: !VENV_ACTIVATE_PATH!
call "!VENV_ACTIVATE_PATH!"
if errorlevel 1 (
    echo [X] ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo [*] Running Python build script: !BUILD_SCRIPT_PATH!
echo ==================================================
python "!BUILD_SCRIPT_PATH!"
set BUILD_EXIT_CODE=%ERRORLEVEL%
echo ==================================================
echo [*] Python build script finished with exit code: %BUILD_EXIT_CODE%
echo.

:: Optional: Deactivate is usually automatic when script ends, but can be explicit
:: echo [*] Deactivating virtual environment...
:: call deactivate > nul 2>&1

if %BUILD_EXIT_CODE% neq 0 (
    echo [X] Build script reported errors (exit code %BUILD_EXIT_CODE%).
    pause
) else (
    echo [✓] Build script completed successfully.
)

endlocal
exit /b %BUILD_EXIT_CODE%