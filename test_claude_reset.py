#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit and integration tests for Claude Anti-Ban & Telemetry Cleaner.
Tests run with standard library 'unittest' - 0 external dependencies required.
"""

import os
import sys
import re
import json
import shutil
import zipfile
import tempfile
import unittest
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_reset import (
    random_sha256_hex,
    ClaudePaths,
    create_backup,
    perform_clean,
    stop_claude_processes,
    I18N,
    t,
)


class TestClaudeReset(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary test directory
        self.test_dir = tempfile.mkdtemp(prefix="claude_test_")
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        # Clean up temporary test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_random_sha256_hex(self):
        """Verify generated IDs are valid 64-character lowercase hex strings."""
        id1 = random_sha256_hex()
        id2 = random_sha256_hex()

        self.assertEqual(len(id1), 64)
        self.assertEqual(len(id2), 64)
        self.assertNotEqual(id1, id2)
        self.assertTrue(re.match(r"^[0-9a-f]{64}$", id1) is not None)
        self.assertTrue(re.match(r"^[0-9a-f]{64}$", id2) is not None)

    def test_no_utf8_bom(self):
        """Verify that written JSON files do NOT contain the UTF-8 BOM (\xef\xbb\xbf)."""
        sample_file = self.test_path / "test_config.json"
        data = {"machineID": "test", "userID": "test"}
        
        sample_file.write_text(json.dumps(data), encoding="utf-8")
        raw_bytes = sample_file.read_bytes()

        # Electron crashes if file begins with BOM bytes: 0xEF 0xBB 0xBF
        self.assertFalse(raw_bytes.startswith(b"\xef\xbb\xbf"), "File contains UTF-8 BOM which crashes Electron/Node.js!")

    def test_cli_config_id_replacement(self):
        """Test regex replacement in CLI configuration files without breaking JSON."""
        original_json = {
            "machineID": "old_machine_id_1111111111111111111111111111111111111111111111111111",
            "userID": "old_user_id_22222222222222222222222222222222222222222222222222222222",
            "anonymousId": "claudecode_old_anonymous_33333333333333333333333333333333",
            "customUserSetting": "keep_this_setting",
            "theme": "dark"
        }
        config_file = self.test_path / ".claude.json"
        config_file.write_text(json.dumps(original_json, indent=2), encoding="utf-8")

        new_machine = random_sha256_hex()
        new_user = random_sha256_hex()
        new_anon = f"claudecode_{random_sha256_hex()[:32]}"

        raw = config_file.read_text(encoding="utf-8")
        raw = re.sub(r'("machineID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_machine}"', raw)
        raw = re.sub(r'("userID"\s*:\s*)"[^"]+"', rf'\g<1>"{new_user}"', raw)
        raw = re.sub(r'("anonymousId"\s*:\s*)"[^"]+"', rf'\g<1>"{new_anon}"', raw)
        config_file.write_text(raw, encoding="utf-8")

        # Parse back and verify
        parsed = json.loads(config_file.read_text(encoding="utf-8"))
        self.assertEqual(parsed["machineID"], new_machine)
        self.assertEqual(parsed["userID"], new_user)
        self.assertEqual(parsed["anonymousId"], new_anon)
        self.assertEqual(parsed["customUserSetting"], "keep_this_setting")
        self.assertEqual(parsed["theme"], "dark")

    def test_desktop_config_sanitization(self):
        """Verify sensitive auth tokens and machine linkage are removed while settings remain."""
        desktop_config = {
            "lastKnownAccountUuid": "00000000-0000-0000-0000-000000000001",
            "oauth:tokenCache": {"token": "secret_access_token"},
            "oauth:tokenCacheV2": {"token": "secret_v2"},
            "dxt:allowlist:some_account": True,
            "chromeExtension.pairedDeviceId": "device_xyz",
            "hasTrackedInitialActivation": True,
            "theme": "system",
            "preferredModel": "claude-3-5-sonnet",
            "first_launch_at": 1700000000000
        }

        # Emulate sanitization
        keys_to_remove = [
            "lastKnownAccountUuid",
            "oauth:tokenCache",
            "oauth:tokenCacheV2",
            "chromeExtension.pairedDeviceId",
            "hasTrackedInitialActivation"
        ]
        keys_to_remove.extend([k for k in desktop_config.keys() if k.startswith("dxt:allowlist")])

        for k in keys_to_remove:
            desktop_config.pop(k, None)

        self.assertNotIn("lastKnownAccountUuid", desktop_config)
        self.assertNotIn("oauth:tokenCache", desktop_config)
        self.assertNotIn("oauth:tokenCacheV2", desktop_config)
        self.assertNotIn("dxt:allowlist:some_account", desktop_config)
        self.assertNotIn("chromeExtension.pairedDeviceId", desktop_config)
        self.assertEqual(desktop_config["theme"], "system")
        self.assertEqual(desktop_config["preferredModel"], "claude-3-5-sonnet")

    def test_multilingual_i18n_keys(self):
        """Verify all supported languages (en, ru, es, zh) contain full translations."""
        base_keys = set(I18N["en"].keys())
        for lang_code in ("ru", "es", "zh"):
            self.assertIn(lang_code, I18N, f"Language {lang_code} missing from I18N dictionary")
            target_keys = set(I18N[lang_code].keys())
            missing = base_keys - target_keys
            self.assertEqual(len(missing), 0, f"Language {lang_code} is missing keys: {missing}")

    def test_mock_safe_vs_full_clean(self):
        """Verify that safe mode preserves session files, whereas full mode wipes them."""
        class MockPaths(ClaudePaths):
            def __init__(self, root: Path):
                self.os_type = "Linux"
                self.home = root / "home"
                self.home.mkdir(parents=True, exist_ok=True)
                self.base_dir = root / "cleaner"
                self.base_dir.mkdir(parents=True, exist_ok=True)
                self.backup_dir = self.base_dir / "backups"
                self.backup_dir.mkdir(parents=True, exist_ok=True)

                self.cli_dir = self.home / ".claude"
                self.cli_dir.mkdir(parents=True, exist_ok=True)
                self.cli_config_main = self.home / ".claude.json"
                self.cli_config_nested = self.cli_dir / ".claude.json"
                self.cli_telemetry_dir = self.cli_dir / "telemetry"
                self.cli_sessions_dir = self.cli_dir / "sessions"
                self.cli_projects_dir = self.cli_dir / "projects"
                self.cli_stats_cache = self.cli_dir / "stats-cache.json"
                self.cli_daemon_status = self.cli_dir / "daemon-auth-status.json"
                self.cli_daemon_cooldown = self.cli_dir / "daemon-auth-cooldown"
                self.cli_paste_cache = self.cli_dir / "paste-cache"
                self.cli_shell_snapshots = self.cli_dir / "shell-snapshots"

                self.desktop_dir = self.home / "DesktopClaude"
                self.desktop_dir.mkdir(parents=True, exist_ok=True)
                self.desktop_exe = self.desktop_dir / "claude"

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

        # Setup mock files
        mock = MockPaths(self.test_path)
        mock.cli_config_main.write_text(json.dumps({"machineID": "old1", "userID": "old2"}), encoding="utf-8")
        mock.cli_stats_cache.write_text(json.dumps({"version": 4, "dailyActivity": [{"date": "2026-01-01"}]}), encoding="utf-8")
        mock.ant_did.write_text("old_ant_did_cookie", encoding="utf-8")
        mock.ant_device_registry.write_text('{"account":"key"}', encoding="utf-8")
        mock.desktop_plan_usage.write_text(json.dumps({"history": [{"org": "old_org_uuid"}]}), encoding="utf-8")
        mock.desktop_local_state.write_text(json.dumps({"uninstall_metrics": {"installation_date2": "1000000000"}}), encoding="utf-8")

        # Create session files
        session_subdir = mock.claude_code_sessions / "account_uuid" / "project_uuid"
        session_subdir.mkdir(parents=True, exist_ok=True)
        session_file = session_subdir / "session_1.json"
        session_file.write_text('{"messages": ["important session data"]}', encoding="utf-8")

        # 1. Run Safe Clean (wipe_sessions=False)
        perform_clean(mock, wipe_sessions=False)

        # Verify IDs were reset
        self.assertFalse(mock.ant_did.exists(), "ant-did should be unlinked")
        self.assertFalse(mock.ant_device_registry.exists(), "ant-device-registry should be unlinked")

        # Verify deep telemetry sanitized
        plan_usage_data = json.loads(mock.desktop_plan_usage.read_text(encoding="utf-8"))
        self.assertEqual(plan_usage_data.get("history"), [], "plan-usage-history should be cleared to empty list")

        stats_data = json.loads(mock.cli_stats_cache.read_text(encoding="utf-8"))
        self.assertEqual(stats_data.get("dailyActivity"), [], "CLI stats-cache should be cleared")

        # Verify sessions ARE PRESERVED in safe mode
        self.assertTrue(mock.claude_code_sessions.exists(), "Sessions directory MUST be preserved in safe mode")
        self.assertTrue(session_file.exists(), "Session JSON file MUST be preserved in safe mode")
        self.assertIn("important session data", session_file.read_text(encoding="utf-8"))

        # Verify backup was created
        backups = list(mock.backup_dir.glob("*.zip"))
        self.assertGreater(len(backups), 0, "A safety backup ZIP should be created")

        # 2. Run Full Clean (wipe_sessions=True)
        perform_clean(mock, wipe_sessions=True)
        self.assertFalse(mock.claude_code_sessions.exists(), "Sessions directory should be deleted in full factory reset")

    def test_dry_run_mode(self):
        """Verify that dry-run mode makes NO modifications to any files."""
        class MockPathsDry(ClaudePaths):
            def __init__(self, root: Path):
                self.os_type = "Linux"
                self.home = root / "home"
                self.home.mkdir(parents=True, exist_ok=True)
                self.base_dir = root / "cleaner"
                self.base_dir.mkdir(parents=True, exist_ok=True)
                self.backup_dir = self.base_dir / "backups"
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                self.cli_dir = self.home / ".claude"
                self.cli_dir.mkdir(parents=True, exist_ok=True)
                self.cli_config_main = self.home / ".claude.json"
                self.cli_config_nested = self.cli_dir / ".claude.json"
                self.cli_telemetry_dir = self.cli_dir / "telemetry"
                self.cli_sessions_dir = self.cli_dir / "sessions"
                self.cli_projects_dir = self.cli_dir / "projects"
                self.cli_stats_cache = self.cli_dir / "stats-cache.json"
                self.cli_daemon_status = self.cli_dir / "daemon-auth-status.json"
                self.cli_daemon_cooldown = self.cli_dir / "daemon-auth-cooldown"
                self.cli_paste_cache = self.cli_dir / "paste-cache"
                self.cli_shell_snapshots = self.cli_dir / "shell-snapshots"
                self.desktop_dir = self.home / "DesktopClaude"
                self.desktop_dir.mkdir(parents=True, exist_ok=True)
                self.desktop_exe = self.desktop_dir / "claude"
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

        mock = MockPathsDry(self.test_path)
        mock.cli_config_main.write_text(json.dumps({"machineID": "original_id"}), encoding="utf-8")
        mock.ant_did.write_text("original_ant_did", encoding="utf-8")

        # Run with dry_run=True
        perform_clean(mock, wipe_sessions=False, dry_run=True)

        # Assert files were NOT changed
        self.assertEqual(json.loads(mock.cli_config_main.read_text(encoding="utf-8"))["machineID"], "original_id")
        self.assertTrue(mock.ant_did.exists())
        self.assertEqual(mock.ant_did.read_text(encoding="utf-8"), "original_ant_did")


if __name__ == "__main__":
    unittest.main()
