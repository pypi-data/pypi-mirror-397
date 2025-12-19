# Setup Development Environment
# Run: .\scripts\setup_dev.ps1

Write-Host "=== MOA Telehealth Governor - Dev Setup ===" -ForegroundColor Cyan

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+" -ForegroundColor Red
    exit 1
}

Write-Host "Python: $($python.Source)" -ForegroundColor Green

# Create venv if not exists
$venvPath = ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
Write-Host "Setting up git hooks..." -ForegroundColor Yellow
if (Test-Path ".githooks") {
    git config core.hooksPath .githooks
}

# Verify installation
Write-Host "`n=== Verification ===" -ForegroundColor Cyan
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import stripe; print(f'Stripe: {stripe.VERSION}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Run: python run_demo.py" -ForegroundColor White
Write-Host "Or:  uvicorn src.billing_webhook:app --reload" -ForegroundColor White
