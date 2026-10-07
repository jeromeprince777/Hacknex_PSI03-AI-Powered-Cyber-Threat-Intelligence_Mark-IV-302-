@echo off
setlocal enabledelayedexpansion
title ThreatWeave - One-Click Shutdown

echo ===============================================================================
echo   THREATWEAVE (HNX26PSI03) - SHUTDOWN UTILITY
echo ===============================================================================
echo.

echo [*] Stopping processes on port 8000 (FastAPI Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":8000 "') do (
    if "%%a" neq "0" (
        echo     Terminating PID %%a
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo [*] Stopping processes on port 3000 (Next.js Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":3000 "') do (
    if "%%a" neq "0" (
        echo     Terminating PID %%a
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo [+] ThreatWeave services stopped cleanly.
echo.
timeout /t 2 >nul 2>&1 || ping 127.0.0.1 -n 3 >nul
