#!/bin/bash

# Health Check Test Script
# Tests the local server health endpoint

echo "======================================"
echo "PesacodeDB Health Check Test"
echo "======================================"
echo ""

# Check if server is running
echo "Testing server health endpoint..."
echo ""

# Test root health endpoint
echo "1. Testing /health endpoint (should work without API key):"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/health)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

echo "   HTTP Status: $HTTP_CODE"
echo "   Response: $RESPONSE_BODY"

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Health check PASSED"
else
    echo "   ❌ Health check FAILED"
fi
echo ""

# Test detailed health endpoint
echo "2. Testing /api/health endpoint (detailed, should work without API key):"
API_HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/health)
API_HTTP_CODE=$(echo "$API_HEALTH_RESPONSE" | tail -n 1)
API_RESPONSE_BODY=$(echo "$API_HEALTH_RESPONSE" | head -n -1)

echo "   HTTP Status: $API_HTTP_CODE"
echo "   Response: $API_RESPONSE_BODY"

if [ "$API_HTTP_CODE" = "200" ]; then
    echo "   ✅ Detailed health check PASSED"
else
    echo "   ❌ Detailed health check FAILED"
fi
echo ""

# Test root endpoint
echo "3. Testing /api/ endpoint:"
ROOT_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/)
ROOT_HTTP_CODE=$(echo "$ROOT_RESPONSE" | tail -n 1)
ROOT_RESPONSE_BODY=$(echo "$ROOT_RESPONSE" | head -n -1)

echo "   HTTP Status: $ROOT_HTTP_CODE"
echo "   Response: $ROOT_RESPONSE_BODY"

if [ "$ROOT_HTTP_CODE" = "200" ]; then
    echo "   ✅ Root endpoint PASSED"
else
    echo "   ❌ Root endpoint FAILED (might need API key)"
fi
echo ""

echo "======================================"
echo "Test Summary"
echo "======================================"

if [ "$HTTP_CODE" = "200" ] && [ "$API_HTTP_CODE" = "200" ]; then
    echo "✅ All health checks PASSED"
    echo ""
    echo "Your server is ready for deployment!"
    echo "Railway/Render health checks should succeed."
    exit 0
else
    echo "❌ Some health checks FAILED"
    echo ""
    echo "Please check:"
    echo "  1. Is the server running? (python backend/server.py)"
    echo "  2. Is it listening on port 8000?"
    echo "  3. Check the server logs for errors"
    exit 1
fi
