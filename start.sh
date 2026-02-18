#!/bin/bash

# System Monitor Dashboard
# Author: M. Nafiurohman

echo "========================================="
echo "  System Monitor Dashboard"
echo "  by M. Nafiurohman"
echo "========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "Checking dependencies..."
if ! python -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start server
echo ""
echo "Starting System Monitor Dashboard..."
echo "Access at: http://127.0.0.1:9999"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python app.py
