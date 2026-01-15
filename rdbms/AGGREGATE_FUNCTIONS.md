# PesaDB Aggregate Functions - Technical Documentation

## Overview

This document describes the implementation and usage of SQL aggregate functions in PesaDB RDBMS. Aggregate functions perform calculations on sets of rows and return a single value, enabling common database operations like counting records, summing values, and finding averages.

## Supported Aggregate Functions

PesaDB supports the following SQL aggregate functions:

| Function | Description | Example | Return Type |
|----------|-------------|---------|-------------|
| `COUNT(*)` | Counts all rows in the result set | `SELECT COUNT(*) FROM users` | Integer |
| `COUNT(column)` | Counts non-NULL values in a column | `SELECT COUNT(email) FROM users` | Integer |
| `SUM(column)` | Sums numeric values in a column | `SELECT SUM(salary) FROM employees` | Number |
| `AVG(column)` | Calculates average of numeric values | `SELECT AVG(age) FROM users` | Float |
| `MIN(column)` | Finds minimum value in a column | `SELECT MIN(price) FROM products` | Same as column type |
| `MAX(column)` | Finds maximum value in a column | `SELECT MAX(score) FROM tests` | Same as column type |

## Usage Examples

### Basic Aggregate Queries

```sql
-- Count all users
SELECT COUNT(*) FROM users;

-- Count users with email addresses (non-NULL)
SELECT COUNT(email) FROM users WHERE email IS NOT NULL;

-- Calculate total salary
SELECT SUM(salary) FROM employees;

-- Get average age
SELECT AVG(age) FROM users;

-- Find minimum and maximum prices
SELECT MIN(price), MAX(price) FROM products;
```

### Aggregate with WHERE Clause

Aggregate functions are computed **after** the WHERE clause filters rows:

```sql
-- Count active users
SELECT COUNT(*) FROM users WHERE status = 'active';

-- Average salary of senior employees
SELECT AVG(salary) FROM employees WHERE level >= 5;

-- Sum of completed orders
SELECT SUM(amount) FROM orders WHERE status = 'completed';
```

### Multiple Aggregates

You can use multiple aggregate functions in a single query:

```sql
SELECT 
    COUNT(*) AS total_users,
    AVG(age) AS avg_age,
    MIN(age) AS youngest,
    MAX(age) AS oldest
FROM users;
```

### GROUP BY

Aggregate functions can be combined with GROUP BY to compute aggregates for each group:

```sql
-- Count users by status
SELECT status, COUNT(*) FROM users GROUP BY status;

-- Average salary by department
SELECT department, AVG(salary) FROM employees GROUP BY department;

-- Total sales by product
SELECT product_id, SUM(amount) FROM sales GROUP BY product_id;
```

### HAVING Clause

Use HAVING to filter groups based on aggregate results:

```sql
-- Departments with more than 5 employees
SELECT department, COUNT(*) 
FROM employees 
GROUP BY department 
HAVING COUNT(*) > 5;

-- Products with average price over $100
SELECT category, AVG(price)
FROM products
GROUP BY category
HAVING AVG(price) > 100;
```

### Aggregate with ORDER BY and LIMIT

```sql
-- Top 5 highest-paid employees
SELECT MAX(salary) FROM employees LIMIT 5;

-- Count of users ordered by count
SELECT status, COUNT(*) AS user_count
FROM users
GROUP BY status
ORDER BY user_count DESC;
```

### Table-Qualified Columns

Aggregate functions support table-qualified column names:

```sql
SELECT COUNT(users.user_id) FROM users;

SELECT SUM(orders.amount) FROM orders;
```

## NULL Handling

Aggregate functions handle NULL values according to SQL standards:

- **COUNT(\*)**: Counts all rows, including those with NULL values
- **COUNT(column)**: Counts only non-NULL values in the specified column
- **SUM, AVG, MIN, MAX**: Ignore NULL values in calculations
- If all values are NULL, SUM/AVG/MIN/MAX return NULL
- Empty result sets: COUNT returns 0, other aggregates return NULL

### Example

```sql
-- Table with NULLs
-- id | value
--  1 | 10
--  2 | NULL
--  3 | 20

SELECT COUNT(*) FROM table;      -- Returns 3
SELECT COUNT(value) FROM table;  -- Returns 2
SELECT SUM(value) FROM table;    -- Returns 30 (ignores NULL)
SELECT AVG(value) FROM table;    -- Returns 15.0 (30/2)
```

## Implementation Details

### Parser Changes

The following parser enhancements were made to support aggregate functions:

1. **Token Recognition**: Modified `_is_aggregate_function()` to accept both `IDENTIFIER` and `KEYWORD` tokens, as the tokenizer marks aggregate function names (COUNT, SUM, etc.) as KEYWORD tokens.

2. **Function Parsing**: Updated `_parse_aggregate_function()` to:
   - Accept KEYWORD tokens for function names
   - Validate recognized aggregate functions
   - Parse `*` for COUNT(*) or column expressions for other functions
   - Generate appropriate aliases (e.g., "COUNT(*)", "SUM(salary)")

