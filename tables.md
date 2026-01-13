# Table Persistence and Password Protection Implementation Guide

## Current Issue: Tables Disappear After Reload

### Why This Happens
Your RDBMS currently stores all data **in-memory only**. When you look at `backend/server.py` line 38:

```python
database = Database()
```

This creates a new, empty `Database` object each time the server starts. The `Database` class (in `rdbms/engine/database.py`) stores tables in a Python dictionary:

```python
def __init__(self):
    self.tables: Dict[str, Table] = {}
```

**Problem**: When the server restarts or reloads, this dictionary is recreated empty, losing all your tables and data.

---

## Solution 1: Implement Persistent Storage

You need to save the database state to disk and load it when the server starts.

### Option A: JSON File Storage (Simplest)

#### Files to Modify:

**1. `rdbms/engine/database.py`**

Add these methods to the `Database` class:

```python
import json
from pathlib import Path
from datetime import datetime

class Database:
    def __init__(self, storage_path: str = "data/database.json"):
        """Initialize database with persistent storage."""
        self.tables: Dict[str, Table] = {}
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if available
        self.load_from_disk()
    
    def save_to_disk(self):
        """Persist database to disk."""
        data = {
            "tables": {},
            "metadata": {
                "last_saved": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Serialize each table
        for table_name, table in self.tables.items():
            data["tables"][table_name] = {
                "name": table.name,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.data_type.value,
                        "is_primary_key": col.is_primary_key,
                        "is_unique": col.is_unique
                    }
                    for col in table.columns
                ],
                "rows": [
                    {col.name: row.values[idx] for idx, col in enumerate(table.columns)}
                    for row in table.rows
                ],
                "indexes": list(table.indexes.keys())
            }
        
        # Write to file
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_disk(self):
        """Load database from disk."""
        if not self.storage_path.exists():
            return  # No saved data yet
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct tables
            from .table import Table, Column
            from .row import DataType
            
            for table_name, table_data in data.get("tables", {}).items():
                # Recreate columns
                columns = [
                    Column(
                        name=col["name"],
                        data_type=DataType(col["type"]),
                        is_primary_key=col["is_primary_key"],
                        is_unique=col["is_unique"]
                    )
                    for col in table_data["columns"]
                ]
                
                # Create table
                table = Table(table_name, columns)
                
                # Restore rows
                from .row import Row
                for row_data in table_data["rows"]:
                    values = [row_data[col.name] for col in columns]
                    row = Row(values)
                    table.rows.append(row)
                    
                    # Rebuild indexes
                    for idx, col in enumerate(columns):
                        if col.is_primary_key or col.is_unique:
                            if col.name not in table.indexes:
                                table.indexes[col.name] = {}
                            table.indexes[col.name][values[idx]] = row
                
                self.tables[table_name] = table
                
        except Exception as e:
            print(f"Error loading database: {e}")
            # Continue with empty database
```

**2. Modify all data-changing methods to auto-save:**

After `create_table()`, `drop_table()`, add:
```python
self.save_to_disk()
```

**3. `rdbms/engine/table.py`**

After methods that modify data (insert, update, delete), call:
```python
# You'll need to pass database reference or use a callback
self.database.save_to_disk()
```

**4. `backend/server.py`**

Keep the database instance global, but it will now auto-load on startup:

```python
# Line 38 - database now loads from disk automatically
database = Database(storage_path="data/database.json")
```

After each successful query that modifies data:
```python
database.save_to_disk()
```

#### Where to Call `save_to_disk()`:

In `backend/server.py`, in the `execute_query` endpoint, after successful execution:

```python
@api_router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    # ... existing code ...
    
    # Execute the command
    result = executor.execute(command)
    
    # Save to disk after any data-changing operation
    if command["type"] in ["CREATE", "INSERT", "UPDATE", "DELETE", "DROP"]:
        database.save_to_disk()
    
    # ... rest of code ...
```

---

### Option B: SQLite Backend Storage (More Robust)

