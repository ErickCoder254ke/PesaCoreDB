# SQL Commands Reference

This document lists all SQL commands supported by the custom RDBMS system.

## Database Management

### CREATE DATABASE
```sql
CREATE DATABASE database_name;
```
Creates a new database.

### DROP DATABASE
```sql
DROP DATABASE database_name;
```
Deletes an existing database.

### USE
```sql
USE database_name;
```
Switches to the specified database for subsequent operations.

### SHOW DATABASES
```sql
SHOW DATABASES;
```
Lists all available databases.

---

## Table Management

### CREATE TABLE
```sql
CREATE TABLE table_name (
    column_name TYPE [PRIMARY KEY] [UNIQUE] [REFERENCES other_table(column)],
    column_name TYPE,
    ...
);
```

**Supported Data Types:**
- `INT` - Integer numbers
- `FLOAT` / `REAL` / `DOUBLE` / `DECIMAL` - Floating point numbers
- `STRING` - Text values
- `BOOL` - Boolean (TRUE/FALSE)

**Column Constraints:**
- `PRIMARY KEY` - Marks column as primary key (exactly one required per table)
- `UNIQUE` - Ensures column values are unique
- `REFERENCES table(column)` - Foreign key constraint

**Example:**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    is_active BOOL
);
```

### DROP TABLE
```sql
DROP TABLE table_name;
```
Deletes an existing table.

### SHOW TABLES
```sql
SHOW TABLES;
```
Lists all tables in the current database.

### DESCRIBE / DESC
```sql
DESCRIBE table_name;
DESC table_name;
```
Shows the schema (columns and types) of a table.

---

## Data Manipulation

### INSERT
```sql
INSERT INTO table_name VALUES (value1, value2, ...);
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);
```

**Note:** Currently requires values for all columns in the table.

**Example:**
```sql
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice', TRUE);
```

### SELECT

#### Basic SELECT
```sql
SELECT * FROM table_name;
SELECT column1, column2 FROM table_name;
SELECT DISTINCT column1 FROM table_name;
```

#### SELECT with WHERE
```sql
SELECT * FROM table_name WHERE condition;
```

**WHERE Operators:**
- Comparison: `=`, `!=`, `<>`, `<`, `>`, `<=`, `>=`
- Logical: `AND`, `OR`, `NOT`
- Pattern matching: `LIKE`, `NOT LIKE`
- Range: `BETWEEN`, `NOT BETWEEN`
- Set membership: `IN`, `NOT IN`
- Null checking: `IS NULL`, `IS NOT NULL`
- Parentheses for grouping: `(condition)`

**Examples:**
```sql
SELECT * FROM users WHERE is_active = TRUE;
SELECT * FROM users WHERE email LIKE '%@example.com';
SELECT * FROM users WHERE id IN (1, 2, 3);
SELECT * FROM users WHERE id BETWEEN 1 AND 10;
SELECT * FROM users WHERE name IS NOT NULL AND is_active = TRUE;
```

#### SELECT with Aggregates
```sql
SELECT COUNT(*) FROM table_name;
SELECT COUNT(column), SUM(column), AVG(column), MIN(column), MAX(column) FROM table_name;
```

**Supported Aggregate Functions:**
- `COUNT(*)` - Count all rows
- `COUNT(column)` - Count non-null values in column
- `SUM(column)` - Sum of numeric values
- `AVG(column)` - Average of numeric values
- `MIN(column)` - Minimum value
- `MAX(column)` - Maximum value

#### SELECT with GROUP BY
```sql
SELECT column, COUNT(*) FROM table_name GROUP BY column;
SELECT column1, column2, SUM(column3) FROM table_name GROUP BY column1, column2;
```

#### SELECT with HAVING
```sql
SELECT column, COUNT(*) FROM table_name GROUP BY column HAVING COUNT(*) > 5;
```

#### SELECT with ORDER BY
```sql
SELECT * FROM table_name ORDER BY column;
SELECT * FROM table_name ORDER BY column ASC;
SELECT * FROM table_name ORDER BY column DESC;
SELECT * FROM table_name ORDER BY column1, column2 DESC;
```

#### SELECT with LIMIT and OFFSET
```sql
SELECT * FROM table_name LIMIT 10;
SELECT * FROM table_name LIMIT 10 OFFSET 20;
```

#### SELECT with INNER JOIN
```sql
SELECT table1.column1, table2.column2 
FROM table1 
INNER JOIN table2 ON table1.id = table2.foreign_id;
```

**Note:** WHERE clause after JOIN is not fully supported yet.

**Complete Example:**
```sql
SELECT status, COUNT(*) as order_count, AVG(amount) as avg_amount
FROM orders
WHERE status != 'cancelled'
GROUP BY status
HAVING COUNT(*) > 5
ORDER BY order_count DESC
LIMIT 10;
```

### UPDATE
```sql
UPDATE table_name SET column = value WHERE condition;
UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
```

**Example:**
```sql
UPDATE users SET is_active = FALSE WHERE id = 2;
UPDATE users SET name = 'Alice Smith', email = 'alice.smith@example.com' WHERE id = 1;
```

### DELETE
```sql
DELETE FROM table_name WHERE condition;
```

**Example:**
```sql
DELETE FROM orders WHERE status = 'cancelled';
DELETE FROM users WHERE is_active = FALSE;
```

---

## HTTP API Endpoints

### Execute SQL Query
```
POST /api/query
Content-Type: application/json

