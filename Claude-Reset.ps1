# ==============================================================================
# Claude Anti-Ban & Telemetry Cleaner
# Universal native PowerShell reset & privacy utility for Windows (0 dependencies)
# Bilingual support: English & Russian
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$Auto,
    [switch]$WipeSessions,
    [switch]$LaunchAfter,
    [switch]$DryRun,
    [switch]$CreateShortcuts,
    [ValidateSet("en", "ru")][string]$Lang
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) { $scriptDir = Join-Path $HOME ".claude-cleaner" }
$backupRootDir = Join-Path $scriptDir "backups"
if (-not (Test-Path $backupRootDir)) {
    New-Item -ItemType Directory -Path $backupRootDir -Force | Out-Null
}

$cleanerConfigDir = Join-Path $HOME ".claude-cleaner"
if (-not (Test-Path $cleanerConfigDir)) {
    New-Item -ItemType Directory -Path $cleanerConfigDir -Force | Out-Null
}
$langConfigFile = Join-Path $cleanerConfigDir "language.txt"

# Resolve language: Param > Saved Config > System UI Culture
if ($Lang) {
    $script:ActiveLang = $Lang
    try { Set-Content -Path $langConfigFile -Value $Lang -Encoding UTF8 -Force } catch {}
} elseif (Test-Path $langConfigFile) {
    $savedLang = (Get-Content $langConfigFile -Raw).Trim().ToLower()
    if ($savedLang -eq "ru" -or $savedLang -eq "en") {
        $script:ActiveLang = $savedLang
    } else {
        $script:ActiveLang = if ([System.Globalization.CultureInfo]::CurrentUICulture.TwoLetterISOLanguageName -eq "ru") { "ru" } else { "en" }
    }
} else {
    $script:ActiveLang = if ([System.Globalization.CultureInfo]::CurrentUICulture.TwoLetterISOLanguageName -eq "ru") { "ru" } else { "en" }
}

# --- Multilingual Strings (RU / EN) ---
$script:I18N = @{
    "ru" = @{
        "Title" = "CLAUDE ANTI-BAN & СБРОС ИДЕНТИФИКАТОРОВ УСТРОЙСТВА"
        "Sub" = "Сброс ID железа, глубокой телеметрии и защита от привязки аккаунтов"
        "MenuHeader" = "Выберите действие:"
        "Menu1" = "[1] 🚀 Безопасный Anti-Ban сброс (сброс ID железа и телеметрии, СЕССИИ СОХРАНЯЮТСЯ)"
        "Menu2" = "[2] 🔍 Посмотреть текущие идентификаторы устройства"
        "Menu3" = "[3] 💻 Глубокий аудит отпечатка системы и железа"
        "Menu4" = "[4] 🛡️ Создать только резервную копию файлов"
        "Menu5" = "[5] 🔄 Восстановить из резервной копии"
        "Menu6" = "[6] ⚠️ Полный Factory Reset (сброс ID + удаление всех локальных сессий)"
        "MenuShortcuts" = "[S] 📌 Создать ярлыки на Рабочем столе и в Пуск"
        "Menu7" = "[7] 📁 Открыть папку с резервными копиями"
        "Menu8" = "[8] ▶️ Запустить Claude Desktop"
        "MenuLang" = "[L] 🌐 Switch Language / Сменить язык (EN / RU)"
        "Menu0" = "[0] ❌ Выход"
        "Prompt" = "Введите номер действия [1-8, S, L, 0]: "
        "ConfirmSafe" = "Будут сброшены идентификаторы устройства и телеметрия.`nСессии и диалоги БУДУТ СОХРАНЕНЫ.`nПродолжить? (Y/N): "
        "ConfirmFullWarn" = "ВНИМАНИЕ: Будут удалены все локальные сессии Claude Code!"
        "ConfirmFullPrompt" = "Для подтверждения полного сброса введите 'YES': "
        "Cancelled" = "Отменено пользователем."
        "PressEnter" = "Нажмите Enter для продолжения..."
        "ProcTerminated" = "Проверены и завершены активные процессы Claude."
        "Step1" = "[1/6] Создание защитной резервной копии..."
        "Step2" = "[2/6] Сброс аппаратных ID и телеметрии Claude CLI..."
        "Step3" = "[3/6] Сброс привязок десктопного приложения Claude..."
        "Step4" = "[4/6] Очистка config.json и телеметрии сессий..."
        "Step5" = "[5/6] Очистка истории использования тарифа и системных метрик..."
        "Step6" = "[6/6] Проверка сохранности файлов сессий и очистка логов..."
        "Completed" = "СБРОС И ОЧИСТКА УСПЕШНО ЗАВЕРШЕНЫ!"
        "CompletedDesc" = "Все метаданные, связывающие устройство с прежними учетками, сброшены."
        "BackupSaved" = "Резервная копия сохранена в:"
        "LaunchPrompt" = "Желаете запустить Claude Desktop сейчас? (Y/N): "
        "DryRunNotice" = "[ТЕСТОВЫЙ РЕЖИМ] Изменения не будут записаны на диск."
        "ShortcutsCreated" = "Ярлыки успешно созданы на Рабочем столе и в меню «Пуск»."
    }
    "en" = @{
        "Title" = "CLAUDE ANTI-BAN & DEVICE ID RESET UTILITY"
        "Sub" = "Reset Hardware IDs, Deep Telemetry & Account Linkages"
        "MenuHeader" = "Select an action:"
        "Menu1" = "[1] 🚀 Safe Anti-Ban Reset (Reset device IDs & deep telemetry, KEEP sessions)"
        "Menu2" = "[2] 🔍 View Current Identifiers & Telemetry Status"
        "Menu3" = "[3] 💻 Deep Hardware & Fingerprint Audit"
        "Menu4" = "[4] 🛡️ Create Safety Backup ZIP Now"
        "Menu5" = "[5] 🔄 Restore From Backup"
        "Menu6" = "[6] ⚠️ Full Factory Reset (Reset IDs + Wipe All Sessions)"
        "MenuShortcuts" = "[S] 📌 Create Desktop & Start Menu Shortcuts"
        "Menu7" = "[7] 📁 Open Backups Directory"
        "Menu8" = "[8] ▶️ Launch Claude Desktop"
        "MenuLang" = "[L] 🌐 Switch Language / Сменить язык (EN / RU)"
        "Menu0" = "[0] ❌ Exit"
        "Prompt" = "Enter option [1-8, S, L, 0]: "
        "ConfirmSafe" = "Hardware identifiers and deep telemetry will be reset.`nSessions and chats WILL BE PRESERVED.`nProceed? (Y/N): "
        "ConfirmFullWarn" = "WARNING: All local Claude Code sessions and chat turns will be deleted!"
        "ConfirmFullPrompt" = "Type 'YES' to confirm full factory reset: "
        "Cancelled" = "Operation cancelled."
        "PressEnter" = "Press Enter to continue..."
        "ProcTerminated" = "Checked and terminated any running Claude processes."
        "Step1" = "[1/6] Creating safety backup..."
        "Step2" = "[2/6] Resetting CLI hardware IDs & telemetry..."
        "Step3" = "[3/6] Resetting Desktop application device binding..."
        "Step4" = "[4/6] Sanitizing config.json & session telemetry..."
        "Step5" = "[5/6] Sanitizing plan usage history & system metrics..."
        "Step6" = "[6/6] Verifying session preservation & clearing logs..."
        "Completed" = "ANTI-BAN & TELEMETRY RESET COMPLETED SUCCESSFULLY!"
        "CompletedDesc" = "All metadata linking this machine to previous accounts has been severed."
        "BackupSaved" = "Safety backup saved at:"
        "LaunchPrompt" = "Would you like to launch Claude Desktop now? (Y/N): "
        "DryRunNotice" = "[DRY-RUN MODE] No changes will be written to disk."
        "ShortcutsCreated" = "Shortcuts successfully created on Desktop and Start Menu."
    }
}

