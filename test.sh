#!/bin/bash
# Simple test script to verify the Docker setup

echo "Testing Paprika Showcase Docker Setup"
echo "======================================"
echo ""

# Check if containers are running
echo "1. Checking container status..."
docker compose ps
echo ""

# Test app container health
echo "2. Testing app container health endpoint..."
APP_HEALTH=$(docker exec paprika-app curl -s http://localhost:8000/health 2>/dev/null || echo "Container not running or app not responding")
echo "Response: $APP_HEALTH"
echo ""

# Test main endpoint
echo "3. Testing app main endpoint..."
APP_MAIN=$(docker exec paprika-app curl -s http://localhost:8000/ 2>/dev/null || echo "Container not running or app not responding")
echo "Response: $APP_MAIN"
echo ""

# Test Caddy reverse proxy
echo "4. Testing Caddy reverse proxy (paprika.local)..."
CADDY_RESPONSE=$(curl -s -H "Host: paprika.local" http://localhost/)
echo "Response: $CADDY_RESPONSE"
echo ""

# Verify Python version
echo "5. Verifying Python version..."
PYTHON_VERSION=$(docker exec paprika-app python --version)
echo "Python version: $PYTHON_VERSION"
echo ""

echo "======================================"
echo "All tests completed!"
