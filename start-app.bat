@echo off
echo ==========================================
echo 🚀 Starting Custom RDBMS Application
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Start Backend
echo 📦 Starting Backend Server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Start backend in new window
echo 🐍 Starting Python backend on port 8000...
start "RDBMS Backend" cmd /k "venv\Scripts\activate.bat && python server.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

cd ..

REM Start Frontend
echo.
echo 📦 Starting Frontend Server...
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend in new window
echo ⚛️ Starting React frontend on port 3000...
start "RDBMS Frontend" cmd /k "npm start"

cd ..

echo.
echo ==========================================
echo ✅ Application Started Successfully!
echo ==========================================
echo.
echo 📍 Frontend: http://localhost:3000
echo 📍 Backend API: http://localhost:8000
echo 📍 API Docs: http://localhost:8000/docs
echo.
echo Two new windows have been opened for backend and frontend.
echo Close those windows to stop the servers.
echo.
pause
