# Custom RDBMS - Testing Guide

## Overview

Your project is now configured to use the **custom RDBMS** (Relational Database Management System) built from scratch. The backend no longer depends on MongoDB and instead uses your own database engine.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   React Frontend│         │  FastAPI Backend│         │  Custom RDBMS   │
│                 │────────▶│                 │────────▶│                 │
│  - SQL Editor   │  HTTP   │  - REST API     │         │  - Database     │
│  - Query UI     │         │  - Query Exec   │         │  - Tables       │
│  - Results View │◀────────│  - JSON Response│◀────────│  - Indexes      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## What Changed

### Backend (`backend/server.py`)
✅ **Removed**: MongoDB/Motor dependencies  
✅ **Added**: Custom RDBMS integration  
✅ **New Endpoints**:
- `POST /api/query` - Execute SQL queries
- `GET /api/tables` - List all tables
- `GET /api/tables/{name}` - Get table info
- `DELETE /api/tables/{name}` - Drop a table
- `POST /api/initialize-demo` - Create demo data

### Frontend (`frontend/src/`)
✅ **New Component**: `DatabaseInterface.jsx` - Full SQL query interface  
✅ **Updated**: `App.js` to use new database interface  
✅ **Features**:
- SQL query editor
- Execute queries and view results
- Table management
- Example queries
- Demo data initialization

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages** (all MongoDB dependencies removed):
- fastapi
- uvicorn
- python-dotenv
- pydantic
- requests
- python-multipart

### 2. Start the Backend Server

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Custom RDBMS API server started
INFO:     Database initialized with 0 tables
```

### 3. Frontend is Already Running

The frontend should already be running on `http://localhost:3000`.

If not, start it:
```bash
cd frontend
npm start
```

## Testing the Application

### Option 1: Use the Web Interface

1. Open **http://localhost:3000** in your browser
2. Click **"Initialize Demo Data"** button to create sample tables
3. Try the example queries by clicking them in the sidebar
4. Write custom SQL queries in the editor

### Option 2: Test Backend API Directly

#### Execute a Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "CREATE TABLE users (id INT PRIMARY KEY, name STRING)"}'
```

#### List Tables
```bash
curl http://localhost:8000/api/tables
```

#### Initialize Demo Data
```bash
curl -X POST http://localhost:8000/api/initialize-demo
```

### Option 3: Use the REPL (Command Line)

The RDBMS also has a standalone REPL:

```bash
cd rdbms
python repl.py
```

Example session:
```sql
db> CREATE TABLE users (id INT PRIMARY KEY, email STRING UNIQUE, name STRING);
Table 'users' created successfully.

db> INSERT INTO users VALUES (1, 'alice@example.com', 'Alice');
1 row inserted into 'users'.

db> SELECT * FROM users;
id | email             | name 
---+-------------------+------
1  | alice@example.com | Alice
(1 row)

db> exit
Goodbye!
```

## Example SQL Queries

### Create a Table
```sql
CREATE TABLE products (
  id INT PRIMARY KEY,
  name STRING UNIQUE,
  price INT,
  in_stock BOOL
)
```

### Insert Data
```sql
INSERT INTO products VALUES (1, 'Laptop', 999, TRUE)
INSERT INTO products VALUES (2, 'Mouse', 25, TRUE)
INSERT INTO products VALUES (3, 'Keyboard', 75, FALSE)
```

### Select Data
```sql
SELECT * FROM products
SELECT name, price FROM products WHERE in_stock = TRUE
```

### Update Data
```sql
UPDATE products SET price = 950 WHERE id = 1
UPDATE products SET in_stock = TRUE
```

### Join Tables
```sql
CREATE TABLE orders (order_id INT PRIMARY KEY, product_id INT, quantity INT)
INSERT INTO orders VALUES (101, 1, 2)
INSERT INTO orders VALUES (102, 2, 5)

