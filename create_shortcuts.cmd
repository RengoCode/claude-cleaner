@echo off
chcp 65001 >nul
title Install Claude Anti-Ban Shortcuts
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcuts.ps1"
echo.
pause
