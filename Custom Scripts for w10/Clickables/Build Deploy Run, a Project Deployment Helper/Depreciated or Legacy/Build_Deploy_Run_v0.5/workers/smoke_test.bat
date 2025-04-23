@echo off
setlocal enabledelayedexpansion

echo.
echo [*] Starting Smoke Test...
echo.

REM === EXE Smoke Test ===
if exist dist\Super_Power_Options\Super_Power_Options.exe (
    echo [*] Testing EXE...
    dist\Super_Power_Options\Super_Power_Options.exe --help >nul 2>&1
    if %errorlevel%==0 (
        echo [✓] EXE launched successfully.
    ) else (
        echo [X] EXE failed to launch.
    )
) else (
    echo [!] EXE not found at dist\Super_Power_Options\Super_Power_Options.exe
)

echo.

REM === Docker Smoke Test ===
echo [*] Testing Docker image...

REM Replace with your actual image name if needed
set IMAGE=super_power_options

docker run --rm %IMAGE% --help >nul 2>&1
if %errorlevel%==0 (
    echo [✓] Docker container ran successfully.
) else (
    echo [X] Docker container failed.
)

echo.
pause
