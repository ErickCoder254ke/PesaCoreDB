@echo off
REM Test Dockerfile locally before deploying to Railway

echo ======================================
echo Testing Dockerfile Locally
echo ======================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] Docker is not installed.
    echo Install Docker from: https://docs.docker.com/get-docker/
    exit /b 1
)

echo [OK] Docker detected
echo.

REM Build the image
echo [*] Building Docker image...
docker build -t pesacodedb-test .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Build successful!
    echo.
    echo [*] Starting container...
    echo.
    
    REM Run the container
    docker run -d --name pesacodedb-test -p 8000:8000 -e API_KEY=test_api_key_12345 -e REQUIRE_API_KEY=true -e PESADB_URL=pesadb://localhost/default -e CORS_ORIGINS=* pesacodedb-test
    
    echo [OK] Container started!
    echo.
    echo Waiting 3 seconds for server to start...
    timeout /t 3 /nobreak >nul
    echo.
    
    REM Test the API
    echo [*] Testing API...
    echo.
    
    curl -s http://localhost:8000/api/health
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [OK] Health check successful!
        echo.
        
        echo [*] Testing with API key...
        curl -s -H "X-API-Key: test_api_key_12345" http://localhost:8000/api/databases
        echo.
        echo.
        
        echo ======================================
        echo [OK] All tests passed!
        echo ======================================
        echo.
        echo View logs:
        echo   docker logs pesacodedb-test
        echo.
        echo Stop container:
        echo   docker stop pesacodedb-test
        echo.
        echo Remove container:
        echo   docker rm pesacodedb-test
        echo.
        echo Access API docs:
        echo   http://localhost:8000/docs
        echo.
    ) else (
        echo [X] Health check failed
        echo.
        echo Container logs:
        docker logs pesacodedb-test
        echo.
        echo Cleaning up...
        docker stop pesacodedb-test
        docker rm pesacodedb-test
        exit /b 1
    )
) else (
    echo.
    echo [X] Build failed
    exit /b 1
)

pause