Instead of JSON, use SQLite to store your RDBMS metadata:

**Advantages:**
- Better performance with large datasets
- ACID compliance
- Built into Python (no extra dependencies)

**Implementation:**
- Create `data/rdbms_storage.db` 
- Store table schemas in a `tables` table
- Store actual data in a `table_data` table with JSON columns
- Load/save using `sqlite3` module

---

### Option C: Pickle Serialization (Fastest, Less Portable)

**Pros:** Very fast, preserves Python objects exactly
**Cons:** Not human-readable, version-dependent

```python
import pickle

def save_to_disk(self):
    with open(self.storage_path, 'wb') as f:
        pickle.dump(self.tables, f)

def load_from_disk(self):
    if self.storage_path.exists():
        with open(self.storage_path, 'rb') as f:
            self.tables = pickle.load(f)
```

---

## Solution 2: Password Protection for Tables

### Implementation Strategy

#### Backend Changes Required:

**1. `rdbms/engine/table.py`**

Add password protection to the `Table` class:

```python
import hashlib
from typing import Optional

class Table:
    def __init__(self, name: str, columns: List[Column], password: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.rows: List[Row] = []
        self.indexes: Dict[str, Dict] = {}
        
        # Password protection
        self.is_protected = password is not None
        self.password_hash = self._hash_password(password) if password else None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches."""
        if not self.is_protected:
            return True
        return self._hash_password(password) == self.password_hash
    
    def set_password(self, password: Optional[str]):
        """Set or remove password protection."""
        if password:
            self.is_protected = True
            self.password_hash = self._hash_password(password)
        else:
            self.is_protected = False
            self.password_hash = None
```

**2. Extend SQL Parser for Password Support**

In `rdbms/sql/parser.py`, extend CREATE TABLE syntax:

```sql
CREATE TABLE users (...) WITH PASSWORD 'mypassword123'
```

Parse this and pass password to table creation.

**3. Add Access Control to Operations**

In `rdbms/sql/executor.py`, before executing operations:

```python
class Executor:
    def execute(self, command: dict, password: Optional[str] = None):
        table_name = command.get("table")
        
        if table_name:
            table = self.database.get_table(table_name)
            
            # Check password protection
            if table.is_protected and not table.verify_password(password):
                raise ValueError(f"Access denied: Invalid password for table '{table_name}'")
        
        # Continue with execution...
```

**4. API Changes in `backend/server.py`**

Update the request model:

```python
class QueryRequest(BaseModel):
    sql: str
    password: Optional[str] = None  # Table password if protected

@api_router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    # Pass password to executor
    result = executor.execute(command, password=request.password)
```

**5. New API Endpoints for Password Management**

```python
class TablePasswordRequest(BaseModel):
    password: str

@api_router.post("/tables/{table_name}/set-password")
async def set_table_password(table_name: str, request: TablePasswordRequest):
    """Set password protection on a table."""
    table = database.get_table(table_name)
    table.set_password(request.password)
    database.save_to_disk()
    return {"success": True, "message": f"Password set for table '{table_name}'"}

@api_router.delete("/tables/{table_name}/remove-password")
async def remove_table_password(table_name: str, current_password: str):
    """Remove password protection."""
    table = database.get_table(table_name)
    if not table.verify_password(current_password):
        raise HTTPException(status_code=403, detail="Invalid password")
    table.set_password(None)
    database.save_to_disk()
    return {"success": True, "message": "Password protection removed"}
```

#### Frontend Changes Required:

**1. `frontend/src/components/DatabaseInterface.jsx`**

Add password input field:

```jsx
const [tablePassword, setTablePassword] = useState("");

const executeQuery = async () => {
    // Include password in request
    const response = await axios.post(`${API}/query`, { 
        sql: query,
        password: tablePassword || undefined
    });
};

// Add password input UI
<Input
    type="password"
    placeholder="Table password (if protected)"
    value={tablePassword}
    onChange={(e) => setTablePassword(e.target.value)}
/>
```

**2. `frontend/src/components/SchemaVisualizer.jsx`**

