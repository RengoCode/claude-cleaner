# Contributing to Claude Anti-Ban & Telemetry Cleaner

Thank you for your interest in contributing! This project is dedicated to protecting user privacy, investigating AI developer tools telemetry, and helping users recover from hardware ID bans.

---

## Code of Principles

1. **Zero External Dependencies**: The core Python script (`claude_reset.py`) must only rely on the Python Standard Library (`os`, `sys`, `re`, `json`, `shutil`, `zipfile`, `secrets`, etc.). No `pip install` required.
2. **User Data Safety First**: Under no circumstances should user sessions (`claude-code-sessions`) or project directories be deleted without explicit confirmation (`--full` or manual option `[5]`).
3. **Electron / Node.js Integrity**: Never output files with UTF-8 BOM (`\uFEFF`). Always write strictly UTF-8 No-BOM.
4. **Cross-Platform Compatibility**: Changes must be tested across Windows, macOS, and Linux.

---

## Development & Testing

### Running Tests Locally
Ensure Python 3.8+ is installed. Run the built-in test suite:

```bash
python test_claude_reset.py -v
```

### Checking Syntax
```bash
python -m py_compile claude_reset.py
```

### PowerShell Validation (Windows)
```powershell
[System.Management.Automation.Language.Parser]::ParseInput((Get-Content Claude-AntiBan-Reset.ps1 -Raw), [ref]$null, [ref]$null, [ref]$errors)
```

---

## Pull Request Guidelines

1. Fork the repository and create your branch from `main`.
2. Ensure all tests in `test_claude_reset.py` pass.
3. If adding a new telemetry file or token key to sanitize, add a test case verifying it is safely handled.
4. Keep commits descriptive and follow conventional commits (e.g. `feat:`, `fix:`, `docs:`).
