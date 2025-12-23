#!/bin/bash

# ProtonX Legal API Deployment Script
# This script helps deploy the API for testing

set -e

echo "=========================================="
echo "ProtonX Legal API Deployment Script"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Docker Compose (standalone) is available${NC}"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Docker Compose (plugin) is available${NC}"
else
    echo -e "${RED}Error: Docker Compose is not available${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo ""
echo "Deployment Options:"
echo "1. Build and start the API"
echo "2. Stop the API"
echo "3. View API logs"
echo "4. Restart the API"
echo "5. Pre-download model (optional, for offline use)"
echo ""

read -p "Select an option (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Building Docker image...${NC}"
        $COMPOSE_CMD build
        
        echo ""
        echo -e "${YELLOW}Starting API service...${NC}"
        $COMPOSE_CMD up -d
        
        echo ""
        echo -e "${GREEN}✓ API is starting up${NC}"
        echo ""
        echo "The API will be available at: http://localhost:8000"
        echo "Swagger UI: http://localhost:8000/docs"
        echo "ReDoc: http://localhost:8000/redoc"
        echo ""
        echo "Note: First startup may take a few minutes to download the model from HuggingFace"
        echo ""
        echo "View logs with: $COMPOSE_CMD logs -f"
        echo "Stop the API with: $COMPOSE_CMD down"
        ;;
    2)
        echo ""
        echo -e "${YELLOW}Stopping API service...${NC}"
        $COMPOSE_CMD down
        echo -e "${GREEN}✓ API stopped${NC}"
        ;;
    3)
        echo ""
        echo -e "${YELLOW}Viewing API logs (press Ctrl+C to exit)...${NC}"
        echo ""
        $COMPOSE_CMD logs -f
        ;;
    4)
        echo ""
        echo -e "${YELLOW}Restarting API service...${NC}"
        $COMPOSE_CMD restart
        echo -e "${GREEN}✓ API restarted${NC}"
        ;;
    5)
        echo ""
        echo -e "${YELLOW}Pre-downloading model...${NC}"
        echo "This will download the model cache that can be used offline"
        
        # Check if python3 is available
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Error: Python 3 is not installed${NC}"
            echo "Please install Python 3 first"
            exit 1
        fi
        
        # Create a secure temporary Python script to download the model
        TEMP_SCRIPT=$(mktemp)
        chmod 600 "$TEMP_SCRIPT"
        cat > "$TEMP_SCRIPT" << 'EOF'
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

model_name = "protonx-models/protonx-legal-tc"
cache_dir = "./model_cache"

print(f"Downloading model: {model_name}")
print(f"Cache directory: {cache_dir}")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
    print("✓ Model downloaded successfully!")
except Exception as e:
    print(f"Error downloading model: {e}")
    exit(1)
EOF
        
        # Run the download script
        python3 "$TEMP_SCRIPT"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Model downloaded successfully${NC}"
            echo "The model is cached in ./model_cache directory"
        else
            echo -e "${RED}Error downloading model${NC}"
            echo "Please ensure you have internet access and the model is accessible"
        fi
        
        # Clean up
        rm -f "$TEMP_SCRIPT"
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac
