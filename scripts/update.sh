#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/bmonitor"
SRC_DIR="$INSTALL_DIR/src"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="bmonitor"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

[[ $EUID -ne 0 ]] && error "This script must be run as root (use sudo)."
[[ ! -d "$SRC_DIR/.git" ]] && error "Source directory not found at $SRC_DIR."

info "Pulling latest changes..."
git -C "$SRC_DIR" pull --ff-only

info "Updating Python dependencies..."
"$VENV_DIR/bin/pip" install -r "$SRC_DIR/backend/requirements.txt" -q

# Build frontend if present
if [[ -d "$SRC_DIR/frontend" ]] && command -v npm &>/dev/null; then
    info "Rebuilding frontend..."
    cd "$SRC_DIR/frontend" && npm install && npm run build
    cd -
fi

info "Restarting service..."
systemctl restart "$SERVICE_NAME"

info "BMonitor updated successfully."
