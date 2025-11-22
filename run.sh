#!/bin/bash

# Run the ProtonX Legal OCR Service

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
python -m src.main