3. **Argument Parsing**: Enhanced `_parse_aggregate_expression_argument()` to support:
   - Simple column names: `COUNT(id)`
   - Table-qualified columns: `COUNT(users.id)`
   - KEYWORD tokens as column names (for columns that match SQL keywords)

### Execution Flow

1. **Tokenization**: SQL statement is tokenized, with aggregate function names marked as KEYWORD tokens
2. **Parsing**: Parser identifies aggregate functions and builds `AggregateExpression` objects stored in `SelectCommand.aggregates`
3. **Execution**:
   - Fetch all rows from table
   - Apply WHERE clause to filter rows **before** aggregation
   - If GROUP BY present:
     - Group rows by specified columns
     - Compute aggregates for each group
     - Validate non-aggregate columns appear in GROUP BY
   - If no GROUP BY:
     - Compute aggregates across all filtered rows
     - Return single result row
   - Apply HAVING, ORDER BY, DISTINCT, LIMIT/OFFSET

### Error Messages

The implementation provides clear, actionable error messages:

- `"Invalid aggregate function: FOO. Supported aggregate functions are: COUNT, SUM, AVG, MIN, MAX"`
- `"SUM(*) is not valid. Only COUNT(*) is allowed. Use SUM(column_name) instead."`
- `"COUNT requires either * or a column name. Usage: COUNT(*) or COUNT(column_name)"`
- `"SUM requires numeric values. Cannot compute SUM on column with non-numeric data types."`

## Limitations

### Current Limitations

1. **No DISTINCT in Aggregates**: PesaDB does not yet support `COUNT(DISTINCT column)` or other aggregate functions with DISTINCT modifiers.

   ```sql
   -- NOT SUPPORTED YET
   SELECT COUNT(DISTINCT user_id) FROM orders;
   ```

2. **No Nested Aggregates**: Cannot nest aggregate functions.

   ```sql
   -- NOT SUPPORTED
   SELECT AVG(COUNT(*)) FROM users GROUP BY status;
   ```

3. **No Expressions in Aggregates**: Aggregate arguments must be column references, not arithmetic expressions.

   ```sql
   -- NOT SUPPORTED YET
   SELECT SUM(price * quantity) FROM order_items;
   ```

4. **No Conditional Aggregates**: No support for CASE statements or conditional expressions within aggregates.

   ```sql
   -- NOT SUPPORTED YET
   SELECT SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) FROM users;
   ```

5. **No Window Functions**: No support for window functions like `ROW_NUMBER()`, `RANK()`, etc.

6. **Limited Alias Support**: Aggregate result aliases are auto-generated (e.g., "COUNT(*)"). Custom aliases using AS are not yet supported.

   ```sql
   -- NOT SUPPORTED YET
   SELECT COUNT(*) AS total FROM users;
   ```

### Type Restrictions

- **SUM**: Requires numeric column (INT, FLOAT, etc.). Raises error on non-numeric data.
- **AVG**: Requires numeric column. Raises error on non-numeric data.
- **MIN/MAX**: Work on any comparable type (numbers, strings, dates).
- **COUNT**: Works on any column type.

## Backward Compatibility

All changes maintain full backward compatibility with existing non-aggregate queries:

- SELECT without aggregates continues to work unchanged
- INSERT, UPDATE, DELETE operations are unaffected
- WHERE clause evaluation remains consistent
- JOIN operations work as before

## Testing

A comprehensive test suite (`tests/test_aggregate_functions.py`) validates:

- ✅ All aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- ✅ COUNT(*) and COUNT(column) variations
- ✅ Aggregates with WHERE clauses
- ✅ Multiple aggregates in single query
- ✅ GROUP BY and HAVING clauses
- ✅ NULL value handling
- ✅ Empty result sets
- ✅ Error conditions (invalid aggregates, non-numeric SUM/AVG)
- ✅ Case insensitivity
- ✅ Table-qualified column names
- ✅ Complex WHERE conditions with aggregates
- ✅ ORDER BY and LIMIT with aggregates

Run tests with:

```bash
python -m pytest tests/test_aggregate_functions.py -v
```

Or using unittest:

```bash
python tests/test_aggregate_functions.py
```

## Migration Guide

### For Application Developers

**Before** (workaround without aggregate support):
```python
# Application-level counting
cursor.execute("SELECT * FROM users WHERE status = 'active'")
rows = cursor.fetchall()
count = len(rows)  # Manual counting in application
```

**After** (with aggregate support):
```python
# Database-level counting (more efficient)
cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
result = cursor.fetchone()
count = result['COUNT(*)']
```

### Common Migration Patterns

1. **Count Records**:
   ```python
   # Before: Fetch all and count
   rows = execute("SELECT * FROM table WHERE condition")
   count = len(rows)
   
   # After: Use COUNT
   result = execute("SELECT COUNT(*) FROM table WHERE condition")
   count = result[0]['COUNT(*)']
   ```

2. **Sum Values**:
   ```python
   # Before: Application-level sum
   rows = execute("SELECT amount FROM orders")
   total = sum(row['amount'] for row in rows)
   
   # After: Use SUM
   result = execute("SELECT SUM(amount) FROM orders")
   total = result[0]['SUM(amount)']
   ```

