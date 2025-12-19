# Clean C: Drive Hogs
Write-Host "Cleaning C: Drive..."
# 1. Windows Temp
Remove-Item -Path "$env:LOCALAPPDATA\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Package Caches (Big culprits for devs)
Remove-Item -Path "$env:LOCALAPPDATA\pip\cache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\npm-cache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.nuget\packages" -Recurse -Force -ErrorAction SilentlyContinue

# 3. VS Code / AWS Toolkits (Since logs showed errors there)
# Warning: This might reset some VS Code state, but strictly caches
Remove-Item -Path "$env:APPDATA\Code\CachedData" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\Code\User\workspaceStorage" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup Complete. Checking Space..."
Get-PSDrive C
