@echo off
REM PesacodeDB Railway Deployment Script for Windows
REM This script helps you deploy your backend to Railway.app

echo ======================================
echo PesacodeDB Railway Deployment Helper
echo ======================================
echo.

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] Railway CLI is not installed.
    echo.
    echo Install it with:
    echo   npm i -g @railway/cli
    echo.
    echo Or deploy via the Railway dashboard: https://railway.app
    exit /b 1
)

echo [OK] Railway CLI detected
echo.

REM Check if logged in
railway whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Logging in to Railway...
    railway login
) else (
    echo [OK] Already logged in to Railway
)

echo.
echo [*] Initializing Railway project...
railway init
if %ERRORLEVEL% NEQ 0 (
    echo Project already initialized
)

echo.
echo [*] Linking to Railway...
railway link
if %ERRORLEVEL% NEQ 0 (
    echo Already linked
)

echo.
echo ======================================
echo Setting Environment Variables
echo ======================================
echo.

REM Generate API key (Windows doesn't have openssl by default)
echo [!] Please generate a secure API key
echo You can use: https://www.random.org/strings/?num=1^&len=64^&digits=on^&loweralpha=on^&unique=on^&format=plain
echo.
set /p API_KEY="Enter your API key: "

echo.
echo Setting environment variables...
railway variables set API_KEY=%API_KEY%
railway variables set REQUIRE_API_KEY=true
railway variables set PESADB_URL=pesadb://localhost/default
railway variables set CORS_ORIGINS=*
railway variables set DEBUG=false

echo.
echo [OK] Environment variables set
echo.

REM Ask about AI features
set /p ENABLE_AI="Do you want to enable AI features? (y/n): "
if /i "%ENABLE_AI%"=="y" (
    echo.
    echo Get your Gemini API key from: https://makersuite.google.com/app/apikey
    set /p GEMINI_KEY="Enter your Gemini API key: "
    railway variables set GEMINI_API_KEY=%GEMINI_KEY%
    railway variables set GEMINI_MODEL=gemini-1.5-flash-latest
    echo [OK] AI features enabled
) else (
    echo [*] Skipping AI features
)

echo.
echo ======================================
echo Adding Persistent Volume
echo ======================================
echo.

set /p ADD_VOLUME="Do you want to add persistent storage for your database? (recommended) (y/n): "
if /i "%ADD_VOLUME%"=="y" (
    echo Adding volume...
    railway volume add --mount-path /app/data
    railway variables set PESADB_URL=pesadb://localhost/default?data_dir=/app/data
    echo [OK] Persistent volume configured
) else (
    echo [!] Warning: Data will not persist across deployments!
)

echo.
echo ======================================
echo Deploying to Railway
echo ======================================
echo.

railway up

echo.
echo ======================================
echo [*] Deployment Complete!
echo ======================================
echo.

REM Get the URL
echo Getting your deployment URL...
echo.
railway domain

echo.
echo ======================================
echo Next Steps:
echo ======================================
echo.
echo 1. View logs: railway logs
echo 2. Open dashboard: railway open
echo 3. Generate a domain in Railway dashboard -^> Settings -^> Networking
echo 4. Test your API: https://your-app.railway.app/api/health
echo 5. View API docs: https://your-app.railway.app/docs
echo.
echo Your API Key: %API_KEY%
echo (Save this securely! You'll need it to access your API)
echo.
echo Update your frontend config with:
echo   API_BASE_URL: https://your-app.railway.app/api
echo   API_KEY: %API_KEY%
echo.
echo ======================================
echo Happy coding! ^_^
echo ======================================

pause
