# Claude Anti-Ban & Telemetry Cleaner 🛡️

[![Latest Release](https://img.shields.io/github/v/release/RengoCode/claude-cleaner?color=brightgreen&label=Release)](https://github.com/RengoCode/claude-cleaner/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0%20(Pure%20Native)-success.svg)]()
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20RU-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Branch](https://img.shields.io/badge/Branch-Python%20GUI%20%26%20CLI-brightgreen.svg)](../../tree/python)

> **Clean hardware identifiers, deep telemetry, and account linkages across Claude Desktop & Claude Code CLI while keeping your local sessions, project histories, and bookmarks 100% safe.**

[🇷🇺 Читать на русском языке](README.ru.md) • [🐍 Python Version Branch (with GUI)](../../tree/python) • [⭐ Star on GitHub](https://github.com/RengoCode/claude-cleaner)

---

## 📌 Table of Contents
- [The Problem: How Anthropic Links Accounts](#-the-problem-how-anthropic-links-accounts)
- [What This Tool Does](#-what-this-tool-does)
- [Anthropic Telemetry Fingerprint Matrix](#-anthropic-telemetry-fingerprint-matrix)
- [Critical Technical Discovery: The Electron UTF-8 BOM Bug](#-critical-technical-discovery-the-electron-utf-8-bom-bug)
- [Quick Start](#-quick-start)
  - [Windows (1-Click or PowerShell)](#windows-1-click-or-powershell)
  - [macOS & Linux (Pure Native Bash)](#macos--linux-pure-native-bash)
  - [Python Version (Dedicated Branch)](#python-version-dedicated-branch)
- [Safe Anti-Ban vs. Session Wiping](#-safe-anti-ban-vs-session-wiping)
- [Project Structure](#-project-structure)
- [Disclaimer & Legal Notice](#-disclaimer--legal-notice)
- [License](#-license)

---

## 🔍 The Problem: How Anthropic Links Accounts
Anthropic embeds persistent hardware IDs, device salts, telemetry tokens, and signed machine registries across both the **Claude Code CLI** and **Claude Desktop** applications. 

Even if you log out, reinstall, or register a new account, these identifiers remain identical, allowing Anthropic to fingerprint and link all accounts running on the same computer:
* **Hardware ID association:** If one account gets flagged or banned, secondary accounts on the same machine face immediate collateral restriction.
* **Persistent installation timestamp:** `Local State` preserves the original installation date (`installation_date2`).
* **Hardware registry:** `ant-device-registry.json` binds the machine's cryptographic hardware key (`pk1:...`) to account records.
* **Billing & organization footprint:** `plan-usage-history.json` tracks all historical organization UUIDs and billing periods.

---

## ⚡ What This Tool Does
This repository provides a **100% native, zero-dependency** privacy utility that breaks device fingerprinting chains across Windows, macOS, and Linux:

1. **Automated Safety Backup:** Creates a complete timestamped backup in `~/.claude-cleaner/backups/` before modifying any file. You can restore your previous state in 1 click.
2. **CLI Hardware Spoofing:** Generates fresh, cryptographically strong random `machineID` and `userID` (SHA-256 hex) in `~/.claude.json` and nested cowork configs.
3. **Desktop Machine Binding Severance:** Purges `ant-did` and `ant-device-registry.json`, enabling Claude Desktop to register as a brand-new device with a fresh keypair on next launch.
4. **Sanitizes `config.json`:** Strips `lastKnownAccountUuid`, cached OAuth tokens (`oauth:tokenCache`), Chrome extension paired device IDs, and organization feature caches.
5. **Neutralizes Deep Telemetry:**
   - Clears **`plan-usage-history.json`** (purges tracked Organization UUIDs and usage timestamps).
   - Resets **`Local State`** installation timestamp.
   - Clears **`~/.claude/stats-cache.json`** (daily activity, tool calls, and session counts).
   - Removes Sentry crash queues, failed telemetry event queues, and Crashpad minidumps.
6. **PRESERVES Local Sessions by Default:** Your local chat turns, project files, and bookmarks (`claude-code-sessions/` and `~/.claude/projects/`) are kept intact.
7. **Bilingual UI:** Native interactive console supporting **English** and **Russian** (`-Lang ru|en` or press `[L]` in menu).
8. **Built-in Shortcut Creator:** Installs Desktop and Start Menu shortcuts on Windows (`[S]` menu option).

---

## 📊 Anthropic Telemetry Fingerprint Matrix

| Target File | Stored Identifier | Role in Tracking | Sanitization Method |
|---|---|---|---|
| `~/.claude.json` | `machineID` | Persistent machine GUID; identical across all accounts | Replaced with random 64-char SHA256 hex |
| `~/.claude.json` | `userID` | Telemetry device UUID | Replaced with random 64-char SHA256 hex |
| `~/.claude.json` | `anonymousId` | Anonymous tracking ID (`claudecode_...`) | Regenerated with random hash |
| `~/.claude/.claude.json` | `machineID` / `userID` | Secondary VM / cowork-mode hardware IDs | Replaced with random 64-char SHA256 hex |
| `~/.claude/stats-cache.json` | `dailyActivity` | Daily message, session, and tool call activity counts | Cleared to empty history |
| `~/.claude/telemetry/` | `1p_failed_events.*.json` | Failed telemetry event queue with machine UUIDs | Purged |
| `AppData\Roaming\Claude\ant-did` | `ant-did` | Base64-encoded application device UUID | Removed (recreated cleanly on start) |
| `AppData\Roaming\Claude\ant-device-registry.json` | `ant-device-registry` | Cryptographically binds hardware key (`pk1:...`) to account UUID | Removed / spoofed |
| `AppData\Roaming\Claude\config.json` | `lastKnownAccountUuid` | Binds last logged-in account UUID | Purged from JSON |
| `AppData\Roaming\Claude\config.json` | `oauth:tokenCache` | Cached credentials & JWT access tokens | Purged |
| `AppData\Roaming\Claude\config.json` | `chromeExtension.pairedDeviceId` | Binds Claude Chrome Extension to machine | Purged |
| `AppData\Roaming\Claude\config.json` | `dxt:allowlist*` | Per-account organization feature caches | Purged |
| `AppData\Roaming\Claude\plan-usage-history.json` | `history[].org` | Complete history of Organization UUIDs & usage timestamps | Cleared to empty history |
| `AppData\Roaming\Claude\Local State` | `installation_date2` | Persistent timestamp of initial software installation | Reset to current timestamp |
| `AppData\Roaming\Claude\declarative_performance_observer.db` | Tracing data | SQLite performance & telemetry observer database | Removed |
| `AppData\Roaming\Claude\Crashpad\` | Minidumps (`.dmp`) | Process crash dumps containing memory/registers | Purged |
| `AppData\Roaming\Claude\ccd-ids.json` | `salt` | Claude Code Desktop tracking salt | Regenerated with fresh UUID |
| `AppData\Roaming\Claude\bridge-state.json` | `bridge-state` | Local-to-remote org/account session bridge | Purged |
| `AppData\Roaming\Claude\sentry\` | `scope_v3.json` | Sentry crash telemetry with user & device context | Purged |
| `AppData\Roaming\Claude\claude-code-sessions\` | Session records | Local history of chat turns | **Preserved by default** (`--full` to wipe) |

---

## 🛠️ Critical Technical Discovery: The Electron UTF-8 BOM Bug
On Windows, naive scripts written in PowerShell often save files using UTF-8 with a Byte Order Mark (`\uFEFF`). 

Electron / Node.js internal `JSON.parse(fs.readFileSync(...))` **crashes immediately** with `SyntaxError: Unexpected token '﻿'` when reading files with a BOM, preventing Claude Desktop from opening entirely.

This utility strictly enforces **UTF-8 No-BOM** across all file modifications, ensuring 100% startup stability.

---

## 🚀 Quick Start

### Windows (1-Click or PowerShell)
Zero prerequisites. Runs out-of-the-box on Windows 10/11:

* **Option 1 (1-Click):** Double-click **`Claude-Reset.cmd`** to open the interactive management console.
* **Option 2 (PowerShell):** Run `Claude-Reset.ps1` from terminal:
  ```powershell
  # Interactive console menu
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1

  # Non-interactive safe reset
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -Auto

  # Create Desktop & Start Menu shortcuts
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -CreateShortcuts

  # Dry-run simulation (preview without changing files)
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -DryRun -Auto
  ```

### macOS & Linux (Pure Native Bash)
Zero prerequisites. Runs directly in Bash (requires `openssl` or `/dev/urandom`):

```bash
# Make script executable
chmod +x claude-reset.sh

# Interactive terminal menu
./claude-reset.sh

# Non-interactive safe reset
./claude-reset.sh --auto

# Dry-run simulation
./claude-reset.sh --dry-run --auto

# Force language (English / Russian)
./claude-reset.sh --lang en
```

### Python Version (Dedicated Branch)
If you prefer a Python-based engine with unit tests, check out our [`python`](../../tree/python) branch:
```bash
git checkout python
python claude_reset.py --safe
```

---

## 🛡️ Safe Anti-Ban vs. Session Wiping
In many online guides, authors mistakenly recommend deleting the entire `claude-code-sessions` directory. **This is a mistake** that permanently wipes your local project chat history and pinned contexts.

* **Safe Anti-Ban Reset (Default):** Resets hardware identifiers, device keys, telemetry logs, and account bindings. **All of your local session chats and projects are preserved intact.**
* **Factory Reset (Optional):** Completely cleans sessions in addition to identifiers (`--full` flag or menu item `[6]`). Requires explicit confirmation (`YES`).

---

## 📂 Project Structure

```text
claude-cleaner/
├── .github/
│   ├── workflows/ci.yml     # Multi-platform CI (Ubuntu, macOS, Windows)
│   └── ISSUE_TEMPLATE/      # Bug report & feature request templates
├── Claude-Reset.cmd         # 1-click Windows batch launcher
├── Claude-Reset.ps1         # Native PowerShell engine & shortcut creator
├── claude-reset.sh          # Pure native Bash engine for macOS & Linux (0 dependencies)
├── CONTRIBUTING.md          # Development guidelines
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── README.md                # English documentation
└── README.ru.md             # Russian documentation (1:1 identical)
```

---

## ⚖️ Disclaimer & Legal Notice
This project is an independent open-source research and privacy tool. It is **not** affiliated with, endorsed, or sponsored by Anthropic, PBC. "Claude" is a registered trademark of Anthropic, PBC. All brand names and trademarks belong to their respective owners. 

This tool does not tamper with server-side infrastructure, manipulate API tokens, or bypass server authentication; it solely inspects, backs up, and sanitizes local configuration and telemetry files stored on the user's computer.

---

## 📄 License
This project is released under the [MIT License](LICENSE). You are free to use, modify, and distribute it.