3. **Average Calculation**:
   ```python
   # Before: Application-level average
   rows = execute("SELECT age FROM users")
   avg = sum(row['age'] for row in rows) / len(rows)
   
   # After: Use AVG
   result = execute("SELECT AVG(age) FROM users")
   avg = result[0]['AVG(age)']
   ```

## Performance Considerations

### Efficiency

Aggregate functions are computed by the database engine, which is more efficient than fetching all rows and computing aggregates in application code:

- **Reduced Data Transfer**: Only aggregate results are returned, not full row sets
- **Single-Pass Processing**: Aggregates computed in one pass over the data
- **WHERE Optimization**: Filtering happens before aggregation

### Best Practices

1. **Use WHERE to Filter Early**: Apply filters in WHERE clause to reduce rows processed by aggregates:
   ```sql
   -- Good: Filter first, then aggregate
   SELECT COUNT(*) FROM orders WHERE date >= '2024-01-01';
   
   -- Avoid: Aggregate everything, filter later (if possible)
   ```

2. **Limit GROUP BY Columns**: Keep GROUP BY clauses focused to avoid excessive grouping:
   ```sql
   -- Good: Group by relevant columns
   SELECT department, COUNT(*) FROM employees GROUP BY department;
   ```

3. **Use HAVING for Group Filters**: Use HAVING to filter groups, not WHERE:
   ```sql
   -- Correct: HAVING filters groups
   SELECT department, COUNT(*) 
   FROM employees 
   GROUP BY department 
   HAVING COUNT(*) > 10;
   
   -- Wrong: WHERE can't filter on aggregates
   -- SELECT department, COUNT(*) FROM employees WHERE COUNT(*) > 10;
   ```

## Future Enhancements

Planned improvements for aggregate function support:

1. **COUNT(DISTINCT column)**: Count unique values
2. **Arithmetic Expressions**: Support expressions in aggregate arguments (e.g., `SUM(price * quantity)`)
3. **Custom Aliases**: Support `AS` keyword for custom aggregate result names
4. **Conditional Aggregates**: Support CASE expressions within aggregates
5. **String Aggregates**: GROUP_CONCAT or STRING_AGG for concatenating strings
6. **Statistical Functions**: STDDEV, VARIANCE, MEDIAN, etc.
7. **Window Functions**: ROW_NUMBER, RANK, LAG, LEAD, etc.

## Troubleshooting

### Common Errors

**Error**: `"SyntaxError: Expected IDENTIFIER near 'COUNT'"`

**Cause**: Old parser version that doesn't recognize KEYWORD tokens for aggregate functions.

**Solution**: Ensure you're using the updated parser that accepts both IDENTIFIER and KEYWORD tokens.

---

**Error**: `"SUM(*) is not valid, only COUNT(*) is allowed"`

**Cause**: Attempting to use `*` with aggregate functions other than COUNT.

**Solution**: Specify a column name: `SUM(column_name)` instead of `SUM(*)`.

---

**Error**: `"SUM requires numeric values"`

**Cause**: Attempting to SUM a non-numeric column (e.g., STRING).

**Solution**: Ensure the column contains numeric data (INT, FLOAT, etc.).

---

**Error**: `"Column 'x' must appear in GROUP BY clause or be used in an aggregate function"`

**Cause**: Selecting a non-aggregated column without including it in GROUP BY.

**Solution**: Either add the column to GROUP BY or remove it from SELECT:
```sql
-- Wrong
SELECT department, name, COUNT(*) FROM employees GROUP BY department;

-- Correct
SELECT department, COUNT(*) FROM employees GROUP BY department;

-- Or correct
SELECT department, name, COUNT(*) FROM employees GROUP BY department, name;
```

## References

- SQL Standard Aggregate Functions: ISO/IEC 9075 (SQL Standard)
- PesaDB Parser Implementation: `rdbms/sql/parser.py`
- PesaDB Expression System: `rdbms/sql/expressions.py`
- PesaDB Executor: `rdbms/sql/executor.py`
- Test Suite: `tests/test_aggregate_functions.py`

## Changelog

### Version 1.0 (Current)

**Added:**
- Full support for COUNT, SUM, AVG, MIN, MAX aggregate functions
- COUNT(*) and COUNT(column) variants
- Aggregate functions with WHERE, GROUP BY, HAVING, ORDER BY, LIMIT
- Table-qualified column names in aggregates
- Proper NULL value handling
- Comprehensive error messages
- Test suite with 30+ test cases

**Fixed:**
- Parser now accepts KEYWORD tokens for aggregate function names
- Resolved "Expected IDENTIFIER near 'COUNT'" syntax error
- Improved error messages for aggregate misuse

**Limitations:**
- No DISTINCT in aggregates
- No nested aggregates
- No expressions in aggregate arguments
- No conditional aggregates
- No custom aliases with AS keyword

---

*Last Updated: January 2025*
*PesaDB RDBMS Development Team*
