# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-03

### Added
- **Internationalization (i18n)**:
  - Full multilingual support in `claude_reset.py`: **English**, **Russian**, **Spanish**, and **Simplified Chinese**.
  - Bilingual support in native PowerShell utility `Claude-AntiBan-Reset.ps1` (**English** and **Russian**).
  - Auto-detection of system UI culture and persistent language settings (`~/.claude-cleaner/language.txt`).
  - Interactive language switcher `[L]` accessible directly from the main menu.
  - `--lang` CLI flag (`en`, `ru`, `es`, `zh`).
- **Deep Telemetry Discovery & Sanitization**:
  - `plan-usage-history.json`: purges historical Organization UUIDs and request timestamps that link accounts to billing organizations.
  - `Local State`: resets Chromium `uninstall_metrics.installation_date2` installation timestamp to prevent initial install fingerprinting.
  - `stats-cache.json`: clears cumulative CLI daily activity counts (messages, sessions, tool invocations).
  - `Crashpad/`: purges process minidumps (`.dmp`) containing hardware registers and memory states.
  - `declarative_performance_observer.db`: clears internal Electron SQLite performance observer database.
  - `daemon-auth-status.json` and `daemon-auth-cooldown`: resets background daemon session tokens.
- **Hardware & Fingerprint Audit**:
  - `--inspect` flag and menu option `[3]` for deep audit of OS Machine GUID (Windows Registry `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid`, macOS `IOPlatformUUID`, Linux `/etc/machine-id`) and account association risk factors.
- **Dry-Run Simulation**:
  - `--dry-run` flag in Python and `-DryRun` switch in PowerShell to preview planned actions without modifying any files.
- **Expanded Test Suite**:
  - Unit tests for multilingual key completeness across all 4 languages.
  - Unit tests for deep telemetry sanitization and dry-run safety.

---

## [1.0.0] - 2026-10-03

### Added
- **Cross-Platform Python Engine (`claude_reset.py`)**:
  - Full support for Windows, macOS, and Linux without any external `pip` dependencies.
  - Automatic timestamped ZIP safety backups before any modifications.
  - Safe Anti-Ban reset mode preserving all user chat histories and pins in `claude-code-sessions`.
  - Full Factory Reset mode (`--full`) with confirmation guards.
  - Interactive terminal UI with color support.
  - CLI flags: `--safe`, `--full`, `--status`, `--backup`, `--restore`, `--launch`.
- **Windows Integration**:
  - `Claude-AntiBan-Reset.cmd` 1-click batch launcher.
  - `Claude-AntiBan-Reset.ps1` PowerShell utility with terminal menu.
  - `create_shortcuts.cmd` & `create_shortcuts.ps1` for Desktop and Start Menu shortcut generation.
- **macOS & Linux Integration**:
  - `claude-reset.sh` universal shell launcher.
- **Telemetry & Identity Matrix**:
  - CLI: `machineID` (SHA-256), `userID` (SHA-256), `anonymousId` (`claudecode_*`), clearing `1p_failed_events.*.json`.
  - Desktop: Unlinking cryptographic `ant-did` cookie and `ant-device-registry.json` keys to allow clean regeneration.
  - Telemetry: Clearing `sentry/`, `logs/`, `bridge-state.json`, `remote-control-state.json`, `buddy-tokens.json`, and rotating `ccd-ids.json` salt.
  - Desktop Config: Sanitizing stale OAuth token caches, `lastKnownAccountUuid`, and updating activation timestamps.
- **Test Suite & CI**:
  - `test_claude_reset.py` unit and mock integration tests with `unittest`.
  - Multi-OS GitHub Actions CI workflow (`.github/workflows/ci.yml`) testing on Python 3.8 - 3.13 across Windows, Ubuntu, and macOS.

### Fixed
- **Electron UTF-8 BOM Bug**:
  - Fixed syntax crash (`SyntaxError: Unexpected token '﻿', "﻿{..." is not valid JSON`) by enforcing UTF-8 No-BOM encoding on all JSON write operations.
- **Session Preservation**:
  - Fixed unintentional loss of Claude Code sessions by isolating session removal behind explicit opt-in flags.
- **Cryptographic Key Invalidation**:
  - Fixed invalid `{}` JSON format in `ant-device-registry.json` by unlinking the file, allowing Claude Desktop to sign genuine fresh keys on startup.
