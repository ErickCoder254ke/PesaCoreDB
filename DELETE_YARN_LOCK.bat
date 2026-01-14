@echo off
echo ========================================
echo Fixing Yarn/npm conflict for deployment
echo ========================================
echo.

cd frontend

echo [1/5] Deleting yarn.lock...
if exist yarn.lock (
    del yarn.lock
    echo     - yarn.lock deleted
) else (
    echo     - yarn.lock not found (already deleted)
)

echo.
echo [2/5] Deleting old package-lock.json...
if exist package-lock.json (
    del package-lock.json
    echo     - package-lock.json deleted
) else (
    echo     - package-lock.json not found
)

echo.
echo [3/5] Installing dependencies with npm...
call npm install --legacy-peer-deps
if errorlevel 1 (
    echo     ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo [4/5] Staging changes for git...
cd ..
git add frontend/package.json frontend/package-lock.json
git add frontend/.npmrc frontend/.node-version
git status

echo.
echo [5/5] Ready to commit!
echo.
echo Run these commands to complete:
echo   git commit -m "Fix deployment: remove yarn.lock, use npm only"
echo   git push
echo.
echo ========================================
echo Done! Now commit and push to deploy
echo ========================================
pause
