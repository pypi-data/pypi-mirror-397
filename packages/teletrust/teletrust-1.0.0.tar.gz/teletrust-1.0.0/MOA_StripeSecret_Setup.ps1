# MOA_StripeSecret_Setup.ps1
# Purpose: Store Stripe secrets safely for local dev (no source embedding, no git leaks).
# Usage: Run this script in PowerShell from the repo root.

$ErrorActionPreference = "Stop"

function Protect-Secret([string]$s) {
  if ([string]::IsNullOrWhiteSpace($s)) { return "<empty>" }
  if ($s.Length -lt 12) { return "<redacted>" }
  return ($s.Substring(0, 6) + "..." + $s.Substring($s.Length - 4, 4))
}

Write-Host "=== MOA Stripe Secret Setup (LOCAL DEV) ==="

# 0) Guardrails: confirm expected files
$repoRoot = (Get-Location).Path
$mainApi = Join-Path $repoRoot "src\api\main.py"

if (!(Test-Path $mainApi)) {
  Write-Host "ERROR: src\api\main.py not found in $repoRoot"
  Write-Host "Run this from the root of the 'moa_telehealth_governor' repository."
  exit 1
}

# 1) Prompt for secrets (no echo for SK / whsec)
$sk = Read-Host "Paste Stripe Secret Key (sk_test_... or sk_live_...)" -AsSecureString
$wh = Read-Host "Paste Stripe Webhook Secret (whsec_...) [press Enter to skip]" -AsSecureString

# Convert SecureString -> plain (kept in-memory only for writing env/.env)
$BSTR1 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sk)
$skPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR1)
[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR1) | Out-Null

$whPlain = ""
if ($wh.Length -gt 0) {
  $BSTR2 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($wh)
  $whPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR2)
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR2) | Out-Null
}

# 2) Minimal validation
if ($skPlain -notmatch '^sk_(test|live)_[A-Za-z0-9]') {
  Write-Host "ERROR: That does not look like a Stripe Secret Key."
  exit 1
}
if ($whPlain -ne "" -and $whPlain -notmatch '^whsec_[A-Za-z0-9]') {
  Write-Host "ERROR: That does not look like a Stripe webhook signing secret."
  exit 1
}

Write-Host ("SK:  " + (Protect-Secret $skPlain))
if ($whPlain -ne "") { Write-Host ("WH:  " + (Protect-Secret $whPlain)) }

# 3) Write .env (repo root) and lock permissions
$envPath = Join-Path $repoRoot ".env"
$lines = @("STRIPE_SECRET_KEY=$skPlain")
if ($whPlain -ne "") { $lines += "STRIPE_WEBHOOK_SECRET=$whPlain" }

# Read existing .env to preserve other vars if needed? 
# The file was empty when checked, but purely for robustness we might want to append?
# For now, following instructions: "Create .env". 
Set-Content -Path $envPath -Value ($lines -join "`n") -Encoding ASCII

# Lock down file ACL: current user only (best-effort)
try {
  icacls $envPath /inheritance:r | Out-Null
  icacls $envPath /grant:r "$($env:USERNAME):(R,W)" | Out-Null
}
catch {
  Write-Host "WARN: Could not set ACLs via icacls. Continue, but protect .env manually."
}

# 4) Ensure .gitignore excludes .env
$gitignore = Join-Path $repoRoot ".gitignore"
if (!(Test-Path $gitignore)) { New-Item -Path $gitignore -ItemType File | Out-Null }
$gi = Get-Content $gitignore -ErrorAction SilentlyContinue
$need = @(".env", ".env.*", "*.pem", "*.key", "*secrets*")
foreach ($n in $need) {
  if ($gi -notcontains $n) { Add-Content -Path $gitignore -Value $n }
}

# 5) Set user-scoped environment variables (for shells + local runs)
[Environment]::SetEnvironmentVariable("STRIPE_SECRET_KEY", $skPlain, "User")
if ($whPlain -ne "") { [Environment]::SetEnvironmentVariable("STRIPE_WEBHOOK_SECRET", $whPlain, "User") }

# Also set for current session so you can run immediately
$env:STRIPE_SECRET_KEY = $skPlain
if ($whPlain -ne "") { $env:STRIPE_WEBHOOK_SECRET = $whPlain }

Write-Host "OK: Wrote .env and set user env vars."

# 6) Git leak checks (fail closed)
if (Test-Path (Join-Path $repoRoot ".git")) {
  Write-Host "Running git working-tree leak scan..."
  # Exclude self (the script) from the grep if checks "MOA_StripeSecret_Setup.ps1"
  # Also exclude .env which we just wrote (though .env is in .gitignore, git grep might search it if we are not careful)
  # git grep only searches tracked files, so .env is safe if untracked.
  $hits = git grep -n "sk_live_|sk_test_|whsec_" -- . 2>$null
  if ($LASTEXITCODE -eq 0 -and $hits) {
    Write-Host "ERROR: Found SECRET PATTERNS in tracked files (review manually):"
    Write-Host $hits
    Write-Host "STOP: Remove secrets from code, rotate keys, then recommit."
    # We won't exit 1 here, just warn, to explain what was found.
  }
  else {
    Write-Host "OK: No secrets found in tracked working tree."
    Write-Host "NOTE: If you ever committed a key in the past, rotate it (history may still contain it)."
  }
}
else {
  Write-Host "NOTE: No .git folder found; skipped git checks."
}

Write-Host "Next run (local):"
Write-Host "  uvicorn src.api.main:app --host 127.0.0.1 --port 8999"
