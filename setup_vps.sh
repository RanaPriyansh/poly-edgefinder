#!/bin/bash
# Setup script for VPS deployment

set -e

echo "===  Polymarket Edge Finder Setup ==="

# 1. System packages
echo "Installing system packages..."
apt update
apt install -y python3 python3-pip python3-venv git

# 2. Create app directory
APP_DIR="/opt/poly-edgefinder"
if [ ! -d "$APP_DIR" ]; then
    mkdir -p $APP_DIR
    # Copy project files from current location if run locally
    if [ -d "src" ]; then
        cp -r . $APP_DIR/
        echo "Copied project files to $APP_DIR"
    else
        echo "Please clone the repo manually to $APP_DIR"
        exit 1
    fi
fi

cd $APP_DIR

# 3. Python venv
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo " ⚠️  Please edit .env and add your Simmer API key"
    echo "   nano .env"
fi

# 6. Create data directories
mkdir -p data/raw data/processed logs

# 7. Test collector (dry run)
echo "Testing collector (will not run continuously)..."
source venv/bin/activate
python -m src.data_collectors.simmer_collector || {
    echo " ⚠️  Collector test failed. Check your .env configuration."
    exit 1
}

# 8. Suggest running as service
echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano $APP_DIR/.env"
echo "   - Add SIMMER_API_KEY"
echo "2. Test collector: cd $APP_DIR && source venv/bin/activate && python -m src.data_collectors.simmer_collector"
echo "   (Press Ctrl+C to stop test)"
echo ""
echo "To run continuously, you can:"
echo "  - Use screen/tmux: 'screen -S collector' then run command"
echo "  - Or create systemd service (see systemd.service example)"
echo ""
echo "Data will be saved to: $APP_DIR/data/raw/YYYY-MM-DD.jsonl"