function Get-Msg([string]$key) {
    $lang = $script:ActiveLang
    if ($script:I18N[$lang] -and $script:I18N[$lang][$key]) {
        return $script:I18N[$lang][$key]
    }
    return $script:I18N["en"][$key]
}

# Пути к файлам Claude CLI
$cliDir = Join-Path $HOME ".claude"
$cliConfigPath1 = Join-Path $HOME ".claude.json"
$cliConfigPath2 = Join-Path $cliDir ".claude.json"
$cliTelemetryDir = Join-Path $cliDir "telemetry"
$cliStatsCache = Join-Path $cliDir "stats-cache.json"
$cliDaemonStatus = Join-Path $cliDir "daemon-auth-status.json"
$cliDaemonCooldown = Join-Path $cliDir "daemon-auth-cooldown"

# Пути к файлам Claude Desktop (Windows AppData)
$appDataClaude = Join-Path $env:APPDATA "Claude"
$desktopAntDid = Join-Path $appDataClaude "ant-did"
$desktopAntRegistry = Join-Path $appDataClaude "ant-device-registry.json"
$desktopConfig = Join-Path $appDataClaude "config.json"
$desktopLocalState = Join-Path $appDataClaude "Local State"
$desktopPlanUsage = Join-Path $appDataClaude "plan-usage-history.json"
$desktopPerfDb = Join-Path $appDataClaude "declarative_performance_observer.db"
$desktopPerfJournal = Join-Path $appDataClaude "declarative_performance_observer.db-journal"
$desktopCrashpad = Join-Path $appDataClaude "Crashpad"
$desktopCcdIds = Join-Path $appDataClaude "ccd-ids.json"
$desktopBridgeState = Join-Path $appDataClaude "bridge-state.json"
$desktopRemoteControl = Join-Path $appDataClaude "remote-control-state.json"
$desktopBuddyTokens = Join-Path $appDataClaude "buddy-tokens.json"
$desktopSessionsDir = Join-Path $appDataClaude "claude-code-sessions"
$desktopSentryDir = Join-Path $appDataClaude "sentry"
$desktopLogsDir = Join-Path $appDataClaude "logs"
$claudeExePath = "$env:LOCALAPPDATA\AnthropicClaude\claude.exe"

