# RDBMS v2.0 - Example SQL Scripts

This directory contains example SQL scripts demonstrating the capabilities of the RDBMS engine.

## Files

### 1. `demo_commands.sql`
Comprehensive demonstration of all supported SQL commands:
- Database management (CREATE DATABASE, DROP DATABASE, USE, SHOW DATABASES)
- Table management (CREATE TABLE, DROP TABLE, SHOW TABLES, DESCRIBE)
- Data manipulation (INSERT, SELECT, UPDATE, DELETE)
- Joins (INNER JOIN)
- Constraints (PRIMARY KEY, UNIQUE, FOREIGN KEY)
- All data types (INT, STRING, BOOL)

**Usage:**
```bash
# From the rdbms directory
python repl.py

# Then copy/paste commands from demo_commands.sql
# Or run individual commands
```

### 2. `test_constraints.sql`
Focused testing of constraint enforcement and edge cases:
- PRIMARY KEY constraints
- UNIQUE constraints
- Type validation
- Foreign key references (schema support)
- Index usage and cleanup
- Constraint violation error messages

**Usage:**
Same as above - copy/paste into the REPL or run individual commands.

## Supported SQL Commands

### Database Management
```sql
CREATE DATABASE database_name;
DROP DATABASE database_name;
USE database_name;
SHOW DATABASES;
```

### Table Management
```sql
CREATE TABLE table_name (
    column_name TYPE [PRIMARY KEY] [UNIQUE] [REFERENCES other_table(column)],
    ...
);
DROP TABLE table_name;
SHOW TABLES;
DESCRIBE table_name;  -- or DESC table_name
```

### Data Types
- `INT` - Integer numbers
- `STRING` - Text strings
- `BOOL` - Boolean (TRUE/FALSE)

### Data Manipulation

#### Insert
```sql
-- All columns
INSERT INTO table_name VALUES (value1, value2, ...);

-- Specific columns
INSERT INTO table_name (col1, col2) VALUES (value1, value2);
```

#### Select
```sql
-- All columns
SELECT * FROM table_name;

-- Specific columns
SELECT col1, col2 FROM table_name;

-- With filter
SELECT * FROM table_name WHERE column = value;

-- With join
SELECT * FROM table1 
INNER JOIN table2 ON table1.col = table2.col;
```

#### Update
```sql
UPDATE table_name SET column = value WHERE condition_col = condition_value;
```

#### Delete
```sql
DELETE FROM table_name WHERE column = value;
```

## Features

### 1. Separation of Concerns
- **Tokenizer** → breaks SQL into tokens
- **Parser** → builds AST from tokens
- **Executor** → executes commands against the database
- **Engine** → manages tables, rows, indexes

### 2. Index Optimization
- Automatic hash-based indexes on PRIMARY KEY and UNIQUE columns
- Fast O(1) lookups for equality conditions on indexed columns
- Automatic index maintenance during INSERT, UPDATE, DELETE

### 3. Constraint Enforcement
- PRIMARY KEY uniqueness
- UNIQUE constraint enforcement
- Type validation (INT, STRING, BOOL)
- Clear error messages for violations

### 4. Error Handling
SQL-style error messages:
- `SyntaxError: Unexpected token near '...'`
- `TableNotFoundError: table 'users' does not exist`
- `ConstraintViolation: UNIQUE constraint violation: ...`
- `DatabaseNotFoundError: database 'xyz' does not exist`

### 5. Persistence
- Databases saved to disk as JSON
- Automatic save after each modification
- Load databases on startup

## Example Session

```sql
-- Create and use a database
CREATE DATABASE mydb;
USE mydb;

-- Create a table
CREATE TABLE users (
    id INT PRIMARY KEY,
    name STRING,
    email STRING UNIQUE,
    active BOOL
);

-- Insert data
INSERT INTO users VALUES (1, 'Alice', 'alice@example.com', TRUE);
INSERT INTO users VALUES (2, 'Bob', 'bob@example.com', TRUE);

-- Query data
SELECT * FROM users;
SELECT name, email FROM users WHERE active = TRUE;

-- Update data
UPDATE users SET active = FALSE WHERE id = 1;

-- Delete data
DELETE FROM users WHERE id = 2;

-- View table structure
DESCRIBE users;

-- Clean up
DROP TABLE users;
DROP DATABASE mydb;
```

## Architecture Highlights

### Extensibility
The system is designed for future enhancements:
- External API access (REST endpoints)
- AI-assisted query help (natural language → SQL)
- Additional data types (DATE, FLOAT, etc.)
- More complex WHERE clauses (AND, OR, NOT, comparisons)
- Aggregate functions (COUNT, SUM, AVG, etc.)
- GROUP BY, ORDER BY, LIMIT

### Performance
- Hash-based indexes for O(1) lookups
- Index usage optimization in WHERE clauses
- Efficient row storage and retrieval

### Reliability
- Atomic database saves (temp file + rename)
- Schema validation at table creation
- Type validation at insert/update
- Constraint enforcement with clear error messages
