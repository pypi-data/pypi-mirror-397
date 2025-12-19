# TeleTrust Tradewinds Demo Launcher
# Starts all demo services for Video Solution Brief recording

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   TeleTrust - DoD Tradewinds Demo Suite   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Navigate to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Split-Path -Parent $scriptDir)

# Load environment
if (Test-Path ".env") {
    Write-Host "[INFO] Loading environment from .env" -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

Write-Host ""
Write-Host "[1/3] Starting Compliance Gateway API on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000"

Write-Host "[2/3] Starting Pre-Bill Scrubber UI on port 8501..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run demo/prebill_demo.py --server.port 8501"

Write-Host "[3/3] Starting ESM Metrics Dashboard on port 8502..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run demo/esm_metrics.py --server.port 8502"

# Wait for services to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   All Demo Services Started!              " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo URLs:" -ForegroundColor White
Write-Host "  - API Docs:       http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - Pre-Bill Demo:  http://localhost:8501" -ForegroundColor Yellow
Write-Host "  - ESM Metrics:    http://localhost:8502" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ready to record your 5-minute Video Solution Brief!" -ForegroundColor Green
Write-Host "Press any key to open all demos in browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browsers
Start-Process "http://localhost:8000/docs"
Start-Sleep -Seconds 1
Start-Process "http://localhost:8501"
Start-Sleep -Seconds 1
Start-Process "http://localhost:8502"

Write-Host ""
Write-Host "Demos opened. Close this window when done." -ForegroundColor Cyan
Pause
