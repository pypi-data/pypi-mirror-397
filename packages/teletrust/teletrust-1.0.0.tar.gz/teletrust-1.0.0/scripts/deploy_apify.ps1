# scripts/deploy_apify.ps1
# Deploys the MCP Regulatory Gateway to Apify

$ActorDir = "mcp-gateway-v2"

if (-not (Test-Path $ActorDir)) {
    Write-Error "Directory '$ActorDir' not found via $(Get-Location)"
    exit 1
}

# Check for CLI
if (-not (Get-Command "apify" -ErrorAction SilentlyContinue)) {
    Write-Warning "Apify CLI not found. Installing via NPM..."
    npm install -g apify-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install apify-cli."
        exit 1
    }
}

# Check login status (naive verify)
# We assume user is logged in or has APIFY_TOKEN env var.
# If not, 'apify push' will prompt or fail.

Write-Host ">>> Deploying Apify Actor from $ActorDir..."
Push-Location $ActorDir
try {
    npx apify push
}
finally {
    Pop-Location
}
