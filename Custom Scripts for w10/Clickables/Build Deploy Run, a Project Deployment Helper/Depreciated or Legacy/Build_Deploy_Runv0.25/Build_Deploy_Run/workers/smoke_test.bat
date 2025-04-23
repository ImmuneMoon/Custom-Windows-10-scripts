@echo off
setlocal enabledelayedexpansion

echo.
echo [*] Starting Smoke Test...
echo.

REM === EXE Smoke Test ===
set "EXE_PATH=dist\Super Power Options\Super Power Options.exe"

if exist "!EXE_PATH!" (
    echo [*] Testing EXE...
    "!EXE_PATH!" --help >nul 2>&1
    if !errorlevel! == 0 (
        echo [✓] EXE launched successfully.
    ) else (
        echo [X] EXE failed to launch.
    )
) else (
    echo [!] "!EXE_PATH!" not found — skipping EXE test.
    goto docker_test
)

echo.

REM === Docker Smoke Test ===
:docker_test
echo [*] Testing Docker image: "!IMAGE!"...

REM Replace with your actual image name if needed
set "IMAGE=super_power_options"

docker run --rm "!IMAGE!" --help >nul 2>&1
if !errorlevel! == 0 (
    echo [✓] Docker container ran successfully.
) else (
    echo [X] Docker container failed.
)

echo.
pause
