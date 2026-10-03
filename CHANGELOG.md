# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-04

### Changed
- **Minimalist & Universal Repository Structure (`main`)**:
  - The `main` branch is now 100% native with zero prerequisites (PowerShell for Windows, pure Bash for macOS/Linux).
  - Python implementation moved to dedicated [`python`](../../tree/python) branch for cleaner separation and maximum out-of-the-box compatibility.
  - Replaced multiple separate batch and PowerShell scripts with unified `Claude-Reset.cmd` and `Claude-Reset.ps1`.
  - Integrated shortcut creation directly into `Claude-Reset.ps1` (`[S]` menu item and `-CreateShortcuts` switch).
  - Rewrote `claude-reset.sh` to be 100% pure native Bash (using standard system tools `openssl`/`urandom`/`sed`/`pkill`), removing all Python dependencies on macOS/Linux.
- **Documentation Refactoring**:
  - Separated monolithic bilingual README into mirror-identical `README.md` (English) and `README.ru.md` (Russian).
  - Added instant header language switchers eliminating inconvenient long-scrolling.
  - Full parity of matrices, tables, and quick-start instructions across both languages.

---

## [1.1.0] - 2026-10-03

### Added
- **Internationalization (i18n)**:
  - Full multilingual support in `claude_reset.py`: **English**, **Russian**, **Spanish**, and **Simplified Chinese**.
  - Bilingual support in native PowerShell utility `Claude-Reset.ps1` (**English** and **Russian**).
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
  - `--inspect` flag and menu option for deep audit of OS Machine GUID and account association risk factors.
- **Dry-Run Simulation**:
  - `-DryRun` switch in PowerShell and `--dry-run` flag in Bash to preview planned actions without modifying any files.

---

## [1.0.0] - 2026-10-03

### Added
- **Native Windows & Shell Engines**:
  - Automatic timestamped safety backups before any modifications.
  - Safe Anti-Ban reset mode preserving all user chat histories and pins in `claude-code-sessions`.
  - Full Factory Reset mode (`--full`) with confirmation guards.
  - Interactive terminal UI with color support.
- **Telemetry & Identity Matrix**:
  - CLI: `machineID` (SHA-256), `userID` (SHA-256), `anonymousId` (`claudecode_*`), clearing `1p_failed_events.*.json`.
  - Desktop: Unlinking cryptographic `ant-did` cookie and `ant-device-registry.json` keys to allow clean regeneration.
  - Telemetry: Clearing `sentry/`, `logs/`, `bridge-state.json`, `remote-control-state.json`, `buddy-tokens.json`, and rotating `ccd-ids.json` salt.
  - Desktop Config: Sanitizing stale OAuth token caches, `lastKnownAccountUuid`, and updating activation timestamps.

### Fixed
- **Electron UTF-8 BOM Bug**:
  - Enforced UTF-8 No-BOM across all file modifications to prevent Electron JSON parsing syntax crashes (`SyntaxError: Unexpected token '﻿'`).
