# Foreign Key Relationship Improvements

This document describes the improvements made to the foreign key relationship handling in the RDBMS backend.

## Summary of Improvements

### 1. ✅ Foreign Key Validation at CREATE TABLE Time

**What was added:**
- Foreign keys are now validated when tables are created, not just when data is inserted
- Checks that referenced tables exist
- Checks that referenced columns exist
- Ensures referenced columns are PRIMARY KEY or UNIQUE

**Example:**
```sql
-- This will now fail immediately at CREATE TABLE time:
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES non_existent_table(id)
);
-- Error: referenced table 'non_existent_table' does not exist

-- This will also fail:
CREATE TABLE users (
    id INT PRIMARY KEY,
    email STRING,
    age INT
);

CREATE TABLE profiles (
    id INT PRIMARY KEY,
    user_age INT REFERENCES users(age)  -- age is not PRIMARY KEY or UNIQUE
);
-- Error: referenced column 'users.age' must be PRIMARY KEY or UNIQUE
```

### 2. ✅ ON DELETE CASCADE/SET NULL/RESTRICT Support

**What was added:**
- Full support for `ON DELETE` actions: CASCADE, SET NULL, RESTRICT, NO ACTION
- Full support for `ON UPDATE` actions: CASCADE, SET NULL, RESTRICT, NO ACTION
- Default behavior is RESTRICT (prevent delete/update if referenced)

**Syntax:**
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);
```

**ON DELETE Actions:**

1. **CASCADE**: Automatically delete referencing rows when referenced row is deleted
```sql
CREATE TABLE users (id INT PRIMARY KEY, name STRING);
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE CASCADE);

INSERT INTO users VALUES (1, 'Alice');
INSERT INTO orders VALUES (1, 1);
INSERT INTO orders VALUES (2, 1);

DELETE FROM users WHERE id = 1;
-- Result: Both orders are automatically deleted
```

2. **SET NULL**: Set foreign key to NULL when referenced row is deleted
```sql
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE SET NULL);

DELETE FROM users WHERE id = 1;
-- Result: user_id in orders is set to NULL
```

3. **RESTRICT** (default): Prevent deletion if referenced
```sql
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));
-- or explicitly:
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE RESTRICT);

DELETE FROM users WHERE id = 1;
-- Error: Cannot delete, referenced by orders
```

4. **NO ACTION**: Same as RESTRICT
```sql
CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE NO ACTION);
```

**ON UPDATE Actions:**

Same actions available for UPDATE operations on primary keys:

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id) ON UPDATE CASCADE
);

UPDATE users SET id = 100 WHERE id = 1;
-- Result: user_id in orders is automatically updated to 100
```

### 3. ✅ Circular Foreign Key Dependency Detection

**What was added:**
- Detects circular dependencies in foreign key relationships at CREATE TABLE time
- Prevents creation of tables that would create dependency cycles

**Example:**
```sql
CREATE TABLE users (id INT PRIMARY KEY, dept_id INT);
CREATE TABLE departments (id INT PRIMARY KEY, manager_id INT REFERENCES users(id));

-- If we could add FK to users later (requires ALTER TABLE):
-- ALTER TABLE users ADD FOREIGN KEY (dept_id) REFERENCES departments(id);
-- Error: Circular foreign key dependency detected
```

### 4. ✅ Persistence of FK Actions

**What was added:**
- ON DELETE and ON UPDATE actions are now persisted to disk
- When database is loaded, all FK actions are restored correctly

## Implementation Details

### Files Modified

1. **rdbms/engine/table.py**
   - Added `on_delete` and `on_update` parameters to `ColumnDefinition`
   - Implemented `check_referential_integrity_for_delete()` with CASCADE/SET NULL support
   - Implemented `check_referential_integrity_for_update()` with CASCADE/SET NULL support
   - Updated `update()` method to check referential integrity for PK/unique column updates

2. **rdbms/engine/database.py**
   - Updated `to_dict()` to serialize on_delete and on_update actions
   - Updated `from_dict()` to deserialize on_delete and on_update actions

3. **rdbms/sql/parser.py**
   - Added parsing for `ON DELETE` clause (CASCADE, SET NULL, RESTRICT, NO ACTION)
   - Added parsing for `ON UPDATE` clause (CASCADE, SET NULL, RESTRICT, NO ACTION)

