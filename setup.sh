#!/usr/bin/env bash
set -e

echo "Setting up O2Ring Monitor Application..."

# Check for Python
if ! command -v python3 &>/dev/null; then
    echo "Python 3 not found. Please install Python 3.9+ and rerun this script."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete! Starting O2Ring Monitor..."
echo ""

# Start the app
python o2ring_ui_real.py 