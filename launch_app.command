#!/bin/bash
# ==============================================================================
# AI Studio Pro — macOS Desktop App Launcher
# Double-click this file from Finder or Terminal to launch the Desktop Studio.
# ==============================================================================

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure Homebrew and standard macOS developer tools are in PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Prefer virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Clear terminal screen and show banner
clear
echo "================================================================================"
echo "               🎬 AI STUDIO PRO — AUTONOMOUS YOUTUBE PIPELINE                   "
echo "                             macOS Desktop Edition                             "
echo "================================================================================"
echo "  [✓] Working Dir:   $SCRIPT_DIR"
echo "  [✓] Python:        $(which python3)"
echo "  [✓] FFmpeg:        $(which ffmpeg || echo 'Not found')"
echo "  [✓] Audio Engine:  macOS Studio Voice (/usr/bin/say)"
echo "  [✓] YPP Shield:    Active (Monetization & Compliance Guard)"
echo "--------------------------------------------------------------------------------"
echo "  🚀 Starting Desktop Dashboard Server at http://127.0.0.1:8501..."
echo "  🌐 Opening your browser in 2 seconds..."
echo "================================================================================"

# Automatically open default browser after a brief delay
(sleep 2 && open "http://127.0.0.1:8501") &

# Run desktop server (keeps process alive in foreground)
python3 desktop_server.py 8501
