#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/aquastrap"
DESKTOP_DIR="$HOME/.local/share/applications"
MAIN="$INSTALL_DIR/main.py"
DESKTOP="$DESKTOP_DIR/aqua.desktop"
URL="https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/AQUASTRAP.py"

echo "[AQUA]: installer starting"
mkdir -p "$INSTALL_DIR" "$DESKTOP_DIR"

echo "[AQUA]: downloading Main.py"
TMP="$(mktemp)"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP" "$URL"
else
  echo "[ERROR]: curl or wget is required"
  exit 1
fi

if ! python3 -m py_compile "$TMP" 2>/dev/null; then
  echo "[ERROR]: downloaded file is broken, aborting"
  rm -f "$TMP"
  exit 1
fi

mv "$TMP" "$MAIN"
chmod +x "$MAIN"
echo "[AQUA]: main.py installed at $MAIN"

cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=Aquastrap
Comment=Launches Aquastrap
Exec=python3 $MAIN
Icon=aquastrap
Terminal=false
Categories=Game;Utility;
StartupWMClass=Aquastrap
EOF
chmod +x "$DESKTOP"
echo "[AQUA]: desktop entry installed at $DESKTOP"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
echo "[AQUA]: installation complete"
