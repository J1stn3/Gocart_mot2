@echo off
REM GoCart Web Launcher
REM This batch file runs GoCart as a web application

echo Starting GoCart Web Application...
echo.

cd /d "%~dp0"

REM Run flet with web mode using full path
C:\Users\USER\AppData\Roaming\Python\Python314\Scripts\flet.exe run -w web_main.py

pause