#!/bin/bash

# Test Dockerfile locally before deploying to Railway

echo "======================================"
echo "Testing Dockerfile Locally"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker detected"
echo ""

# Build the image
echo "🔨 Building Docker image..."
docker build -t pesacodedb-test .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Starting container..."
    echo ""
    
    # Run the container
    docker run -d \
        --name pesacodedb-test \
        -p 8000:8000 \
        -e API_KEY="test_api_key_12345" \
        -e REQUIRE_API_KEY=true \
        -e PESADB_URL="pesadb://localhost/default" \
        -e CORS_ORIGINS="*" \
        pesacodedb-test
    
    echo "✅ Container started!"
    echo ""
    echo "Waiting 3 seconds for server to start..."
    sleep 3
    echo ""
    
    # Test the API
    echo "🧪 Testing API..."
    echo ""
    
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
    
    if [ $? -eq 0 ]; then
        echo "✅ Health check successful!"
        echo "Response: $HEALTH_RESPONSE"
        echo ""
        
        # Test with API key
        echo "🧪 Testing with API key..."
        API_RESPONSE=$(curl -s -H "X-API-Key: test_api_key_12345" http://localhost:8000/api/databases)
        echo "Response: $API_RESPONSE"
        echo ""
        
        echo "======================================"
        echo "✅ All tests passed!"
        echo "======================================"
        echo ""
        echo "View logs:"
        echo "  docker logs pesacodedb-test"
        echo ""
        echo "Stop container:"
        echo "  docker stop pesacodedb-test"
        echo ""
        echo "Remove container:"
        echo "  docker rm pesacodedb-test"
        echo ""
        echo "Access API docs:"
        echo "  http://localhost:8000/docs"
        echo ""
    else
        echo "❌ Health check failed"
        echo ""
        echo "Container logs:"
        docker logs pesacodedb-test
        echo ""
        echo "Cleaning up..."
        docker stop pesacodedb-test
        docker rm pesacodedb-test
        exit 1
    fi
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi
