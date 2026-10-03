# Claude Anti-Ban & Telemetry Cleaner 🛡️

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20RU%20%7C%20ES%20%7C%20ZH-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-None%20(Pure%20Stdlib)-success.svg)]()

> **Clean hardware identifiers, deep telemetry, and account linkages across Claude Desktop & CLI while keeping your local sessions, project files, and bookmarks 100% safe.**

[English](#english-version) • [🇷🇺 Русский](#russian-version--на-русском)

---

## English Version

### The Problem: How Anthropic Links Accounts to Your Computer
Anthropic stores persistent hardware IDs, device salts, telemetry tokens, and signed machine registries in both the **Claude CLI** and **Claude Desktop** applications. Even if you log out or switch accounts, these identifiers remain identical, allowing Anthropic to fingerprint and link all accounts running on the same machine.

If one account gets banned or flagged, secondary accounts on the same machine risk being associated and blocked.

### What This Tool Does
This utility breaks the fingerprinting chain by generating fresh, cryptographically strong random identifiers and sanitizing telemetry records:
1. **Creates an automated `.zip` backup** of all affected files before making any changes.
2. **Generates fresh random `machineID` and `userID`** (SHA256 hex) in `~/.claude.json` and nested cowork configs.
3. **Severes desktop machine bindings** by removing `ant-did` and `ant-device-registry.json` (allowing Claude to generate a fresh, legitimate cryptographic keypair on next start).
4. **Sanitizes `config.json`**: strips `lastKnownAccountUuid`, cached OAuth tokens (`oauth:tokenCache`), Chrome extension paired device IDs, and dynamic account allowlist caches.
5. **Neutralizes deep tracking**:
   - Clears **`plan-usage-history.json`** (purges tracked Organization UUIDs and billing timestamps).
   - Resets **`Local State`** (`installation_date2` installation timestamp).
   - Sanitizes **`~/.claude/stats-cache.json`** (daily activity and usage metrics).
   - Removes Sentry crash queues, failed telemetry event queues, and Crashpad minidumps.
6. **PRESERVES your local Claude Code sessions by default** (`claude-code-sessions/` and `~/.claude/projects/` are kept intact so you do NOT lose your chat history or pinned items).
7. **Supports 4 languages**: English, Russian, Spanish, Chinese (`--lang en|ru|es|zh` or switch in interactive menu).
8. **Hardware & Fingerprint Audit**: Run `--inspect` to check your OS Machine GUID and assess association risk factors.

---

### Anthropic Telemetry Fingerprint Matrix

| Target File | Stored Identifier | Role in Tracking | Sanitization Method |
|---|---|---|---|
| `~/.claude.json` | `machineID` | Persistent machine GUID; identical across all accounts | Replaced with random 64-char SHA256 hex |
| `~/.claude.json` | `userID` | Telemetry device UUID | Replaced with random 64-char SHA256 hex |
| `~/.claude.json` | `anonymousId` | Anonymous tracking ID (`claudecode_...`) | Regenerated or purged |
| `~/.claude/.claude.json` | `machineID` / `userID` | Secondary VM / cowork-mode hardware IDs | Replaced with random 64-char SHA256 hex |
| `~/.claude/stats-cache.json` | `dailyActivity` | Daily message, session, and tool call activity counts | Cleared to empty history |
| `~/.claude/telemetry/` | `1p_failed_events.*.json` | Failed telemetry event queue with machine UUIDs | Purged |
| `AppData\Roaming\Claude\ant-did` | `ant-did` | Base64-encoded application device UUID | Removed (recreated cleanly on start) |
| `AppData\Roaming\Claude\ant-device-registry.json` | `ant-device-registry` | Cryptographically binds hardware key (`pk1:...`) to account UUID | Removed (unlinks machine) |
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

### Critical Technical Discovery: The Electron UTF-8 BOM Bug
On Windows, naive scripts written in PowerShell often save files using UTF-8 with a Byte Order Mark (`\uFEFF`). 

Electron / Node.js's internal `JSON.parse(fs.readFileSync(...))` **crashes immediately** with `SyntaxError: Unexpected token '﻿'` when reading files with a BOM, preventing Claude Desktop from starting up.

This utility strictly enforces **UTF-8 No-BOM** across all operations, ensuring 100% startup reliability.

---

### Quick Start

#### Option A: Cross-Platform Python (Windows, macOS, Linux)
Requires Python 3.8+ with **no external dependencies**:

```bash
# 1. Audit hardware & ban association risks
python claude_reset.py --inspect

# 2. Show current hardware IDs & status
python claude_reset.py --status

# 3. Dry-run simulation (preview changes without modifying files)
python claude_reset.py --safe --dry-run

# 4. Safe Anti-Ban Reset (keeps your sessions & chats intact)
python claude_reset.py --safe

# 5. Create a safety backup zip
python claude_reset.py --backup

# 6. Restore from backup
python claude_reset.py --restore

# 7. Select language (en, ru, es, zh)
python claude_reset.py --lang en

# 8. Interactive terminal menu
python claude_reset.py
```

#### Option B: Windows 1-Click Launchers
* Double-click **`Claude-AntiBan-Reset.cmd`** to launch the interactive management console.
* Double-click **`create_shortcuts.cmd`** to create shortcuts directly on your **Desktop** and **Start Menu**.

#### Option C: macOS & Linux Shell Launcher
```bash
chmod +x claude-reset.sh
./claude-reset.sh           # Interactive menu
./claude-reset.sh --inspect # Audit hardware fingerprint & risks
./claude-reset.sh --safe    # Safe anti-ban reset
```

#### Automated Test Suite
```bash
python test_claude_reset.py -v
```

<br>

---

## Russian Version / На русском

### Проблема: как Anthropic связывает аккаунты с одним компьютером
В конфигурационных файлах **Claude CLI** и десктопного приложения **Claude Desktop** сохраняется обширный набор метаданных, привязывающих ваш компьютер к учетным записям:
* **CLI (`~/.claude.json`):** `machineID`, `userID`, `anonymousId` — создаются один раз и остаются неизменными для всех аккаунтов на этой машине.
* **CLI статистика (`~/.claude/stats-cache.json`):** ежедневный учет вызовов инструментов, сообщений и сессий.
* **Десктопное приложение (`AppData\Roaming\Claude\` на Windows / `~/Library/Application Support/Claude/` на macOS):**
  * `ant-did` — уникальный ID устройства.
  * `ant-device-registry.json` — реестр, привязывающий машину к каждому аккаунту с цифровой подписью ключа устройства (`pk1:...`).
  * `config.json` — кэш токенов авторизации, ID последнего пользователя (`lastKnownAccountUuid`), метка первого запуска и ID расширения Chrome.
  * `plan-usage-history.json` — история использования тарифа и запросов с привязкой к конкретным Organization UUID.
  * `Local State` — сохраняет неизменяемый таймстемп первоначальной установки (`installation_date2`).
  * `declarative_performance_observer.db` — внутренняя SQLite база телеметрии Electron.
  * `Crashpad/` — дампы падений процессов (`.dmp`) с регистрами процессора и памятью.
  * `ccd-ids.json` и `bridge-state.json` — сессионные мосты и соль отслеживания.
  * Логи и кэш Sentry со старыми сессиями и ошибками.

При блокировке одного аккаунта Anthropic может автоматически ассоциировать и заблокировать другие учетные записи, запускаемые на том же ПК.

---

### Безопасный Anti-Ban против удаления сессий
В ряде публикаций энтузиасты предлагают полностью очищать папку `claude-code-sessions`. **Это грубая ошибка**, из-за которой пользователи теряют свою историю диалогов, контекст кода и закрепления.

**Данная утилита работает безопасно:**
* **По умолчанию (Safe Mode):** сбрасываются только аппаратные ID, телеметрия, логи организации и токены привязки к аккаунту, а **все ваши сессии, история и проекты остаются полностью нетронутыми**.
* **Полный сброс (Factory Reset):** опциональный режим (`--full` или пункт `[6]` в меню), требующий явного текстового подтверждения `YES`.
* **Автоматический ZIP-бэкап:** перед любым изменением создаётся полноценный архив в папке `backups/`, из которого всё можно вернуть назад в 1 клик.
* **Поддержка языков:** русский, английский, испанский и китайский (переключение прямо в меню клавишей `[L]` или через `--lang`).
* **Аудит отпечатка:** режим `--inspect` детально проверяет MachineGuid операционной системы и оценивает риски связывания аккаунтов.

---

### Использование

#### Способ 1: Универсальный скрипт Python (Windows / macOS / Linux)
Работает на любой ОС без установки сторонних библиотек:

```bash
# Проверить текущие идентификаторы
python claude_reset.py --status

# Безопасный сброс идентификаторов и телеметрии (сессии сохраняются)
python claude_reset.py --safe

# Создать резервную копию
python claude_reset.py --backup

# Восстановить из резервной копии
python claude_reset.py --restore

# Интерактивное цветное меню
python claude_reset.py
```

#### Способ 2: Для Windows (в 1 клик)
* Запустите файл **`Claude-AntiBan-Reset.cmd`** для входа в меню.
* Запустите **`create_shortcuts.cmd`**, чтобы создать ярлыки на Рабочем столе и в меню «Пуск» (иконка подтягивается динамически из локально установленного Claude Desktop).

---

### Структура проекта

```text
claude-cleaner/
├── .github/
│   ├── workflows/ci.yml     # Multi-platform CI (Ubuntu, macOS, Windows)
│   └── ISSUE_TEMPLATE/      # Bug report & feature request templates
├── claude_reset.py          # Кроссплатформенное ядро (Windows / macOS / Linux)
├── claude-reset.sh          # Универсальный лаунчер для macOS и Linux (bash)
├── Claude-AntiBan-Reset.ps1 # Нативный PowerShell-скрипт с цветным меню
├── Claude-AntiBan-Reset.cmd # Пакетный лаунчер для Windows (двойной клик)
├── create_shortcuts.ps1     # Установщик ярлыков на Рабочий стол и в Пуск
├── create_shortcuts.cmd     # Быстрый запуск установки ярлыков
├── test_claude_reset.py     # Модульные тесты (0 зависимостей, unittest)
├── CONTRIBUTING.md          # Руководство для разработчиков
├── CHANGELOG.md             # История изменений (Keep a Changelog)
├── LICENSE                  # Лицензия MIT
├── .gitignore               # Исключение архивов бэкапов и кэша
└── backups/                 # Локальные ZIP-бэкапы (создаются автоматически)
```

---

### Disclaimer / Правовая оговорка

> **EN:** This project is an independent open-source research and privacy tool. It is **not** affiliated with, endorsed, or sponsored by Anthropic, PBC. "Claude" is a registered trademark of Anthropic, PBC. All brand names and trademarks belong to their respective owners. This tool does not bypass authentication or tamper with server-side infrastructure; it solely manages and sanitizes local configuration and telemetry files on the user's computer.
>
> **RU:** Данный проект является независимым инструментом для исследования и обеспечения конфиденциальности с открытым исходным кодом. Он **не** связан с компанией Anthropic, PBC, не поддерживается и не спонсируется ею. Все торговые марки («Claude», логотипы) принадлежат их законным владельцам. Утилита не вмешивается в работу удалённых серверов и не обходит защиту, а исключительно управляет локальными файлами конфигурации и телеметрии на компьютере пользователя.

---

### Лицензия
Распространяется под свободной лицензией **MIT License**. Разрешено свободное использование, модификация и публикация.
