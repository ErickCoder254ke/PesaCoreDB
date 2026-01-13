# ⚡ Quick Start - Custom RDBMS

## 🚀 One-Command Start

### Windows
```powershell
.\start-app.bat
```

### macOS/Linux
```bash
chmod +x start-app.sh  # First time only
./start-app.sh
```

---

## 🔧 Manual Start (2 Terminals)

### Terminal 1: Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python server.py
```
✅ Backend runs on **http://localhost:8000**

### Terminal 2: Frontend
```bash
cd frontend
npm install  # First time only
npm start
```
✅ Frontend runs on **http://localhost:3000**

---

## 📍 Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend App** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/health | Server health status |
| **Statistics** | http://localhost:8000/api/stats | Server performance stats |

---

## 🎮 First Steps

1. **Open** http://localhost:3000 in your browser
2. **Click** "Demo Data" button to initialize sample tables
3. **Explore** the schema in the left sidebar
4. **Try** example queries or write your own SQL
5. **Execute** with the button or press `Ctrl/Cmd + Enter`
6. **View** results and export if needed

---

## 💡 Example Queries

### Create a Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    is_active BOOL
)
```

### Insert Data
```sql
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice Johnson', TRUE)
```

### Query Data
```sql
SELECT * FROM users WHERE is_active = TRUE
```

### Join Tables
```sql
SELECT users.name, orders.amount 
FROM users 
INNER JOIN orders ON users.id = orders.user_id
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Execute query |
| `Tab` | Indent in editor |

---

## ✨ Key Features

- 🎨 Dark/Light theme toggle
- 📊 Visual schema explorer
- 💾 Query history with search
- ⭐ Save favorite queries
- 📤 Export results (CSV, JSON, SQL)
- ⚡ Real-time execution stats
- 🎯 Syntax highlighting
- 📱 Responsive design

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Kill any process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Frontend won't start?
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Can't connect to backend?
- ✅ Ensure backend is running on port 8000
- ✅ Check browser console for CORS errors
- ✅ Restart both servers

---

## 📚 Full Documentation

See **STARTUP_GUIDE.md** for complete documentation.

---

**Made with ❤️ for award-winning database experiences!**
