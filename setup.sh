#!/bin/bash

# Setup script for ProtonX Legal OCR Service

set -e

echo "=========================================="
echo "ProtonX Legal OCR Service Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Create model cache directory
mkdir -p model_cache

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the service:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the service: ./run.sh"
echo "     or: python -m src.main"
echo ""
echo "To test the service:"
echo "  python test_structure.py"
echo ""
echo "To test the API (after starting the service):"
echo "  python example_client.py"
echo ""
echo "API documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
