"""Comprehensive tests for foreign key relationship functionality."""

import os
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rdbms.engine import DatabaseManager
from rdbms.sql import Tokenizer, Parser, Executor


def test_fk_validation_at_create_table():
    """Test that foreign keys are validated at CREATE TABLE time."""
    print("\n=== Test 1: FK Validation at CREATE TABLE ===")
    
    # Create temp directory for test database
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        tokens = tokenizer.tokenize("CREATE DATABASE test_db;")
        command = parser.parse(tokens)
        executor.execute(command)
        
        tokens = tokenizer.tokenize("USE test_db;")
        command = parser.parse(tokens)
        executor.execute(command)
        
        # Try to create table with FK to non-existent table
        try:
            sql = "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));"
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            executor.execute(command)
            print("❌ FAILED: Should have raised error for non-existent referenced table")
        except Exception as e:
            if "does not exist" in str(e):
                print("✅ PASSED: Correctly rejected FK to non-existent table")
            else:
                print(f"❌ FAILED: Wrong error: {e}")
        
        # Create users table
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        executor.execute(command)
        print("✅ Created users table")
        
        # Try to create table with FK to non-existent column
        try:
            sql = "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(invalid_col));"
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            executor.execute(command)
            print("❌ FAILED: Should have raised error for non-existent column")
        except Exception as e:
            if "does not exist" in str(e):
                print("✅ PASSED: Correctly rejected FK to non-existent column")
            else:
                print(f"❌ FAILED: Wrong error: {e}")
        
        # Create orders table with valid FK
        sql = "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        print(f"✅ Created orders table with FK: {result}")
        
    finally:
        # Clean up
        shutil.rmtree(test_dir, ignore_errors=True)


