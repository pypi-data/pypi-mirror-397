# Emergency Cleanup Script
Remove-Item -Path "M:\Archived-Downloads\WHAT_extracted" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "M:\Archived-Downloads\fix1218_extracted" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cleanup finished."
