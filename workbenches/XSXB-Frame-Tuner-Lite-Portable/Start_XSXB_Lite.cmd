@echo off
setlocal
cd /d "%~dp0"

if not exist "runtime\node.exe" (
  echo [ERROR] Portable Node.js runtime is missing: runtime\node.exe
  pause
  exit /b 1
)

set "LITE_PORT=5180"
start "" "http://127.0.0.1:%LITE_PORT%/"
echo XSXB Frame Tuner Lite is starting at http://127.0.0.1:%LITE_PORT%/
echo Keep this window open while using the editor. Press Ctrl+C to stop it.
echo.
"runtime\node.exe" "tools\frame_tuner_lite\server.js"

if errorlevel 1 (
  echo.
  echo [ERROR] The Lite service stopped unexpectedly. Port 5180 may already be in use.
  pause
)

