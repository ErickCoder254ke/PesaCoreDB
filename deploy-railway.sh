#!/bin/bash

# PesacodeDB Railway Deployment Script
# This script helps you deploy your backend to Railway.app

set -e

echo "======================================"
echo "PesacodeDB Railway Deployment Helper"
echo "======================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo ""
    echo "Install it with:"
    echo "  npm i -g @railway/cli"
    echo ""
    echo "Or deploy via the Railway dashboard: https://railway.app"
    exit 1
fi

echo "✅ Railway CLI detected"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Logging in to Railway..."
    railway login
else
    echo "✅ Already logged in to Railway"
fi

echo ""
echo "📦 Initializing Railway project..."
railway init || echo "Project already initialized"

echo ""
echo "🔗 Linking to Railway..."
railway link || echo "Already linked"

echo ""
echo "======================================"
echo "Setting Environment Variables"
echo "======================================"
echo ""

# Generate API key
echo "🔑 Generating secure API key..."
API_KEY=$(openssl rand -hex 32)
echo "Generated API Key: $API_KEY"
echo "(Save this key securely!)"
echo ""

# Set environment variables
echo "Setting environment variables..."
railway variables set API_KEY="$API_KEY"
railway variables set REQUIRE_API_KEY=true
railway variables set PESADB_URL=pesadb://localhost/default
railway variables set CORS_ORIGINS='*'
railway variables set DEBUG=false

echo ""
echo "✅ Environment variables set"
echo ""

# Ask about AI features
read -p "Do you want to enable AI features? (y/n): " enable_ai
if [[ $enable_ai == "y" || $enable_ai == "Y" ]]; then
    echo ""
    echo "Get your Gemini API key from: https://makersuite.google.com/app/apikey"
    read -p "Enter your Gemini API key: " gemini_key
    railway variables set GEMINI_API_KEY="$gemini_key"
    railway variables set GEMINI_MODEL=gemini-1.5-flash-latest
    echo "✅ AI features enabled"
else
    echo "⏭️  Skipping AI features"
fi

echo ""
echo "======================================"
echo "Adding Persistent Volume"
echo "======================================"
echo ""

read -p "Do you want to add persistent storage for your database? (recommended) (y/n): " add_volume
if [[ $add_volume == "y" || $add_volume == "Y" ]]; then
    echo "Adding volume..."
    railway volume add --mount-path /app/data || echo "Volume may already exist"
    railway variables set PESADB_URL=pesadb://localhost/default?data_dir=/app/data
    echo "✅ Persistent volume configured"
else
    echo "⚠️  Warning: Data will not persist across deployments!"
fi

echo ""
echo "======================================"
echo "Deploying to Railway"
echo "======================================"
echo ""

railway up

echo ""
echo "======================================"
echo "🎉 Deployment Complete!"
echo "======================================"
echo ""

# Get the URL
echo "Getting your deployment URL..."
echo ""
railway domain || echo "Generate a domain in the Railway dashboard"

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. View logs: railway logs"
echo "2. Open dashboard: railway open"
echo "3. Generate a domain in Railway dashboard → Settings → Networking"
echo "4. Test your API: https://your-app.railway.app/api/health"
echo "5. View API docs: https://your-app.railway.app/docs"
echo ""
echo "Your API Key: $API_KEY"
echo "(Save this securely! You'll need it to access your API)"
echo ""
echo "Update your frontend config with:"
echo "  API_BASE_URL: https://your-app.railway.app/api"
echo "  API_KEY: $API_KEY"
echo ""
echo "======================================"
echo "Happy coding! 🚀"
echo "======================================"
