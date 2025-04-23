@echo off
setlocal enabledelayedexpansion

REM === Where this script actually lives ===
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM === Where .vscode should be (parent dir of this) ===
set PROJECT_ROOT=%SCRIPT_DIR%\..

REM === Normalize full path ===
pushd "%PROJECT_ROOT%" >nul
set PROJECT_ROOT=%CD%
popd >nul

REM === Ensure .vscode exists ===
if not exist "%PROJECT_ROOT%\.vscode" (
    mkdir "%PROJECT_ROOT%\.vscode"
)

REM === Copy VS Code config ===
copy "%SCRIPT_DIR%\tasks.json" "%PROJECT_ROOT%\.vscode\tasks.json" >nul
copy "%SCRIPT_DIR%\keybindings.json" "%PROJECT_ROOT%\.vscode\keybindings.json" >nul

REM === Now execute the deployer from inside Build_Deploy_Run/ ===
start "" cmd.exe /k "%SCRIPT_DIR%\build_and_deploy_venv_locked.bat"