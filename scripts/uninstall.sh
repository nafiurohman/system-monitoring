#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="bmonitor"
INSTALL_DIR="/opt/bmonitor"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

[[ $EUID -ne 0 ]] && error "This script must be run as root (use sudo)."

echo -e "${YELLOW}This will completely remove BMonitor from your system.${NC}"
read -rp "Are you sure? (y/N): " CONFIRM
[[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]] && { echo "Aborted."; exit 0; }

# Stop and disable service
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl stop "$SERVICE_NAME"
    info "Service stopped."
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    systemctl disable "$SERVICE_NAME"
    info "Service disabled."
fi

# Remove service file
rm -f /etc/systemd/system/bmonitor.service
systemctl daemon-reload
info "Systemd service removed."

# Remove CLI wrapper
rm -f /usr/local/bin/bmonitor
info "CLI wrapper removed."

# Remove install directory
if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    info "Removed $INSTALL_DIR."
fi

# Remove system user
if id "$SERVICE_NAME" &>/dev/null; then
    userdel "$SERVICE_NAME"
    info "System user '$SERVICE_NAME' removed."
fi

echo ""
echo -e "${GREEN}BMonitor has been completely uninstalled.${NC}"
