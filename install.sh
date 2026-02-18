#!/bin/bash

# System Monitor Dashboard - Installer
# Author: M. Nafiurohman

INSTALL_DIR="$HOME/.system-monitor"
BIN_DIR="$HOME/.local/bin"

echo "========================================="
echo "  System Monitor Dashboard - Installer"
echo "  by M. Nafiurohman"
echo "========================================="
echo ""

# Create directories
mkdir -p "$BIN_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Installing System Monitor Dashboard..."
cp -r . "$INSTALL_DIR/"

# Remove venv if exists (will be recreated on first run)
rm -rf "$INSTALL_DIR/venv"

# Create executable script
cat > "$BIN_DIR/monitor" << 'EOF'
#!/bin/bash
cd "$HOME/.system-monitor"
./start.sh
EOF

chmod +x "$BIN_DIR/monitor"

# Add to PATH if not already
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "Adding $BIN_DIR to PATH..."
    
    # Detect shell
    if [ -f "$HOME/.bashrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo "Added to ~/.bashrc"
    fi
    
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        echo "Added to ~/.zshrc"
    fi
fi

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Usage:"
echo "  1. Restart your terminal or run: source ~/.bashrc"
echo "  2. Run: monitor"
echo "  3. Open browser: http://127.0.0.1:9999"
echo ""
echo "To uninstall:"
echo "  rm -rf $INSTALL_DIR"
echo "  rm $BIN_DIR/monitor"
echo ""
