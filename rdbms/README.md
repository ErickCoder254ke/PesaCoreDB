# RDBMS - Relational Database Management System

A relational database management system (RDBMS) built from first principles in Python. This project demonstrates core database internals including data storage, indexing, constraint enforcement, and query execution.

## Overview

This RDBMS implements fundamental database features without relying on any external database engines, ORMs, or storage systems. All data is stored in-memory using Python data structures, and all query processing is implemented from scratch.

**Key Features:**
- Relational data modeling with schema enforcement
- Hash-based indexing for fast lookups
- PRIMARY KEY and UNIQUE constraint enforcement
- Full CRUD operations (CREATE, INSERT, SELECT, UPDATE, DELETE)
- INNER JOIN support for relational queries
- SQL-like query language with custom parser
- Interactive REPL interface

## Supported SQL Syntax

### Data Types

The RDBMS supports three data types:
- `INT` - Integer numbers
- `STRING` - Text strings
- `BOOL` - Boolean values (TRUE/FALSE)

### CREATE TABLE

Create a new table with column definitions:

```sql
CREATE TABLE table_name (
  column_name TYPE [PRIMARY KEY] [UNIQUE],
  ...
);
```

**Rules:**
- Each table must have exactly one PRIMARY KEY column
- Multiple UNIQUE columns are allowed
- PRIMARY KEY automatically implies UNIQUE

**Examples:**
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email STRING UNIQUE,
  name STRING,
  is_active BOOL
);

CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  user_id INT,
  amount INT,
  status STRING
);
```

### INSERT

Insert a row into a table:

```sql
INSERT INTO table_name VALUES (value1, value2, ...);
```

**Rules:**
- Values must match the table schema order
- All columns must be provided
- Data types are validated
- PRIMARY KEY and UNIQUE constraints are enforced

**Examples:**
```sql
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice', TRUE);
INSERT INTO users VALUES (2, 'bob@example.com', 'Bob', FALSE);
INSERT INTO orders VALUES (101, 1, 250, 'pending');
```

### SELECT

Query data from a table:

```sql
SELECT * | column_list FROM table_name [WHERE column = value];
```

**Examples:**
```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, name FROM users;

-- Select with WHERE clause
SELECT * FROM users WHERE is_active = TRUE;
SELECT name FROM users WHERE id = 1;
```

### INNER JOIN

Join two tables on equality condition:

```sql
SELECT columns
FROM tableA
INNER JOIN tableB
ON tableA.column = tableB.column;
```

**Examples:**
```sql
-- Join users and orders
SELECT *
FROM users
INNER JOIN orders
ON users.id = orders.user_id;

-- Join with specific columns
SELECT users.name, orders.amount
FROM users
INNER JOIN orders
ON users.id = orders.user_id;
```

### UPDATE

Update rows in a table:

```sql
UPDATE table_name SET column = value [WHERE column = value];
```

**Examples:**
```sql
-- Update all rows
UPDATE users SET is_active = FALSE;

-- Update with WHERE clause
UPDATE users SET name = 'Alice Smith' WHERE id = 1;
UPDATE orders SET status = 'completed' WHERE order_id = 101;
```

### DELETE

Delete rows from a table:

```sql
DELETE FROM table_name [WHERE column = value];
```

**Examples:**
```sql
-- Delete specific rows
DELETE FROM users WHERE id = 2;
DELETE FROM orders WHERE status = 'cancelled';

-- Delete all rows (use with caution!)
DELETE FROM users;
```

## Architecture

### Project Structure

```
/rdbms/
├── engine/              # Core database engine
│   ├── database.py      # Database container managing tables
│   ├── table.py         # Table with schema, rows, and constraints
│   ├── index.py         # Hash-based indexing
│   └── row.py           # Row representation with type validation
│
├── sql/                 # SQL processing pipeline
│   ├── tokenizer.py     # Lexical analysis (SQL → tokens)
│   ├── parser.py        # Syntax analysis (tokens → commands)
│   └── executor.py      # Command execution (commands → results)
│
├── repl.py              # Interactive REPL interface
└── README.md            # This file
```

### Internal Components

#### 1. Data Storage (`engine/row.py`, `engine/table.py`)

**Row Representation:**
- Each row is a Python object with schema-validated values
- Type checking enforced on insert and update
- Converts string inputs to appropriate types (INT, STRING, BOOL)

**Table Structure:**
- Tables store rows in a Python list (in-memory)
- Schema defined by column definitions with data types and constraints
- Each table maintains its own indexes for fast lookups

**Data Structure:**
```python
Table:
  - name: str
  - schema: Dict[column_name -> DataType]
  - rows: List[Row]
  - indexes: Dict[column_name -> Index]
  - primary_key_column: str
  - unique_columns: Set[str]
