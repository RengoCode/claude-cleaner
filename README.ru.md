# Claude Anti-Ban & Telemetry Cleaner 🛡️

[![Latest Release](https://img.shields.io/github/v/release/RengoCode/claude-cleaner?color=brightgreen&label=Release)](https://github.com/RengoCode/claude-cleaner/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0%20(Pure%20Native)-success.svg)]()
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20RU-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Branch](https://img.shields.io/badge/Branch-Python%20GUI%20%26%20CLI-brightgreen.svg)](../../tree/python)

> **Очистка идентификаторов оборудования, глубокой телеметрии и привязок аккаунтов в Claude Desktop и Claude Code CLI с полным сохранением ваших локальных сессий, истории проектов и закладок.**

[🇬🇧 Read in English](README.md) • [🐍 Ветка с Python-версией (с GUI)](../../tree/python) • [⭐ Поддержать проект на GitHub](https://github.com/RengoCode/claude-cleaner)

---

## 📌 Оглавление
- [Проблема: как Anthropic связывает аккаунты](#-проблема-как-anthropic-связывает-аккаунты)
- [Что делает эта утилита](#-что-делает-эта-утилита)
- [Матрица телеметрии и отпечатков Anthropic](#-матрица-телеметрии-и-отпечатков-anthropic)
- [Важное техническое открытие: баг Electron UTF-8 BOM](#-важное-техническое-открытие-баг-electron-utf-8-bom)
- [Быстрый старт](#-быстрый-старт)
  - [Windows (в 1 клик или через PowerShell)](#windows-в-1-клик-или-через-powershell)
  - [macOS и Linux (чистый нативный Bash)](#macos-и-linux-чистый-нативный-bash)
  - [Python-версия (выделенная ветка)](#python-версия-выделенная-ветка)
- [Безопасный Anti-Ban против удаления сессий](#-безопасный-anti-ban-против-удаления-сессий)
- [Структура проекта](#-структура-проекта)
- [Правовая оговорка и безопасность](#-правовая-оговорка-и-безопасность)
- [Лицензия](#-лицензия)

---

## 🔍 Проблема: как Anthropic связывает аккаунты
В конфигурационных файлах **Claude Code CLI** и десктопного приложения **Claude Desktop** сохраняется обширный набор аппаратных ID, солей отслеживания, токенов телеметрии и подписанных реестров оборудования.

Даже если вы выйдете из учетной записи, переустановите приложение или зарегистрируете новый аккаунт, эти идентификаторы остаются прежними, позволяя Anthropic связывать все аккаунты с одним ПК:
* **Ассоциация по ID железа:** Если один аккаунт попадает под ограничение или бан, вторичные аккаунты на этой же машине рискуют получить цепную блокировку.
* **Неизменяемый таймстемп установки:** В `Local State` хранится метка времени первого запуска (`installation_date2`).
* **Аппаратный реестр:** В `ant-device-registry.json` сохраняется привязка криптографического ключа машины (`pk1:...`) к аккаунтам.
* **История тарифов и организаций:** В `plan-usage-history.json` ведется полный аудит посещенных Organization UUID и периодов списания.

---

## ⚡ Что делает эта утилита
Репозиторий содержит **100% нативные скрипты без сторонних зависимостей**, разрывающие цепочки отпечатков устройства на Windows, macOS и Linux:

1. **Автоматический бэкап:** Перед внесением изменений создает полный архив в `~/.claude-cleaner/backups/`. Восстановление в 1 клик.
2. **Спуфинг ID оборудования CLI:** Генерирует новые криптографически стойкие `machineID` и `userID` (SHA-256 hex) в `~/.claude.json` и вложенных cowork-конфигах.
3. **Разрыв аппаратной привязки Desktop:** Удаляет `ant-did` и подменяет `ant-device-registry.json`, позволяя Claude Desktop инициализировать чистую ключевую пару при следующем запуске.
4. **Очистка `config.json`:** Удаляет `lastKnownAccountUuid`, сохраненный OAuth-кэш (`oauth:tokenCache`), ID сопряжения расширения Chrome и кэш организаций.
5. **Нейтрализация глубокой телеметрии:**
   - Очищает **`plan-usage-history.json`** (удаляет историю Organization UUID и времени запросов).
   - Сбрасывает таймстемп установки в **`Local State`**.
   - Сбрасывает **`~/.claude/stats-cache.json`** (ежедневная статистика активности, сообщений и вызовов инструментов).
   - Удаляет очереди падений Sentry, неудачные события телеметрии и дампы Crashpad.
6. **СОХРАНЯЕТ локальные сессии по умолчанию:** Ваши диалоги, файлы проектов и закрепления (`claude-code-sessions/` и `~/.claude/projects/`) остаются нетронутыми.
7. **Двуязычный интерфейс:** Поддержка **русского** и **английского** языков в терминальном меню (`-Lang ru|en` или клавиша `[L]`).
8. **Создание ярлыков:** Установка ярлыков на Рабочий стол и в меню «Пуск» на Windows в 1 действие (пункт меню `[S]`).

---

## 📊 Матрица телеметрии и отпечатков Anthropic

| Целевой файл | Сохраняемый идентификатор | Роль в отслеживании | Метод очистки |
|---|---|---|---|
| `~/.claude.json` | `machineID` | Постоянный GUID машины; одинаковый для всех учетных записей | Заменяется на случайный 64-значный SHA256 hex |
| `~/.claude.json` | `userID` | UUID устройства телеметрии | Заменяется на случайный 64-значный SHA256 hex |
| `~/.claude.json` | `anonymousId` | Анонимный ID отслеживания (`claudecode_...`) | Перегенерируется случайным хэшем |
| `~/.claude/.claude.json` | `machineID` / `userID` | Аппаратные ID для вторичных VM / cowork-режима | Заменяется на случайный 64-значный SHA256 hex |
| `~/.claude/stats-cache.json` | `dailyActivity` | Ежедневная статистика сессий, сообщений и инструментов | Сбрасывается в пустую историю |
| `~/.claude/telemetry/` | `1p_failed_events.*.json` | Очередь неотправленных событий телеметрии с UUID машины | Удаляется |
| `AppData\Roaming\Claude\ant-did` | `ant-did` | Base64-токен устройства приложения Claude Desktop | Удаляется (создается заново при запуске) |
| `AppData\Roaming\Claude\ant-device-registry.json` | `ant-device-registry` | Привязка ключа устройства (`pk1:...`) к аккаунту | Удаляется / подменяется новым UUID |
| `AppData\Roaming\Claude\config.json` | `lastKnownAccountUuid` | UUID последней авторизованной учетной записи | Вычищается из JSON |
| `AppData\Roaming\Claude\config.json` | `oauth:tokenCache` | Кэш учетных данных и сессионные токены JWT | Вычищается |
| `AppData\Roaming\Claude\config.json` | `chromeExtension.pairedDeviceId` | ID привязки расширения Claude Chrome | Вычищается |
| `AppData\Roaming\Claude\config.json` | `dxt:allowlist*` | Кэш функций конкретных организаций | Вычищается |
| `AppData\Roaming\Claude\plan-usage-history.json` | `history[].org` | История Organization UUID и времени запросов | Очищается до пустого массива |
| `AppData\Roaming\Claude\Local State` | `installation_date2` | Метка даты первой установки ПО | Сбрасывается на текущее время |
| `AppData\Roaming\Claude\declarative_performance_observer.db` | Трассировка | SQLite база данных телеметрии производительности | Удаляется |
| `AppData\Roaming\Claude\Crashpad\` | Минидампы (`.dmp`) | Дампы падений с содержимым регистров и памяти | Очищается |
| `AppData\Roaming\Claude\ccd-ids.json` | `salt` | Соль отслеживания Claude Code Desktop | Перегенерируется новым случайным UUID |
| `AppData\Roaming\Claude\bridge-state.json` | `bridge-state` | Мост локальных и удаленных сессий | Удаляется |
| `AppData\Roaming\Claude\sentry\` | `scope_v3.json` | Контекст пользователя и устройства в логах Sentry | Очищается |
| `AppData\Roaming\Claude\claude-code-sessions\` | Файлы сессий | Локальная история диалогов и контекста | **Сохраняется по умолчанию** (удаление только с `--full`) |

---

## 🛠️ Важное техническое открытие: баг Electron UTF-8 BOM
На Windows скрипты PowerShell часто по умолчанию сохраняют файлы в кодировке UTF-8 с меткой порядка байтов (BOM, `\uFEFF`).

Внутренний парсер Electron / Node.js (`JSON.parse(fs.readFileSync(...))`) при наличии BOM **немедленно падает** с критической ошибкой `SyntaxError: Unexpected token '﻿'`, из-за чего Claude Desktop просто не запускается.

Эта утилита принудительно применяет режим **UTF-8 No-BOM** при любых модификациях файлов, гарантируя 100% стабильность запуска.

---

## 🚀 Быстрый старт

### Windows (в 1 клик или через PowerShell)
Не требует установки сторонних программ. Работает сразу на Windows 10/11:

* **Вариант 1 (в 1 клик):** Дважды кликните по **`Claude-Reset.cmd`**, чтобы открыть интерактивное меню.
* **Вариант 2 (через PowerShell):** Запустите `Claude-Reset.ps1` из терминала:
  ```powershell
  # Интерактивное цветное меню
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1

  # Автоматический безопасный сброс без лишних вопросов
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -Auto

  # Создать ярлыки на Рабочем столе и в Пуск
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -CreateShortcuts

  # Тестовый прогон без записи изменений
  powershell -ExecutionPolicy Bypass -File .\Claude-Reset.ps1 -DryRun -Auto
  ```

### macOS и Linux (чистый нативный Bash)
Не требует установки сторонних пакетов. Работает прямо в Bash:

```bash
# Дать права на выполнение
chmod +x claude-reset.sh

# Интерактивное меню
./claude-reset.sh

# Автоматический безопасный сброс
./claude-reset.sh --auto

# Тестовый прогон (Dry-Run)
./claude-reset.sh --dry-run --auto

# Принудительный выбор языка (Русский / Английский)
./claude-reset.sh --lang ru
```

### Python-версия (выделенная ветка)
Если вам нужна реализация на Python 3 с полным набором модульных тестов, перейдите в ветку [`python`](../../tree/python):
```bash
git checkout python
python claude_reset.py --safe
```

---

## 🛡️ Безопасный Anti-Ban против удаления сессий
В некоторых руководствах в сети советуют полностью удалять папку `claude-code-sessions`. **Это грубая ошибка**, безвозвратно уничтожающая историю переписки, контекст проектов и закрепления.

* **Безопасный Anti-Ban сброс (По умолчанию):** Сбрасывает аппаратные ID, ключи устройств, логи телеметрии и привязки аккаунтов. **Все ваши локальные сессии и проекты остаются в полной сохранности.**
* **Полный Factory Reset (Опционально):** Полное удаление сессий вместе с идентификаторами (флаг `--full` или пункт `[6]` в меню). Требует явного текстового подтверждения (`YES`).

---

## 📂 Структура проекта

```text
claude-cleaner/
├── .github/
│   ├── workflows/ci.yml     # Многоплатформенный CI (Ubuntu, macOS, Windows)
│   └── ISSUE_TEMPLATE/      # Шаблоны баг-репортов и предложений
├── Claude-Reset.cmd         # Пакетный лаунчер для Windows (в 1 клик)
├── Claude-Reset.ps1         # Нативный движок PowerShell и установщик ярлыков
├── claude-reset.sh          # Чистый Bash-скрипт для macOS и Linux (0 зависимостей)
├── CONTRIBUTING.md          # Руководство для разработчиков
├── CHANGELOG.md             # История версий
├── LICENSE                  # Лицензия MIT
├── README.md                # Англоязычная документация
└── README.ru.md             # Русскоязычная документация (1:1 идентична)
```

---

## ⚖️ Правовая оговорка и безопасность
Данный проект является независимым инструментом для исследования и обеспечения конфиденциальности с открытым исходным кодом. Он **не** связан с компанией Anthropic, PBC, не поддерживается и не спонсируется ею. Все торговые марки («Claude», логотипы) принадлежат их законным владельцам.

Утилита не вмешивается в работу удалённых серверов, не манипулирует токенами API и не обходит аутентификацию, а исключительно управляет локальными файлами конфигурации и телеметрии на компьютере пользователя.

---

## 📄 Лицензия
Проект распространяется под свободной лицензией [MIT License](LICENSE). Разрешено свободное использование, модификация и публикация.
