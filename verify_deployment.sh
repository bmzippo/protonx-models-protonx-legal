#!/bin/bash

# Deployment Verification Script
# This script verifies that the API is deployed and working correctly

set -e

echo "=========================================="
echo "ProtonX Legal API Deployment Verification"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
PASSED=0
FAILED=0

# Function to test an endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        ((FAILED++))
    fi
}

# Check if API is running
echo "1. Checking if API is accessible..."
if curl -s --connect-timeout 5 --max-time 10 "$API_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ API is not accessible${NC}"
    echo "Make sure the API is running: docker compose up -d"
    exit 1
fi

echo ""
echo "2. Testing API Endpoints..."
echo ""

# Test root endpoint
test_endpoint "Root endpoint" "$API_URL/" "GET"

# Test health endpoint
test_endpoint "Health check" "$API_URL/health" "GET"

# Test model info endpoint
test_endpoint "Model info" "$API_URL/model-info" "GET"

# Test prediction endpoint (requires model to be loaded)
echo ""
echo -e "${YELLOW}Note: Prediction tests may fail if model is still downloading${NC}"
test_endpoint "Text prediction" "$API_URL/predict" "POST" '{"text": "Test text"}'

# Test batch prediction endpoint
test_endpoint "Batch prediction" "$API_URL/predict/batch" "POST" '{"texts": ["Test 1", "Test 2"]}'

echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "The API is deployed and working correctly."
    echo ""
    echo "Access the API at:"
    echo "  - API: $API_URL"
    echo "  - Swagger UI: $API_URL/docs"
    echo "  - ReDoc: $API_URL/redoc"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    echo ""
    echo "Check the logs for more information:"
    echo "  docker compose logs -f"
    echo ""
    exit 1
fi
