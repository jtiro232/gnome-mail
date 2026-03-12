#!/bin/bash
# Gnome Mail Launcher - always runs the latest version
cd "$(dirname "$0")"

# Pull latest changes
git pull origin main --quiet 2>/dev/null

# Install/update dependencies
pip3 install -q -r requirements.txt 2>/dev/null

# Launch the app
python3 run.py
