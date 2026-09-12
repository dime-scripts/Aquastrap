#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/aquastrap"
DESKTOP_DIR="$HOME/.local/share/applications"
LAUNCHER="$INSTALL_DIR/Aquastrap.py"
MAIN="$INSTALL_DIR/main.py"
DESKTOP="$DESKTOP_DIR/aqua.desktop"
BASE_URL="https://raw.githubusercontent.com/dime-scripts/Aquastrap/main"

echo "[AQUA]: installer starting"
command -v python3 >/dev/null 2>&1 || { echo "[ERROR]: python3 is required"; exit 1; }
if command -v curl >/dev/null 2>&1; then
    fetch(){ curl -fsSL "$1" -o "$2"; }
elif command -v wget >/dev/null 2>&1; then
    fetch(){ wget -q "$1" -O "$2"; }
else
    echo "[ERROR]: curl or wget is required"; exit 1
fi

mkdir -p "$INSTALL_DIR" "$DESKTOP_DIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[AQUA]: downloading launcher"
fetch "$BASE_URL/Aquastrap.py" "$TMP/launcher"
echo "[AQUA]: downloading main application"
fetch "$BASE_URL/Main.py" "$TMP/main"

python3 -m py_compile "$TMP/launcher" || { echo "[ERROR]: downloaded launcher is broken"; exit 1; }
python3 -m py_compile "$TMP/main" || { echo "[ERROR]: downloaded application is broken"; exit 1; }

mv "$TMP/launcher" "$LAUNCHER"
mv "$TMP/main" "$MAIN"
chmod +x "$LAUNCHER" "$MAIN"
echo "[AQUA]: files installed in $INSTALL_DIR"
chmod +x "$DESKTOP"
echo "[AQUA]: desktop entry installed"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
echo "[AQUA]: installation complete"
echo "[AQUA]: run with: python3 $LAUNCHER  (or launch Aquastrap from the app menu)"
