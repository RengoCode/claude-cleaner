#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude Anti-Ban & Telemetry Cleaner v1.1.0
Cross-platform device ID reset, deep telemetry sanitizer & privacy tool for Claude CLI & Desktop.
Supports Windows, macOS, and Linux with zero external dependencies.
Bilingual & Multilingual: English, Russian, Spanish, Chinese.
"""

import os
import sys
import re
import json
import shutil
import zipfile
import uuid
import secrets
import platform
import argparse
import subprocess
import locale
from datetime import datetime
from pathlib import Path

# Force UTF-8 encoding on standard streams (critical for Windows cp1251/cp866)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# --- ANSI Colors for Terminal UI ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

# Windows terminal ANSI enable
if platform.system() == "Windows":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


# ==============================================================================
# Internationalization (i18n)
# ==============================================================================

I18N = {
    "en": {
        "title": "CLAUDE ANTI-BAN & DEVICE ID RESET UTILITY",
        "subtitle": "Clean hardware identifiers, deep telemetry & anti-ban reset",
        "menu_header": "Select an action:",
        "menu_1": "[1] 🚀 Safe Anti-Ban Reset (Reset device IDs & deep telemetry, KEEP sessions)",
        "menu_2": "[2] 🔍 View Current Identifiers & Telemetry Status",
        "menu_3": "[3] 💻 Deep Hardware & Fingerprint Inspection",
        "menu_4": "[4] 🛡️ Create Safety Backup ZIP Now",
        "menu_5": "[5] 🔄 Restore From Backup",
        "menu_6": "[6] ⚠️ Full Factory Reset (Reset IDs + Wipe All Sessions)",
        "menu_7": "[7] ▶️ Launch Claude Desktop",
        "menu_lang": "[L] 🌐 Switch Language / Сменить язык / Cambiar idioma / 切换语言",
        "menu_exit": "[0] ❌ Exit",
        "prompt_choice": "Enter option: ",
        "confirm_safe": "Reset hardware IDs & deep telemetry? (Sessions will be preserved) [Y/N]: ",
        "confirm_full_warn": "WARNING: This will wipe your local session histories in addition to telemetry!",
        "confirm_full_prompt": "Type 'YES' to proceed with Full Factory Reset: ",
        "cancelled": "Operation cancelled.",
        "press_enter": "Press Enter to return to menu...",
        "proc_terminated": "Checked and terminated any running Claude processes.",
        "step_1": "[1/6] Creating safety backup archive...",
        "step_2": "[2/6] Resetting CLI hardware & telemetry IDs...",
        "step_3": "[3/6] Resetting Desktop application device binding...",
        "step_4": "[4/6] Sanitizing config.json & deep telemetry records...",
        "step_5": "[5/6] Checking session storage...",
        "step_6": "[6/6] Sanitizing plan usage history & system metrics...",
        "completed": "ANTI-BAN & TELEMETRY RESET COMPLETED SUCCESSFULLY!",
        "backup_saved": "Safety backup saved at:",
        "sessions_preserved": "PRESERVED: {count} Claude Code session files and bookmarks remain intact.",
        "sessions_deleted": "Factory reset: Deleted local claude-code-sessions.",
        "status_title": "--- CURRENT CLAUDE IDENTIFIERS & FINGERPRINT ---",
        "insp_title": "--- DEEP HARDWARE & FINGERPRINT AUDIT ---",
        "dry_run_notice": "[DRY-RUN MODE] No files will be modified.",
        "lang_name": "English",
    },
    "ru": {
        "title": "CLAUDE ANTI-BAN & СБРОС ИДЕНТИФИКАТОРОВ УСТРОЙСТВА",
        "subtitle": "Очистка ID железа, глубокой телеметрии и защита от привязки аккаунтов",
        "menu_header": "Выберите действие:",
        "menu_1": "[1] 🚀 Безопасный Anti-Ban сброс (сброс ID железа и телеметрии, СЕССИИ СОХРАНЯЮТСЯ)",
        "menu_2": "[2] 🔍 Посмотреть текущие идентификаторы и статус телеметрии",
        "menu_3": "[3] 💻 Глубокий аудит отпечатка системы и железа",
        "menu_4": "[4] 🛡️ Создать резервную копию ZIP прямо сейчас",
        "menu_5": "[5] 🔄 Восстановить из резервной копии",
        "menu_6": "[6] ⚠️ Полный Factory Reset (сброс ID + удаление всех сессий)",
        "menu_7": "[7] ▶️ Запустить Claude Desktop",
        "menu_lang": "[L] 🌐 Сменить язык / Switch Language / Cambiar idioma / 切换语言",
        "menu_exit": "[0] ❌ Выход",
        "prompt_choice": "Введите номер действия: ",
        "confirm_safe": "Сбросить идентификаторы устройства и телеметрию? (Сессии сохранятся) [Y/N]: ",
        "confirm_full_warn": "ВНИМАНИЕ: Будут удалены все локальные сессии и диалоги Claude Code!",
        "confirm_full_prompt": "Для подтверждения полного сброса введите 'YES': ",
        "cancelled": "Операция отменена пользователем.",
        "press_enter": "Нажмите Enter для возврата в меню...",
        "proc_terminated": "Проверены и завершены активные процессы Claude.",
        "step_1": "[1/6] Создание защитного архива резервной копии...",
        "step_2": "[2/6] Сброс аппаратных ID и телеметрии Claude CLI...",
        "step_3": "[3/6] Сброс привязок десктопного приложения Claude...",
        "step_4": "[4/6] Очистка config.json и глубоких записей телеметрии...",
        "step_5": "[5/6] Проверка сохранности файлов сессий...",
        "step_6": "[6/6] Очистка истории использования тарифа и системных метрик...",
        "completed": "СБРОС ИДЕНТИФИКАТОРОВ И ТЕЛЕМЕТРИИ УСПЕШНО ЗАВЕРШЕН!",
        "backup_saved": "Резервная копия сохранена в:",
        "sessions_preserved": "СОХРАНЕНО: {count} файлов сессий Claude Code и закладок остались нетронутыми.",
        "sessions_deleted": "Полный сброс: локальная история claude-code-sessions удалена.",
        "status_title": "--- ТЕКУЩИЕ ИДЕНТИФИКАТОРЫ И СТАТУС CLAUDE ---",
        "insp_title": "--- ГЛУБОКИЙ АУДИТ ОТПЕЧАТКА СИСТЕМЫ И ЖЕЛЕЗА ---",
        "dry_run_notice": "[РЕЖИМ ТЕСТА] Файлы не будут изменены.",
        "lang_name": "Русский",
    },
    "es": {
        "title": "UTILIDAD DE REINICIO DE ID Y ANTI-BAN DE CLAUDE",
        "subtitle": "Limpieza de identificadores de hardware, telemetría profunda y anti-ban",
        "menu_header": "Seleccione una acción:",
        "menu_1": "[1] 🚀 Reinicio Anti-Ban Seguro (Restablece ID y telemetría, MANTIENE sesiones)",
        "menu_2": "[2] 🔍 Ver identificadores actuales y estado de telemetría",
        "menu_3": "[3] 💻 Inspección profunda de hardware y huella digital",
        "menu_4": "[4] 🛡️ Crear copia de seguridad ZIP ahora",
        "menu_5": "[5] 🔄 Restaurar desde copia de seguridad",
        "menu_6": "[6] ⚠️ Restablecimiento de Fábrica (Reinicia ID + borra todas las sesiones)",
        "menu_7": "[7] ▶️ Iniciar Claude Desktop",
        "menu_lang": "[L] 🌐 Cambiar idioma / Switch Language / Сменить язык / 切换语言",
        "menu_exit": "[0] ❌ Salir",
        "prompt_choice": "Ingrese opción: ",
        "confirm_safe": "¿Restablecer ID de hardware y telemetría? (Se conservan sesiones) [Y/N]: ",
        "confirm_full_warn": "ADVERTENCIA: ¡Esto borrará todos sus historiales de sesiones locales!",
        "confirm_full_prompt": "Escriba 'YES' para proceder con el restablecimiento total: ",
        "cancelled": "Operación cancelada.",
        "press_enter": "Presione Enter para volver al menú...",
        "proc_terminated": "Procesos de Claude comprobados y terminados.",
        "step_1": "[1/6] Creando archivo de copia de seguridad...",
        "step_2": "[2/6] Restableciendo ID de hardware y telemetría de CLI...",
        "step_3": "[3/6] Restableciendo vinculación de dispositivo de escritorio...",
        "step_4": "[4/6] Sanitizando config.json y telemetría profunda...",
        "step_5": "[5/6] Comprobando almacenamiento de sesiones...",
        "step_6": "[6/6] Sanitizando historial de uso y métricas...",
        "completed": "¡REINICIO ANTI-BAN Y TELEMETRÍA COMPLETADO CON ÉXITO!",
        "backup_saved": "Copia de seguridad guardada en:",
        "sessions_preserved": "PRESERVADO: {count} archivos de sesión permanecen intactos.",
        "sessions_deleted": "Restablecimiento de fábrica: claude-code-sessions borradas.",
        "status_title": "--- IDENTIFICADORES ACTUALES Y ESTADO DE CLAUDE ---",
        "insp_title": "--- AUDITORÍA PROFUNDA DE HARDWARE Y HUELLA DIGITAL ---",
        "dry_run_notice": "[MODO DE PRUEBA] No se modificarán archivos.",
        "lang_name": "Español",
    },
    "zh": {
        "title": "CLAUDE 反封禁与硬件 ID 重置工具",
        "subtitle": "清除硬件指纹、深度遥测与多账号关联重置",
        "menu_header": "请选择操作：",
        "menu_1": "[1] 🚀 安全反封禁重置 (重置硬件ID与深度遥测，保留所有会话与对话)",
        "menu_2": "[2] 🔍 查看当前设备标识符与遥测状态",
        "menu_3": "[3] 💻 深度硬件指纹与系统追踪审计",
        "menu_4": "[4] 🛡️ 立即创建安全备份压缩包 (ZIP)",
        "menu_5": "[5] 🔄 从备份中恢复配置",
        "menu_6": "[6] ⚠️ 恢复出厂设置 (重置ID并清除全部本地会话历史)",
        "menu_7": "[7] ▶️ 启动 Claude 桌面端",
        "menu_lang": "[L] 🌐 切换语言 / Switch Language / Сменить язык / Cambiar idioma",
        "menu_exit": "[0] ❌ 退出",
        "prompt_choice": "请输入选项编号: ",
        "confirm_safe": "确定重置硬件标识符与深度遥测吗？(会话将被完整保留) [Y/N]: ",
        "confirm_full_warn": "警告：此操作将清除所有本地 Claude Code 会话历史记录！",
        "confirm_full_prompt": "请输入 'YES' 确认执行恢复出厂设置: ",
        "cancelled": "操作已取消。",
        "press_enter": "按回车键返回菜单...",
        "proc_terminated": "已检查并关闭正在运行的 Claude 进程。",
        "step_1": "[1/6] 正在创建完整配置安全备份...",
        "step_2": "[2/6] 正在重置 CLI 硬件 ID 与遥测标识...",
        "step_3": "[3/6] 正在解除桌面端设备指纹与账号绑定...",
        "step_4": "[4/6] 正在清理 config.json 与深度遥测记录...",
        "step_5": "[5/6] 正在验证会话文件存储...",
        "step_6": "[6/6] 正在清理用量历史记录与系统指标...",
        "completed": "反封禁与深度遥测重置成功完成！",
        "backup_saved": "安全备份保存于:",
        "sessions_preserved": "已妥善保留: {count} 个会话文件与书签完好无损。",
        "sessions_deleted": "恢复出厂设置: 已清除本地会话记录。",
        "status_title": "--- 当前 CLAUDE 标识符与状态 ---",
        "insp_title": "--- 深度硬件与系统指纹审计 ---",
        "dry_run_notice": "[演练模式] 不会修改任何文件。",
        "lang_name": "简体中文",
    }
}


class ClaudePaths:
    """Detects and resolves paths for Claude CLI and Desktop across OS platforms."""

    def __init__(self):
        self.os_type = platform.system()
        self.home = Path.home()
        self.base_dir = Path(__file__).resolve().parent
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.cleaner_dir = self.home / ".claude-cleaner"
        self.cleaner_dir.mkdir(parents=True, exist_ok=True)
        self.lang_file = self.cleaner_dir / "language.txt"

        # CLI configuration paths
        self.cli_dir = self.home / ".claude"
        self.cli_config_main = self.home / ".claude.json"
        self.cli_config_nested = self.cli_dir / ".claude.json"
        self.cli_telemetry_dir = self.cli_dir / "telemetry"
        self.cli_sessions_dir = self.cli_dir / "sessions"
        self.cli_projects_dir = self.cli_dir / "projects"
        self.cli_stats_cache = self.cli_dir / "stats-cache.json"
        self.cli_credentials = self.cli_dir / ".credentials.json"
        self.cli_daemon_status = self.cli_dir / "daemon-auth-status.json"
        self.cli_daemon_cooldown = self.cli_dir / "daemon-auth-cooldown"
        self.cli_paste_cache = self.cli_dir / "paste-cache"
        self.cli_shell_snapshots = self.cli_dir / "shell-snapshots"

        # Desktop configuration paths
        if self.os_type == "Windows":
            appdata = Path(os.environ.get("APPDATA", self.home / "AppData" / "Roaming"))
            localappdata = Path(os.environ.get("LOCALAPPDATA", self.home / "AppData" / "Local"))
            self.desktop_dir = appdata / "Claude"
            self.desktop_exe = localappdata / "AnthropicClaude" / "claude.exe"
        elif self.os_type == "Darwin":  # macOS
            self.desktop_dir = self.home / "Library" / "Application Support" / "Claude"
            self.desktop_exe = Path("/Applications/Claude.app/Contents/MacOS/Claude")
        else:  # Linux
            xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", self.home / ".config"))
            self.desktop_dir = xdg_config / "Claude"
            self.desktop_exe = Path("/usr/bin/claude")

        # Specific files in Desktop AppData
        self.ant_did = self.desktop_dir / "ant-did"
        self.ant_device_registry = self.desktop_dir / "ant-device-registry.json"
        self.desktop_config = self.desktop_dir / "config.json"
        self.desktop_local_state = self.desktop_dir / "Local State"
        self.desktop_plan_usage = self.desktop_dir / "plan-usage-history.json"
        self.desktop_perf_db = self.desktop_dir / "declarative_performance_observer.db"
        self.desktop_perf_journal = self.desktop_dir / "declarative_performance_observer.db-journal"
        self.desktop_crashpad = self.desktop_dir / "Crashpad"
        self.ccd_ids = self.desktop_dir / "ccd-ids.json"
        self.bridge_state = self.desktop_dir / "bridge-state.json"
        self.remote_control_state = self.desktop_dir / "remote-control-state.json"
        self.buddy_tokens = self.desktop_dir / "buddy-tokens.json"
        self.claude_code_sessions = self.desktop_dir / "claude-code-sessions"
        self.sentry_dir = self.desktop_dir / "sentry"
        self.logs_dir = self.desktop_dir / "logs"

    def get_language(self) -> str:
        """Determines active language code ('en', 'ru', 'es', 'zh')."""
        if self.lang_file.is_file():
            try:
                lang = self.lang_file.read_text(encoding="utf-8").strip().lower()
                if lang in I18N:
                    return lang
            except Exception:
                pass

        # Auto-detect from system locale
        try:
            loc = locale.getlocale()[0]
            sys_lang = (loc or "").lower()
            if sys_lang.startswith("ru"):
                return "ru"
            if sys_lang.startswith("es"):
                return "es"
            if sys_lang.startswith("zh"):
                return "zh"
        except Exception:
            pass

        env_lang = (os.environ.get("LANG", "") + os.environ.get("LC_ALL", "")).lower()
        if "ru" in env_lang:
            return "ru"
        if "es" in env_lang:
            return "es"
        if "zh" in env_lang:
            return "zh"

        return "en"

    def set_language(self, lang_code: str):
        """Saves preferred language."""
        if lang_code in I18N:
            try:
                self.lang_file.write_text(lang_code, encoding="utf-8")
            except Exception:
                pass


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Translates a message key to the specified language with fallback to English."""
    dict_lang = I18N.get(lang, I18N["en"])
    text = dict_lang.get(key, I18N["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def print_banner(lang: str = "en"):
    banner = f"""{Colors.CYAN}{Colors.BOLD}
======================================================================
           {t('title', lang)}
     {t('subtitle', lang)}
======================================================================{Colors.RESET}"""
    print(banner)


def random_sha256_hex():
    """Generates a random 64-character lowercase hex string (SHA256 format)."""
    return secrets.token_hex(32)


def stop_claude_processes(lang: str = "en"):
    """Gracefully terminates running Claude desktop processes."""
    os_name = platform.system()
    try:
        if os_name == "Windows":
            cmd = 'taskkill /F /IM claude.exe /IM AnthropicClaude.exe 2>nul'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os_name == "Darwin":
            cmd = "pkill -x -i Claude 2>/dev/null"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os_name == "Linux":
            cmd = "pkill -x -i claude 2>/dev/null"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Colors.GREEN}[+] {t('proc_terminated', lang)}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Process note: {e}{Colors.RESET}")


def create_backup(paths: ClaudePaths, tag="auto", lang: str = "en") -> Path:
    """Creates a timestamped ZIP archive containing all Claude config & telemetry files."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = paths.backup_dir / f"backup_{timestamp}_{tag}.zip"

    files_to_backup = []

    # CLI configs
    if paths.cli_config_main.is_file():
        files_to_backup.append((paths.cli_config_main, "cli_home_claude.json"))
    if paths.cli_config_nested.is_file():
        files_to_backup.append((paths.cli_config_nested, "cli_nested_claude.json"))
    if paths.cli_stats_cache.is_file():
        files_to_backup.append((paths.cli_stats_cache, "cli_stats_cache.json"))

    # Desktop files
    desktop_files = [
        paths.ant_did,
        paths.ant_device_registry,
        paths.desktop_config,
        paths.desktop_local_state,
        paths.desktop_plan_usage,
        paths.ccd_ids,
        paths.bridge_state,
        paths.remote_control_state,
        paths.buddy_tokens
    ]
    for df in desktop_files:
        if df.is_file():
            files_to_backup.append((df, f"desktop/{df.name}"))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path, arc_name in files_to_backup:
            try:
                zipf.write(file_path, arcname=arc_name)
            except Exception as e:
                print(f"{Colors.YELLOW}[!] Backup warning for {file_path.name}: {e}{Colors.RESET}")

        # Backup claude-code-sessions if present
        if paths.claude_code_sessions.is_dir():
            for root, _, files in os.walk(paths.claude_code_sessions):
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(paths.claude_code_sessions)
                    zipf.write(full_p, arcname=f"desktop/claude-code-sessions/{rel_p}")

    size_kb = max(1, zip_path.stat().st_size // 1024)
    print(f"{Colors.GREEN}[+] {t('backup_saved', lang)}{Colors.RESET}")
    print(f"    {Colors.CYAN}{zip_path}{Colors.RESET} ({size_kb} KB)")
    return zip_path


def list_backups(paths: ClaudePaths):
    """Returns a sorted list of existing backup zip files."""
    return sorted(paths.backup_dir.glob("backup_*.zip"), key=os.path.getmtime, reverse=True)


def restore_backup(paths: ClaudePaths, lang: str = "en"):
    """Restores configuration and sessions from an existing ZIP backup."""
    backups = list_backups(paths)
    if not backups:
        print(f"{Colors.RED}[-] No backups found in {paths.backup_dir}{Colors.RESET}")
        return False

    print(f"\n{Colors.YELLOW}--- AVAILABLE BACKUPS ---{Colors.RESET}")
    for idx, b in enumerate(backups, 1):
        mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime("%d.%m.%Y %H:%M:%S")
        size_kb = b.stat().st_size // 1024
        print(f"  [{idx}] {b.name}  ({mtime}, {size_kb} KB)")
    print(f"  [0] Cancel\n")

    choice = input("Select backup number to restore: ").strip()
    if not choice or choice == "0":
        return False

    try:
        selected_idx = int(choice) - 1
        if selected_idx < 0 or selected_idx >= len(backups):
            print(f"{Colors.RED}[-] Invalid selection.{Colors.RESET}")
            return False
    except ValueError:
        print(f"{Colors.RED}[-] Invalid number.{Colors.RESET}")
        return False

    selected_backup = backups[selected_idx]
    stop_claude_processes(lang)

    print(f"\n{Colors.CYAN}[*] Restoring from {selected_backup.name}...{Colors.RESET}")

    with zipfile.ZipFile(selected_backup, 'r') as zipf:
        for member in zipf.namelist():
            if member == "cli_home_claude.json":
                with zipf.open(member) as src, open(paths.cli_config_main, "wb") as dst:
                    dst.write(src.read())
                print(f"{Colors.GREEN}  [+] Restored ~/.claude.json{Colors.RESET}")

            elif member == "cli_nested_claude.json":
                paths.cli_config_nested.parent.mkdir(parents=True, exist_ok=True)
                with zipf.open(member) as src, open(paths.cli_config_nested, "wb") as dst:
                    dst.write(src.read())
                print(f"{Colors.GREEN}  [+] Restored ~/.claude/.claude.json{Colors.RESET}")

            elif member == "cli_stats_cache.json":
                with zipf.open(member) as src, open(paths.cli_stats_cache, "wb") as dst:
                    dst.write(src.read())
                print(f"{Colors.GREEN}  [+] Restored ~/.claude/stats-cache.json{Colors.RESET}")

            elif member.startswith("desktop/claude-code-sessions/"):
                rel_path = member[len("desktop/claude-code-sessions/"):]
                target_file = paths.claude_code_sessions / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with zipf.open(member) as src, open(target_file, "wb") as dst:
                    dst.write(src.read())

            elif member.startswith("desktop/"):
                file_name = member[len("desktop/"):]
                if "/" not in file_name:
                    target_file = paths.desktop_dir / file_name
                    paths.desktop_dir.mkdir(parents=True, exist_ok=True)
                    with zipf.open(member) as src, open(target_file, "wb") as dst:
                        dst.write(src.read())
                    print(f"{Colors.GREEN}  [+] Restored Desktop file: {file_name}{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}[+] Restoration completed successfully!{Colors.RESET}")
    return True


def show_status(paths: ClaudePaths, lang: str = "en"):
    """Displays current identifiers and telemetry status."""
    print(f"\n{Colors.YELLOW}{t('status_title', lang)}{Colors.RESET}\n")

    # CLI main
    if paths.cli_config_main.is_file():
        try:
            content = paths.cli_config_main.read_text(encoding="utf-8")
            m_id = re.search(r'"machineID"\s*:\s*"([^"]+)"', content)
            u_id = re.search(r'"userID"\s*:\s*"([^"]+)"', content)
            a_id = re.search(r'"anonymousId"\s*:\s*"([^"]+)"', content)
            print(f"{Colors.CYAN}CLI (~/.claude.json):{Colors.RESET}")
            print(f"  machineID:   {m_id.group(1) if m_id else 'None'}")
            print(f"  userID:      {u_id.group(1) if u_id else 'None'}")
            print(f"  anonymousId: {a_id.group(1) if a_id else 'None'}")
        except Exception as e:
            print(f"{Colors.RED}CLI: Error reading config ({e}){Colors.RESET}")
    else:
        print(f"{Colors.DIM}CLI (~/.claude.json): Not found{Colors.RESET}")

    # CLI nested
    if paths.cli_config_nested.is_file():
        try:
            content = paths.cli_config_nested.read_text(encoding="utf-8")
            m_id = re.search(r'"machineID"\s*:\s*"([^"]+)"', content)
            u_id = re.search(r'"userID"\s*:\s*"([^"]+)"', content)
            print(f"\n{Colors.CYAN}Nested CLI (~/.claude/.claude.json):{Colors.RESET}")
            print(f"  machineID:   {m_id.group(1) if m_id else 'None'}")
            print(f"  userID:      {u_id.group(1) if u_id else 'None'}")
        except Exception as e:
            print(f"{Colors.RED}Nested CLI: Error reading config ({e}){Colors.RESET}")

    # CLI stats cache
    if paths.cli_stats_cache.is_file():
        print(f"\n{Colors.CYAN}CLI Telemetry Stats (~/.claude/stats-cache.json):{Colors.RESET}")
        try:
            st = json.loads(paths.cli_stats_cache.read_text(encoding="utf-8"))
            days = len(st.get("dailyActivity", []))
            print(f"  Activity days recorded: {days}")
        except Exception:
            print(f"  Status: Present ({paths.cli_stats_cache.stat().st_size} bytes)")

    # Desktop App
    print(f"\n{Colors.CYAN}Desktop Application ({paths.desktop_dir.name}):{Colors.RESET}")
    if paths.ant_did.is_file():
        print(f"  ant-did: {paths.ant_did.read_text(encoding='utf-8', errors='ignore').strip()}")
    else:
        print(f"  ant-did: {Colors.DIM}None (unlinked, will be freshly generated on startup){Colors.RESET}")

    if paths.ant_device_registry.is_file():
        reg_text = paths.ant_device_registry.read_text(encoding='utf-8', errors='ignore').strip()
        print(f"  ant-device-registry: {reg_text[:60]}...")
    else:
        print(f"  ant-device-registry: {Colors.DIM}None (unlinked){Colors.RESET}")

    if paths.desktop_config.is_file():
        try:
            cfg = json.loads(paths.desktop_config.read_text(encoding="utf-8"))
            acc = cfg.get("lastKnownAccountUuid")
            print(f"  lastKnownAccountUuid: {acc or 'None'}")
            print(f"  cached OAuth tokens:  {'oauth:tokenCache' in cfg or 'oauth:tokenCacheV2' in cfg}")
        except Exception as e:
            print(f"{Colors.RED}  config.json error: {e}{Colors.RESET}")

    if paths.desktop_local_state.is_file():
        try:
            ls = json.loads(paths.desktop_local_state.read_text(encoding="utf-8"))
            inst_date = ls.get("uninstall_metrics", {}).get("installation_date2", "None")
            print(f"  installation_date2 (Local State): {inst_date}")
        except Exception:
            pass

    if paths.desktop_plan_usage.is_file():
        try:
            sz = paths.desktop_plan_usage.stat().st_size // 1024
            pu = json.loads(paths.desktop_plan_usage.read_text(encoding="utf-8"))
            orgs = set()
            for item in pu.get("history", []):
                if isinstance(item, dict) and "org" in item:
                    orgs.add(item["org"])
            print(f"  plan-usage-history: {sz} KB, contains {len(orgs)} tracked Org UUID(s)")
        except Exception:
            print(f"  plan-usage-history: Present ({paths.desktop_plan_usage.stat().st_size} bytes)")

    if paths.claude_code_sessions.is_dir():
        session_files = list(paths.claude_code_sessions.rglob("*.json"))
        print(f"  claude-code-sessions: {len(session_files)} session files preserved")


def inspect_deep_fingerprint(paths: ClaudePaths, lang: str = "en"):
    """Deep inspection of hardware IDs, OS machine GUID, MAC addresses and ban risks."""
    print(f"\n{Colors.YELLOW}{t('insp_title', lang)}{Colors.RESET}\n")

    os_type = platform.system()
    print(f"{Colors.CYAN}Platform:{Colors.RESET} {platform.platform()} ({platform.machine()})")

    # 1. OS Machine GUID
    sys_guid = "Unknown"
    if os_type == "Windows":
        try:
            out = subprocess.check_output(
                'powershell -NoProfile -Command "(Get-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Cryptography\').MachineGuid"',
                shell=True, text=True, stderr=subprocess.DEVNULL
            ).strip()
            if out:
                sys_guid = out
        except Exception:
            pass
    elif os_type == "Darwin":
        try:
            out = subprocess.check_output(
                "ioreg -rd1 -c IOPlatformExpertDevice | grep -i IOPlatformUUID",
                shell=True, text=True, stderr=subprocess.DEVNULL
            ).strip()
            sys_guid = out
        except Exception:
            pass
    elif os_type == "Linux":
        for p in ("/var/lib/dbus/machine-id", "/etc/machine-id"):
            if os.path.exists(p):
                try:
                    sys_guid = Path(p).read_text().strip()
                    break
                except Exception:
                    pass

    print(f"{Colors.CYAN}OS Machine GUID / Hardware UUID:{Colors.RESET} {sys_guid}")

    # 2. Risk Assessment
    print(f"\n{Colors.YELLOW}Risk Assessment & Recommendations:{Colors.RESET}")
    risks = 0

    if paths.ant_device_registry.is_file():
        print(f"  {Colors.RED}[!] HIGH RISK:{Colors.RESET} ant-device-registry.json is present (machine cryptographically bound to old account).")
        risks += 1
    else:
        print(f"  {Colors.GREEN}[✓] SAFE:{Colors.RESET} ant-device-registry.json is unlinked.")

    if paths.desktop_config.is_file():
        try:
            cfg = json.loads(paths.desktop_config.read_text(encoding="utf-8"))
            if "lastKnownAccountUuid" in cfg:
                print(f"  {Colors.RED}[!] HIGH RISK:{Colors.RESET} config.json retains lastKnownAccountUuid ({cfg['lastKnownAccountUuid']}).")
                risks += 1
            if "oauth:tokenCache" in cfg or "oauth:tokenCacheV2" in cfg:
                print(f"  {Colors.RED}[!] MEDIUM RISK:{Colors.RESET} config.json contains cached session OAuth tokens.")
                risks += 1
        except Exception:
            pass

    if paths.desktop_plan_usage.is_file() and paths.desktop_plan_usage.stat().st_size > 500:
        print(f"  {Colors.RED}[!] MEDIUM RISK:{Colors.RESET} plan-usage-history.json contains logged organization tokens.")
        risks += 1

    if paths.cli_stats_cache.is_file() and paths.cli_stats_cache.stat().st_size > 500:
        print(f"  {Colors.YELLOW}[!] LOW RISK:{Colors.RESET} CLI stats-cache.json contains activity dates across accounts.")
        risks += 1

    if risks == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All clear! Your machine identifiers and telemetry are completely unlinked and sanitized.{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}Found {risks} potential account association risk factor(s). Run option [1] (Safe Anti-Ban Reset) to clear them.{Colors.RESET}")


def perform_clean(paths: ClaudePaths, wipe_sessions=False, dry_run=False, lang: str = "en"):
    """
    Executes deep anti-ban reset and telemetry sanitizer.
    - Default mode (wipe_sessions=False): preserves user chat sessions and projects!
    - Full mode (wipe_sessions=True): factory reset wiping all session history.
    - Dry-run mode: prints planned changes without writing anything.
    """
    print_banner(lang)
    if dry_run:
        print(f"\n{Colors.YELLOW}{t('dry_run_notice', lang)}{Colors.RESET}")

    mode_text = "FULL FACTORY RESET" if wipe_sessions else "SAFE ANTI-BAN RESET (SESSIONS PRESERVED)"
    print(f"\n{Colors.YELLOW}[*] Mode: {mode_text}{Colors.RESET}\n")

    # Step 1: Stop processes
    if not dry_run:
        stop_claude_processes(lang)

    # Step 2: Backup
    print(f"\n{Colors.CYAN}{t('step_1', lang)}{Colors.RESET}")
    backup_file = None
    if not dry_run:
        backup_file = create_backup(paths, tag="pre-reset", lang=lang)
    else:
        print(f"  [Dry-run] Would create safety backup archive in {paths.backup_dir}")

    # Step 3: CLI Reset
    print(f"\n{Colors.CYAN}{t('step_2', lang)}{Colors.RESET}")
    new_cli_machine = random_sha256_hex()
    new_cli_user = random_sha256_hex()
    new_anon_id = f"claudecode_{secrets.token_hex(16)}"

    if paths.cli_config_main.is_file():
        try:
            raw = paths.cli_config_main.read_text(encoding="utf-8")
            raw = re.sub(r'("machineID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_cli_machine}"', raw)
            raw = re.sub(r'("userID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_cli_user}"', raw)
            raw = re.sub(r'("anonymousId"\s*:\s*)"[^"]+"', rf'\g<1>"{new_anon_id}"', raw)
            if not dry_run:
                # Write strictly UTF-8 NO-BOM
                paths.cli_config_main.write_text(raw, encoding="utf-8")
            print(f"{Colors.GREEN}  [+] New CLI machineID: {new_cli_machine}{Colors.RESET}")
            print(f"{Colors.GREEN}  [+] New CLI userID:    {new_cli_user}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}  [-] Error updating ~/.claude.json: {e}{Colors.RESET}")

    if paths.cli_config_nested.is_file():
        try:
            raw_nested = paths.cli_config_nested.read_text(encoding="utf-8")
            new_nested_machine = random_sha256_hex()
            new_nested_user = random_sha256_hex()
            raw_nested = re.sub(r'("machineID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_nested_machine}"', raw_nested)
            raw_nested = re.sub(r'("userID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_nested_user}"', raw_nested)
            if not dry_run:
                paths.cli_config_nested.write_text(raw_nested, encoding="utf-8")
            print(f"{Colors.GREEN}  [+] New Nested CLI machineID: {new_nested_machine}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}  [-] Error updating nested config: {e}{Colors.RESET}")

    # Remove failed telemetry events in ~/.claude/telemetry
    if paths.cli_telemetry_dir.is_dir() and not dry_run:
        for event_file in paths.cli_telemetry_dir.glob("1p_failed_events.*.json"):
            try:
                event_file.unlink(missing_ok=True)
            except Exception:
                pass
        print(f"{Colors.GREEN}  [+] Cleared failed CLI telemetry event cache.{Colors.RESET}")

    # Clean CLI stats cache & daemon status
    if paths.cli_stats_cache.is_file() and not dry_run:
        try:
            paths.cli_stats_cache.write_text(json.dumps({"version": 4, "dailyActivity": []}), encoding="utf-8")
            print(f"{Colors.GREEN}  [+] Cleared CLI stats-cache.json.{Colors.RESET}")
        except Exception:
            pass

    for d_file in (paths.cli_daemon_status, paths.cli_daemon_cooldown):
        if d_file.is_file() and not dry_run:
            try:
                d_file.unlink(missing_ok=True)
            except Exception:
                pass

    # Step 4: Desktop device identity and registries
    print(f"\n{Colors.CYAN}{t('step_3', lang)}{Colors.RESET}")
    if paths.desktop_dir.is_dir():
        if paths.ant_did.is_file():
            if not dry_run:
                paths.ant_did.unlink(missing_ok=True)
            print(f"{Colors.GREEN}  [+] Removed ant-did (Claude will generate a fresh clean ID on startup).{Colors.RESET}")

        if paths.ant_device_registry.is_file():
            if not dry_run:
                paths.ant_device_registry.unlink(missing_ok=True)
            print(f"{Colors.GREEN}  [+] Removed ant-device-registry.json (hardware account linkage severed).{Colors.RESET}")

        if paths.remote_control_state.is_file():
            if not dry_run:
                paths.remote_control_state.unlink(missing_ok=True)
            print(f"{Colors.GREEN}  [+] Removed remote-control-state.json.{Colors.RESET}")

        if paths.ccd_ids.is_file():
            new_salt = str(uuid.uuid4())
            if not dry_run:
                try:
                    paths.ccd_ids.write_text(json.dumps({"salt": new_salt}), encoding="utf-8")
                except Exception:
                    pass
            print(f"{Colors.GREEN}  [+] Generated new ccd-ids salt: {new_salt}{Colors.RESET}")

        for b_file in (paths.bridge_state, paths.buddy_tokens):
            if b_file.is_file():
                if not dry_run:
                    b_file.unlink(missing_ok=True)
                print(f"{Colors.GREEN}  [+] Cleared {b_file.name}.{Colors.RESET}")

    # Step 5: Clean config.json & Telemetry
    print(f"\n{Colors.CYAN}{t('step_4', lang)}{Colors.RESET}")
    if paths.desktop_config.is_file():
        try:
            cfg = json.loads(paths.desktop_config.read_text(encoding="utf-8"))
            keys_to_remove = [
                "lastKnownAccountUuid",
                "oauth:tokenCache",
                "oauth:tokenCacheV2",
                "chromeExtension.pairedDeviceId",
                "hasTrackedInitialActivation"
            ]
            keys_to_remove.extend([k for k in cfg.keys() if k.startswith("dxt:allowlist")])

            for k in keys_to_remove:
                cfg.pop(k, None)

            now_ms = int(datetime.now().timestamp() * 1000)
            if "first_launch_at" in cfg:
                cfg["first_launch_at"] = now_ms
            if "version_first_launch" in cfg and isinstance(cfg["version_first_launch"], dict):
                cfg["version_first_launch"]["at"] = now_ms

            if not dry_run:
                # Strictly UTF-8 NO-BOM
                paths.desktop_config.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{Colors.GREEN}  [+] Sanitized config.json: removed stale tokens and account linkage.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}  [-] Error updating config.json: {e}{Colors.RESET}")

    # Step 6: Deep telemetry: plan-usage-history, Local State, Sentry, Crashpad
    print(f"\n{Colors.CYAN}{t('step_6', lang)}{Colors.RESET}")
    if paths.desktop_plan_usage.is_file():
        if not dry_run:
            try:
                paths.desktop_plan_usage.write_text(json.dumps({"history": []}), encoding="utf-8")
            except Exception:
                pass
        print(f"{Colors.GREEN}  [+] Sanitized plan-usage-history.json (purged historical Org UUID tracking).{Colors.RESET}")

    if paths.desktop_local_state.is_file():
        try:
            ls = json.loads(paths.desktop_local_state.read_text(encoding="utf-8"))
            if "uninstall_metrics" in ls:
                ls["uninstall_metrics"]["installation_date2"] = str(int(datetime.now().timestamp()))
            if not dry_run:
                paths.desktop_local_state.write_text(json.dumps(ls), encoding="utf-8")
            print(f"{Colors.GREEN}  [+] Reset installation_date2 in Local State to current time.{Colors.RESET}")
        except Exception:
            pass

    for db_f in (paths.desktop_perf_db, paths.desktop_perf_journal):
        if db_f.is_file():
            if not dry_run:
                db_f.unlink(missing_ok=True)
            print(f"{Colors.GREEN}  [+] Cleared {db_f.name}.{Colors.RESET}")

    if paths.desktop_crashpad.is_dir() and not dry_run:
        for cf in paths.desktop_crashpad.rglob("*.dmp"):
            try:
                cf.unlink(missing_ok=True)
            except Exception:
                pass
        print(f"{Colors.GREEN}  [+] Purged Crashpad minidumps.{Colors.RESET}")

    if paths.sentry_dir.is_dir() and not dry_run:
        for sf in paths.sentry_dir.rglob("*"):
            if sf.is_file():
                try:
                    sf.unlink(missing_ok=True)
                except Exception:
                    pass
        print(f"{Colors.GREEN}  [+] Cleared Sentry crash report & telemetry queue.{Colors.RESET}")

    if paths.logs_dir.is_dir() and not dry_run:
        for lf in paths.logs_dir.glob("*.log"):
            try:
                lf.unlink(missing_ok=True)
            except Exception:
                pass
        print(f"{Colors.GREEN}  [+] Cleared session log files.{Colors.RESET}")

    # Step 7: Sessions handling
    print(f"\n{Colors.CYAN}{t('step_5', lang)}{Colors.RESET}")
    if wipe_sessions:
        if paths.claude_code_sessions.is_dir() and not dry_run:
            shutil.rmtree(paths.claude_code_sessions, ignore_errors=True)
        print(f"{Colors.YELLOW}  [!] {t('sessions_deleted', lang)}{Colors.RESET}")
    else:
        s_count = 0
        if paths.claude_code_sessions.is_dir():
            s_count = len(list(paths.claude_code_sessions.rglob("*.json")))
        print(f"{Colors.GREEN}  [+] {t('sessions_preserved', lang, count=s_count)}{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}======================================================================{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}          {t('completed', lang)}          {Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}======================================================================{Colors.RESET}")
    if backup_file:
        print(f"{t('backup_saved', lang)} {Colors.CYAN}{backup_file}{Colors.RESET}\n")


def launch_claude(paths: ClaudePaths):
    """Launches the Claude Desktop application."""
    if paths.desktop_exe.is_file():
        print(f"{Colors.CYAN}[*] Launching Claude Desktop ({paths.desktop_exe})...{Colors.RESET}")
        if platform.system() == "Windows":
            subprocess.Popen([str(paths.desktop_exe)], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Claude"])
        else:
            subprocess.Popen([str(paths.desktop_exe)])
    else:
        print(f"{Colors.YELLOW}[!] Claude executable not found at {paths.desktop_exe}. Please open Claude manually.{Colors.RESET}")


def language_picker(paths: ClaudePaths, current_lang: str) -> str:
    """Interactive language selector."""
    print(f"\n{Colors.YELLOW}--- SELECT LANGUAGE / ВЫБЕРИТЕ ЯЗЫК ---{Colors.RESET}")
    print("  [1] English (English)")
    print("  [2] Русский (Russian)")
    print("  [3] Español (Spanish)")
    print("  [4] 简体中文 (Simplified Chinese)")
    print("  [0] Keep current\n")

    c = input("Select [1-4]: ").strip()
    mapping = {"1": "en", "2": "ru", "3": "es", "4": "zh"}
    chosen = mapping.get(c, current_lang)
    paths.set_language(chosen)
    return chosen


def interactive_menu(paths: ClaudePaths):
    """Terminal interactive menu with multi-language support."""
    active_lang = paths.get_language()

    while True:
        print_banner(active_lang)
        print(f"{Colors.BOLD}{t('menu_header', active_lang)}{Colors.RESET}")
        print(f"  {Colors.GREEN}{t('menu_1', active_lang)}{Colors.RESET}")
        print(f"  {Colors.CYAN}{t('menu_2', active_lang)}{Colors.RESET}")
        print(f"  {Colors.BLUE}{t('menu_3', active_lang)}{Colors.RESET}")
        print(f"  {Colors.YELLOW}{t('menu_4', active_lang)}{Colors.RESET}")
        print(f"  {Colors.HEADER}{t('menu_5', active_lang)}{Colors.RESET}")
        print(f"  {Colors.RED}{t('menu_6', active_lang)}{Colors.RESET}")
        print(f"  {Colors.WHITE}{t('menu_7', active_lang)}{Colors.RESET}")
        print(f"  {Colors.CYAN}{t('menu_lang', active_lang)}{Colors.RESET}")
        print(f"  {Colors.DIM}{t('menu_exit', active_lang)}{Colors.RESET}\n")

        try:
            choice = input(f"{Colors.BOLD}{t('prompt_choice', active_lang)}{Colors.RESET}").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if choice == "1":
            confirm = input(f"\n{Colors.YELLOW}{t('confirm_safe', active_lang)}{Colors.RESET}").strip().lower()
            if confirm in ("y", "yes", "д", "да", "s", "si", "是"):
                perform_clean(paths, wipe_sessions=False, lang=active_lang)
            else:
                print(f"{Colors.DIM}{t('cancelled', active_lang)}{Colors.RESET}")
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "2":
            show_status(paths, lang=active_lang)
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "3":
            inspect_deep_fingerprint(paths, lang=active_lang)
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "4":
            stop_claude_processes(active_lang)
            create_backup(paths, tag="manual", lang=active_lang)
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "5":
            restore_backup(paths, lang=active_lang)
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "6":
            print(f"\n{Colors.RED}{Colors.BOLD}{t('confirm_full_warn', active_lang)}{Colors.RESET}")
            confirm = input(f"{Colors.RED}{t('confirm_full_prompt', active_lang)}{Colors.RESET}").strip()
            if confirm == "YES":
                perform_clean(paths, wipe_sessions=True, lang=active_lang)
            else:
                print(f"{Colors.DIM}{t('cancelled', active_lang)}{Colors.RESET}")
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice == "7":
            launch_claude(paths)
            input(f"\n{Colors.DIM}{t('press_enter', active_lang)}{Colors.RESET}")

        elif choice in ("L", "LANG", "LANGUAGE"):
            active_lang = language_picker(paths, active_lang)

        elif choice == "0":
            print(f"\n{Colors.CYAN}Goodbye! / До свидания! / ¡Adiós! / 再见！{Colors.RESET}")
            break
        else:
            print(f"{Colors.RED}Invalid option.{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="Claude Anti-Ban & Telemetry Cleaner - Cross-platform hardware ID reset & privacy tool."
    )
    parser.add_argument("--safe", action="store_true", help="Perform safe anti-ban reset (preserves sessions).")
    parser.add_argument("--full", action="store_true", help="Perform full factory reset (wipes session records).")
    parser.add_argument("--backup", action="store_true", help="Create a backup zip archive without modifying files.")
    parser.add_argument("--restore", action="store_true", help="Restore from an existing backup.")
    parser.add_argument("--status", action="store_true", help="Show current hardware and telemetry IDs.")
    parser.add_argument("--inspect", action="store_true", help="Deep audit of hardware identifiers and ban risks.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without modifying any files.")
    parser.add_argument("--lang", choices=["en", "ru", "es", "zh"], help="Set interface language.")
    parser.add_argument("--launch", action="store_true", help="Launch Claude Desktop after operation.")

    args = parser.parse_args()
    paths = ClaudePaths()

    active_lang = args.lang or paths.get_language()
    if args.lang:
        paths.set_language(args.lang)

    if args.status:
        show_status(paths, lang=active_lang)
    elif args.inspect:
        inspect_deep_fingerprint(paths, lang=active_lang)
    elif args.backup:
        stop_claude_processes(active_lang)
        create_backup(paths, tag="manual", lang=active_lang)
    elif args.restore:
        restore_backup(paths, lang=active_lang)
    elif args.safe:
        perform_clean(paths, wipe_sessions=False, dry_run=args.dry_run, lang=active_lang)
        if args.launch and not args.dry_run:
            launch_claude(paths)
    elif args.full:
        perform_clean(paths, wipe_sessions=True, dry_run=args.dry_run, lang=active_lang)
        if args.launch and not args.dry_run:
            launch_claude(paths)
    else:
        if not sys.stdin.isatty():
            parser.print_help()
        else:
            interactive_menu(paths)


if __name__ == "__main__":
    main()
