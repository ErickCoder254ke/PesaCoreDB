# PesacodeDB SQL Commands Reference

Comprehensive guide to all SQL commands supported by the PesacodeDB custom RDBMS.

---

## 📋 Table of Contents

- [Database Management](#database-management)
- [Table Management](#table-management)
- [Data Manipulation](#data-manipulation)
- [Data Types](#data-types)
- [Constraints](#constraints)
- [WHERE Clause & Expressions](#where-clause--expressions)
- [Joins](#joins)
- [Aggregates & Grouping](#aggregates--grouping)
- [Date/Time Functions](#datetime-functions)
- [HTTP API Endpoints](#http-api-endpoints)
- [Limitations & Known Issues](#limitations--known-issues)
- [Complete Examples](#complete-examples)

---

## Database Management

### CREATE DATABASE
Create a new database.

```sql
CREATE DATABASE database_name;
```

**Example:**
```sql
CREATE DATABASE myapp;
```

---

### DROP DATABASE
Delete an existing database.

```sql
DROP DATABASE database_name;
```

**Example:**
```sql
DROP DATABASE old_database;
```

**⚠️ Warning:** Cannot drop the 'default' database.

---

### USE
Switch to a specific database for subsequent operations.

```sql
USE database_name;
```

**Example:**
```sql
USE myapp;
```

---

### SHOW DATABASES
List all available databases.

```sql
SHOW DATABASES;
```

**Returns:**
```json
{
  "success": true,
  "databases": ["default", "myapp", "test"],
  "total": 3
}
```

---

## Table Management

### CREATE TABLE
Create a new table with columns and constraints.

**Syntax:**
```sql
CREATE TABLE table_name (
    column_name TYPE [PRIMARY KEY] [UNIQUE] [REFERENCES other_table(column)],
    column_name TYPE,
    ...
);
```

**Example:**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    birth_date DATE,
    is_active BOOL
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT REFERENCES users(id),
    amount FLOAT,
    status STRING,
    created_at DATETIME
);
```

**✅ Supported:**
- Single-column PRIMARY KEY (required - exactly one per table)
- UNIQUE constraint
- FOREIGN KEY via REFERENCES other_table(column)
- Multiple columns per table

**❌ Not Supported:**
- Composite (multi-column) PRIMARY KEY
- DEFAULT values
- NOT NULL constraint (all columns currently required)
- CHECK constraints
- AUTO_INCREMENT

---

### DROP TABLE
Delete an existing table.

```sql
DROP TABLE table_name;
```

**Example:**
```sql
DROP TABLE old_users;
```

**⚠️ Warning:** Deleting a table that is referenced by foreign keys in other tables may cause issues.

---

### SHOW TABLES
List all tables in the current database.

```sql
SHOW TABLES;
```

**Returns:**
```json
{
  "tables": ["users", "orders", "products"],
  "total_tables": 3
}
```

---

### DESCRIBE / DESC
Show the schema (columns, types, constraints) of a table.

```sql
DESCRIBE table_name;
DESC table_name;  -- Shorthand
```

**Example:**
```sql
DESCRIBE users;
```

**Returns:**
```json
{
  "name": "users",
  "columns": [
    {
      "name": "id",
      "type": "INT",
      "is_primary_key": true,
      "is_unique": false
    },
    {
      "name": "email",
      "type": "STRING",
      "is_primary_key": false,
      "is_unique": true
    }
  ],
  "row_count": 42,
  "indexes": ["id", "email"]
}
```

---

## Data Types

PesacodeDB supports the following data types:

### Numeric Types

| Type | Aliases | Description | Example |
|------|---------|-------------|---------|
| `INT` | - | Integer numbers | `42`, `-17` |
| `FLOAT` | `REAL`, `DOUBLE`, `DECIMAL` | Floating-point numbers | `3.14`, `-99.99` |

### String Type

| Type | Description | Example |
|------|-------------|---------|
| `STRING` | Text values (single quotes) | `'Alice'`, `'alice@example.com'` |

### Boolean Type

| Type | Description | Example |
|------|-------------|---------|
| `BOOL` | Boolean values | `TRUE`, `FALSE` |

### Date/Time Types

| Type | Aliases | Description | Format |
|------|---------|-------------|--------|
| `DATE` | - | Date only | `'2025-01-14'` (ISO 8601) |
| `TIME` | - | Time only | `'14:30:00'` (ISO 8601) |
| `DATETIME` | `TIMESTAMP` | Date and time | `'2025-01-14T14:30:00'` or `'2025-01-14 14:30:00'` |

**Note:** Date/time values must be provided as strings in ISO 8601 format.

---

## Constraints

### PRIMARY KEY
Every table **must** have exactly one PRIMARY KEY column.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name STRING
);
```

**Features:**
- Automatically creates a unique index
- Must contain unique values
- Used for referential integrity checks

**❌ Not Supported:**
- Composite (multi-column) primary keys
- Multiple PRIMARY KEY columns

---

### UNIQUE
Ensures all values in a column are unique.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING UNIQUE
);
```

**Features:**
- Automatically creates a unique index
- Duplicate values raise an error

---

### FOREIGN KEY (REFERENCES)
Create a foreign key relationship to another table.

```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT REFERENCES users(id)
);
```

**Features:**
- Validates that referenced value exists on INSERT/UPDATE
- Automatically creates an index on the foreign key column
- Prevents deletion of referenced primary key values

**Validation:**
- On INSERT: Checks that the foreign key value exists in the referenced table
- On UPDATE: Checks that the new foreign key value exists
- On DELETE: Checks that no other table references the deleted primary key

---

## Data Manipulation

### INSERT
Insert a single row into a table.

**Syntax:**
```sql
INSERT INTO table_name VALUES (value1, value2, ...);
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);
```

**Examples:**
```sql
-- All columns
INSERT INTO users VALUES (1, 'alice@example.com', 'Alice Johnson', '1990-05-15', TRUE);

-- Specific columns (currently requires all columns anyway)
INSERT INTO users (id, email, name, birth_date, is_active) 
VALUES (2, 'bob@example.com', 'Bob Smith', '1985-08-20', TRUE);

-- With NULL
INSERT INTO users VALUES (3, 'carol@example.com', 'Carol White', NULL, FALSE);
```

**Value Types:**
- Numbers: `123`, `45.67`
- Strings: `'text'` (single quotes required)
- Booleans: `TRUE`, `FALSE`
- NULL: `NULL`

**⚠️ Important Limitations:**
- Only single-row INSERT supported (no multi-row VALUES)
- Currently requires values for **all columns** (no partial inserts with defaults)
- NULL insertion is parsed but may cause validation errors (inconsistent support)

**❌ Not Supported:**
- Multi-row INSERT: `INSERT INTO t VALUES (1,2), (3,4);`
- INSERT ... SELECT: `INSERT INTO t SELECT * FROM other;`

---

### SELECT

#### Basic SELECT
Retrieve data from a table.

```sql
-- All columns
SELECT * FROM users;

-- Specific columns
SELECT id, name, email FROM users;

-- Distinct values
SELECT DISTINCT status FROM orders;
```

---

#### SELECT with WHERE
Filter rows based on conditions.

```sql
SELECT * FROM users WHERE is_active = TRUE;
SELECT * FROM orders WHERE amount > 100;
SELECT * FROM users WHERE name = 'Alice' AND is_active = TRUE;
```

See [WHERE Clause & Expressions](#where-clause--expressions) for full details.

---

#### SELECT with ORDER BY
Sort results by one or more columns.

```sql
-- Ascending (default)
SELECT * FROM users ORDER BY name;
SELECT * FROM users ORDER BY name ASC;

-- Descending
SELECT * FROM users ORDER BY created_at DESC;

-- Multiple columns
SELECT * FROM users ORDER BY is_active DESC, name ASC;
```

**Features:**
- Supports multiple columns
- ASC (ascending) or DESC (descending)
- NULL values sorted to the end

---

#### SELECT with LIMIT and OFFSET
Paginate results.

```sql
-- First 10 rows
SELECT * FROM users LIMIT 10;

-- Rows 21-30 (skip first 20)
SELECT * FROM users LIMIT 10 OFFSET 20;

-- Pagination example (page 3, 10 per page)
SELECT * FROM users LIMIT 10 OFFSET 20;
```

**Features:**
- LIMIT: Maximum number of rows to return
- OFFSET: Number of rows to skip
- Both must be non-negative integers

---

#### Complete SELECT Example
All clauses together:

```sql
SELECT DISTINCT status, COUNT(*) as count, AVG(amount) as avg_amount
FROM orders
WHERE status != 'cancelled'
GROUP BY status
HAVING COUNT(*) > 5
ORDER BY count DESC
LIMIT 10 OFFSET 0;
```

**Execution order:**
1. FROM - Choose table
2. WHERE - Filter rows
3. GROUP BY - Group rows
4. HAVING - Filter groups
5. SELECT - Choose columns
6. DISTINCT - Remove duplicates
7. ORDER BY - Sort results
8. LIMIT/OFFSET - Paginate

---

### UPDATE
Modify existing rows in a table.

**Syntax:**
```sql
UPDATE table_name SET column = value WHERE condition;
UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
```

**Examples:**
```sql
-- Update single column
UPDATE users SET is_active = FALSE WHERE id = 3;

-- Update multiple columns
UPDATE orders SET status = 'completed', updated_at = '2025-01-14T15:30:00' 
WHERE order_id = 101;

-- Update with complex WHERE
UPDATE users SET is_active = FALSE 
WHERE created_at < '2020-01-01' AND last_login IS NULL;
```

**Features:**
- Supports WHERE clause with full expressions
- Can update multiple columns in one statement
- Validates foreign key constraints after update

**⚠️ Limitations:**
- SET values must be literals (no expressions like `count = count + 1`)
- Parser only supports one SET assignment (multi-column update may be limited)

**❌ Not Supported:**
- Arithmetic in SET: `SET count = count + 1`
- Subqueries in SET: `SET price = (SELECT AVG(price) FROM products)`

---

### DELETE
Remove rows from a table.

**Syntax:**
```sql
DELETE FROM table_name WHERE condition;
```

**Examples:**
```sql
-- Delete specific rows
DELETE FROM orders WHERE status = 'cancelled';

-- Delete with complex condition
DELETE FROM users WHERE is_active = FALSE AND created_at < '2020-01-01';

-- Delete all rows (use with caution!)
DELETE FROM temp_data;
```

**Features:**
- Supports WHERE clause with full expressions
- Checks referential integrity (prevents deletion if row is referenced by foreign key)

**⚠️ Important:**
- Deleting a row referenced by a foreign key will raise an error
- DELETE without WHERE removes all rows from the table

---

## WHERE Clause & Expressions

The WHERE clause supports rich expression evaluation.

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal to | `id = 5` |
| `!=` or `<>` | Not equal to | `status != 'cancelled'` |
| `<` | Less than | `age < 18` |
| `>` | Greater than | `amount > 100` |
| `<=` | Less than or equal | `price <= 50.00` |
| `>=` | Greater than or equal | `quantity >= 10` |

---

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | Both conditions true | `is_active = TRUE AND age > 18` |
| `OR` | Either condition true | `status = 'pending' OR status = 'processing'` |
| `NOT` | Negates condition | `NOT is_deleted` |
| `()` | Grouping | `(status = 'pending' OR status = 'processing') AND is_active = TRUE` |

**Example:**
```sql
SELECT * FROM users 
WHERE (age > 18 AND country = 'US') OR (age > 21 AND country = 'UK');
```

---

### Pattern Matching (LIKE)

Match string patterns using wildcards.

| Operator | Description |
|----------|-------------|
| `LIKE` | Pattern match |
| `NOT LIKE` | Negated pattern match |

**Wildcards:**
- `%` - Matches any sequence of characters
- `_` - Matches any single character

**Examples:**
```sql
-- Starts with 'John'
SELECT * FROM users WHERE name LIKE 'John%';

-- Ends with '@example.com'
SELECT * FROM users WHERE email LIKE '%@example.com';

-- Contains 'admin'
SELECT * FROM users WHERE role LIKE '%admin%';

-- Exactly 5 characters
SELECT * FROM codes WHERE code LIKE '_____';

-- Negation
SELECT * FROM users WHERE email NOT LIKE '%@spam.com';
```

---

### Range Checking (BETWEEN)

Check if a value is within a range.

**Syntax:**
```sql
column BETWEEN min AND max
column NOT BETWEEN min AND max
```

**Examples:**
```sql
-- Numeric range
SELECT * FROM products WHERE price BETWEEN 10 AND 100;

-- Date range
SELECT * FROM orders WHERE created_at BETWEEN '2025-01-01' AND '2025-01-31';

-- Negation
SELECT * FROM users WHERE age NOT BETWEEN 18 AND 65;
```

**Note:** BETWEEN is inclusive (includes both min and max values).

---

### Set Membership (IN)

Check if a value is in a list.

**Syntax:**
```sql
column IN (value1, value2, ...)
column NOT IN (value1, value2, ...)
```

**Examples:**
```sql
-- Check against list
SELECT * FROM orders WHERE status IN ('pending', 'processing', 'shipped');

-- Numeric list
SELECT * FROM users WHERE id IN (1, 5, 10, 15);

-- Negation
SELECT * FROM products WHERE category NOT IN ('archived', 'deleted');
```

---

### NULL Checking

Check for NULL values.

**Syntax:**
```sql
column IS NULL
column IS NOT NULL
```

**Examples:**
```sql
-- Find rows with NULL
SELECT * FROM users WHERE deleted_at IS NULL;

-- Find rows without NULL
SELECT * FROM orders WHERE shipping_address IS NOT NULL;

-- Combined with other conditions
SELECT * FROM users WHERE is_active = TRUE AND last_login IS NOT NULL;
```

**⚠️ Important:** 
- Use `IS NULL`, not `= NULL`
- NULL support is inconsistent in INSERT (may cause validation errors)

---

### Complex Expression Examples

```sql
-- Multiple conditions
SELECT * FROM orders 
WHERE (status = 'pending' OR status = 'processing')
  AND amount > 100
  AND created_at > '2025-01-01'
  AND user_id NOT IN (5, 10, 15);

-- Pattern matching with NULL check
SELECT * FROM users 
WHERE email LIKE '%@company.com' 
  AND deleted_at IS NULL
  AND (role = 'admin' OR role = 'manager');

-- Range and comparison
SELECT * FROM products
WHERE price BETWEEN 10 AND 1000
  AND stock_quantity >= 5
  AND category NOT LIKE 'clearance%';
```

---

## Joins

Join multiple tables together.

### Supported Join Types

| Join Type | Description |
|-----------|-------------|
| `INNER JOIN` | Returns rows with matching values in both tables |
| `LEFT JOIN` / `LEFT OUTER JOIN` | Returns all rows from left table, with matching rows from right |
| `RIGHT JOIN` / `RIGHT OUTER JOIN` | Returns all rows from right table, with matching rows from left |
| `FULL OUTER JOIN` | Returns all rows from both tables |

---

### INNER JOIN
Return only rows with matching values in both tables.

**Syntax:**
```sql
SELECT columns
FROM table1
INNER JOIN table2 ON table1.column = table2.column;
```

**Examples:**
```sql
-- Basic join
SELECT users.name, orders.order_id, orders.amount
FROM users
INNER JOIN orders ON users.id = orders.user_id;

-- Multiple joins
SELECT users.name, orders.order_id, products.product_name
FROM users
INNER JOIN orders ON users.id = orders.user_id
INNER JOIN order_items ON orders.order_id = order_items.order_id
INNER JOIN products ON order_items.product_id = products.id;

-- Join with WHERE
SELECT users.name, orders.total
FROM users
INNER JOIN orders ON users.id = orders.user_id
WHERE orders.status = 'completed' AND users.is_active = TRUE;
```

---

### LEFT JOIN
Return all rows from the left table, with matching rows from the right (NULL if no match).

**Syntax:**
```sql
SELECT columns
FROM table1
LEFT JOIN table2 ON table1.column = table2.column;

-- Alternative syntax
SELECT columns
FROM table1
LEFT OUTER JOIN table2 ON table1.column = table2.column;
```

**Example:**
```sql
-- Find all users, even those without orders
SELECT users.name, COUNT(orders.order_id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
GROUP BY users.name;
```

---

### RIGHT JOIN
Return all rows from the right table, with matching rows from the left (NULL if no match).

**Syntax:**
```sql
SELECT columns
FROM table1
RIGHT JOIN table2 ON table1.column = table2.column;
```

---

### FULL OUTER JOIN
Return all rows from both tables, with NULL where no match exists.

**Syntax:**
```sql
SELECT columns
FROM table1
FULL OUTER JOIN table2 ON table1.column = table2.column;
```

---

### Join Limitations & Notes

**✅ Supported:**
- INNER, LEFT, RIGHT, FULL OUTER joins
- Multiple joins in one query
- Simple equality conditions: `table1.column = table2.column`
- WHERE clause after joins

**❌ Not Supported:**
- Complex ON conditions (only simple equality)
- Non-equality join conditions (`table1.col > table2.col`)
- Table aliases (AS): `FROM users AS u` - not parsed
- Self-joins may be problematic without aliases

**⚠️ Important:**
- JOIN ON condition must be in the format: `table.column = table.column`
- Both tables and columns must be explicitly specified with dot notation

---

## Aggregates & Grouping

Perform calculations on groups of rows.

### Aggregate Functions

| Function | Description | Example |
|----------|-------------|---------|
| `COUNT(*)` | Count all rows | `SELECT COUNT(*) FROM users;` |
| `COUNT(column)` | Count non-null values | `SELECT COUNT(email) FROM users;` |
| `SUM(column)` | Sum of numeric values | `SELECT SUM(amount) FROM orders;` |
| `AVG(column)` | Average of numeric values | `SELECT AVG(price) FROM products;` |
| `MIN(column)` | Minimum value | `SELECT MIN(price) FROM products;` |
| `MAX(column)` | Maximum value | `SELECT MAX(created_at) FROM orders;` |

---

### Basic Aggregates

```sql
-- Total row count
SELECT COUNT(*) FROM orders;

-- Sum of column
SELECT SUM(amount) FROM orders WHERE status = 'completed';

-- Average, min, max
SELECT AVG(price) as avg_price, 
       MIN(price) as min_price, 
       MAX(price) as max_price
FROM products;
```

---

### GROUP BY
Group rows and calculate aggregates per group.

**Syntax:**
```sql
SELECT column, aggregate_function(column)
FROM table
GROUP BY column;
```

**Examples:**
```sql
-- Count orders per user
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id;

-- Total amount per status
SELECT status, SUM(amount) as total, COUNT(*) as count
FROM orders
GROUP BY status;

-- Multiple grouping columns
SELECT user_id, status, COUNT(*) as count, AVG(amount) as avg_amount
FROM orders
GROUP BY user_id, status;

-- With ORDER BY
SELECT category, COUNT(*) as product_count
FROM products
GROUP BY category
ORDER BY product_count DESC;
```

**Rules:**
- Every non-aggregate column in SELECT must be in GROUP BY
- Aggregate functions compute one value per group

---

### HAVING
Filter groups after aggregation (like WHERE but for groups).

**Syntax:**
```sql
SELECT column, aggregate_function(column)
FROM table
GROUP BY column
HAVING condition;
```

**Examples:**
```sql
-- Users with more than 5 orders
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5;

-- Categories with average price over 50
SELECT category, AVG(price) as avg_price
FROM products
GROUP BY category
HAVING AVG(price) > 50;

-- Combined with WHERE
SELECT status, COUNT(*) as count, SUM(amount) as total
FROM orders
WHERE created_at > '2025-01-01'
GROUP BY status
HAVING COUNT(*) > 10
ORDER BY total DESC;
```

**⚠️ Known Issue:**
- HAVING with aggregate functions may not work reliably
- Simple HAVING on group keys is safer than HAVING with aggregates

---

### Complete Aggregation Example

```sql
SELECT 
    user_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order,
    MIN(amount) as smallest_order,
    MAX(amount) as largest_order
FROM orders
WHERE status IN ('completed', 'shipped')
  AND created_at >= '2025-01-01'
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY total_spent DESC
LIMIT 10;
```

---

## Date/Time Functions

Special functions for working with dates and times in WHERE clauses and SELECT.

### Date/Time Extraction Functions

| Function | Description | Example |
|----------|-------------|---------|
| `YEAR(date)` | Extract year | `YEAR('2025-01-14') → 2025` |
| `MONTH(date)` | Extract month (1-12) | `MONTH('2025-01-14') → 1` |
| `DAY(date)` | Extract day (1-31) | `DAY('2025-01-14') → 14` |
| `HOUR(datetime)` | Extract hour (0-23) | `HOUR('2025-01-14T15:30:00') → 15` |
| `MINUTE(datetime)` | Extract minute (0-59) | `MINUTE('2025-01-14T15:30:00') → 30` |
| `SECOND(datetime)` | Extract second (0-59) | `SECOND('2025-01-14T15:30:00') → 0` |

**Examples:**
```sql
-- Orders from 2025
SELECT * FROM orders WHERE YEAR(created_at) = 2025;

-- Orders from January
SELECT * FROM orders WHERE MONTH(created_at) = 1;

-- Orders on the 15th of any month
SELECT * FROM orders WHERE DAY(created_at) = 15;
```

---

### Date Conversion Functions

| Function | Description |
|----------|-------------|
| `DATE(datetime)` | Extract date part from datetime |
| `TIME(datetime)` | Extract time part from datetime |

**Examples:**
```sql
-- Orders on a specific date
SELECT * FROM orders WHERE DATE(created_at) = '2025-01-14';

-- Orders between certain times
SELECT * FROM orders 
WHERE TIME(created_at) BETWEEN '09:00:00' AND '17:00:00';
```

---

### Date Arithmetic Functions

| Function | Description |
|----------|-------------|
| `NOW()` | Current date and time |
| `DATE_ADD(date, days)` | Add days to a date |
| `DATE_SUB(date, days)` | Subtract days from a date |
| `DATEDIFF(date1, date2)` | Days between two dates |

**Examples:**
```sql
-- Orders from today
SELECT * FROM orders WHERE DATE(created_at) = DATE(NOW());

-- Orders from the last 7 days
SELECT * FROM orders WHERE created_at >= DATE_SUB(NOW(), 7);

-- Orders from the next 30 days
SELECT * FROM orders WHERE created_at <= DATE_ADD(NOW(), 30);

-- Orders older than 90 days
SELECT * FROM orders WHERE DATEDIFF(NOW(), created_at) > 90;
```

---

### Day of Week Functions

| Function | Description |
|----------|-------------|
| `DAYOFWEEK(date)` | Day of week (1=Sunday, 7=Saturday) |
| `DAYNAME(date)` | Name of day (Monday, Tuesday, ...) |

**Examples:**
```sql
-- Orders on weekends (Saturday or Sunday)
SELECT * FROM orders WHERE DAYOFWEEK(created_at) IN (1, 7);

-- Orders on Mondays
SELECT * FROM orders WHERE DAYNAME(created_at) = 'Monday';
```

---

### Complete Date/Time Example

```sql
SELECT 
    DATE(created_at) as order_date,
    DAYNAME(created_at) as day_name,
    COUNT(*) as order_count,
    SUM(amount) as total
FROM orders
WHERE created_at >= DATE_SUB(NOW(), 30)
  AND DAYOFWEEK(created_at) NOT IN (1, 7)  -- Exclude weekends
GROUP BY DATE(created_at), DAYNAME(created_at)
ORDER BY order_date DESC;
```

---

## HTTP API Endpoints

Access the database via REST API.

### Execute SQL Query

**Endpoint:** `POST /api/query`

**Request:**
```json
{
  "sql": "SELECT * FROM users WHERE is_active = TRUE;",
  "db": "myapp"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Query executed successfully. 5 row(s) returned.",
  "data": [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "is_active": true},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "is_active": true}
  ],
  "execution_time_ms": 2.34
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Table 'nonexistent' does not exist",
  "execution_time_ms": 0.12
}
```

---

### Database Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/databases` | List all databases |
| POST | `/api/databases` | Create a database |
| DELETE | `/api/databases/{db_name}` | Delete a database |
| GET | `/api/databases/{db_name}/info` | Get database info |

**Examples:**

**List databases:**
```bash
GET /api/databases
```

**Create database:**
```bash
POST /api/databases
Content-Type: application/json

{
  "name": "new_database"
}
```

**Get database info:**
```bash
GET /api/databases/myapp/info
```

**Response:**
```json
{
  "name": "myapp",
  "tables": ["users", "orders", "products"],
  "table_count": 3,
  "total_rows": 1523
}
```

---

### Table Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tables?db=database_name` | List tables |
| GET | `/api/tables/{table_name}?db=database_name` | Get table schema |
| DELETE | `/api/tables/{table_name}?db=database_name` | Drop table |

**Get table schema:**
```bash
GET /api/tables/users?db=myapp
```

**Response:**
```json
{
  "name": "users",
  "columns": [
    {
      "name": "id",
      "type": "INT",
      "is_primary_key": true,
      "is_unique": false
    },
    {
      "name": "email",
      "type": "STRING",
      "is_primary_key": false,
      "is_unique": true,
      "foreign_key_table": null
    }
  ],
  "row_count": 142,
  "indexes": ["id", "email"]
}
```

---

### Relationships

**Endpoint:** `GET /api/relationships?db=database_name`

Get all foreign key relationships in the database.

**Response:**
```json
{
  "success": true,
  "tables": {
    "users": {
      "columns": [...],
      "row_count": 142
    },
    "orders": {
      "columns": [...],
      "row_count": 523
    }
  },
  "relationships": [
    {
      "from_table": "orders",
      "from_column": "user_id",
      "to_table": "users",
      "to_column": "id"
    }
  ]
}
```

---

### Health & Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Server statistics |

**Health check:**
```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T15:30:00Z",
  "databases": 3,
  "uptime": "2:15:30",
  "ai_enabled": true
}
```

---

### Authentication

All API requests require an API key (if `REQUIRE_API_KEY=true`).

**Add header:**
```
X-API-Key: your_api_key_here
```

**Example with curl:**
```bash
curl -X POST https://your-backend.com/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"sql": "SELECT * FROM users;", "db": "myapp"}'
```

---

## Limitations & Known Issues

### Supported ✅

- ✅ Single-column PRIMARY KEY (required per table)
- ✅ UNIQUE constraints
- ✅ FOREIGN KEY constraints (REFERENCES)
- ✅ WHERE with complex expressions (AND, OR, NOT, parentheses)
- ✅ Comparison operators (=, !=, <, >, <=, >=)
- ✅ Pattern matching (LIKE, NOT LIKE)
- ✅ Set operations (IN, NOT IN, BETWEEN)
- ✅ NULL checks (IS NULL, IS NOT NULL)
- ✅ INNER, LEFT, RIGHT, FULL OUTER joins
- ✅ Aggregates (COUNT, SUM, AVG, MIN, MAX)
- ✅ GROUP BY with multiple columns
- ✅ HAVING clause
- ✅ ORDER BY with multiple columns and ASC/DESC
- ✅ LIMIT and OFFSET
- ✅ DISTINCT
- ✅ Date/time functions in expressions
- ✅ Automatic indexing for PK, UNIQUE, FK columns
- ✅ Referential integrity enforcement

### Not Supported ❌

**Schema Limitations:**
- ❌ Composite (multi-column) PRIMARY KEY
- ❌ DEFAULT values for columns
- ❌ NOT NULL constraint (all columns implicitly required)
- ❌ CHECK constraints
- ❌ AUTO_INCREMENT / SERIAL columns
- ❌ ALTER TABLE (cannot modify existing tables)
- ❌ RENAME TABLE / RENAME COLUMN
- ❌ Table or column comments

**DML Limitations:**
- ❌ Multi-row INSERT: `INSERT INTO t VALUES (1,2), (3,4);`
- ❌ INSERT ... SELECT: `INSERT INTO t SELECT * FROM other;`
- ❌ Partial INSERT with defaults (must provide all columns)
- ❌ Arithmetic expressions in UPDATE SET: `SET count = count + 1`
- ❌ Subqueries in UPDATE/INSERT

**Query Limitations:**
- ❌ Subqueries (SELECT within SELECT)
- ❌ Table or column aliases (AS): `FROM users AS u` or `SELECT name AS fullname`
- ❌ Self-joins (requires aliases)
- ❌ Complex JOIN ON conditions (only simple equality)
- ❌ Non-equality JOIN conditions (>, <, !=)
- ❌ UNION / INTERSECT / EXCEPT
- ❌ Window functions (ROW_NUMBER, RANK, PARTITION BY)
- ❌ CTEs (WITH clauses)
- ❌ CASE expressions

**Other Limitations:**
- ❌ Transactions (BEGIN, COMMIT, ROLLBACK)
- ❌ Views
- ❌ Stored procedures / functions
- ❌ Triggers
- ❌ User permissions / roles
- ❌ Indexes on expressions
- ❌ Full-text search
- ❌ JSON data type and functions

### Known Issues ⚠️

1. **NULL Handling Inconsistent:**
   - Parser accepts NULL in VALUES
   - Row validation may reject NULL for typed columns
   - NULL storage is effectively unsupported

2. **UPDATE Single Column:**
   - Parser only supports setting one column per statement
   - Multi-column UPDATE may not work reliably

3. **HAVING with Aggregates:**
   - HAVING that references aggregate functions may fail
   - Safer to use simple HAVING on group keys

4. **INSERT Requires All Columns:**
   - Cannot omit columns (no defaults or optional columns)
   - Even if you specify a column list, all columns must have values

5. **No Table Aliases:**
   - Cannot use `AS` for table aliasing
   - Self-joins are not possible without aliases

6. **JOIN ON Simple Equality Only:**
   - ON condition must be `table.column = table.column`
   - No complex expressions or non-equality conditions

---

## Complete Examples

### Example 1: E-commerce Database

```sql
-- Create database
CREATE DATABASE ecommerce;
USE ecommerce;

-- Create tables
CREATE TABLE customers (
    id INT PRIMARY KEY,
    email STRING UNIQUE,
    name STRING,
    country STRING,
    created_at DATETIME
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name STRING,
    price FLOAT,
    category STRING,
    stock_quantity INT
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    total_amount FLOAT,
    status STRING,
    order_date DATETIME
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(id),
    quantity INT,
    price FLOAT
);

-- Insert data
INSERT INTO customers VALUES (1, 'alice@example.com', 'Alice Johnson', 'USA', '2024-01-15T10:00:00');
INSERT INTO customers VALUES (2, 'bob@example.com', 'Bob Smith', 'UK', '2024-02-20T14:30:00');

INSERT INTO products VALUES (1, 'Laptop', 999.99, 'Electronics', 50);
INSERT INTO products VALUES (2, 'Mouse', 29.99, 'Electronics', 200);
INSERT INTO products VALUES (3, 'Desk', 299.99, 'Furniture', 25);

INSERT INTO orders VALUES (101, 1, 1029.98, 'completed', '2025-01-10T11:00:00');
INSERT INTO orders VALUES (102, 2, 329.98, 'pending', '2025-01-12T09:30:00');

INSERT INTO order_items VALUES (1, 101, 1, 1, 999.99);
INSERT INTO order_items VALUES (2, 101, 2, 1, 29.99);
INSERT INTO order_items VALUES (3, 102, 3, 1, 299.99);
INSERT INTO order_items VALUES (4, 102, 2, 1, 29.99);

-- Queries

-- Get all orders for a customer
SELECT o.order_id, o.total_amount, o.status, o.order_date
FROM orders o
WHERE o.customer_id = 1
ORDER BY o.order_date DESC;

-- Get order details with customer info
SELECT 
    c.name as customer_name,
    c.email,
    o.order_id,
    o.total_amount,
    o.status,
    DATE(o.order_date) as order_date
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
ORDER BY o.order_date DESC;

-- Get products in an order
SELECT 
    p.name as product_name,
    oi.quantity,
    oi.price,
    (oi.quantity * oi.price) as line_total
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.id
WHERE oi.order_id = 101;

-- Sales by category
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as units_sold,
    SUM(oi.quantity * oi.price) as revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY revenue DESC;

-- Top customers by total spent
SELECT 
    c.name,
    c.email,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.name, c.email
HAVING COUNT(o.order_id) >= 1
ORDER BY total_spent DESC
LIMIT 10;

-- Low stock products
SELECT name, stock_quantity, price
FROM products
WHERE stock_quantity < 30
ORDER BY stock_quantity ASC;

-- Recent orders (last 30 days)
SELECT 
    o.order_id,
    c.name as customer,
    o.total_amount,
    o.status,
    o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE o.order_date >= DATE_SUB(NOW(), 30)
ORDER BY o.order_date DESC;
```

---

### Example 2: User Management System

```sql
-- Create database
CREATE DATABASE user_management;
USE user_management;

-- Create tables
CREATE TABLE users (
    id INT PRIMARY KEY,
    username STRING UNIQUE,
    email STRING UNIQUE,
    full_name STRING,
    is_active BOOL,
    created_at DATETIME,
    last_login DATETIME
);

CREATE TABLE roles (
    role_id INT PRIMARY KEY,
    role_name STRING UNIQUE,
    description STRING
);

CREATE TABLE user_roles (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id),
    role_id INT REFERENCES roles(role_id),
    assigned_at DATETIME
);

-- Insert data
INSERT INTO users VALUES (1, 'alice', 'alice@company.com', 'Alice Johnson', TRUE, '2024-01-01T08:00:00', '2025-01-14T09:30:00');
INSERT INTO users VALUES (2, 'bob', 'bob@company.com', 'Bob Smith', TRUE, '2024-01-15T10:00:00', '2025-01-13T14:20:00');
INSERT INTO users VALUES (3, 'carol', 'carol@company.com', 'Carol White', FALSE, '2024-02-01T11:00:00', '2024-12-20T16:00:00');

INSERT INTO roles VALUES (1, 'admin', 'System administrator');
INSERT INTO roles VALUES (2, 'editor', 'Content editor');
INSERT INTO roles VALUES (3, 'viewer', 'Read-only access');

INSERT INTO user_roles VALUES (1, 1, 1, '2024-01-01T08:00:00');
INSERT INTO user_roles VALUES (2, 1, 2, '2024-01-01T08:00:00');
INSERT INTO user_roles VALUES (3, 2, 2, '2024-01-15T10:00:00');
INSERT INTO user_roles VALUES (4, 3, 3, '2024-02-01T11:00:00');

-- Queries

-- Get user with their roles
SELECT 
    u.username,
    u.full_name,
    u.email,
    r.role_name,
    u.is_active
FROM users u
INNER JOIN user_roles ur ON u.id = ur.user_id
INNER JOIN roles r ON ur.role_id = r.role_id
WHERE u.is_active = TRUE
ORDER BY u.username, r.role_name;

-- Active users who haven't logged in recently
SELECT 
    username,
    full_name,
    last_login,
    DATEDIFF(NOW(), last_login) as days_since_login
FROM users
WHERE is_active = TRUE
  AND DATEDIFF(NOW(), last_login) > 7
ORDER BY days_since_login DESC;

-- Users by role
SELECT 
    r.role_name,
    COUNT(ur.user_id) as user_count
FROM roles r
LEFT JOIN user_roles ur ON r.role_id = ur.role_id
GROUP BY r.role_name
ORDER BY user_count DESC;

-- Find users with specific email domain
SELECT username, email, is_active
FROM users
WHERE email LIKE '%@company.com'
  AND is_active = TRUE;

-- Users created in specific month
SELECT 
    username,
    full_name,
    created_at
FROM users
WHERE YEAR(created_at) = 2024
  AND MONTH(created_at) = 1
ORDER BY created_at;
```

---

### Example 3: Inventory System

```sql
-- Create database
CREATE DATABASE inventory;
USE inventory;

-- Create tables
CREATE TABLE warehouses (
    id INT PRIMARY KEY,
    name STRING,
    location STRING,
    capacity INT
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name STRING,
    sku STRING UNIQUE,
    unit_price FLOAT,
    reorder_level INT
);

CREATE TABLE inventory (
    id INT PRIMARY KEY,
    warehouse_id INT REFERENCES warehouses(id),
    product_id INT REFERENCES products(product_id),
    quantity INT,
    last_updated DATETIME
);

-- Insert data
INSERT INTO warehouses VALUES (1, 'Main Warehouse', 'New York', 10000);
INSERT INTO warehouses VALUES (2, 'West Coast Hub', 'Los Angeles', 8000);

INSERT INTO products VALUES (1, 'Widget A', 'WGT-001', 19.99, 100);
INSERT INTO products VALUES (2, 'Widget B', 'WGT-002', 29.99, 50);
INSERT INTO products VALUES (3, 'Gadget X', 'GDG-001', 99.99, 25);

INSERT INTO inventory VALUES (1, 1, 1, 150, '2025-01-14T10:00:00');
INSERT INTO inventory VALUES (2, 1, 2, 75, '2025-01-14T10:00:00');
INSERT INTO inventory VALUES (3, 1, 3, 30, '2025-01-14T10:00:00');
INSERT INTO inventory VALUES (4, 2, 1, 80, '2025-01-14T10:00:00');
INSERT INTO inventory VALUES (5, 2, 2, 40, '2025-01-14T10:00:00');

-- Queries

-- Total inventory by product
SELECT 
    p.product_name,
    p.sku,
    SUM(i.quantity) as total_quantity,
    p.unit_price,
    (SUM(i.quantity) * p.unit_price) as total_value
FROM products p
LEFT JOIN inventory i ON p.product_id = i.product_id
GROUP BY p.product_name, p.sku, p.unit_price
ORDER BY total_value DESC;

-- Products below reorder level
SELECT 
    p.product_name,
    p.sku,
    p.reorder_level,
    SUM(i.quantity) as current_stock,
    (p.reorder_level - SUM(i.quantity)) as units_needed
FROM products p
INNER JOIN inventory i ON p.product_id = i.product_id
GROUP BY p.product_name, p.sku, p.reorder_level
HAVING SUM(i.quantity) < p.reorder_level;

-- Inventory by warehouse
SELECT 
    w.name as warehouse,
    w.location,
    COUNT(DISTINCT i.product_id) as product_count,
    SUM(i.quantity) as total_units
FROM warehouses w
LEFT JOIN inventory i ON w.id = i.warehouse_id
GROUP BY w.name, w.location
ORDER BY total_units DESC;

-- Detailed inventory report
SELECT 
    w.name as warehouse,
    p.product_name,
    p.sku,
    i.quantity,
    p.unit_price,
    (i.quantity * p.unit_price) as inventory_value,
    i.last_updated
FROM inventory i
INNER JOIN warehouses w ON i.warehouse_id = w.id
INNER JOIN products p ON i.product_id = p.product_id
ORDER BY w.name, p.product_name;
```

---

## Additional Resources

- **Project README:** [README.md](./README.md)
- **Deployment Guide:** [hosting.md](./hosting.md)
- **AI Features Guide:** [AI_DEPLOYMENT_GUIDE.md](./AI_DEPLOYMENT_GUIDE.md)
- **Backend API:** Visit `/docs` on your backend for interactive API documentation

---

**Last Updated:** January 14, 2025  
**Version:** 2.0.0  
**PesacodeDB** - A custom RDBMS built from scratch
