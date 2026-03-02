#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  BMonitor Installer
#  Usage: curl -fsSL https://raw.githubusercontent.com/beznlabs/bmonitor/main/scripts/install.sh | sudo bash
# ============================================================

REPO="https://github.com/beznlabs/bmonitor.git"
INSTALL_DIR="/opt/bmonitor"
SERVICE_NAME="bmonitor"
CONFIG_DIR="$INSTALL_DIR/config"
VENV_DIR="$INSTALL_DIR/venv"
SRC_DIR="$INSTALL_DIR/src"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# --- Pre-flight checks ---
[[ $EUID -ne 0 ]] && error "This script must be run as root (use sudo)."
[[ "$(uname -s)" != "Linux" ]] && error "BMonitor only supports Linux."

for cmd in python3 git curl; do
    command -v "$cmd" &>/dev/null || error "Required command '$cmd' not found. Install it first."
done

python3 -c "import venv" 2>/dev/null || error "python3-venv is not installed. Run: apt install python3-venv"

info "All pre-flight checks passed."

# --- Create system user ---
if ! id "$SERVICE_NAME" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_NAME"
    info "Created system user '$SERVICE_NAME'."
else
    info "System user '$SERVICE_NAME' already exists."
fi

# --- Create directories ---
mkdir -p "$SRC_DIR" "$CONFIG_DIR" "$VENV_DIR"
info "Created directory structure at $INSTALL_DIR."

# --- Clone / update repository ---
if [[ -d "$SRC_DIR/.git" ]]; then
    info "Updating existing source..."
    git -C "$SRC_DIR" pull --ff-only
else
    info "Cloning repository..."
    git clone "$REPO" "$SRC_DIR"
fi

# --- Setup virtual environment ---
info "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$SRC_DIR/backend/requirements.txt" -q
info "Python dependencies installed."

# --- Build frontend (optional) ---
if [[ -d "$SRC_DIR/frontend" ]] && command -v npm &>/dev/null; then
    info "Building frontend..."
    cd "$SRC_DIR/frontend" && npm install && npm run build
    cd -
fi

# --- Default config ---
if [[ ! -f "$CONFIG_DIR/app.ini" ]]; then
    cat > "$CONFIG_DIR/app.ini" <<EOF
[server]
port = 9999

[security]
secret_key = $(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF
    info "Default config created at $CONFIG_DIR/app.ini."
fi

if [[ ! -f "$CONFIG_DIR/users.json" ]]; then
    echo "{}" > "$CONFIG_DIR/users.json"
fi

# --- Create CLI wrapper ---
cat > /usr/local/bin/bmonitor <<'WRAPPER'
#!/usr/bin/env bash
exec /opt/bmonitor/venv/bin/python /opt/bmonitor/src/cli/main.py "$@"
WRAPPER
chmod +x /usr/local/bin/bmonitor
info "CLI installed at /usr/local/bin/bmonitor."

# --- Create systemd service ---
cat > /etc/systemd/system/bmonitor.service <<EOF
[Unit]
Description=BMonitor System Monitoring
After=network.target

[Service]
Type=simple
User=bmonitor
Group=bmonitor
WorkingDirectory=$SRC_DIR/backend
ExecStart=$VENV_DIR/bin/gunicorn -w 1 -b 0.0.0.0:9999 app:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
info "Systemd service created."

# --- Set permissions ---
chown -R "$SERVICE_NAME":"$SERVICE_NAME" "$INSTALL_DIR"

# --- Create first admin user ---
echo ""
info "Create the first admin user for the web UI."
read -rp "Admin username: " ADMIN_USER
while true; do
    read -rsp "Admin password: " ADMIN_PASS; echo
    read -rsp "Confirm password: " ADMIN_CONFIRM; echo
    [[ "$ADMIN_PASS" == "$ADMIN_CONFIRM" ]] && break
    warn "Passwords do not match. Try again."
done

HASHED=$("$VENV_DIR/bin/python" -c "
import bcrypt, json
h = bcrypt.hashpw('''$ADMIN_PASS'''.encode(), bcrypt.gensalt()).decode()
users = {'$ADMIN_USER': {'password': h}}
print(json.dumps(users, indent=2))
")
echo "$HASHED" > "$CONFIG_DIR/users.json"
chown "$SERVICE_NAME":"$SERVICE_NAME" "$CONFIG_DIR/users.json"
chmod 600 "$CONFIG_DIR/users.json"
info "Admin user '$ADMIN_USER' created."

# --- Enable & start ---
systemctl enable "$SERVICE_NAME" --now
info "BMonitor service started."

# --- Summary ---
PORT=$(grep -oP 'port\s*=\s*\K\d+' "$CONFIG_DIR/app.ini" 2>/dev/null || echo "9999")
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} BMonitor installed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  URL:       http://$(hostname -I | awk '{print $1}'):${PORT}"
echo -e "  Config:    $CONFIG_DIR/app.ini"
echo -e "  Logs:      bmonitor logs"
echo ""
echo -e "  CLI Usage:"
echo -e "    bmonitor status        — Check service status"
echo -e "    bmonitor start|stop    — Manage service"
echo -e "    bmonitor logs -f       — Follow logs"
echo -e "    bmonitor add-user      — Add web user"
echo -e "    bmonitor port 8080     — Change port"
echo ""
