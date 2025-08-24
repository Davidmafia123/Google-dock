#!/bin/bash
# This script automates the setup process for the Google Dorking Automation tool
# on Linux and macOS.

set -e

echo "--- [GDA] Setting up Google Dorking Automation Tool ---"

# 1. Check for Python 3
echo "[1/5] Checking for Python 3..."
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi
echo "Python 3 found."

# 2. Create virtual environment
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "[2/5] Virtual environment '$VENV_DIR' already exists. Skipping creation."
else
    echo "[2/5] Creating Python virtual environment in './$VENV_DIR'..."
    python3 -m venv $VENV_DIR
fi

# 3. Activate virtual environment and upgrade pip
echo "[3/5] Activating virtual environment and upgrading pip..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
echo "Pip upgraded."

# 4. Install project dependencies
echo "[4/5] Installing project dependencies from pyproject.toml..."
pip install -e ".[dev]"
echo "Dependencies installed."

# 5. Install Playwright browsers
echo "[5/5] Installing Playwright browser binaries (this might take a few minutes)..."
playwright install
echo "Playwright browsers installed."

echo ""
echo "--- [GDA] Setup Complete! ---"
echo ""
echo "To run the tool, first activate the virtual environment:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Then, you can run the interactive runner:"
echo "  python runner.py"
echo ""
echo "Or use the direct CLI command:"
echo "  gda --help"
echo ""
