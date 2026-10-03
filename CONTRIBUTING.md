# Contributing to Claude Anti-Ban & Telemetry Cleaner

Thank you for your interest in contributing! This project is dedicated to protecting user privacy, investigating AI developer tools telemetry, and helping users recover from hardware ID bans.

---

## Repository Structure & Branches

* **`main` (Default Branch)**: 100% native implementations with **zero external prerequisites**:
  - Windows: PowerShell (`Claude-Reset.ps1`) and batch launcher (`Claude-Reset.cmd`).
  - macOS & Linux: Pure native Bash (`claude-reset.sh`).
* **`python` Branch**: Cross-platform Python implementation (`claude_reset.py`) with unit test suite (`test_claude_reset.py`).

---

## Code of Principles

1. **Zero External Dependencies**: All scripts must run out-of-the-box on clean operating systems without requiring users to install third-party packages or runtimes.
2. **User Data Safety First**: Under no circumstances should user sessions (`claude-code-sessions`) or project directories be deleted without explicit user confirmation (`--full` or manual option `[6]`).
3. **Electron / Node.js Integrity**: Never output files with UTF-8 BOM (`\uFEFF`). Always write strictly UTF-8 No-BOM.
4. **Cross-Platform Compatibility**: Changes must be tested across Windows, macOS, and Linux.
5. **Documentation Parity**: Any changes to features or documentation must be reflected equally in both `README.md` (English) and `README.ru.md` (Russian).

---

## Development & Local Testing

### Validating PowerShell on Windows
```powershell
[System.Management.Automation.Language.Parser]::ParseInput((Get-Content Claude-Reset.ps1 -Raw), [ref]$null, [ref]$null, [ref]$errors)
.\Claude-Reset.ps1 -DryRun -Auto
```

### Validating Bash on macOS / Linux
```bash
bash -n claude-reset.sh
./claude-reset.sh --dry-run --auto
```

---

## Pull Request Guidelines

1. Fork the repository and create your branch from `main` (for shell utilities) or `python` (for the Python engine).
2. Ensure syntax validation and dry-run tests pass on your target platform.
3. If adding a new telemetry file or token key to sanitize, update both PowerShell and Bash implementations and document it in the table.
4. Keep commits descriptive and follow conventional commits (e.g. `feat:`, `fix:`, `docs:`).