{
  "sql": "SELECT * FROM users;",
  "db": "database_name"
}
```

### Database Operations
- `GET /api/databases` - List all databases
- `POST /api/databases` - Create a database
- `DELETE /api/databases/{db_name}` - Delete a database
- `GET /api/databases/{db_name}/info` - Get database information

### Table Operations
- `GET /api/tables?db=database_name` - List tables in database
- `GET /api/tables/{table_name}?db=database_name` - Get table schema
- `DELETE /api/tables/{table_name}?db=database_name` - Drop table

### Relationships
- `GET /api/relationships?db=database_name` - List foreign key relationships

---

## Literals and Values

### String Literals
```sql
'text value'
```
Strings must be enclosed in single quotes.

### Numeric Literals
```sql
123      -- Integer
45.67    -- Float
```

### Boolean Literals
```sql
TRUE
FALSE
```

### NULL Value
```sql
NULL
```

---

## Important Notes

1. **Primary Key Requirement:** Every table must have exactly one PRIMARY KEY column.

2. **INSERT Constraints:** INSERT statements currently require values for all columns in the table.

3. **Foreign Key Validation:** Foreign key references are validated on INSERT and UPDATE operations. Deleting a row that is referenced by another table will raise an error.

4. **Automatic Indexing:** The system automatically creates hash-based indexes for:
   - Primary key columns (unique index)
   - Columns with UNIQUE constraint
   - Foreign key columns (for join performance)

5. **Type Validation:** Values are validated against column types on INSERT and UPDATE. Columns with names ending in `_at`, `_date`, or containing `timestamp` are validated as ISO-8601 date strings.

6. **JOIN Limitations:** 
   - Only INNER JOIN is currently supported
   - WHERE clauses after JOIN are not fully supported

7. **Aggregate Limitations:** Aggregate functions only accept column references (or COUNT(*)), not expressions.

---

## Example Usage Flow

```sql
-- Create and use database
CREATE DATABASE myapp;
USE myapp;

-- Create tables with relationships
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    is_active BOOL
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT REFERENCES users(id),
    amount FLOAT,
    status STRING,
    created_at STRING
);

-- Insert data
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice', TRUE);
INSERT INTO users VALUES (2, 'bob@example.com', 'Bob', TRUE);
INSERT INTO orders VALUES (101, 1, 99.99, 'completed', '2025-01-01T10:00:00Z');
INSERT INTO orders VALUES (102, 1, 149.99, 'pending', '2025-01-02T15:30:00Z');

-- Query data
SELECT * FROM users WHERE is_active = TRUE;

SELECT users.name, orders.order_id, orders.amount
FROM users
INNER JOIN orders ON users.id = orders.user_id;

SELECT status, COUNT(*) as count, AVG(amount) as avg_amount
FROM orders
GROUP BY status
ORDER BY count DESC;

-- Update and delete
UPDATE orders SET status = 'completed' WHERE order_id = 102;
DELETE FROM orders WHERE status = 'cancelled';
```