4. **rdbms/sql/executor.py**
   - Added `_validate_foreign_key_definitions()` to validate FKs at CREATE TABLE time
   - Added `_detect_circular_fk_dependency()` to detect circular dependencies
   - Updated `_execute_create_table()` to call validation methods

## Testing

A comprehensive test suite has been created: `tests/test_foreign_key_relationships.py`

### Running Tests

```bash
python tests/test_foreign_key_relationships.py
```

### Test Coverage

1. ✅ FK validation at CREATE TABLE time
2. ✅ FK must reference PRIMARY KEY or UNIQUE columns
3. ✅ ON DELETE CASCADE functionality
4. ✅ ON DELETE SET NULL functionality
5. ✅ ON DELETE RESTRICT (default) functionality
6. ✅ ON UPDATE CASCADE functionality
7. ✅ Circular FK dependency detection
8. ✅ Persistence of FK actions

## Usage Examples

### Basic Foreign Key with Default Behavior (RESTRICT)

```sql
CREATE DATABASE mydb;
USE mydb;

CREATE TABLE users (
    id INT PRIMARY KEY,
    name STRING
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id)
);

INSERT INTO users VALUES (1, 'Alice');
INSERT INTO orders VALUES (1, 1);

-- This will fail (RESTRICT is default):
DELETE FROM users WHERE id = 1;
-- Error: Cannot delete, referenced by orders
```

### Cascade Delete

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name STRING
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users VALUES (1, 'Alice');
INSERT INTO orders VALUES (1, 1);
INSERT INTO orders VALUES (2, 1);

-- This will succeed and delete both orders:
DELETE FROM users WHERE id = 1;
-- Result: User and both orders deleted
```

### Set NULL on Delete

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL
);

DELETE FROM users WHERE id = 1;
-- Result: user_id in orders set to NULL
```

### Cascade Update

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id) ON UPDATE CASCADE
);

UPDATE users SET id = 100 WHERE id = 1;
-- Result: user_id in orders automatically updated to 100
```

### Complex Example: Multi-level Cascade

```sql
-- Create a three-level hierarchy
CREATE TABLE categories (
    id INT PRIMARY KEY,
    name STRING
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name STRING,
    category_id INT REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    quantity INT
);

-- Insert data
INSERT INTO categories VALUES (1, 'Electronics');
INSERT INTO products VALUES (1, 'Laptop', 1);
INSERT INTO products VALUES (2, 'Mouse', 1);
INSERT INTO order_items VALUES (1, 1, 5);
INSERT INTO order_items VALUES (2, 2, 10);

-- Delete category cascades down
DELETE FROM categories WHERE id = 1;
-- Result: Category, both products, and both order items deleted
```

## Backwards Compatibility

- Existing databases will continue to work
- If no ON DELETE/ON UPDATE action is specified, default is RESTRICT
- Old database files will be automatically upgraded when loaded (missing on_delete/on_update will default to RESTRICT)

## Future Enhancements

Potential improvements not yet implemented:

1. **ALTER TABLE Support**: Add/drop foreign keys after table creation
2. **Composite Foreign Keys**: Support multi-column foreign keys
3. **Deferred Constraint Checking**: Check constraints at transaction commit instead of immediately
4. **Named Constraints**: Allow naming FK constraints for better error messages
5. **CHECK Constraints**: Add CHECK constraint support alongside FK constraints

## Error Messages

The system provides clear error messages for FK violations:

- `Foreign key error on column 'X': referenced table 'Y' does not exist`
- `Foreign key error on column 'X': referenced column 'Y.Z' must be PRIMARY KEY or UNIQUE`
- `Cannot delete row from 'X' where Y=Z: Referenced by N row(s) in table 'A.B'`
- `Circular foreign key dependency detected: A -> B -> C -> A`

## Conclusion

The foreign key relationship system is now significantly more robust with:
- ✅ Validation at table creation time
- ✅ Proper CASCADE/SET NULL/RESTRICT support
- ✅ Circular dependency detection
- ✅ Complete persistence of FK metadata

This brings the RDBMS much closer to production-ready foreign key handling!