Show lock icon for protected tables and prompt for password:

```jsx
{details && details.is_protected && (
    <Badge variant="destructive" className="gap-1">
        <Lock className="h-3 w-3" />
        Protected
    </Badge>
)}
```

**3. Create Password Management UI Component**

`frontend/src/components/TablePasswordManager.jsx`:
- Dialog to set/change password
- Input to remove password
- Visual indicator of protection status

---

## Recommended Implementation Order

### Phase 1: Persistence (Critical)
1. ✅ Add `save_to_disk()` and `load_from_disk()` to `Database` class
2. ✅ Create `data/` directory for storage
3. ✅ Modify `database.py` to auto-load on init
4. ✅ Call `save_to_disk()` after all data-changing operations
5. ✅ Test: Create tables, restart server, verify tables persist

### Phase 2: Password Protection (Enhancement)
1. ✅ Add password fields to `Table` class
2. ✅ Implement password hashing and verification
3. ✅ Update SQL parser for `WITH PASSWORD` syntax
4. ✅ Add password checking to executor
5. ✅ Create API endpoints for password management
6. ✅ Update frontend with password input
7. ✅ Add visual indicators for protected tables
8. ✅ Test: Create protected table, verify access control

---

## Files You Need to Modify

### Backend:
- ✅ `rdbms/engine/database.py` - Add persistence methods
- ✅ `rdbms/engine/table.py` - Add password protection
- ✅ `rdbms/sql/parser.py` - Parse password syntax (optional)
- ✅ `rdbms/sql/executor.py` - Add password verification
- ✅ `backend/server.py` - Call save_to_disk(), add password endpoints

### Frontend:
- ✅ `frontend/src/components/DatabaseInterface.jsx` - Password input
- ✅ `frontend/src/components/SchemaVisualizer.jsx` - Show protection status
- ⚠️ `frontend/src/components/TablePasswordManager.jsx` - NEW file to create

### New Files/Directories:
- ✅ `data/` - Directory to store database.json
- ✅ `data/.gitignore` - Ignore database files in git

---

## Testing Checklist

### Persistence Tests:
- [ ] Create a table with data
- [ ] Restart the backend server
- [ ] Verify table and data still exist
- [ ] Insert more data
- [ ] Restart again
- [ ] Verify all data persists

### Password Protection Tests:
- [ ] Create a table with password
- [ ] Try to query without password (should fail)
- [ ] Query with correct password (should succeed)
- [ ] Try to query with wrong password (should fail)
- [ ] Change table password
- [ ] Verify old password no longer works
- [ ] Remove password protection
- [ ] Verify table is accessible without password

---

## Security Considerations

### For Password Protection:
1. **Never log passwords** - Remove from all log statements
2. **Use strong hashing** - SHA-256 minimum (consider bcrypt/argon2)
3. **Salt passwords** - Add unique salt per table for better security
4. **HTTPS only** - Passwords sent over HTTP are vulnerable
5. **Rate limiting** - Prevent brute force attacks on passwords

### For Persistence:
1. **Backup regularly** - Implement automatic backups of `database.json`
2. **File permissions** - Restrict access to data directory
3. **Validate on load** - Check data integrity when loading from disk
4. **Handle corruption** - Graceful fallback if storage file is corrupted

---

## Advanced Features (Future)

- 📊 **Database Snapshots** - Save point-in-time copies
- 🔐 **Encryption at Rest** - Encrypt database.json file
- 👥 **User Authentication** - Multi-user with different permissions
- 📝 **Audit Logging** - Track who accessed which tables
- 🔄 **Replication** - Sync database across multiple servers
- ⚡ **Caching Layer** - Redis for frequently accessed tables

---

## Need Help?

If you encounter issues:
1. Check `backend/rdbms.log` for error messages
2. Verify `data/database.json` file is being created
3. Ensure proper file permissions on `data/` directory
4. Test persistence with simple tables first
5. Add password protection only after persistence works

Good luck with the implementation! 🚀