SELECT products.name, orders.quantity 
FROM products 
INNER JOIN orders 
ON products.id = orders.product_id
```

### Delete Data
```sql
DELETE FROM products WHERE id = 3
DELETE FROM products WHERE in_stock = FALSE
```

## Supported Features

### ✅ Data Types
- `INT` - Integer numbers
- `STRING` - Text strings
- `BOOL` - Boolean values (TRUE/FALSE)

### ✅ SQL Operations
- `CREATE TABLE` - Define table schema
- `INSERT INTO` - Add rows
- `SELECT` - Query data (with WHERE)
- `UPDATE` - Modify rows (with WHERE)
- `DELETE` - Remove rows (with WHERE)
- `INNER JOIN` - Relational joins

### ✅ Constraints
- `PRIMARY KEY` - Unique identifier
- `UNIQUE` - Unique values
- Type validation
- Constraint enforcement

### ✅ Indexing
- Hash-based indexes
- Automatic indexing on PRIMARY KEY
- Automatic indexing on UNIQUE columns
- O(1) lookup performance

## Known Limitations

### ❌ No Persistence
- Data is stored **in-memory only**
- Database is cleared when server restarts
- No disk-based storage

### ❌ Limited Query Features
- No `AND`, `OR`, `NOT` operators
- No comparison operators (`<`, `>`, `<=`, `>=`, `!=`)
- No `GROUP BY`, `ORDER BY`, `LIMIT`
- No aggregate functions (COUNT, SUM, AVG, etc.)
- Only equality joins (`=`)

### ❌ No Transactions
- No `BEGIN`, `COMMIT`, `ROLLBACK`
- No ACID guarantees
- No concurrent access control

### ❌ Single User
- No multi-user support
- No locking mechanisms
- No connection pooling

## Troubleshooting

### Backend won't start
**Error**: `ModuleNotFoundError: No module named 'rdbms'`

**Solution**: Make sure you're running the server from the backend directory and the rdbms folder is in the parent directory:
```bash
cd backend
python -c "import sys; sys.path.insert(0, '..'); from rdbms.engine import Database; print('OK')"
uvicorn server:app --reload
```

### Frontend can't connect to backend
**Error**: Network errors in browser console

**Solution**: 
1. Verify backend is running on port 8000
2. Check `frontend/.env` has `REACT_APP_BACKEND_URL=http://localhost:8000`
3. Ensure CORS is enabled (it's set to `*` by default)

### Query execution fails
**Error**: Syntax or constraint errors

**Solution**:
- Check SQL syntax matches supported features
- Verify table exists before querying
- Ensure PRIMARY KEY is unique
- Check data types match schema

## Project Structure

```
.
├── backend/
│   ├── server.py          # FastAPI server with RDBMS integration
│   ├── requirements.txt   # Python dependencies (no MongoDB)
│   └── .env              # Environment variables (CORS only)
│
├── frontend/
│   ├── src/
│   │   ├── App.js                      # Main app
│   │   ├── components/
│   │   │   └── DatabaseInterface.jsx  # SQL query UI
│   │   └── components/ui/             # shadcn components
│   └── .env              # React env (backend URL)
│
└── rdbms/
    ├── engine/           # Database core
    │   ├── database.py   # Database container
    │   ├── table.py      # Table implementation
    │   ├── row.py        # Row & data types
    │   └── index.py      # Hash indexing
    │
    ├── sql/              # SQL processing
    │   ├── tokenizer.py  # Lexical analysis
    │   ├── parser.py     # Syntax analysis
    │   └── executor.py   # Query execution
    │
    ├── repl.py           # CLI interface
    └── README.md         # Full RDBMS documentation
```

## Next Steps

1. ✅ **Start the backend**: `cd backend && uvicorn server:app --reload`
2. ✅ **Frontend already running**: http://localhost:3000
3. ✅ **Initialize demo data**: Click button in UI
4. ✅ **Try queries**: Use examples or write your own
5. ✅ **Read RDBMS docs**: See `rdbms/README.md` for details

## Additional Resources

- **RDBMS Documentation**: `rdbms/README.md` - Full database documentation
- **API Documentation**: http://localhost:8000/docs - FastAPI interactive docs
- **Source Code**: Explore `rdbms/engine/` and `rdbms/sql/` for implementation details

---

**Congratulations!** 🎉 Your custom database is now fully integrated and ready to use!
