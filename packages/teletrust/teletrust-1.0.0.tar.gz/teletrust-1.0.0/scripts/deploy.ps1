# Deploy MOA Telehealth Governor to Fly.io
# Prerequisites: fly CLI installed, authenticated

param(
    [switch]$Production,
    [switch]$Staging
)

$ErrorActionPreference = "Stop"

Write-Host "=== MOA Telehealth Governor Deployment ===" -ForegroundColor Cyan

# Check fly CLI
if (-not (Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Fly CLI not found. Install: irm https://fly.io/install.ps1 | iex" -ForegroundColor Red
    exit 1
}

# Set app name based on environment
$appName = if ($Production) { "moa-telehealth-governor" } else { "moa-telehealth-governor-staging" }

Write-Host "Deploying to: $appName" -ForegroundColor Yellow

# Check if app exists, create if not
$apps = fly apps list --json | ConvertFrom-Json
$appExists = $apps | Where-Object { $_.Name -eq $appName }

if (-not $appExists) {
    Write-Host "Creating new app: $appName" -ForegroundColor Yellow
    fly apps create $appName --org personal
}

# Set secrets (if not already set)
Write-Host "Checking secrets..." -ForegroundColor Yellow
$secrets = fly secrets list -a $appName 2>&1

if ($secrets -notmatch "STRIPE_SECRET_KEY") {
    Write-Host "WARNING: STRIPE_SECRET_KEY not set. Run:" -ForegroundColor Yellow
    Write-Host "  fly secrets set STRIPE_SECRET_KEY=sk_live_... -a $appName" -ForegroundColor White
}

if ($secrets -notmatch "HMAC_SECRET_KEY") {
    Write-Host "Generating HMAC secret..." -ForegroundColor Yellow
    $hmacKey = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    fly secrets set HMAC_SECRET_KEY=$hmacKey -a $appName
}

# Deploy
Write-Host "Deploying..." -ForegroundColor Green
fly deploy -a $appName

# Health check
Write-Host "Checking health..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$healthUrl = "https://$appName.fly.dev/health"
try {
    $response = Invoke-RestMethod -Uri $healthUrl -Method Get
    Write-Host "Health check passed: $($response | ConvertTo-Json)" -ForegroundColor Green
}
catch {
    Write-Host "Health check failed - may need more time to start" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host "API URL: https://$appName.fly.dev" -ForegroundColor Cyan
Write-Host "Health: https://$appName.fly.dev/health" -ForegroundColor Cyan
Write-Host "Govern: POST https://$appName.fly.dev/govern" -ForegroundColor Cyan
