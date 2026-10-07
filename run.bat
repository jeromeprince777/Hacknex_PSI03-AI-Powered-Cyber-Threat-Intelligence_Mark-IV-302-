@echo off
setlocal enabledelayedexpansion
title ThreatWeave - One-Click Launcher

echo ===============================================================================
echo   THREATWEAVE (HNX26PSI03) - AI-POWERED CYBER THREAT INTELLIGENCE
echo   One-Click Launcher and Environment Initializer
echo ===============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

:: -----------------------------------------------------------------------------
:: Step 1: Detect / Prepare Python Environment
:: -----------------------------------------------------------------------------
echo [*] Checking Python environment

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('where python') do (
    set "SYS_PYTHON_DIR=%%~dpi"
    goto :found_sys_python
)
:found_sys_python
if "%SYS_PYTHON_DIR:~-1%"=="\" set "SYS_PYTHON_DIR=%SYS_PYTHON_DIR:~0,-1%"

set "VENV_DIR=%SCRIPT_DIR%\backend\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_DIR%" (
    echo [*] Creating virtual environment at backend\.venv
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [*] Installing backend dependencies from requirements.txt
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%\backend\requirements.txt"
) else (
    "%PYTHON_EXE%" --version >nul 2>&1
    if errorlevel 1 (
        echo [*] Repairing virtual environment configuration for current system
        if exist "%VENV_DIR%\pyvenv.cfg" (
            (
                echo home = %SYS_PYTHON_DIR%
                echo implementation = CPython
                echo include-system-site-packages = false
            ) > "%VENV_DIR%\pyvenv.cfg"
        )
        "%PYTHON_EXE%" --version >nul 2>&1
        if errorlevel 1 (
            echo [*] Re-creating virtual environment
            rmdir /s /q "%VENV_DIR%"
            python -m venv "%VENV_DIR%"
            "%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%\backend\requirements.txt"
        )
    )
)

echo [+] Python environment verified:
"%PYTHON_EXE%" --version

:: -----------------------------------------------------------------------------
:: Step 2: Detect / Prepare Node.js and Frontend Environment
:: -----------------------------------------------------------------------------
echo.
echo [*] Checking Node.js environment

where npm.cmd >nul 2>&1
if errorlevel 1 (
    where npm >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Node.js/npm was not found on PATH. Please install Node.js 18+.
        pause
        exit /b 1
    )
    set "NPM_CMD=npm"
) else (
    set "NPM_CMD=npm.cmd"
)

if not exist "%SCRIPT_DIR%\frontend\node_modules" (
    echo [*] Installing frontend dependencies
    pushd "%SCRIPT_DIR%\frontend"
    call !NPM_CMD! install
    popd
)
echo [+] Frontend environment verified.

:: -----------------------------------------------------------------------------
:: Step 3: Clear Stale Ports (8000 and 3000)
:: -----------------------------------------------------------------------------
echo.
echo [*] Ensuring ports 8000 and 3000 are available
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":8000 "') do (
    if "%%a" neq "0" (
        echo     Closing previous process on port 8000 (PID %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":3000 "') do (
    if "%%a" neq "0" (
        echo     Closing previous process on port 3000 (PID %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)

:: -----------------------------------------------------------------------------
:: Step 4: Launch Backend and Frontend Services
:: -----------------------------------------------------------------------------
echo.
echo [*] Launching ThreatWeave FastAPI Backend on http://127.0.0.1:8000
start "ThreatWeave Backend [FastAPI :8000]" /d "%SCRIPT_DIR%" cmd /k ""%PYTHON_EXE%" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"

echo [*] Initializing backend service
ping 127.0.0.1 -n 4 >nul

echo [*] Launching ThreatWeave Next.js Frontend on http://localhost:3000
start "ThreatWeave Frontend [Next.js :3000]" /d "%SCRIPT_DIR%\frontend" cmd /k "!NPM_CMD! run dev -- -p 3000"

echo [*] Initializing frontend dev server
ping 127.0.0.1 -n 5 >nul

:: -----------------------------------------------------------------------------
:: Step 5: Launch Browser and Display Console Banner
:: -----------------------------------------------------------------------------
echo [*] Opening Tactical SOC Command Dashboard in browser
start http://localhost:3000

echo.
echo ===============================================================================
echo   THREATWEAVE IS ACTIVE AND RUNNING
echo   - Web Console:   http://localhost:3000
echo   - Backend API:   http://127.0.0.1:8000
echo   - API Docs:      http://127.0.0.1:8000/docs
echo.
echo   Press any key or run stop.bat to shut down all ThreatWeave services.
echo ===============================================================================
echo.
pause

call "%SCRIPT_DIR%\stop.bat"
