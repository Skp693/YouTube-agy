#!/bin/bash
# ==============================================================================
# Quick Terminal Launcher: AI Studio Pro
# ==============================================================================
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Starting AI Studio Pro Desktop Dashboard at http://127.0.0.1:8501..."
open "http://127.0.0.1:8501" &
exec python3 desktop_server.py 8501
