#!/usr/bin/env bash
# ==============================================================================
# Claude Anti-Ban & Telemetry Cleaner
# Launcher for macOS and Linux (pure Bash + Python 3)
# ==============================================================================

set -e

# Detect script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Find Python 3
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    # Check if python is version 3
    if python -c 'import sys; exit(0 if sys.version_info.major >= 3 else 1)' &>/dev/null; then
        PYTHON_BIN="python"
    fi
fi

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}[ERROR] Python 3.8+ is required but was not found on your system.${NC}"
    echo "Please install Python 3 using your package manager (e.g., brew install python3, apt install python3) and try again."
    exit 1
fi

# Run the Python engine with all passed arguments
exec "$PYTHON_BIN" "$SCRIPT_DIR/claude_reset.py" "$@"
