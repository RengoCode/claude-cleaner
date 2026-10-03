#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude Anti-Ban & Telemetry Cleaner - Graphical User Interface (GUI)
Modern, zero-dependency desktop UI built with Python's standard library tkinter.
Bilingual support: English & Russian.
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

# Add script dir to path so we can import claude_reset functions directly
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import claude_reset

# Color Palette (Modern Dark Theme)
BG_DARK = "#181825"
BG_CARD = "#1e1e2e"
BG_INPUT = "#313244"
TEXT_WHITE = "#cdd6f4"
TEXT_MUTED = "#a6adc8"
ACCENT_GREEN = "#a6e3a1"
ACCENT_BLUE = "#89b4fa"
ACCENT_YELLOW = "#f9e2af"
ACCENT_RED = "#f38ba8"
BORDER_COLOR = "#45475a"

# GUI Translations
GUI_I18N = {
    "en": {
        "title": "Claude Anti-Ban & Telemetry Cleaner",
        "subtitle": "Break device fingerprinting, reset telemetry & preserve local sessions",
        "status_card": "Current Machine Identifiers & Telemetry Status",
        "refresh": "🔄 Refresh Status",
        "lbl_mid": "CLI machineID:",
        "lbl_uid": "CLI userID:",
        "lbl_did": "Desktop ant-did:",
        "lbl_reg": "Device Registry:",
        "lbl_plan": "Plan Usage:",
        "lbl_sess": "Saved Sessions:",
        "lbl_sessions_safe": "{count} session files (PRESERVED)",
        "actions_card": "Operations",
        "btn_safe_reset": "🚀 Safe Anti-Ban Reset (Keep Sessions)",
        "btn_safe_desc": "Resets hardware IDs, device keys & telemetry. Chat histories stay safe.",
        "btn_inspect": "🔍 Deep Hardware & Fingerprint Audit",
        "btn_backup": "🛡️ Create Backup ZIP Now",
        "btn_restore": "🔄 Restore From Backup",
        "btn_full_reset": "⚠️ Full Factory Reset (Wipe All)",
        "btn_launch": "▶️ Launch Claude Desktop",
        "console_card": "Operation Log",
        "lang_btn": "🇷🇺 Русский",
        "confirm_safe_title": "Confirm Safe Anti-Ban Reset",
        "confirm_safe_msg": "This will reset all hardware identifiers and deep telemetry records.\n\nAll your saved chat turns and local sessions will be PRESERVED.\n\nProceed?",
        "confirm_full_title": "⚠️ Confirm Full Factory Reset",
        "confirm_full_msg": "WARNING: This will permanently wipe all local sessions and chat turns in addition to hardware IDs!\n\nAre you absolutely sure?",
        "reset_success_title": "Reset Completed",
        "reset_success_msg": "Anti-Ban reset and deep telemetry sanitization completed successfully!",
        "backup_success_title": "Backup Created",
        "backup_success_msg": "Safety backup saved successfully at:\n{path}",
        "restore_title": "Select Backup to Restore",
        "no_backups": "No backups found in {dir}",
    },
    "ru": {
        "title": "Claude Anti-Ban & Очистка Телеметрии",
        "subtitle": "Разрыв связывания аккаунтов, сброс ID железа с сохранением ваших сессий",
        "status_card": "Текущие идентификаторы устройства и статус телеметрии",
        "refresh": "🔄 Обновить статус",
        "lbl_mid": "CLI machineID:",
        "lbl_uid": "CLI userID:",
        "lbl_did": "Desktop ant-did:",
        "lbl_reg": "Аппаратный реестр:",
        "lbl_plan": "История тарифа:",
        "lbl_sess": "Сохранённые сессии:",
        "lbl_sessions_safe": "{count} файлов сессий (СОХРАНЯЮТСЯ)",
        "actions_card": "Действия",
        "btn_safe_reset": "🚀 Безопасный Anti-Ban сброс (Сессии сохраняются)",
        "btn_safe_desc": "Сбрасывает ID железа, ключи и телеметрию. Вся переписка остаётся на месте.",
        "btn_inspect": "🔍 Глубокий аудит отпечатка системы",
        "btn_backup": "🛡️ Создать резервную копию ZIP",
        "btn_restore": "🔄 Восстановить из резервной копии",
        "btn_full_reset": "⚠️ Полный Factory Reset (с удалением сессий)",
        "btn_launch": "▶️ Запустить Claude Desktop",
        "console_card": "Журнал выполнения",
        "lang_btn": "🇬🇧 English",
        "confirm_safe_title": "Подтверждение безопасного сброса",
        "confirm_safe_msg": "Будут сброшены все аппаратные идентификаторы и глубокая телеметрия.\n\nВсе ваши локальные сессии и диалоги БУДУТ СОХРАНЕНЫ.\n\nПродолжить?",
        "confirm_full_title": "⚠️ Подтверждение полного сброса",
        "confirm_full_msg": "ВНИМАНИЕ: Будут безвозвратно удалены все локальные сессии и диалоги Claude Code!\n\nВы уверены?",
        "reset_success_title": "Сброс завершён",
        "reset_success_msg": "Анти-бан сброс и очистка телеметрии успешно выполнены!",
        "backup_success_title": "Резервная копия создана",
        "backup_success_msg": "Резервная копия успешно сохранена в:\n{path}",
        "restore_title": "Выберите резервную копию для восстановления",
        "no_backups": "Резервные копии не найдены в {dir}",
    }
}


class ClaudeCleanerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Resolve initial language
        saved_lang = claude_reset.get_system_lang()
        self.lang = "ru" if saved_lang == "ru" else "en"

        self.title("Claude Anti-Ban & Telemetry Cleaner")
        self.geometry("860x780")
        self.minsize(800, 700)
        self.configure(bg=BG_DARK)

        # Style configuration
        self.setup_styles()

        # Build interface
        self.build_ui()

        # Load initial telemetry status
        self.refresh_status()

    def tr(self, key):
        return GUI_I18N.get(self.lang, {}).get(key, key)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG_DARK, foreground=TEXT_WHITE, font=("Segoe UI", 10))
        style.configure("Card.TFrame", background=BG_CARD, relief="solid", borderwidth=1)
        style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_WHITE, font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", background=BG_DARK, foreground=TEXT_MUTED, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=BG_CARD, foreground=ACCENT_BLUE, font=("Segoe UI", 11, "bold"))
        style.configure("Key.TLabel", background=BG_CARD, foreground=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("Val.TLabel", background=BG_CARD, foreground=TEXT_WHITE, font=("Segoe UI", 9))
        style.configure("ValGreen.TLabel", background=BG_CARD, foreground=ACCENT_GREEN, font=("Segoe UI", 9, "bold"))
        style.configure("ValRed.TLabel", background=BG_CARD, foreground=ACCENT_RED, font=("Segoe UI", 9))

    def build_ui(self):
        # Top Bar
        top_frame = tk.Frame(self, bg=BG_DARK, padx=20, pady=12)
        top_frame.pack(fill=tk.X)

        titles_frame = tk.Frame(top_frame, bg=BG_DARK)
        titles_frame.pack(side=tk.LEFT)

        self.lbl_title = tk.Label(titles_frame, text=self.tr("title"), bg=BG_DARK, fg=TEXT_WHITE, font=("Segoe UI", 15, "bold"))
        self.lbl_title.pack(anchor=tk.W)

        self.lbl_sub = tk.Label(titles_frame, text=self.tr("subtitle"), bg=BG_DARK, fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.lbl_sub.pack(anchor=tk.W)

        self.btn_lang = tk.Button(top_frame, text=self.tr("lang_btn"), bg=BG_CARD, fg=TEXT_WHITE,
                                  activebackground=BG_INPUT, activeforeground=TEXT_WHITE,
                                  relief=tk.FLAT, padx=12, pady=6, font=("Segoe UI", 9, "bold"),
                                  command=self.toggle_language)
        self.btn_lang.pack(side=tk.RIGHT)

        # Main scrollable or vertical layout
        content_frame = tk.Frame(self, bg=BG_DARK, padx=20, pady=5)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Status Card
        self.status_box = tk.LabelFrame(content_frame, text=f"  {self.tr('status_card')}  ",
                                        bg=BG_CARD, fg=ACCENT_BLUE, font=("Segoe UI", 10, "bold"),
                                        padx=15, pady=10, relief=tk.GROOVE)
        self.status_box.pack(fill=tk.X, pady=(0, 10))

        status_grid = tk.Frame(self.status_box, bg=BG_CARD)
        status_grid.pack(fill=tk.X)

        # Labels
        self.lbl_mid_key = tk.Label(status_grid, text=self.tr("lbl_mid"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        self.lbl_mid_key.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_mid_val = tk.Label(status_grid, text="...", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 9))
        self.lbl_mid_val.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        self.lbl_uid_key = tk.Label(status_grid, text=self.tr("lbl_uid"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        self.lbl_uid_key.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_uid_val = tk.Label(status_grid, text="...", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 9))
        self.lbl_uid_val.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        self.lbl_did_key = tk.Label(status_grid, text=self.tr("lbl_did"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        self.lbl_did_key.grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_did_val = tk.Label(status_grid, text="...", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 9))
        self.lbl_did_val.grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)

        self.lbl_plan_key = tk.Label(status_grid, text=self.tr("lbl_plan"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        self.lbl_plan_key.grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_plan_val = tk.Label(status_grid, text="...", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 9))
        self.lbl_plan_val.grid(row=3, column=1, sticky=tk.W, padx=10, pady=2)

        self.lbl_sess_key = tk.Label(status_grid, text=self.tr("lbl_sess"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        self.lbl_sess_key.grid(row=4, column=0, sticky=tk.W, pady=2)
        self.lbl_sess_val = tk.Label(status_grid, text="...", bg=BG_CARD, fg=ACCENT_GREEN, font=("Segoe UI", 9, "bold"))
        self.lbl_sess_val.grid(row=4, column=1, sticky=tk.W, padx=10, pady=2)

        self.btn_refresh = tk.Button(self.status_box, text=self.tr("refresh"), bg=BG_INPUT, fg=TEXT_WHITE,
                                     activebackground=BORDER_COLOR, activeforeground=TEXT_WHITE,
                                     relief=tk.FLAT, padx=10, pady=4, font=("Segoe UI", 8),
                                     command=self.refresh_status)
        self.btn_refresh.pack(anchor=tk.E, pady=(5, 0))

        # 2. Operations Card
        self.actions_box = tk.LabelFrame(content_frame, text=f"  {self.tr('actions_card')}  ",
                                         bg=BG_CARD, fg=ACCENT_GREEN, font=("Segoe UI", 10, "bold"),
                                         padx=15, pady=10, relief=tk.GROOVE)
        self.actions_box.pack(fill=tk.X, pady=(0, 10))

        # Safe Reset Prominent Button
        safe_frame = tk.Frame(self.actions_box, bg=BG_CARD)
        safe_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_safe = tk.Button(safe_frame, text=self.tr("btn_safe_reset"),
                                  bg="#22c55e", fg="#0f172a",
                                  activebackground="#16a34a", activeforeground="#ffffff",
                                  font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=15, pady=8,
                                  cursor="hand2", command=self.on_safe_reset)
        self.btn_safe.pack(fill=tk.X)

        self.lbl_safe_desc = tk.Label(safe_frame, text=self.tr("btn_safe_desc"), bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 8))
        self.lbl_safe_desc.pack(anchor=tk.W, pady=(4, 0))

        # Secondary Actions Grid
        sec_grid = tk.Frame(self.actions_box, bg=BG_CARD)
        sec_grid.pack(fill=tk.X)
        sec_grid.columnconfigure(0, weight=1)
        sec_grid.columnconfigure(1, weight=1)

        self.btn_insp = tk.Button(sec_grid, text=self.tr("btn_inspect"), bg=BG_INPUT, fg=TEXT_WHITE,
                                  activebackground=BORDER_COLOR, activeforeground=TEXT_WHITE,
                                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6,
                                  command=self.on_inspect)
        self.btn_insp.grid(row=0, column=0, padx=(0, 5), pady=4, sticky=tk.EW)

        self.btn_bak = tk.Button(sec_grid, text=self.tr("btn_backup"), bg=BG_INPUT, fg=TEXT_WHITE,
                                 activebackground=BORDER_COLOR, activeforeground=TEXT_WHITE,
                                 font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6,
                                 command=self.on_backup)
        self.btn_bak.grid(row=0, column=1, padx=(5, 0), pady=4, sticky=tk.EW)

        self.btn_rest = tk.Button(sec_grid, text=self.tr("btn_restore"), bg=BG_INPUT, fg=TEXT_WHITE,
                                  activebackground=BORDER_COLOR, activeforeground=TEXT_WHITE,
                                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6,
                                  command=self.on_restore)
        self.btn_rest.grid(row=1, column=0, padx=(0, 5), pady=4, sticky=tk.EW)

        self.btn_launch = tk.Button(sec_grid, text=self.tr("btn_launch"), bg=BG_INPUT, fg=TEXT_WHITE,
                                    activebackground=BORDER_COLOR, activeforeground=TEXT_WHITE,
                                    font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6,
                                    command=self.on_launch)
        self.btn_launch.grid(row=1, column=1, padx=(5, 0), pady=4, sticky=tk.EW)

        # Danger Zone / Factory Reset
        self.btn_full = tk.Button(self.actions_box, text=self.tr("btn_full_reset"),
                                  bg=BG_CARD, fg=ACCENT_RED,
                                  activebackground=BG_INPUT, activeforeground=ACCENT_RED,
                                  font=("Segoe UI", 8), relief=tk.FLAT, pady=4,
                                  command=self.on_full_reset)
        self.btn_full.pack(anchor=tk.E, pady=(8, 0))

        # 3. Log Console Card
        self.console_box = tk.LabelFrame(content_frame, text=f"  {self.tr('console_card')}  ",
                                         bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold"),
                                         padx=10, pady=5, relief=tk.GROOVE)
        self.console_box.pack(fill=tk.BOTH, expand=True)

        self.txt_log = scrolledtext.ScrolledText(self.console_box, bg=BG_DARK, fg=TEXT_WHITE,
                                                 insertbackground=TEXT_WHITE, font=("Consolas", 9),
                                                 relief=tk.FLAT, height=10)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)

    def toggle_language(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        claude_reset.CURRENT_LANG = self.lang
        claude_reset.save_language_preference(self.lang)

        # Update all texts
        self.lbl_title.config(text=self.tr("title"))
        self.lbl_sub.config(text=self.tr("subtitle"))
        self.btn_lang.config(text=self.tr("lang_btn"))
        self.status_box.config(text=f"  {self.tr('status_card')}  ")
        self.actions_box.config(text=f"  {self.tr('actions_card')}  ")
        self.console_box.config(text=f"  {self.tr('console_card')}  ")
        self.btn_refresh.config(text=self.tr("refresh"))
        self.lbl_mid_key.config(text=self.tr("lbl_mid"))
        self.lbl_uid_key.config(text=self.tr("lbl_uid"))
        self.lbl_did_key.config(text=self.tr("lbl_did"))
        self.lbl_plan_key.config(text=self.tr("lbl_plan"))
        self.lbl_sess_key.config(text=self.tr("lbl_sess"))
        self.btn_safe.config(text=self.tr("btn_safe_reset"))
        self.lbl_safe_desc.config(text=self.tr("btn_safe_desc"))
        self.btn_insp.config(text=self.tr("btn_inspect"))
        self.btn_bak.config(text=self.tr("btn_backup"))
        self.btn_rest.config(text=self.tr("btn_restore"))
        self.btn_full.config(text=self.tr("btn_full_reset"))
        self.btn_launch.config(text=self.tr("btn_launch"))

        self.refresh_status()

    def refresh_status(self):
        paths = claude_reset.get_paths()

        # 1. CLI machineID and userID
        cli_1 = paths["cli_config_1"]
        mid = "None"
        uid = "None"
        if cli_1.exists():
            try:
                with open(cli_1, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    mid = data.get("machineID", "None")
                    uid = data.get("userID", "None")
            except Exception:
                mid = "Error reading"
                uid = "Error reading"

        if len(mid) > 32:
            self.lbl_mid_val.config(text=f"{mid[:16]}...{mid[-8:]} (64 chars)")
        else:
            self.lbl_mid_val.config(text=mid)

        if len(uid) > 32:
            self.lbl_uid_val.config(text=f"{uid[:16]}...{uid[-8:]} (64 chars)")
        else:
            self.lbl_uid_val.config(text=uid)

        # 2. Desktop ant-did
        did_file = paths["desktop_ant_did"]
        if did_file.exists():
            self.lbl_did_val.config(text="PRESENT (Hardware cookie bound)", fg=ACCENT_YELLOW)
        else:
            self.lbl_did_val.config(text="CLEAN (No tracking cookie)", fg=ACCENT_GREEN)

        # 3. Plan usage
        plan_file = paths["desktop_plan_usage"]
        if plan_file.exists():
            sz = plan_file.stat().st_size
            self.lbl_plan_val.config(text=f"Logged ({sz} bytes)", fg=ACCENT_YELLOW)
        else:
            self.lbl_plan_val.config(text="CLEAN", fg=ACCENT_GREEN)

        # 4. Sessions count
        sess_dir = paths["desktop_sessions"]
        sess_count = 0
        if sess_dir.exists():
            sess_count = len(list(sess_dir.rglob("*.json")))

        self.lbl_sess_val.config(text=self.tr("lbl_sessions_safe").format(count=sess_count))

    def run_async(self, target, *args):
        def worker():
            try:
                target(*args)
            except Exception as e:
                self.log(f"[ERROR] {e}")
            finally:
                self.refresh_status()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def on_safe_reset(self):
        if not messagebox.askyesno(self.tr("confirm_safe_title"), self.tr("confirm_safe_msg")):
            return

        def task():
            self.log("\n=======================================================")
            self.log("[*] Starting Safe Anti-Ban Reset...")
            claude_reset.CURRENT_LANG = self.lang

            # Intercept print to console
            old_print = claude_reset.print_step
            claude_reset.print_step = lambda msg, c=None: self.log(f"[*] {msg}")

            try:
                claude_reset.kill_claude_processes()
                claude_reset.create_backup("pre-reset")
                claude_reset.reset_cli_ids()
                claude_reset.reset_desktop_binding()
                claude_reset.sanitize_config_json()
                claude_reset.sanitize_plan_usage_and_metrics()
                claude_reset.handle_sessions(wipe_sessions=False)
                self.log("[+] Anti-Ban Reset completed successfully!")
                messagebox.showinfo(self.tr("reset_success_title"), self.tr("reset_success_msg"))
            finally:
                claude_reset.print_step = old_print

        self.run_async(task)

    def on_full_reset(self):
        if not messagebox.askyesno(self.tr("confirm_full_title"), self.tr("confirm_full_msg")):
            return

        def task():
            self.log("\n=======================================================")
            self.log("[!] Starting Full Factory Reset (Wiping Sessions)...")
            claude_reset.CURRENT_LANG = self.lang
            try:
                claude_reset.perform_clean(full_clean=True)
                self.log("[+] Full Factory Reset completed!")
                messagebox.showinfo(self.tr("reset_success_title"), self.tr("reset_success_msg"))
            except Exception as e:
                self.log(f"[-] Error: {e}")

        self.run_async(task)

    def on_backup(self):
        def task():
            self.log("\n[*] Creating safety backup archive...")
            p = claude_reset.create_backup("manual")
            if p:
                self.log(f"[+] Backup saved: {p}")
                messagebox.showinfo(self.tr("backup_success_title"), self.tr("backup_success_msg").format(path=p))

        self.run_async(task)

    def on_restore(self):
        backups = claude_reset.list_backups()
        if not backups:
            p = claude_reset.get_paths()["backups_dir"]
            messagebox.showinfo(self.tr("restore_title"), self.tr("no_backups").format(dir=p))
            return

        # Restore Dialog Window
        dlg = tk.Toplevel(self)
        dlg.title(self.tr("restore_title"))
        dlg.geometry("520x360")
        dlg.configure(bg=BG_CARD)

        tk.Label(dlg, text=self.tr("restore_title"), bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 11, "bold")).pack(pady=10)

        listbox = tk.Listbox(dlg, bg=BG_INPUT, fg=TEXT_WHITE, font=("Consolas", 9), selectmode=tk.SINGLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        for b in backups:
            listbox.insert(tk.END, b.name)

        def do_restore():
            sel = listbox.curselection()
            if not sel:
                return
            chosen_backup = backups[sel[0]]
            dlg.destroy()

            def task():
                self.log(f"\n[*] Restoring from {chosen_backup.name}...")
                claude_reset.restore_backup(chosen_backup)
                self.log("[+] Restoration completed successfully!")
                messagebox.showinfo("Restore Completed", f"Successfully restored from:\n{chosen_backup.name}")

            self.run_async(task)

        btn_box = tk.Frame(dlg, bg=BG_CARD)
        btn_box.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(btn_box, text="Restore", bg=ACCENT_GREEN, fg="#000", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=15, pady=5, command=do_restore).pack(side=tk.RIGHT)
        tk.Button(btn_box, text="Cancel", bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=15, pady=5, command=dlg.destroy).pack(side=tk.RIGHT, padx=10)

    def on_inspect(self):
        # Deep audit dialog
        dlg = tk.Toplevel(self)
        dlg.title(self.tr("btn_inspect"))
        dlg.geometry("640x480")
        dlg.configure(bg=BG_CARD)

        tk.Label(dlg, text="Deep Hardware & Fingerprint Audit", bg=BG_CARD, fg=ACCENT_BLUE, font=("Segoe UI", 12, "bold")).pack(pady=10)

        txt = scrolledtext.ScrolledText(dlg, bg=BG_DARK, fg=TEXT_WHITE, font=("Consolas", 9), relief=tk.FLAT)
        txt.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Gather audit info
        paths = claude_reset.get_paths()
        txt.insert(tk.END, f"Operating System: {sys.platform} ({os.name})\n")

        guid = claude_reset.inspect_os_machine_guid()
        txt.insert(tk.END, f"OS Machine GUID:  {guid}\n\n")

        txt.insert(tk.END, "--- Anthropic Telemetry Target Paths ---\n")
        for k, v in paths.items():
            exists = "EXISTS" if v.exists() else "NOT FOUND"
            txt.insert(tk.END, f"  {k:24} -> [{exists:9}] {v}\n")

        txt.insert(tk.END, "\n--- Ban Association Risk Factors ---\n")
        txt.insert(tk.END, "  [!] ant-did cookie:          Persistent base64 machine identifier.\n")
        txt.insert(tk.END, "  [!] ant-device-registry:     Binds pk1 cryptographic machine key.\n")
        txt.insert(tk.END, "  [!] plan-usage-history:      Logs all Organization UUIDs & billing periods.\n")
        txt.insert(tk.END, "  [!] Local State:             Preserves installation timestamp.\n")
        txt.insert(tk.END, "  [v] Safe Reset:              Neutralizes all above risks with 1 click!\n")

        txt.configure(state=tk.DISABLED)

    def on_launch(self):
        claude_reset.launch_claude_desktop()
        self.log("[+] Triggered Claude Desktop launch.")


def main():
    app = ClaudeCleanerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
