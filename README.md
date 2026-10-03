# Claude Anti-Ban & Telemetry Cleaner 🐍 (Python Edition)

[![Latest Release](https://img.shields.io/github/v/release/RengoCode/claude-cleaner?color=brightgreen&label=Release)](https://github.com/RengoCode/claude-cleaner/releases)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI & CLI](https://img.shields.io/badge/Interface-GUI%20%7C%20CLI-blue.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0%20(Pure%20Stdlib)-success.svg)]()
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20RU%20%7C%20ES%20%7C%20ZH-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Native Shell Branch](https://img.shields.io/badge/Branch-Main%20(Native%20Shell)-orange.svg)](../../tree/main)

> **Cross-platform Python implementation with both Graphical User Interface (GUI) and Command-Line Interface (CLI). Cleans hardware identifiers, deep telemetry, and account linkages across Claude Desktop & Claude Code CLI while keeping your local sessions 100% safe.**

[🇷🇺 Читать на русском языке](README.ru.md) • [⚡ Main Branch (Native Shell)](../../tree/main) • [⭐ Star on GitHub](https://github.com/RengoCode/claude-cleaner)

---

## 📌 Table of Contents
- [Why Python Edition?](#-why-python-edition)
- [Interfaces: GUI & CLI](#-interfaces-gui--cli)
  - [1. Graphical User Interface (GUI)](#1-graphical-user-interface-gui)
  - [2. Command-Line Interface (CLI)](#2-command-line-interface-cli)
- [Anthropic Telemetry Fingerprint Matrix](#-anthropic-telemetry-fingerprint-matrix)
- [Critical Technical Discovery: The Electron UTF-8 BOM Bug](#-critical-technical-discovery-the-electron-utf-8-bom-bug)
- [Testing Suite](#-testing-suite)
- [Safe Anti-Ban vs. Session Wiping](#-safe-anti-ban-vs-session-wiping)
- [Project Structure (Python Branch)](#-project-structure-python-branch)
- [Disclaimer & Legal Notice](#-disclaimer--legal-notice)
- [License](#-license)

---

## 🐍 Why Python Edition?
This dedicated **`python`** branch provides:
1. **Zero External Dependencies:** Built strictly using Python's standard library (`tkinter`, `json`, `uuid`, `secrets`, `pathlib`, `zipfile`). No `pip install` required.
2. **Dual Interfaces:** Choose between a sleek modern **Graphical User Interface (GUI)** or an interactive/scriptable **Command-Line Interface (CLI)**.
3. **Comprehensive Test Suite:** Includes automated unit and mock integration tests (`test_claude_reset.py`).
4. **Multi-Language Engine:** English, Russian, Spanish, and Simplified Chinese.

> 💡 *Note: If you do not have Python installed on your computer, switch to the [`main`](../../tree/main) branch, which contains 100% native PowerShell (`.ps1`/`.cmd`) and Bash (`.sh`) scripts with zero prerequisites.*

---

## 🖥️ Interfaces: GUI & CLI

### 1. Graphical User Interface (GUI)
Launch the modern desktop application with live telemetry cards, status indicators, and 1-click actions:

```bash
# Direct launcher
python claude_reset_gui.py

# Or via CLI flag
python claude_reset.py --gui
```

**GUI Features:**
* 📊 **Live Telemetry Dashboard:** Displays current `machineID`, `userID`, `ant-did` cookie status, plan history size, and count of preserved sessions.
* 🚀 **1-Click Safe Reset:** Prominent one-click button to reset hardware bindings while keeping chats safe.
* 🔍 **Deep Hardware & Fingerprint Audit:** Modal window displaying OS Machine GUID and ban risk factors.
* 🛡️ **Backup & Restore Manager:** Create timestamped `.zip` archives and restore from previous points.
* 🌐 **Instant Language Switcher:** One-click toggle between English and Russian.

---

### 2. Command-Line Interface (CLI)
For terminals, automation, and headless environments:

```bash
# Interactive colored terminal menu
python claude_reset.py

# Safe Anti-Ban Reset (keeps your sessions & chats intact)
python claude_reset.py --safe

# Show current hardware identifiers & telemetry status
python claude_reset.py --status

# Deep hardware & ban risk audit
python claude_reset.py --inspect

# Dry-run simulation (preview changes without modifying files)
python claude_reset.py --safe --dry-run

# Create a safety backup zip archive
python claude_reset.py --backup

# Restore from existing backup
python claude_reset.py --restore

# Set language (en, ru, es, zh)
python claude_reset.py --lang en

# Full Factory Reset (wipes sessions - requires YES confirmation)
python claude_reset.py --full
```

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
On Windows, scripts often save files using UTF-8 with a Byte Order Mark (`\uFEFF`). 

Electron / Node.js internal `JSON.parse(fs.readFileSync(...))` **crashes immediately** with `SyntaxError: Unexpected token '﻿'` when reading files with a BOM, preventing Claude Desktop from opening entirely.

This Python utility strictly enforces **UTF-8 No-BOM** across all file operations (`encoding="utf-8"` with raw string write).

---

## 🧪 Testing Suite
Run the built-in unit tests (zero external dependencies required):

```bash
python -m unittest test_claude_reset.py -v
```

Tests cover:
* Regex replacement without JSON corruption
* Desktop config token sanitization
* Safe vs Full reset modes (session preservation verification)
* Dry-run non-modification guarantees
* UTF-8 No-BOM compliance
* Multi-language translation completeness

---

## 🛡️ Safe Anti-Ban vs. Session Wiping
* **Safe Anti-Ban Reset (Default):** Resets hardware identifiers, device keys, telemetry logs, and account bindings. **All of your local session chats and projects are preserved intact.**
* **Factory Reset (Optional):** Completely cleans sessions in addition to identifiers (`--full` flag). Requires explicit confirmation (`YES`).

---

## 📂 Project Structure (Python Branch)

```text
claude-cleaner/ (branch: python)
├── .github/
│   ├── workflows/ci.yml     # Multi-platform CI (Python 3.8-3.13 on Ubuntu, macOS, Windows)
│   └── ISSUE_TEMPLATE/      # Issue templates
├── claude_reset.py          # Core Python CLI engine & business logic
├── claude_reset_gui.py      # Modern tkinter Graphical User Interface (GUI)
├── test_claude_reset.py     # Unit & mock integration test suite
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
