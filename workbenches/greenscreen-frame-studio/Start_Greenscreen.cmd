@echo off
cd /d "%~dp0"
if not exist "runtime\node.exe" (
  echo Please download the complete portable ZIP from GitHub Release.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8791/"
"runtime\node.exe" server.js
pause
