-- ============================================================================
-- CONSTRAINT TESTING SCRIPT
-- ============================================================================
-- This script tests various constraint violations and edge cases
-- ============================================================================

-- Create a test database
CREATE DATABASE test_constraints;
USE test_constraints;

-- ----------------------------------------------------------------------------
-- PRIMARY KEY CONSTRAINT TESTING
-- ----------------------------------------------------------------------------

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username STRING UNIQUE,
    email STRING UNIQUE,
    active BOOL
);

-- Insert valid data
INSERT INTO users VALUES (1, 'alice', 'alice@example.com', TRUE);
INSERT INTO users VALUES (2, 'bob', 'bob@example.com', TRUE);
INSERT INTO users VALUES (3, 'charlie', 'charlie@example.com', FALSE);

-- View data
SELECT * FROM users;

-- Test: Duplicate primary key (should fail)
-- Uncomment to test:
-- INSERT INTO users VALUES (1, 'duplicate', 'dup@example.com', TRUE);
-- Expected: ConstraintViolation: UNIQUE constraint violation: Value '1' already exists in column 'user_id'

-- ----------------------------------------------------------------------------
-- UNIQUE CONSTRAINT TESTING
-- ----------------------------------------------------------------------------

-- Test: Duplicate unique value (should fail)
-- Uncomment to test:
-- INSERT INTO users VALUES (4, 'alice', 'newemail@example.com', TRUE);
-- Expected: ConstraintViolation: UNIQUE constraint violation: Value 'alice' already exists in column 'username'

-- Test: Another duplicate unique value (should fail)
-- Uncomment to test:
-- INSERT INTO users VALUES (5, 'newuser', 'alice@example.com', TRUE);
-- Expected: ConstraintViolation: UNIQUE constraint violation: Value 'alice@example.com' already exists in column 'email'

-- ----------------------------------------------------------------------------
-- UPDATE CONSTRAINT TESTING
-- ----------------------------------------------------------------------------

-- Test: Update to duplicate unique value (should fail)
-- Uncomment to test:
-- UPDATE users SET username = 'alice' WHERE user_id = 2;
-- Expected: ConstraintViolation: UNIQUE constraint violation: Value 'alice' already exists in column 'username'

-- Valid update
UPDATE users SET active = FALSE WHERE user_id = 1;
SELECT * FROM users WHERE user_id = 1;

-- ----------------------------------------------------------------------------
-- TYPE VALIDATION TESTING
-- ----------------------------------------------------------------------------

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name STRING,
    price INT,
    in_stock BOOL
);

-- Insert valid data
INSERT INTO products VALUES (1, 'Laptop', 999, TRUE);
INSERT INTO products VALUES (2, 'Mouse', 25, TRUE);
INSERT INTO products VALUES (3, 'Keyboard', 75, FALSE);

SELECT * FROM products;

-- Test: Wrong type (should fail if uncommented)
-- INSERT INTO products VALUES ('not_a_number', 'Monitor', 300, TRUE);
-- Expected: Column 'product_id' expects INT, got 'not_a_number'

-- ----------------------------------------------------------------------------
-- FOREIGN KEY REFERENCE TESTING
-- ----------------------------------------------------------------------------

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    quantity INT
);

-- Insert valid orders
INSERT INTO orders VALUES (1, 1, 1, 2);
INSERT INTO orders VALUES (2, 2, 2, 1);
INSERT INTO orders VALUES (3, 1, 3, 5);

SELECT * FROM orders;

-- Note: Foreign key enforcement (checking if referenced ID exists) is not
-- currently implemented in the engine, but the schema supports it for
-- future enhancement.

-- ----------------------------------------------------------------------------
-- DELETE AND INDEX CLEANUP TESTING
-- ----------------------------------------------------------------------------

-- Delete a user
DELETE FROM users WHERE user_id = 3;

-- Verify deletion and index cleanup
SELECT * FROM users;

-- Try to insert with the deleted user's ID (should now work)
INSERT INTO users VALUES (3, 'charlie_new', 'charlie_new@example.com', TRUE);

SELECT * FROM users;

-- ----------------------------------------------------------------------------
-- WHERE CLAUSE WITH INDEX TESTING
-- ----------------------------------------------------------------------------

-- These queries should use indexes for fast lookup
SELECT * FROM users WHERE user_id = 1;
SELECT * FROM users WHERE username = 'alice';
SELECT * FROM users WHERE email = 'bob@example.com';

-- These queries will perform full table scans (no index on 'active')
SELECT * FROM users WHERE active = TRUE;

-- ----------------------------------------------------------------------------
-- CLEANUP
-- ----------------------------------------------------------------------------

-- Show all tables
SHOW TABLES;

-- Drop tables
DROP TABLE orders;
DROP TABLE products;
DROP TABLE users;

-- Verify tables are dropped
SHOW TABLES;

-- Drop database
DROP DATABASE test_constraints;

-- Verify database is dropped
SHOW DATABASES;

-- ============================================================================
-- END OF CONSTRAINT TESTING SCRIPT
-- ============================================================================
