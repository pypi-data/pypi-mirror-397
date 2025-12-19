@echo off
REM TeleTrust Portable Launcher
REM Starts the API server and opens browser

echo ============================================
echo   TeleTrust Compliance Gateway - Portable
echo ============================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Using bundled executable...
    if exist TeleTrust.exe (
        start TeleTrust.exe
        goto :open_browser
    ) else (
        echo [ERROR] TeleTrust.exe not found. Please run from Python.
        pause
        exit /b 1
    )
)

REM Set environment
if exist .env (
    echo Loading environment from .env...
    for /f "tokens=*" %%a in (.env) do set %%a
)

REM Start the server
echo Starting TeleTrust API server on port 8000...
start /b python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

:open_browser
REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Open browser
echo Opening browser to http://localhost:8000/docs
start http://localhost:8000/docs

echo.
echo Server is running. Press Ctrl+C to stop.
echo.

REM Keep window open
pause
