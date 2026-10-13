@echo off
setlocal
cd /d "%~dp0"

if not exist "runtime\node.exe" (
  echo [ERROR] Portable Node.js runtime is missing: runtime\node.exe
  pause
  exit /b 1
)

echo [1/3] Checking JavaScript syntax...
"runtime\node.exe" --check "tools\frame_tuner_lite\server.js" || goto :failed
"runtime\node.exe" --check "tools\frame_tuner_lite\store.js" || goto :failed
"runtime\node.exe" --check "tools\frame_tuner_lite\public\lite.js" || goto :failed

echo [2/3] Running built-in self-tests...
"runtime\node.exe" "tools\self_test.js" || goto :failed

echo [3/3] Validating the bundled Lite project...
"runtime\node.exe" "tools\frame_tuner_lite\validate.js" --project lite_project || goto :failed

echo.
echo All portable-package checks passed.
pause
exit /b 0

:failed
echo.
echo [ERROR] Verification failed. Keep this window open and capture the message above.
pause
exit /b 1

