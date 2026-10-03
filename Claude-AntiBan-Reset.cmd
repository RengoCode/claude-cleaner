@echo off
chcp 65001 >nul
title Claude Anti-Ban ^& Telemetry Reset
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Claude-AntiBan-Reset.ps1" %*
