@echo off
setlocal enabledelayedexpansion
title "ThreatWeave - Test and Verification Runner"

echo ===============================================================================
echo   THREATWEAVE (HNX26PSI03) - VERIFICATION ^& TEST RUNNER
echo ===============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

set "PYTHON_EXE=%SCRIPT_DIR%\backend\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [1/2] Running Complete Pytest Suite (42 tests)...
echo -------------------------------------------------------------------------------
"%PYTHON_EXE%" -m pytest backend/tests
if errorlevel 1 (
    echo.
    echo [FAIL] Pytest tests failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Running Headless Evaluator Benchmark (scripts/run_demo.py)...
echo -------------------------------------------------------------------------------
"%PYTHON_EXE%" "%SCRIPT_DIR%\scripts\run_demo.py"
if errorlevel 1 (
    echo.
    echo [FAIL] Evaluator demo failed!
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo   ALL TESTS AND EVALUATOR BENCHMARKS PASSED SUCCESSFULLY (100%)
echo ===============================================================================
echo.
pause