```

#### 2. Indexing (`engine/index.py`)

**Hash-Based Indexes:**
- Implemented using Python dictionaries for O(1) average-case lookups
- Automatically created for PRIMARY KEY and UNIQUE columns
- Maintains mappings: `value -> list of row indices`

**Index Operations:**
- `insert(value, row_index)`: Add entry, enforce uniqueness
- `lookup(value)`: Find all rows with given value
- `update(old_value, new_value, row_index)`: Update index on value change
- `remove(value, row_index)`: Remove entry on row deletion

**Uniqueness Enforcement:**
- UNIQUE indexes reject duplicate values at insert/update time
- PRIMARY KEY indexes automatically enforce uniqueness

#### 3. Query Processing Pipeline

**Step 1: Tokenization (`sql/tokenizer.py`)**
- Breaks SQL string into tokens using regex patterns
- Recognizes keywords, identifiers, numbers, strings, operators
- Example: `SELECT * FROM users` → `[Token(KEYWORD, 'SELECT'), Token(STAR, '*'), ...]`

**Step 2: Parsing (`sql/parser.py`)**
- Converts token stream into structured command objects
- Validates syntax and structure
- Example: `[Token(...), ...]` → `SelectCommand(columns=['*'], table='users')`

**Step 3: Execution (`sql/executor.py`)**
- Executes parsed commands against the database
- Uses indexes when available for WHERE clauses
- Returns results or modifies database state

**Query Execution Flow:**
```
SQL String → Tokenizer → Tokens → Parser → Command → Executor → Result
```

#### 4. Constraint Enforcement

**PRIMARY KEY:**
- Enforced via unique index
- Checked on INSERT
- Cannot be updated (enforced by unique index on UPDATE)

**UNIQUE:**
- Enforced via unique index
- Checked on INSERT and UPDATE
- Multiple UNIQUE columns allowed per table

**Type Validation:**
- Performed in `Row` class on insert and update
- Converts values to correct types or raises error
- Special handling for BOOL (accepts 'true', 'false', TRUE, FALSE)

### Design Decisions

**1. In-Memory Storage:**
- All data stored in Python lists and dictionaries
- Fast access but no persistence
- Designed to allow future disk-based storage backend

**2. Hash Indexes:**
- O(1) average-case lookup performance
- Trade-off: requires more memory, only supports equality checks
- Automatic creation for PRIMARY KEY and UNIQUE columns

**3. Explicit Parsing:**
- Custom tokenizer and parser (no external SQL parsing libraries)
- Clear, readable implementation
- Easy to extend with new SQL features

**4. Index Rebuilding:**
- Indexes rebuilt after DELETE operations (indices shift)
- Trade-off: slower deletes, but maintains consistency
- Alternative: use tombstone markers (not implemented)

**5. Join Implementation:**
- Nested loop join algorithm
- O(n*m) complexity
- Future optimization: use indexes for join columns

## Running the REPL

### Prerequisites
- Python 3.7 or higher
- No external dependencies required

### Starting the REPL

```bash
cd /app/rdbms
python3 repl.py
```

### Example Session

```
RDBMS v1.0 - Relational Database Management System
Type SQL commands or 'exit' to quit.

db> CREATE TABLE users (id INT PRIMARY KEY, name STRING, active BOOL);
Table 'users' created successfully.

db> INSERT INTO users VALUES (1, 'Alice', TRUE);
1 row inserted into 'users'.

db> INSERT INTO users VALUES (2, 'Bob', FALSE);
1 row inserted into 'users'.

db> SELECT * FROM users;
id | name  | active
---+-------+-------
1  | Alice | True  
2  | Bob   | False 
(2 rows)

db> SELECT name FROM users WHERE active = TRUE;
name 
-----
Alice
(1 row)

db> UPDATE users SET active = TRUE WHERE id = 2;
1 row(s) updated in 'users'.

db> DELETE FROM users WHERE id = 1;
1 row(s) deleted from 'users'.

db> SELECT * FROM users;
id | name | active
---+------+-------
2  | Bob  | True  
(1 row)

db> exit
Goodbye!
```

## Error Handling

The RDBMS provides detailed, user-readable error messages:

**Schema Validation:**
```
db> CREATE TABLE test (id INT);
Error: Table must have exactly one PRIMARY KEY column
```

**Constraint Violations:**
```
db> INSERT INTO users VALUES (1, 'Alice', TRUE);
1 row inserted into 'users'.