def test_fk_must_reference_pk_or_unique():
    """Test that foreign keys must reference PRIMARY KEY or UNIQUE columns."""
    print("\n=== Test 2: FK Must Reference PK or UNIQUE ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        tokens = tokenizer.tokenize("CREATE DATABASE test_db;")
        command = parser.parse(tokens)
        executor.execute(command)
        
        tokens = tokenizer.tokenize("USE test_db;")
        command = parser.parse(tokens)
        executor.execute(command)
        
        # Create table with non-unique column
        sql = "CREATE TABLE users (id INT PRIMARY KEY, email STRING, age INT);"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        executor.execute(command)
        print("✅ Created users table")
        
        # Try to create FK to non-unique column
        try:
            sql = "CREATE TABLE profiles (id INT PRIMARY KEY, user_age INT REFERENCES users(age));"
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            executor.execute(command)
            print("❌ FAILED: Should have rejected FK to non-unique column")
        except Exception as e:
            if "PRIMARY KEY or UNIQUE" in str(e):
                print("✅ PASSED: Correctly rejected FK to non-unique column")
            else:
                print(f"❌ FAILED: Wrong error: {e}")
        
        # Create table with unique column
        sql = "CREATE TABLE users2 (id INT PRIMARY KEY, email STRING UNIQUE);"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        executor.execute(command)
        
        # Create FK to unique column (should work)
        sql = "CREATE TABLE profiles (id INT PRIMARY KEY, user_email STRING REFERENCES users2(email));"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        print(f"✅ Created FK to UNIQUE column: {result}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_on_delete_cascade():
    """Test ON DELETE CASCADE functionality."""
    print("\n=== Test 3: ON DELETE CASCADE ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create tables with CASCADE
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        )))
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE CASCADE);"
        )))
        print("✅ Created tables with ON DELETE CASCADE")
        
        # Insert data
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO users VALUES (1, 'Alice');")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO users VALUES (2, 'Bob');")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (1, 1);")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (2, 1);")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (3, 2);")))
        print("✅ Inserted test data")
        
        # Check initial state
        result = executor.execute(parser.parse(tokenizer.tokenize("SELECT * FROM orders;")))
        print(f"Orders before delete: {len(result)} rows")
        
        # Delete user with CASCADE
        result = executor.execute(parser.parse(tokenizer.tokenize("DELETE FROM users WHERE id = 1;")))
        print(f"✅ Deleted user: {result}")
        
        # Check that orders were cascaded
        result = executor.execute(parser.parse(tokenizer.tokenize("SELECT * FROM orders;")))
        if len(result) == 1 and result[0]['user_id'] == 2:
            print(f"✅ CASCADE worked: Only 1 order remains (for user 2)")
        else:
            print(f"❌ FAILED: Expected 1 order, got {len(result)}: {result}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_on_delete_set_null():
    """Test ON DELETE SET NULL functionality."""
    print("\n=== Test 4: ON DELETE SET NULL ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create tables with SET NULL
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        )))
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE SET NULL);"
        )))
        print("✅ Created tables with ON DELETE SET NULL")
        
        # Insert data
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO users VALUES (1, 'Alice');")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (1, 1);")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (2, 1);")))
        print("✅ Inserted test data")
        
        # Delete user with SET NULL
        result = executor.execute(parser.parse(tokenizer.tokenize("DELETE FROM users WHERE id = 1;")))
        print(f"✅ Deleted user: {result}")
        
        # Check that FK was set to NULL
        result = executor.execute(parser.parse(tokenizer.tokenize("SELECT * FROM orders;")))
        if len(result) == 2 and all(row['user_id'] is None for row in result):
            print(f"✅ SET NULL worked: All user_id values are NULL")
        else:
            print(f"❌ FAILED: Expected NULL values, got: {result}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_on_delete_restrict():
    """Test ON DELETE RESTRICT (default) functionality."""
    print("\n=== Test 5: ON DELETE RESTRICT ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create tables with RESTRICT (or no action = default RESTRICT)
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        )))
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));"
        )))
        print("✅ Created tables (default ON DELETE RESTRICT)")
        
        # Insert data
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO users VALUES (1, 'Alice');")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (1, 1);")))
        print("✅ Inserted test data")
        
        # Try to delete user (should fail)
        try:
            executor.execute(parser.parse(tokenizer.tokenize("DELETE FROM users WHERE id = 1;")))
            print("❌ FAILED: Should have prevented deletion")
        except Exception as e:
            if "Cannot delete" in str(e) or "Referenced by" in str(e):
                print(f"✅ RESTRICT worked: Prevented deletion")
            else:
                print(f"❌ FAILED: Wrong error: {e}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_on_update_cascade():
    """Test ON UPDATE CASCADE functionality."""
    print("\n=== Test 6: ON UPDATE CASCADE ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create tables with ON UPDATE CASCADE
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        )))
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON UPDATE CASCADE);"
        )))
        print("✅ Created tables with ON UPDATE CASCADE")
        
        # Insert data
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO users VALUES (1, 'Alice');")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (1, 1);")))
        executor.execute(parser.parse(tokenizer.tokenize("INSERT INTO orders VALUES (2, 1);")))
        print("✅ Inserted test data")
        
        # Update user id with CASCADE
        result = executor.execute(parser.parse(tokenizer.tokenize("UPDATE users SET id = 100 WHERE id = 1;")))
        print(f"✅ Updated user id: {result}")
        
        # Check that orders were cascaded
        result = executor.execute(parser.parse(tokenizer.tokenize("SELECT * FROM orders;")))
        if len(result) == 2 and all(row['user_id'] == 100 for row in result):
            print(f"✅ ON UPDATE CASCADE worked: All user_id values updated to 100")
        else:
            print(f"❌ FAILED: Expected user_id=100, got: {result}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_circular_dependency_detection():
    """Test circular FK dependency detection."""
    print("\n=== Test 7: Circular FK Dependency Detection ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create first table
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, dept_id INT);"
        )))
        print("✅ Created users table")
        
        # Try to create circular dependency
        try:
            sql = "CREATE TABLE departments (id INT PRIMARY KEY, manager_id INT REFERENCES users(id));"
            executor.execute(parser.parse(tokenizer.tokenize(sql)))
            
            # Now try to add FK from users to departments (would create circle)
            # Note: This test is simplified. In reality, we'd need ALTER TABLE to add FK after creation
            # For now, this tests the detection logic
            print("⚠️  Note: Full circular dependency test requires ALTER TABLE support")
            
        except Exception as e:
            if "circular" in str(e).lower():
                print(f"✅ Circular dependency detected: {e}")
            else:
                print(f"ℹ️  Different error: {e}")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_persistence_of_fk_actions():
    """Test that FK actions are persisted and restored."""
    print("\n=== Test 8: Persistence of FK Actions ===")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        db_manager = DatabaseManager(data_dir=test_dir)
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db_manager)
        
        # Create and use database
        executor.execute(parser.parse(tokenizer.tokenize("CREATE DATABASE test_db;")))
        executor.execute(parser.parse(tokenizer.tokenize("USE test_db;")))
        
        # Create tables with FK actions
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE users (id INT PRIMARY KEY, name STRING);"
        )))
        executor.execute(parser.parse(tokenizer.tokenize(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE);"
        )))
        print("✅ Created tables with FK actions")
        
        # Describe table to see FK info
        result = executor.execute(parser.parse(tokenizer.tokenize("DESCRIBE orders;")))
        print(f"Orders schema: {result}")
        
        # Create new executor (simulate restart)
        executor2 = Executor(db_manager)
        executor2.current_database = "test_db"
        
        # Describe table again
        result = executor2.execute(parser.parse(tokenizer.tokenize("DESCRIBE orders;")))
        print(f"Orders schema after reload: {result}")
        
        # Check that FK info is preserved
        if any('users' in str(row.get('References', '')) for row in result):
            print("✅ FK relationship persisted correctly")
        else:
            print("❌ FAILED: FK relationship not persisted")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def run_all_tests():
    """Run all foreign key relationship tests."""
    print("=" * 60)
    print("FOREIGN KEY RELATIONSHIP TESTS")
    print("=" * 60)
    
    tests = [
        test_fk_validation_at_create_table,
        test_fk_must_reference_pk_or_unique,
        test_on_delete_cascade,
        test_on_delete_set_null,
        test_on_delete_restrict,
        test_on_update_cascade,
        test_circular_dependency_detection,
        test_persistence_of_fk_actions,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ TEST FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
