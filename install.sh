#!/bin/bash
# Gnome Mail Desktop Shortcut Installer
# Works on any Linux device with a standard desktop

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/gnome-mail.desktop"
PYTHON="$(which python3)"

# Install dependencies if needed
"$PYTHON" -c "import pygame" 2>/dev/null || "$PYTHON" -m pip install -r "${INSTALL_DIR}/requirements.txt"

mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Gnome Mail
Comment=Toadstool-powered messaging via Ollama
Exec=${PYTHON} ${INSTALL_DIR}/run.py
Path=${INSTALL_DIR}
Terminal=false
Type=Application
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

# Also copy to Desktop if it exists
if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_FILE" "$HOME/Desktop/gnome-mail.desktop"
    chmod +x "$HOME/Desktop/gnome-mail.desktop"
    echo "Shortcut added to your Desktop!"
fi

echo "Gnome Mail installed to your application menu!"
echo "You can find it by searching 'Gnome Mail' in your app launcher."
