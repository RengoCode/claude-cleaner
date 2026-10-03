# ==============================================================================
# Create Desktop & Start Menu Shortcuts for Claude Anti-Ban
# ==============================================================================

[CmdletBinding()]
param()

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wscript = New-Object -ComObject WScript.Shell

$desktopPath = [Environment]::GetFolderPath('Desktop')
$startMenuPath = Join-Path ([Environment]::GetFolderPath('StartMenu')) "Programs"

$targetScript = Join-Path $scriptDir "Claude-AntiBan-Reset.ps1"

# Dynamically resolve icon from user's installed Claude Desktop (if present)
$claudeExe = "$env:LOCALAPPDATA\AnthropicClaude\claude.exe"
$claudeAppIco = "$env:LOCALAPPDATA\AnthropicClaude\app.ico"

if (Test-Path $claudeExe) {
    $iconPath = $claudeExe
} elseif (Test-Path $claudeAppIco) {
    $iconPath = $claudeAppIco
} else {
    $iconPath = "shell32.dll,238" # Standard shield/security icon
}

# 1. Desktop shortcut
$shortcutDesktopPath = Join-Path $desktopPath "Claude Anti-Ban.lnk"
$scDesktop = $wscript.CreateShortcut($shortcutDesktopPath)
$scDesktop.TargetPath = "powershell.exe"
$scDesktop.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$targetScript`""
$scDesktop.WorkingDirectory = $scriptDir
$scDesktop.IconLocation = "$iconPath,0"
$scDesktop.Description = "Claude Anti-Ban & Telemetry Reset Utility"
$scDesktop.Save()

# 2. Start Menu shortcut
$shortcutStartPath = Join-Path $startMenuPath "Claude Anti-Ban.lnk"
$scStart = $wscript.CreateShortcut($shortcutStartPath)
$scStart.TargetPath = "powershell.exe"
$scStart.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$targetScript`""
$scStart.WorkingDirectory = $scriptDir
$scStart.IconLocation = "$iconPath,0"
$scStart.Description = "Claude Anti-Ban & Telemetry Reset Utility"
$scStart.Save()

Write-Host "[+] Shortcuts created successfully!" -ForegroundColor Green
Write-Host "    Desktop:    $shortcutDesktopPath" -ForegroundColor Cyan
Write-Host "    Start Menu: $shortcutStartPath" -ForegroundColor Cyan
