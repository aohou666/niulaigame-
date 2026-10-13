@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0local_game\start-local-game.ps1" -Desktop -Mode main
if errorlevel 1 pause
