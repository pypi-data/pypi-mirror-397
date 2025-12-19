# Find Zombie Blobs in Ollama
$blobPath = "C:\Users\Mike\.ollama\models\blobs"
Write-Host "Scanning $blobPath for large files..."

if (Test-Path $blobPath) {
    Get-ChildItem -Path $blobPath -File | 
    Where-Object { $_.Length -gt 10GB } | 
    Select-Object Name, @{Name = "SizeGB"; Expression = { [math]::round($_.Length / 1GB, 2) } }, LastWriteTime |
    Sort-Object SizeGB -Descending
}
else {
    Write-Host "Ollama blob path not found."
}

# Also check C: Free Space clearly
$drive = Get-PSDrive C
Write-Host "C: Free Space: $([math]::round($drive.Free / 1GB, 2)) GB"
