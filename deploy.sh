#!/bin/bash
# Deployment script for Veefyed Scraper
# Run this script on the Cantabo server after initial setup

set -e  # Exit on error

echo "🚀 Starting Veefyed Scraper Deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="$HOME/veefyed-scraper"
SCRAPER_DIR="$APP_DIR/scraper"
VENV_DIR="$SCRAPER_DIR/venv"

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if directory exists
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found: $APP_DIR"
    print_warning "Please run initial setup first (see DEPLOYMENT_CANTABO.md)"
    exit 1
fi

cd "$APP_DIR"

# Pull latest changes
print_success "Pulling latest changes from Git..."
git pull origin main || git pull origin master

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found. Creating..."
    cd "$SCRAPER_DIR"
    python3 -m venv venv
fi

source "$VENV_DIR/bin/activate"

# Update dependencies
print_success "Updating Python dependencies..."
cd "$SCRAPER_DIR"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Create necessary directories
print_success "Creating necessary directories..."
mkdir -p data/logs data/outputs
chmod -R 755 data

# Restart application
print_success "Restarting application..."
if systemctl is-active --quiet veefyed-scraper 2>/dev/null || systemctl list-unit-files | grep -q veefyed-scraper; then
    sudo systemctl restart veefyed-scraper
    print_success "Application restarted via systemd"
else
    print_warning "Systemd service not found. Please restart manually:"
    echo "  sudo systemctl restart veefyed-scraper"
    echo "  Or: nohup python app.py > data/logs/scraper.log 2>&1 &"
fi

# Check application status
print_success "Checking application status..."
sleep 3

if systemctl list-unit-files | grep -q veefyed-scraper; then
    sudo systemctl status veefyed-scraper --no-pager -l
fi

# Test health endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Application is running and healthy!"
else
    print_warning "Health check failed. Check logs:"
    echo "  tail -f $SCRAPER_DIR/data/logs/scraper.log"
fi

print_success "🎉 Deployment completed!"

