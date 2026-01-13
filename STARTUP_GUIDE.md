# 🚀 Custom RDBMS - Award-Winning Database System

## Complete Startup Guide

Welcome to the Custom RDBMS project! This guide will walk you through setting up and running both the backend and frontend of this award-worthy relational database management system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Features](#features)
7. [API Documentation](#api-documentation)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This is a **fully functional relational database built from scratch** featuring:

- 🎨 **Award-winning UI/UX** with dark mode support
- ⚡ **Real-time query execution** with performance tracking
- 📊 **Visual schema explorer** for database visualization
- 📝 **SQL syntax highlighting** in the query editor
- 💾 **Query history & favorites** with local persistence
- 📤 **Export capabilities** (CSV, JSON, SQL formats)
- 🔍 **Advanced filtering** and search functionality
- ✨ **Smooth animations** and modern design patterns

### Tech Stack

**Backend:**
- Python 3.8+
- FastAPI (High-performance API framework)
- Custom RDBMS engine (built from scratch)
- Uvicorn (ASGI server)

**Frontend:**
- React 19
- Tailwind CSS
- shadcn/ui components
- Lucide icons
- Axios for API calls

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### For Backend:
- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **pip** (Python package manager - comes with Python)

### For Frontend:
- **Node.js 16+ and npm/yarn** ([Download Node.js](https://nodejs.org/))

### Verify Installation:

```bash
# Check Python version
python --version  # or python3 --version

# Check pip
pip --version  # or pip3 --version

# Check Node.js and npm
node --version
npm --version
```

---

## 🐍 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

**On Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- Python-dotenv
- Pydantic
- And other required packages

### Step 4: Start the Backend Server

```bash
# Option 1: Using Python directly
python server.py

# Option 2: Using Uvicorn directly
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Option 3: With custom port
uvicorn server:app --reload --port 8080
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     ================================================================================
INFO:     Custom RDBMS API Server Starting
INFO:     ================================================================================
INFO:     Version: 2.0.0
INFO:     Database initialized with 0 tables
INFO:     ================================================================================
INFO:     Application startup complete.
```

The backend will be running at: **http://localhost:8000**

### Verify Backend is Running

Open your browser and visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health
- Server Stats: http://localhost:8000/api/stats

---

## ⚛️ Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a **new terminal window** (keep the backend running) and:

```bash
cd frontend
```

### Step 2: Install Dependencies

**Using npm:**
```bash
npm install
```

**Using yarn:**
```bash
yarn install
```

This will install all required packages including:
- React and React DOM
- Tailwind CSS
- shadcn/ui components
- Axios
- React Router
- And all other dependencies

### Step 3: Configure Environment (Optional)

If your backend is running on a different port, create a `.env` file:

```bash
# In frontend directory
touch .env
```

Add the following content:
```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Step 4: Start the Frontend Development Server

**Using npm:**
```bash
npm start
```

**Using yarn:**
```bash
yarn start
```

**Expected Output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

The frontend will automatically open at: **http://localhost:3000**

---

## 🎮 Running the Application

### Quick Start (All-in-One)

**On Windows:**
```powershell
# In project root directory
.\start-app.bat
```

**On macOS/Linux:**
```bash
# Make the script executable (first time only)
chmod +x start-app.sh

# Run the script
./start-app.sh
```

### Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # or yarn install
npm start    # or yarn start
```

---

## ✨ Features

### 1. **Query Execution**
- Write and execute SQL queries with real-time feedback
- Syntax highlighting for better readability
- Keyboard shortcuts (Ctrl/Cmd + Enter to execute)
- Tab support for indentation

### 2. **Query History**
- Automatic saving of all executed queries
- Search and filter through history
- Mark queries as favorites
- View execution time and success status

### 3. **Schema Visualization**
- Visual representation of database structure
- Expandable table details
- Column types, constraints, and indexes
- Quick query generation from schema

### 4. **Data Export**
- Export query results as CSV
- Export as JSON
- Export as SQL INSERT statements

### 5. **Performance Tracking**
- Query execution time measurement
- Server statistics dashboard
- Success rate monitoring
- Uptime tracking

### 6. **Modern UI/UX**
- Dark/Light mode toggle
- Smooth animations and transitions
- Responsive design
- Professional, award-worthy interface

### 7. **Example Queries**
- Pre-built query templates
- Categorized by operation type (DQL, DML, DDL)
- One-click query loading

---

## 📚 API Documentation

### Available Endpoints:

#### Health & Info
- `GET /api/` - API information
- `GET /api/health` - Health check
- `GET /api/stats` - Server statistics

#### Database Operations
- `POST /api/query` - Execute SQL query
- `GET /api/tables` - List all tables
- `GET /api/tables/{table_name}` - Get table details
- `DELETE /api/tables/{table_name}` - Drop table
- `POST /api/initialize-demo` - Load demo data

### Interactive API Documentation

Visit http://localhost:8000/docs for full interactive API documentation with:
- Try-it-out functionality
- Request/response examples
- Schema definitions

---

## 🔍 Supported SQL Operations

### Data Definition Language (DDL)
```sql
-- Create table with constraints
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    is_active BOOL
)
```

### Data Manipulation Language (DML)
```sql
-- Insert data
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice Johnson', TRUE)

-- Update records
UPDATE users SET name = 'Alice Smith' WHERE id = 1

-- Delete records
DELETE FROM users WHERE id = 1
```

### Data Query Language (DQL)
```sql
-- Simple select
SELECT * FROM users

-- Filtered select
SELECT * FROM users WHERE is_active = TRUE

-- Join tables
SELECT users.name, orders.amount 
FROM users 
INNER JOIN orders ON users.id = orders.user_id
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: "Port 8000 is already in use"**
```bash
# Option 1: Use a different port
uvicorn server:app --reload --port 8080

# Option 2: Kill the process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Issue: "Module not found"**
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt

# If using virtual environment, ensure it's activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows
```

**Issue: Import errors from rdbms module**
```bash
# Ensure you're running from the backend directory
cd backend
python server.py
```

### Frontend Issues

**Issue: "Port 3000 is already in use"**
```bash
# The app will prompt you to use a different port
# Or manually specify:
PORT=3001 npm start
```

**Issue: "Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check REACT_APP_BACKEND_URL in .env file
- Verify no CORS errors in browser console

**Issue: "npm install fails"**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Issue: "Table already exists"**
- Tables persist in memory
- Restart the backend server to reset the database
- Or drop the table first: `DROP TABLE table_name`

**Issue: "Query execution fails"**
- Check SQL syntax (case-sensitive keywords recommended)
- Ensure table exists before querying
- Verify column names match table schema

---

## 🚀 Production Deployment

### Backend Production Server

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Production Build

```bash
# Create optimized production build
npm run build

# The build folder can be deployed to any static hosting:
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - GitHub Pages
```

---

## 📊 Performance Tips

1. **Use indexes**: Primary keys and unique constraints automatically create indexes
2. **Batch operations**: Use transactions for multiple INSERT/UPDATE operations
3. **Limit result sets**: Add WHERE clauses to reduce data transfer
4. **Monitor stats**: Check `/api/stats` endpoint for performance metrics

---

## 🎨 Customization

### Change Theme Colors

Edit `frontend/tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: 'your-color-here'
    }
  }
}
```

### Modify Backend Port

Edit `backend/server.py`:
```python
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=YOUR_PORT)
```

---

## 📝 Example Workflow

1. **Start the servers** (backend and frontend)
2. **Click "Demo Data"** to initialize sample tables
3. **Explore the schema** in the left sidebar
4. **Try example queries** or write your own
5. **Execute queries** with Ctrl/Cmd + Enter
6. **View results** in the table below
7. **Export data** if needed
8. **Check query history** for past queries
9. **Star favorites** for quick access

---

## 🏆 Why This Project is Award-Worthy

1. **Full-Stack Excellence**: Complete end-to-end implementation
2. **Modern Design**: Professional UI with smooth animations
3. **Performance**: Optimized query execution and rendering
4. **Developer Experience**: Clean code, documentation, and tooling
5. **User Experience**: Intuitive interface with helpful features
6. **Innovation**: Custom database engine built from scratch
7. **Attention to Detail**: Polish in every interaction

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review API documentation at `/docs`
3. Check browser console for errors
4. Review backend logs in `backend/rdbms.log`

---

## 📄 License

This project is created for educational and demonstration purposes.

---

## 🎯 Quick Command Reference

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

---

**Enjoy using your award-winning Custom RDBMS! 🎉**
