@echo off
setlocal enabledelayedexpansion

echo.
echo [*] Starting Smoke Test...
echo.

REM === Setup project name from folder ===
for %%I in ("%cd%") do set "PROJECT_NAME=%%~nxI"
set "EXE_PATH=dist\%PROJECT_NAME%\%PROJECT_NAME%.exe"
set "DOCKER_IMAGE=%PROJECT_NAME: =_%"

REM === EXE Smoke Test ===
if exist "!EXE_PATH!" (
    echo [*] Testing EXE at "!EXE_PATH!"...
    "!EXE_PATH!" --help >nul 2>&1
    if !errorlevel! == 0 (
        echo [✓] EXE launched successfully.
    ) else (
        echo [X] EXE failed to launch.
    )
) else (
    echo [!] "!EXE_PATH!" not found — skipping EXE test.
)

echo.

REM === Docker Smoke Test ===
echo [*] Testing Docker image: "!DOCKER_IMAGE!"...
docker run --rm "!DOCKER_IMAGE!" --help >nul 2>&1
if !errorlevel! == 0 (
    echo [✓] Docker container ran successfully.
) else (
    echo [X] Docker container failed.
)

echo.
pause