$script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Write-Header {
    try { [System.Console]::Clear() } catch {}
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "            $(Get-Msg 'Title')                " -ForegroundColor Yellow
    Write-Host "      $(Get-Msg 'Sub')   " -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Set-SafeFileContent {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Content
    )
    if ($DryRun) { return }
    for ($attempt = 1; $attempt -le 4; $attempt++) {
        try {
            [System.IO.File]::WriteAllText($Path, $Content, $script:Utf8NoBom)
            return
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    [System.IO.File]::WriteAllText($Path, $Content, $script:Utf8NoBom)
}

function Get-RandomSha256Hex {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    return (-join ($bytes | ForEach-Object { "{0:x2}" -f $_ }))
}

function Stop-ClaudeProcesses {
    $procNames = @("claude", "AnthropicClaude")
    $killed = $false
    foreach ($p in $procNames) {
        $found = Get-Process -Name $p -ErrorAction SilentlyContinue
        if ($found) {
            $found | Stop-Process -Force -ErrorAction SilentlyContinue
            $killed = $true
        }
    }
    if ($killed) {
        Start-Sleep -Seconds 1
    }
    Write-Host "[+] $(Get-Msg 'ProcTerminated')" -ForegroundColor Green
}

function Install-Shortcuts {
    $desktopPath = [Environment]::GetFolderPath('Desktop')
    $startMenuPath = Join-Path ([Environment]::GetFolderPath('StartMenu')) "Programs"
    $wscript = New-Object -ComObject WScript.Shell

    $claudeExe = "$env:LOCALAPPDATA\AnthropicClaude\claude.exe"
    $claudeAppIco = "$env:LOCALAPPDATA\AnthropicClaude\app.ico"
    $iconPath = if (Test-Path $claudeExe) { $claudeExe } elseif (Test-Path $claudeAppIco) { $claudeAppIco } else { "shell32.dll,238" }

    $targetCmd = Join-Path $scriptDir "Claude-Reset.cmd"
    if (-not (Test-Path $targetCmd)) {
        $targetCmd = Join-Path $scriptDir "Claude-Reset.ps1"
    }

    # 1. Desktop
    $scDesktop = $wscript.CreateShortcut((Join-Path $desktopPath "Claude Reset.lnk"))
    $scDesktop.TargetPath = $targetCmd
    $scDesktop.WorkingDirectory = $scriptDir
    $scDesktop.IconLocation = "$iconPath,0"
    $scDesktop.Description = "Claude Anti-Ban & Telemetry Reset Utility"
    $scDesktop.Save()

    # 2. Start Menu
    $scStart = $wscript.CreateShortcut((Join-Path $startMenuPath "Claude Reset.lnk"))
    $scStart.TargetPath = $targetCmd
    $scStart.WorkingDirectory = $scriptDir
    $scStart.IconLocation = "$iconPath,0"
    $scStart.Description = "Claude Anti-Ban & Telemetry Reset Utility"
    $scStart.Save()

    Write-Host "`n[+] $(Get-Msg 'ShortcutsCreated')" -ForegroundColor Green
    Write-Host "    Desktop:    $desktopPath\Claude Reset.lnk" -ForegroundColor Cyan
    Write-Host "    Start Menu: $startMenuPath\Claude Reset.lnk`n" -ForegroundColor Cyan
}

function New-ClaudeBackup {
    param([string]$Tag = "backup")

    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupFolderName = "backup_${timestamp}_${Tag}"
    $targetDir = Join-Path $backupRootDir $backupFolderName
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    # CLI
    if (Test-Path $cliConfigPath1) {
        Copy-Item -Path $cliConfigPath1 -Destination (Join-Path $targetDir "user_claude.json") -Force
    }
    if (Test-Path $cliConfigPath2) {
        Copy-Item -Path $cliConfigPath2 -Destination (Join-Path $targetDir "nested_claude.json") -Force
    }
    if (Test-Path $cliStatsCache) {
        Copy-Item -Path $cliStatsCache -Destination (Join-Path $targetDir "cli_stats_cache.json") -Force
    }

    # Desktop
    if (Test-Path $appDataClaude) {
        $destDesktopDir = Join-Path $targetDir "Claude_AppData"
        New-Item -ItemType Directory -Path $destDesktopDir -Force | Out-Null

        $filesToCopy = @(
            $desktopAntDid,
            $desktopAntRegistry,
            $desktopConfig,
            $desktopLocalState,
            $desktopPlanUsage,
            $desktopCcdIds,
            $desktopBridgeState,
            $desktopRemoteControl,
            $desktopBuddyTokens
        )
        foreach ($f in $filesToCopy) {
            if (Test-Path $f) {
                Copy-Item -Path $f -Destination $destDesktopDir -Force
            }
        }

        # Backup sessions
        if (Test-Path $desktopSessionsDir) {
            $destSessions = Join-Path $destDesktopDir "claude-code-sessions"
            Copy-Item -Path $desktopSessionsDir -Destination $destSessions -Recurse -Force
        }
    }

    Write-Host "[+] $(Get-Msg 'BackupSaved') $targetDir" -ForegroundColor Green
    return $targetDir
}

function Restore-ClaudeBackup {
    Write-Header
    $backups = Get-ChildItem -Path $backupRootDir -Directory | Sort-Object CreationTime -Descending

    if (-not $backups -or $backups.Count -eq 0) {
        Write-Host "[-] No backups found in $backupRootDir" -ForegroundColor Red
        Pause
        return
    }

    Write-Host "Available backups / Доступные резервные копии:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $backups.Count; $i++) {
        Write-Host "  [$($i + 1)] $($backups[$i].Name) ($($backups[$i].CreationTime.ToString('dd.MM.yyyy HH:mm:ss')))" -ForegroundColor White
    }
    Write-Host "  [0] Cancel / Отмена`n" -ForegroundColor DarkGray

    $choice = Read-Host "Select backup number / Выберите номер для восстановления"
    if ($choice -eq "0" -or [string]::IsNullOrWhiteSpace($choice)) { return }

    $idx = [int]$choice - 1
    if ($idx -lt 0 -or $idx -ge $backups.Count) {
        Write-Host "[-] Invalid choice." -ForegroundColor Red
        Pause
        return
    }

    $selectedBackup = $backups[$idx].FullName
    Stop-ClaudeProcesses

    Write-Host "[*] Restoring from $selectedBackup..." -ForegroundColor Yellow

    # CLI configs
    $bUserClaude = Join-Path $selectedBackup "user_claude.json"
    if (Test-Path $bUserClaude) {
        Copy-Item -Path $bUserClaude -Destination $cliConfigPath1 -Force
        Write-Host "  [v] Restored: ~/.claude.json" -ForegroundColor Green
    }
    $bNestedClaude = Join-Path $selectedBackup "nested_claude.json"
    if (Test-Path $bNestedClaude) {
        Copy-Item -Path $bNestedClaude -Destination $cliConfigPath2 -Force
        Write-Host "  [v] Restored: ~/.claude/.claude.json" -ForegroundColor Green
    }
    $bStats = Join-Path $selectedBackup "cli_stats_cache.json"
    if (Test-Path $bStats) {
        Copy-Item -Path $bStats -Destination $cliStatsCache -Force
        Write-Host "  [v] Restored: ~/.claude/stats-cache.json" -ForegroundColor Green
    }

    # Desktop files
    $bDesktop = Join-Path $selectedBackup "Claude_AppData"
    if (Test-Path $bDesktop) {
        Get-ChildItem -Path $bDesktop -File | ForEach-Object {
            $dest = Join-Path $appDataClaude $_.Name
            Copy-Item -Path $_.FullName -Destination $dest -Force
            Write-Host "  [v] Restored: AppData\Claude\$($_.Name)" -ForegroundColor Green
        }
        $bSess = Join-Path $bDesktop "claude-code-sessions"
        if (Test-Path $bSess) {
            if (-not (Test-Path $desktopSessionsDir)) { New-Item -ItemType Directory -Path $desktopSessionsDir -Force | Out-Null }
            Get-ChildItem -Path $bSess | Copy-Item -Destination $desktopSessionsDir -Recurse -Force
            Write-Host "  [v] Restored session folder: claude-code-sessions" -ForegroundColor Green
        }
    }

    Write-Host "`n[+] Restoration completed successfully!`n" -ForegroundColor Green
    Pause
}

function Perform-Reset {
    Write-Header
    if ($DryRun) {
        Write-Host "$(Get-Msg 'DryRunNotice')`n" -ForegroundColor Yellow
    }

    # 1. Terminate running processes
    if (-not $DryRun) {
        Stop-ClaudeProcesses
    }

    # 2. Automated backup
    Write-Host (Get-Msg 'Step1') -ForegroundColor Cyan
    $backupPath = $null
    if (-not $DryRun) {
        $backupPath = New-ClaudeBackup -Tag "pre-reset"
    }

    # 3. CLI ~/.claude.json
    Write-Host (Get-Msg 'Step2') -ForegroundColor Cyan
    if (Test-Path $cliConfigPath1) {
        try {
            $content = [System.IO.File]::ReadAllText($cliConfigPath1, [System.Text.Encoding]::UTF8)
            $newMachineId1 = Get-RandomSha256Hex
            $newUserId1 = Get-RandomSha256Hex
            $newAnonId = "claudecode_" + (Get-RandomSha256Hex).Substring(0, 32)

            $content = [regex]::Replace($content, '("machineID"\s*:\s*)"[^"]+"', ('$1"' + $newMachineId1 + '"'))
            $content = [regex]::Replace($content, '("userID"\s*:\s*)"[^"]+"', ('$1"' + $newUserId1 + '"'))
            if ($content -match '"anonymousId"') {
                $content = [regex]::Replace($content, '("anonymousId"\s*:\s*)"[^"]+"', ('$1"' + $newAnonId + '"'))
            }

            Set-SafeFileContent -Path $cliConfigPath1 -Content $content
            Write-Host "  [v] New CLI machineID: $newMachineId1" -ForegroundColor Green
            Write-Host "  [v] New CLI userID:    $newUserId1" -ForegroundColor Green
        } catch {
            Write-Host "  [-] Error updating ~/.claude.json: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # 4. Nested ~/.claude/.claude.json
    if (Test-Path $cliConfigPath2) {
        try {
            $content = [System.IO.File]::ReadAllText($cliConfigPath2, [System.Text.Encoding]::UTF8)
            $newMachineId2 = Get-RandomSha256Hex
            $newUserId2 = Get-RandomSha256Hex

            $content = [regex]::Replace($content, '("machineID"\s*:\s*)"[^"]+"', ('$1"' + $newMachineId2 + '"'))
            $content = [regex]::Replace($content, '("userID"\s*:\s*)"[^"]+"', ('$1"' + $newUserId2 + '"'))

            Set-SafeFileContent -Path $cliConfigPath2 -Content $content
            Write-Host "  [v] New Nested CLI machineID: $newMachineId2" -ForegroundColor Green
            Write-Host "  [v] New Nested CLI userID:    $newUserId2" -ForegroundColor Green
        } catch {
            Write-Host "  [-] Error updating nested config: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Clear CLI telemetry event queue & stats
    if ((Test-Path $cliTelemetryDir) -and (-not $DryRun)) {
        $events = Get-ChildItem -Path $cliTelemetryDir -Filter "1p_failed_events.*.json" -ErrorAction SilentlyContinue
        if ($events) {
            $events | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Cleared CLI telemetry event queue ($($events.Count) files)." -ForegroundColor Green
        }
    }
    if ((Test-Path $cliStatsCache) -and (-not $DryRun)) {
        try {
            Set-SafeFileContent -Path $cliStatsCache -Content '{"version":4,"dailyActivity":[]}'
            Write-Host "  [v] Cleared CLI stats-cache.json." -ForegroundColor Green
        } catch {}
    }
    foreach ($df in @($cliDaemonStatus, $cliDaemonCooldown)) {
        if ((Test-Path $df) -and (-not $DryRun)) {
            Remove-Item -Path $df -Force -ErrorAction SilentlyContinue
        }
    }

    # 5. Desktop Application (%APPDATA%\Claude)
    Write-Host (Get-Msg 'Step3') -ForegroundColor Cyan
    if (Test-Path $appDataClaude) {
        if ((Test-Path $desktopAntDid) -and (-not $DryRun)) {
            Remove-Item -Path $desktopAntDid -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Removed ant-did (Claude Desktop will generate a fresh clean ID on start)." -ForegroundColor Green
        }

        if ((Test-Path $desktopAntRegistry) -and (-not $DryRun)) {
            Remove-Item -Path $desktopAntRegistry -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Removed ant-device-registry.json (hardware-to-account bindings severed)." -ForegroundColor Green
        }

        if ((Test-Path $desktopRemoteControl) -and (-not $DryRun)) {
            Remove-Item -Path $desktopRemoteControl -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Removed remote-control-state.json." -ForegroundColor Green
        }

        if (Test-Path $desktopCcdIds) {
            try {
                $newCcdSalt = [System.Guid]::NewGuid().ToString()
                $ccdJson = "{`"salt`":`"$newCcdSalt`"}"
                Set-SafeFileContent -Path $desktopCcdIds -Content $ccdJson
                Write-Host "  [v] Generated new ccd-ids.json salt: $newCcdSalt" -ForegroundColor Green
            } catch {}
        }

        foreach ($bf in @($desktopBridgeState, $desktopBuddyTokens)) {
            if ((Test-Path $bf) -and (-not $DryRun)) {
                Remove-Item -Path $bf -Force -ErrorAction SilentlyContinue
                Write-Host "  [v] Cleared $($bf | Split-Path -Leaf)." -ForegroundColor Green
            }
        }
    }

    # 6. Sanitize config.json
    Write-Host (Get-Msg 'Step4') -ForegroundColor Cyan
    if (Test-Path $desktopConfig) {
        try {
            $configRaw = [System.IO.File]::ReadAllText($desktopConfig, [System.Text.Encoding]::UTF8)
            $cfg = $configRaw | ConvertFrom-Json

            $propsToRemove = @(
                "lastKnownAccountUuid",
                "oauth:tokenCache",
                "oauth:tokenCacheV2",
                "chromeExtension.pairedDeviceId",
                "hasTrackedInitialActivation"
            )
            $dxtProps = @($cfg.psobject.properties | Where-Object { $_.Name -like "dxt:allowlist*" } | Select-Object -ExpandProperty Name)
            $propsToRemove += $dxtProps

            foreach ($prop in $propsToRemove) {
                if ($cfg.psobject.properties[$prop]) {
                    $cfg.psobject.properties.Remove($prop)
                }
            }

            $currentEpochMs = [long]([datetimeoffset]::UtcNow.ToUnixTimeMilliseconds())
            if ($cfg.psobject.properties["first_launch_at"]) {
                $cfg.first_launch_at = $currentEpochMs
            }
            if ($cfg.psobject.properties["version_first_launch"] -and $cfg.version_first_launch.psobject.properties["at"]) {
                $cfg.version_first_launch.at = $currentEpochMs
            }

            $updatedJson = $cfg | ConvertTo-Json -Depth 100
            Set-SafeFileContent -Path $desktopConfig -Content $updatedJson
            Write-Host "  [v] Sanitized config.json: removed stale tokens, machine UUID, and first launch flags." -ForegroundColor Green
        } catch {
            Write-Host "  [-] Error updating config.json: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # 7. Deep telemetry: plan-usage-history, Local State, Crashpad
    Write-Host (Get-Msg 'Step5') -ForegroundColor Cyan
    if ((Test-Path $desktopPlanUsage) -and (-not $DryRun)) {
        try {
            Set-SafeFileContent -Path $desktopPlanUsage -Content '{"history":[]}'
            Write-Host "  [v] Sanitized plan-usage-history.json (purged historical Org UUID tracking)." -ForegroundColor Green
        } catch {}
    }

    if ((Test-Path $desktopLocalState) -and (-not $DryRun)) {
        try {
            $lsContent = [System.IO.File]::ReadAllText($desktopLocalState, [System.Text.Encoding]::UTF8)
            $lsJson = $lsContent | ConvertFrom-Json
            if ($lsJson.psobject.properties["uninstall_metrics"]) {
                $currentUnixSec = [long]([datetimeoffset]::UtcNow.ToUnixTimeSeconds())
                $lsJson.uninstall_metrics.installation_date2 = "$currentUnixSec"
                Set-SafeFileContent -Path $desktopLocalState -Content ($lsJson | ConvertTo-Json -Depth 20)
                Write-Host "  [v] Reset installation_date2 in Local State to current time." -ForegroundColor Green
            }
        } catch {}
    }

    foreach ($dbF in @($desktopPerfDb, $desktopPerfJournal)) {
        if ((Test-Path $dbF) -and (-not $DryRun)) {
            Remove-Item -Path $dbF -Force -ErrorAction SilentlyContinue
        }
    }

    if ((Test-Path $desktopCrashpad) -and (-not $DryRun)) {
        $dumps = Get-ChildItem -Path $desktopCrashpad -Recurse -Filter "*.dmp" -ErrorAction SilentlyContinue
        if ($dumps) {
            $dumps | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Purged Crashpad minidumps." -ForegroundColor Green
        }
    }

    # 8. Sessions handling & logs
    Write-Host (Get-Msg 'Step6') -ForegroundColor Cyan
    if ($WipeSessions) {
        if ((Test-Path $desktopSessionsDir) -and (-not $DryRun)) {
            $sessDirs = Get-ChildItem -Path $desktopSessionsDir -Directory -ErrorAction SilentlyContinue
            if ($sessDirs) {
                $sessDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  [!] Factory Reset: Deleted local claude-code-sessions ($($sessDirs.Count) accounts)." -ForegroundColor Yellow
            }
        }
    } else {
        if (Test-Path $desktopSessionsDir) {
            $sessionFiles = Get-ChildItem -Path $desktopSessionsDir -Recurse -Filter "*.json" -ErrorAction SilentlyContinue
            Write-Host "  [v] PRESERVED: User sessions ($($sessionFiles.Count) files) remain intact." -ForegroundColor Green
        }
    }

    if ((Test-Path $desktopSentryDir) -and (-not $DryRun)) {
        $sentryFiles = Get-ChildItem -Path $desktopSentryDir -Recurse -File -ErrorAction SilentlyContinue
        if ($sentryFiles) {
            $sentryFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Cleared Sentry crash telemetry queue." -ForegroundColor Green
        }
    }

    if ((Test-Path $desktopLogsDir) -and (-not $DryRun)) {
        $logFiles = Get-ChildItem -Path $desktopLogsDir -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            $logFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  [v] Cleared session log files." -ForegroundColor Green
        }
    }

    Write-Host "`n======================================================================" -ForegroundColor Green
    Write-Host "             $(Get-Msg 'Completed')                       " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host (Get-Msg 'CompletedDesc') -ForegroundColor White
    if ($backupPath) {
        Write-Host "$(Get-Msg 'BackupSaved') $backupPath`n" -ForegroundColor DarkCyan
    }

    if ($Auto) {
        if ($LaunchAfter) { Launch-Claude }
        return
    }

    Write-Host (Get-Msg 'LaunchPrompt') -ForegroundColor Yellow
    $ans = Read-Host
    if ($ans -eq "Y" -or $ans -eq "y" -or $ans -eq "Д" -or $ans -eq "д" -or $ans -eq "S" -or $ans -eq "s") {
        Launch-Claude
    }
}

function Launch-Claude {
    if (Test-Path $claudeExePath) {
        Write-Host "[*] Launching Claude Desktop ($claudeExePath)..." -ForegroundColor Cyan
        Start-Process -FilePath $claudeExePath
    } else {
        Write-Host "[-] Executable $claudeExePath not found. Please open Claude manually." -ForegroundColor Red
        Pause
    }
}

function Show-Status {
    Write-Header
    Write-Host "--- CURRENT CLAUDE IDENTIFIERS & FINGERPRINT ---`n" -ForegroundColor Yellow

    # CLI ~/.claude.json
    if (Test-Path $cliConfigPath1) {
        $c1 = [System.IO.File]::ReadAllText($cliConfigPath1, [System.Text.Encoding]::UTF8)
        $mId1 = [regex]::Match($c1, '"machineID"\s*:\s*"([^"]+)"')
        $uId1 = [regex]::Match($c1, '"userID"\s*:\s*"([^"]+)"')
        Write-Host "CLI (~/.claude.json):" -ForegroundColor Cyan
        Write-Host "  machineID: $(if ($mId1.Success) { $mId1.Groups[1].Value } else { 'None' })" -ForegroundColor White
        Write-Host "  userID:    $(if ($uId1.Success) { $uId1.Groups[1].Value } else { 'None' })" -ForegroundColor White
    } else {
        Write-Host "CLI (~/.claude.json): Not found" -ForegroundColor DarkGray
    }

    # Nested CLI
    if (Test-Path $cliConfigPath2) {
        $c2 = [System.IO.File]::ReadAllText($cliConfigPath2, [System.Text.Encoding]::UTF8)
        $mId2 = [regex]::Match($c2, '"machineID"\s*:\s*"([^"]+)"')
        $uId2 = [regex]::Match($c2, '"userID"\s*:\s*"([^"]+)"')
        Write-Host "`nNested CLI (~/.claude/.claude.json):" -ForegroundColor Cyan
        Write-Host "  machineID: $(if ($mId2.Success) { $mId2.Groups[1].Value } else { 'None' })" -ForegroundColor White
        Write-Host "  userID:    $(if ($uId2.Success) { $uId2.Groups[1].Value } else { 'None' })" -ForegroundColor White
    }

    # Desktop Application
    Write-Host "`nDesktop Application (AppData\Claude):" -ForegroundColor Cyan
    if (Test-Path $desktopAntDid) {
        $did = (Get-Content $desktopAntDid -Raw).Trim()
        Write-Host "  ant-did: $did" -ForegroundColor White
    } else {
        Write-Host "  ant-did: None (unlinked, will generate cleanly on start)" -ForegroundColor DarkGray
    }

    if (Test-Path $desktopAntRegistry) {
        $reg = (Get-Content $desktopAntRegistry -Raw).Trim()
        if ($reg.Length -gt 60) { $reg = $reg.Substring(0, 60) + "..." }
        Write-Host "  ant-device-registry: $reg" -ForegroundColor White
    } else {
        Write-Host "  ant-device-registry: None (unlinked)" -ForegroundColor DarkGray
    }

    if (Test-Path $desktopConfig) {
        try {
            $cfg = Get-Content $desktopConfig -Raw | ConvertFrom-Json
            $acc = $cfg.lastKnownAccountUuid
            Write-Host "  lastKnownAccountUuid: $(if ($acc) { $acc } else { 'Cleared' })" -ForegroundColor White
            Write-Host "  cached OAuth tokens:  $(if ($cfg.'oauth:tokenCache' -or $cfg.'oauth:tokenCacheV2') { 'Yes' } else { 'No' })" -ForegroundColor White
        } catch {}
    }

    if (Test-Path $desktopPlanUsage) {
        $sz = [math]::Round((Get-Item $desktopPlanUsage).Length / 1KB, 1)
        Write-Host "  plan-usage-history.json: $sz KB" -ForegroundColor White
    }

    if (Test-Path $desktopSessionsDir) {
        $sCount = (Get-ChildItem -Path $desktopSessionsDir -Recurse -Filter "*.json" -ErrorAction SilentlyContinue).Count
        Write-Host "  claude-code-sessions: $sCount files preserved" -ForegroundColor White
    }

    Write-Host ""
    Pause
}

function Show-FingerprintAudit {
    Write-Header
    Write-Host "--- DEEP HARDWARE & FINGERPRINT AUDIT ---`n" -ForegroundColor Yellow

    Write-Host "Operating System: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor Cyan
    
    # Windows Machine GUID
    $machGuid = "Unknown"
    try {
        $machGuid = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Cryptography").MachineGuid
    } catch {}
    Write-Host "Windows System MachineGuid: $machGuid" -ForegroundColor White

    Write-Host "`nAccount Association Risk Audit:" -ForegroundColor Yellow
    $risks = 0

    if (Test-Path $desktopAntRegistry) {
        Write-Host "  [!] HIGH RISK: ant-device-registry.json is present (machine cryptographically bound to old account)." -ForegroundColor Red
        $risks++
    } else {
        Write-Host "  [✓] SAFE: ant-device-registry.json is unlinked." -ForegroundColor Green
    }

    if (Test-Path $desktopConfig) {
        try {
            $cfg = Get-Content $desktopConfig -Raw | ConvertFrom-Json
            if ($cfg.lastKnownAccountUuid) {
                Write-Host "  [!] HIGH RISK: config.json retains lastKnownAccountUuid ($($cfg.lastKnownAccountUuid))." -ForegroundColor Red
                $risks++
            }
            if ($cfg.'oauth:tokenCache' -or $cfg.'oauth:tokenCacheV2') {
                Write-Host "  [!] MEDIUM RISK: config.json contains cached session OAuth tokens." -ForegroundColor Red
                $risks++
            }
        } catch {}
    }

    if (Test-Path $desktopPlanUsage) {
        if ((Get-Item $desktopPlanUsage).Length -gt 500) {
            Write-Host "  [!] MEDIUM RISK: plan-usage-history.json contains logged organization tokens." -ForegroundColor Red
            $risks++
        }
    }

    if ($risks -eq 0) {
        Write-Host "`nAll clear! Your machine identifiers and telemetry are completely unlinked and sanitized." -ForegroundColor Green
    } else {
        Write-Host "`nFound $risks potential account association risk factor(s). Run option [1] (Safe Anti-Ban Reset) to clear them." -ForegroundColor Yellow
    }

    Write-Host ""
    Pause
}

function Switch-Language {
    Write-Header
    Write-Host "Select Language / Выберите язык:`n" -ForegroundColor Yellow
    Write-Host "  [1] English" -ForegroundColor White
    Write-Host "  [2] Русский" -ForegroundColor White
    Write-Host "  [0] Keep current / Оставить текущий`n" -ForegroundColor DarkGray

    $ans = Read-Host "Select / Выберите [1, 2, 0]"
    if ($ans -eq "1") {
        $script:ActiveLang = "en"
    } elseif ($ans -eq "2") {
        $script:ActiveLang = "ru"
    } else {
        return
    }

    try {
        Set-Content -Path $langConfigFile -Value $script:ActiveLang -Encoding UTF8 -Force
    } catch {}
}

# Shortcut only mode
if ($CreateShortcuts) {
    Install-Shortcuts
    exit 0
}

# Auto mode
if ($Auto) {
    Perform-Reset
    exit 0
}

# Interactive Menu Loop
do {
    if ([Console]::IsInputRedirected) {
        Write-Host "Input redirected, exiting interactive loop." -ForegroundColor DarkYellow
        break
    }

    Write-Header
    Write-Host (Get-Msg 'MenuHeader') -ForegroundColor White
    Write-Host "  $(Get-Msg 'Menu1')" -ForegroundColor Green
    Write-Host "  $(Get-Msg 'Menu2')" -ForegroundColor Cyan
    Write-Host "  $(Get-Msg 'Menu3')" -ForegroundColor Blue
    Write-Host "  $(Get-Msg 'Menu4')" -ForegroundColor Yellow
    Write-Host "  $(Get-Msg 'Menu5')" -ForegroundColor Magenta
    Write-Host "  $(Get-Msg 'Menu6')" -ForegroundColor Red
    Write-Host "  $(Get-Msg 'MenuShortcuts')" -ForegroundColor DarkCyan
    Write-Host "  $(Get-Msg 'Menu7')" -ForegroundColor Gray
    Write-Host "  $(Get-Msg 'Menu8')" -ForegroundColor White
    Write-Host "  $(Get-Msg 'MenuLang')" -ForegroundColor Cyan
    Write-Host "  $(Get-Msg 'Menu0')" -ForegroundColor DarkGray
    Write-Host ""

    $choice = Read-Host (Get-Msg 'Prompt')
    if ([string]::IsNullOrWhiteSpace($choice)) {
        continue
    }

    switch ($choice.Trim().ToUpper()) {
        "1" {
            Write-Host ""
            Write-Host (Get-Msg 'ConfirmSafe') -ForegroundColor Yellow
            $confirm = Read-Host
            if ($confirm -eq "Y" -or $confirm -eq "y" -or $confirm -eq "Д" -or $confirm -eq "д" -or $confirm -eq "S" -or $confirm -eq "s") {
                Perform-Reset
            } else {
                Write-Host (Get-Msg 'Cancelled') -ForegroundColor DarkGray
                Start-Sleep -Milliseconds 600
            }
        }
        "2" {
            Show-Status
        }
        "3" {
            Show-FingerprintAudit
        }
        "4" {
            Write-Header
            Stop-ClaudeProcesses
            New-ClaudeBackup -Tag "manual"
            Pause
        }
        "5" {
            Restore-ClaudeBackup
        }
        "6" {
            Write-Host "`n$(Get-Msg 'ConfirmFullWarn')" -ForegroundColor Red
            $confirm = Read-Host (Get-Msg 'ConfirmFullPrompt')
            if ($confirm -eq "YES") {
                Perform-Reset -WipeSessions
            } else {
                Write-Host (Get-Msg 'Cancelled') -ForegroundColor DarkGray
                Start-Sleep -Milliseconds 600
            }
        }
        "S" {
            Install-Shortcuts
            Pause
        }
        "7" {
            Start-Process explorer.exe $backupRootDir
        }
        "8" {
            Launch-Claude
        }
        "L" {
            Switch-Language
        }
        "0" {
            Write-Host "`nGoodbye! / До свидания!" -ForegroundColor Cyan
            Start-Sleep -Milliseconds 500
            break
        }
        default {
            Write-Host "Invalid option. / Неверный ввод." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
} while ($choice -ne "0")
