# GoCart Web Launcher
# This script runs GoCart as a web application

Write-Host "Starting GoCart Web Application..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Run flet with web mode using full path
& "C:\Users\USER\AppData\Roaming\Python\Python314\Scripts\flet.exe" run -w web_main.py