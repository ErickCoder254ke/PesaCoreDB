@echo off
REM Health Check Test Script for Windows
REM Tests the local server health endpoint

echo ======================================
echo PesacodeDB Health Check Test
echo ======================================
echo.

echo Testing server health endpoint...
echo.

REM Test root health endpoint
echo 1. Testing /health endpoint (should work without API key):
curl -s -w "HTTP_CODE: %%{http_code}" http://localhost:8000/health
echo.
echo.

REM Test detailed health endpoint
echo 2. Testing /api/health endpoint (detailed, should work without API key):
curl -s -w "HTTP_CODE: %%{http_code}" http://localhost:8000/api/health
echo.
echo.

REM Test root endpoint
echo 3. Testing /api/ endpoint:
curl -s -w "HTTP_CODE: %%{http_code}" http://localhost:8000/api/
echo.
echo.

echo ======================================
echo Test Complete
echo ======================================
echo.
echo If you see HTTP_CODE: 200, the health checks are working!
echo Your server is ready for deployment.
echo.
pause
