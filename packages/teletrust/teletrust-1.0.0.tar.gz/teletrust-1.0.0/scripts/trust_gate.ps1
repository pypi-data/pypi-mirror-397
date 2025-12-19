Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ========= SETTINGS =========
$RepoRoot = Resolve-Path "..\.."
# Use a valid path under the repo dist folder
$ReportRoot = Join-Path $RepoRoot "dist\trust_gate_report"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $ReportRoot "Run_$ts"
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
$Log = Join-Path $RunDir "RUNLOG.txt"
function Log([string]$s) { ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $s) | Tee-Object -FilePath $Log -Append | Out-Null }

Log "RepoRoot=$RepoRoot"
Log "RunDir=$RunDir"

# ========= PRECHECKS =========
if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    Log "WARNING: Not a git repo root, checking if parent is..."
    # Fallback to known path if relative path failed
    $RepoRoot = Resolve-Path "M:\workspace\moa_telehealth_governor"
}

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) { $git = $gitCmd.Source } else { $git = $null }

if (-not $git) { throw "git not found on PATH" }

# ========= INVENTORY =========
$Inventory = Join-Path $RunDir "inventory.txt"
Get-ChildItem -Path $RepoRoot -Force | Select-Object FullName, Mode, Length, LastWriteTime | Format-Table -Auto | Out-String | Set-Content -Path $Inventory -Encoding UTF8
Log "Wrote inventory.txt"

# ========= SECRET SCAN (HIGH SIGNAL) =========
$patterns = @(
    "sk_live_", "sk_test_", "STRIPE_SECRET", "STRIPE_API",
    "BEGIN PRIVATE KEY", "PRIVATE KEY-----",
    "AIza", "xoxb-", "xoxp-"
)

$hits = New-Object System.Collections.Generic.List[object]
# Exclude dist to avoid scanning report reports or own output
Get-ChildItem -Path $RepoRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
Where-Object {
    $_.FullName -notmatch "\\.git\\" -and
    $_.FullName -notmatch "node_modules" -and
    $_.FullName -notmatch ".venv" -and
    $_.FullName -notmatch "\\dist\\"
} |
ForEach-Object {
    $p = $_.FullName
    try {
        $c = Get-Content -Path $p -Raw -ErrorAction SilentlyContinue
        foreach ($pat in $patterns) {
            if ($c -like "*$pat*") {
                $hits.Add([pscustomobject]@{ File = $p; Pattern = $pat })
            }
        }
    }
    catch {}
}

$SecretReport = Join-Path $RunDir "secret_hits.json"
$hits | ConvertTo-Json -Depth 4 | Set-Content -Path $SecretReport -Encoding UTF8
Log ("Secret hits count = {0}" -f $hits.Count)

if ($hits.Count -gt 0) {
    Log "FAIL CLOSED: Potential secrets detected. Rotate affected keys NOW. Do not share repo or logs."
}

# ========= FLAG DANGEROUS FILES =========
$danger = @(".env", ".env.*", "id_rsa", "*.pfx", "*.p12")
$DangerReport = Join-Path $RunDir "danger_files.txt"
Get-ChildItem -Path $RepoRoot -Recurse -Force -ErrorAction SilentlyContinue |
Where-Object { $_.FullName -notmatch "\\.git\\" } |
Where-Object {
    $fname = $_.Name
    $match = $false
    foreach ($d in $danger) { if ($fname -like $d) { $match = $true; break } }
    $match
} |
Select-Object FullName | Out-String | Set-Content -Path $DangerReport -Encoding UTF8
Log "Wrote danger_files.txt"

# ========= .GITIGNORE HARDENING (SAFE APPEND) =========
$gi = Join-Path $RepoRoot ".gitignore"
if (-not (Test-Path $gi)) { "" | Set-Content -Path $gi -Encoding UTF8 }

$AppendBlock = @"
# --- TeleTrust hygiene ---
.env
.env.*
.venv/
**/.venv/
node_modules/
__pycache__/
*.pyc
dist/
build/
*.log
audit_chain.jsonl
"@

$existing = Get-Content -Path $gi -Raw -ErrorAction SilentlyContinue
if ($existing -notlike "*TeleTrust hygiene*") {
    Add-Content -Path $gi -Value "`n$AppendBlock`n" -Encoding UTF8
    Log "Appended hygiene block to .gitignore"
}
else {
    Log ".gitignore already contains hygiene block"
}

# ========= ADVICE OUTPUT =========
$Advice = Join-Path $RunDir "NEXT_ACTIONS.txt"
$AdviceText = @"
NEXT ACTIONS (in order):
1) Rotate any keys flagged by secret_hits.json.
2) Remove secrets from git history if found.
3) Commit .gitignore changes.
4) Enable GitHub secret scanning.
"@

$AdviceText | Set-Content -Path $Advice -Encoding UTF8

Log "Wrote NEXT_ACTIONS.txt"
Write-Host "Trust Gate report: $RunDir"