db> INSERT INTO users VALUES (1, 'Bob', FALSE);
Error: UNIQUE constraint violation: Value '1' already exists in column 'id'
```

**Type Errors:**
```
db> INSERT INTO users VALUES ('invalid', 'Alice', TRUE);
Error: Column 'id' expects INT, got 'invalid'
```

**Missing Columns:**
```
db> SELECT invalid_col FROM users;
Error: Column 'invalid_col' does not exist in table 'users'
```

## Known Limitations

**1. No Persistence:**
- Data is stored in-memory only
- Database state is lost when REPL exits
- Future: implement write-ahead log and disk-based storage

**2. Limited Data Types:**
- Only INT, STRING, and BOOL supported
- No DATE, FLOAT, or complex types
- Future: add more types as needed

**3. Simple WHERE Clauses:**
- Only equality checks (`column = value`)
- No comparison operators (`<`, `>`, `<=`, `>=`, `!=`)
- No logical operators (AND, OR, NOT)
- Future: extend parser and executor for complex conditions

**4. No Aggregation:**
- No COUNT, SUM, AVG, MIN, MAX functions
- No GROUP BY or HAVING clauses
- Future: implement aggregation pipeline

**5. Basic JOIN:**
- Only INNER JOIN supported
- Only equality-based join conditions
- No LEFT JOIN, RIGHT JOIN, or FULL OUTER JOIN
- Future: implement other join types

**6. No Transactions:**
- No BEGIN, COMMIT, ROLLBACK
- No ACID guarantees
- Future: implement transaction support with isolation levels

**7. Single-User Only:**
- No concurrent access control
- No locking mechanisms
- Future: implement multi-user support with locking

**8. Index Limitations:**
- Only hash indexes (equality lookups)
- No range queries on indexed columns
- Future: implement B-tree indexes for range queries

## Future Extensibility

### Application Integration

The architecture is designed to support external application integration:

**1. Network Protocol:**
- Add TCP/IP server listening on a port
- Implement wire protocol (e.g., simple text-based or binary)
- Executor and Database classes can be used as-is

**2. API Server:**
- Wrap Database and Executor in REST or GraphQL API
- Add authentication and authorization
- Handle multiple concurrent connections

**3. Client Libraries:**
- Implement client drivers in various languages
- Provide connection pooling
- Abstract SQL generation

**Example API Integration:**
```python
from fastapi import FastAPI
from engine import Database
from sql import Tokenizer, Parser, Executor

app = FastAPI()
database = Database()
tokenizer = Tokenizer()
parser = Parser()
executor = Executor(database)

@app.post("/query")
def execute_query(sql: str):
    tokens = tokenizer.tokenize(sql)
    command = parser.parse(tokens)
    result = executor.execute(command)
    return {"result": result}
```

### Persistence Layer

To add persistence:

**1. Write-Ahead Log (WAL):**
- Log all modifications before applying
- Replay log on startup for crash recovery

**2. Page-Based Storage:**
- Store rows in fixed-size pages on disk
- Implement page cache for frequently accessed data
- Add buffer pool manager

**3. Index Persistence:**
- Serialize indexes to disk
- Rebuild on startup or implement persistent index structures

### Performance Optimizations

**1. Query Optimizer:**
- Cost-based optimization for JOIN order
- Index selection for complex WHERE clauses
- Query plan caching

**2. Better Indexes:**
- B-tree indexes for range queries
- Composite indexes for multi-column lookups
- Covering indexes to avoid table lookups

**3. Execution Improvements:**
- Hash join for better JOIN performance
- Parallel query execution
- Result set streaming for large queries

## Testing

This RDBMS is designed for manual testing via the REPL. To verify functionality:

**1. Test Data Types:**
```sql
CREATE TABLE test (id INT PRIMARY KEY, name STRING, flag BOOL);
INSERT INTO test VALUES (1, 'test', TRUE);
SELECT * FROM test;
```

**2. Test Constraints:**
```sql
CREATE TABLE users (id INT PRIMARY KEY, email STRING UNIQUE);
INSERT INTO users VALUES (1, 'alice@example.com');
INSERT INTO users VALUES (1, 'bob@example.com');  -- Should fail (PRIMARY KEY)
INSERT INTO users VALUES (2, 'alice@example.com');  -- Should fail (UNIQUE)
```

**3. Test CRUD Operations:**
```sql
INSERT INTO users VALUES (2, 'bob@example.com');
SELECT * FROM users;
UPDATE users SET email = 'bob.new@example.com' WHERE id = 2;
DELETE FROM users WHERE id = 2;
```

**4. Test JOIN:**
```sql
CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, amount INT);
INSERT INTO orders VALUES (101, 1, 250);
SELECT users.email, orders.amount FROM users INNER JOIN orders ON users.id = orders.user_id;
```

**5. Test Indexing:**
- Verify that WHERE clauses on PRIMARY KEY/UNIQUE columns are fast
- Compare query performance with and without indexes (via code inspection)

## Conclusion

This RDBMS demonstrates fundamental database concepts:
- Relational data modeling and schema enforcement
- Hash-based indexing for fast lookups
- Constraint enforcement (PRIMARY KEY, UNIQUE)
- Query parsing and execution pipeline
- CRUD operations and relational joins

The modular architecture allows for future enhancements including persistence, advanced query features, and external application integration.
