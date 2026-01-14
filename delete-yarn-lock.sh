#!/bin/bash

echo "========================================"
echo "Fixing Yarn/npm conflict for deployment"
echo "========================================"
echo ""

cd frontend

echo "[1/5] Deleting yarn.lock..."
if [ -f yarn.lock ]; then
    rm yarn.lock
    echo "    ✓ yarn.lock deleted"
else
    echo "    - yarn.lock not found (already deleted)"
fi

echo ""
echo "[2/5] Deleting old package-lock.json..."
if [ -f package-lock.json ]; then
    rm package-lock.json
    echo "    ✓ package-lock.json deleted"
else
    echo "    - package-lock.json not found"
fi

echo ""
echo "[3/5] Installing dependencies with npm..."
npm install --legacy-peer-deps
if [ $? -ne 0 ]; then
    echo "    ✗ ERROR: npm install failed"
    exit 1
fi

echo ""
echo "[4/5] Staging changes for git..."
cd ..
git add frontend/package.json frontend/package-lock.json
git add frontend/.npmrc frontend/.node-version
git status

echo ""
echo "[5/5] Ready to commit!"
echo ""
echo "Run these commands to complete:"
echo "  git commit -m 'Fix deployment: remove yarn.lock, use npm only'"
echo "  git push"
echo ""
echo "========================================"
echo "Done! Now commit and push to deploy"
echo "========================================"
