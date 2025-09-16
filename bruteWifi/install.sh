#!/usr/bin/env bash
set -euo pipefail

# Simple installer: installs wireless tools and rockyou wordlist.
# Usage: chmod +x install.sh && sudo ./install.sh
REQ_PKGS=(iw aircrack-ng wireless-tools net-tools)

# rockyou sources (tries in order)
ROCKYOU_URLS=(
  "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
  "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou.txt"
)

# destination for rockyou (system if root, local otherwise)
if [ "$(id -u)" -eq 0 ]; then
  ROCKYOU_DEST="/usr/share/wordlists/rockyou.txt"
else
  mkdir -p ./wordlists
  ROCKYOU_DEST="$(pwd)/wordlists/rockyou.txt"
fi

# detect package manager and prepare commands
if command -v apt >/dev/null 2>&1; then
  PKG_MGR="apt"
  UPDATE_CMD="sudo apt update -y"
  INSTALL_CMD="sudo apt install -y"
elif command -v dnf >/dev/null 2>&1; then
  PKG_MGR="dnf"
  UPDATE_CMD="sudo dnf makecache"
  INSTALL_CMD="sudo dnf install -y"
elif command -v pacman >/dev/null 2>&1; then
  PKG_MGR="pacman"
  UPDATE_CMD="sudo pacman -Syu --noconfirm"
  INSTALL_CMD="sudo pacman -S --noconfirm --needed"
else
  echo "No supported package manager found (apt/dnf/pacman). Exiting."
  exit 1
fi

echo "Using package manager: $PKG_MGR"
echo "Updating package metadata..."
eval "$UPDATE_CMD"

echo "Installing packages: ${REQ_PKGS[*]}"
eval "$INSTALL_CMD ${REQ_PKGS[*]}"

# download rockyou
echo "Preparing to download rockyou -> $ROCKYOU_DEST"
TMPFILE="$(mktemp)"
downloaded=0

for url in "${ROCKYOU_URLS[@]}"; do
  echo "Trying: $url"
  if command -v wget >/dev/null 2>&1; then
    if wget -c --tries=3 --timeout=30 -O "$TMPFILE" "$url"; then
      downloaded=1
      break
    fi
  elif command -v curl >/dev/null 2>&1; then
    if curl -L --fail --retry 3 -o "$TMPFILE" "$url"; then
      downloaded=1
      break
    fi
  else
    echo "Neither wget nor curl available to download files. Exiting."
    rm -f "$TMPFILE"
    exit 1
  fi
done

if [ "$downloaded" -ne 1 ]; then
  echo "Failed to download rockyou from default mirrors."
  echo "You can add a direct URL to the script or download manually."
  rm -f "$TMPFILE"
  exit 1
fi

# Ensure destination dir exists (may need sudo)
DESTDIR="$(dirname "$ROCKYOU_DEST")"
if [ "$(id -u)" -eq 0 ]; then
  mkdir -p "$DESTDIR"
else
  mkdir -p "$DESTDIR"
fi

# Detect gzip and unpack if necessary, else move the file
if gzip -t "$TMPFILE" >/dev/null 2>&1; then
  echo "Downloaded file is gzip-compressed; decompressing to $ROCKYOU_DEST"
  if [ "$(id -u)" -eq 0 ]; then
    gzip -dc "$TMPFILE" > "$ROCKYOU_DEST"
  else
    gzip -dc "$TMPFILE" > "$ROCKYOU_DEST"
  fi
else
  echo "Saving rockyou to $ROCKYOU_DEST"
  if [ "$(id -u)" -eq 0 ]; then
    mv "$TMPFILE" "$ROCKYOU_DEST"
    # tmpfile moved — keep variable valid
    TMPFILE=""
  else
    mv "$TMPFILE" "$ROCKYOU_DEST"
    TMPFILE=""
  fi
fi

# set permissions
if [ -f "$ROCKYOU_DEST" ]; then
  sudo chmod 644 "$ROCKYOU_DEST" 2>/dev/null || chmod 644 "$ROCKYOU_DEST"
  echo "rockyou ready: $ROCKYOU_DEST"
else
  echo "rockyou download/extract failed."
  [ -n "$TMPFILE" ] && rm -f "$TMPFILE"
  exit 1
fi

# cleanup
[ -n "${TMPFILE:-}" ] && rm -f "$TMPFILE" || true

echo "Done. Installed packages and rockyou installed at $ROCKYOU_DEST"
