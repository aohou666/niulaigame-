@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0local_game\start-local-game.ps1" -Mode admin
if errorlevel 1 pause
