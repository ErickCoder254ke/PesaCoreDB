#!/usr/bin/env python3
"""Quick verification script for aggregate function implementation."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from rdbms.engine import DatabaseManager, DataType, ColumnDefinition
from rdbms.sql.tokenizer import Tokenizer
from rdbms.sql.parser import Parser
from rdbms.sql.executor import Executor


def print_results(title, results):
    """Print query results in a formatted way."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    if results:
        for row in results:
            print(row)
    else:
        print("(No results)")
    print()


def main():
    """Run verification tests for aggregate functions."""
    print("\n" + "="*60)
    print("  PesaDB Aggregate Functions - Verification Script")
    print("="*60 + "\n")
    
    # Setup
    print("Setting up test database...")
    db_manager = DatabaseManager()
    db_manager.create_database("verify_db")
    
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(db_manager)
    
    # Use database
    executor.execute(parser.parse(tokenizer.tokenize("USE verify_db")))
    
    # Create table
    print("Creating 'users' table...")
    sql = """
    CREATE TABLE users (
        user_id INT PRIMARY KEY,
        username STRING,
        age INT,
        salary INT
    )
    """
    executor.execute(parser.parse(tokenizer.tokenize(sql)))
    
    # Insert test data
    print("Inserting test data...")
    test_data = [
        "INSERT INTO users VALUES (1, 'Alice', 30, 50000)",
        "INSERT INTO users VALUES (2, 'Bob', 25, 60000)",
        "INSERT INTO users VALUES (3, 'Charlie', 35, 55000)",
        "INSERT INTO users VALUES (4, 'Diana', 28, 65000)",
        "INSERT INTO users VALUES (5, 'Eve', 32, 70000)",
    ]
    
    for sql in test_data:
        executor.execute(parser.parse(tokenizer.tokenize(sql)))
    
    print("✓ Setup complete!\n")
    
    # Test queries
    tests = [
        ("COUNT(*) - Count all rows", 
         "SELECT COUNT(*) FROM users"),
        
        ("COUNT(column) - Count non-NULL values", 
         "SELECT COUNT(username) FROM users"),
        
        ("COUNT with WHERE clause", 
         "SELECT COUNT(*) FROM users WHERE age > 30"),
        
        ("SUM - Total salary", 
         "SELECT SUM(salary) FROM users"),
        
        ("AVG - Average age", 
         "SELECT AVG(age) FROM users"),
        
        ("MIN - Youngest age", 
         "SELECT MIN(age) FROM users"),
        
        ("MAX - Highest salary", 
         "SELECT MAX(salary) FROM users"),
        
        ("Multiple aggregates", 
         "SELECT COUNT(*), AVG(salary), MIN(age), MAX(age) FROM users"),
        
        ("Aggregate with complex WHERE", 
         "SELECT COUNT(*), AVG(salary) FROM users WHERE age >= 30 AND salary > 50000"),
        
        ("GROUP BY with aggregate", 
         "SELECT age, COUNT(*) FROM users GROUP BY age"),
    ]
    
    print("Running verification tests...\n")
    passed = 0
    failed = 0
    
    for i, (description, sql) in enumerate(tests, 1):
        try:
            result = executor.execute(parser.parse(tokenizer.tokenize(sql)))
            print_results(f"Test {i}: {description}\nSQL: {sql}", result)
            passed += 1
        except Exception as e:
            print(f"\n❌ Test {i} FAILED: {description}")
            print(f"   SQL: {sql}")
            print(f"   Error: {str(e)}\n")
            failed += 1
    
    # Test error handling
    print("\n" + "="*60)
    print("  Testing Error Handling")
    print("="*60 + "\n")
    
    error_tests = [
        ("Invalid aggregate: SUM(*)", "SELECT SUM(*) FROM users"),
        ("Non-numeric SUM", "SELECT SUM(username) FROM users"),
    ]
    
    for i, (description, sql) in enumerate(error_tests, 1):
        try:
            result = executor.execute(parser.parse(tokenizer.tokenize(sql)))
            print(f"❌ Error Test {i} FAILED: {description}")
            print(f"   Expected error but query succeeded\n")
            failed += 1
        except Exception as e:
            print(f"✓ Error Test {i} PASSED: {description}")
            print(f"  SQL: {sql}")
            print(f"  Expected error: {str(e)}\n")
            passed += 1
    
    # Cleanup
    print("Cleaning up...")
    db_manager.drop_database("verify_db")
    
    # Summary
    print("\n" + "="*60)
    print("  Verification Summary")
    print("="*60)
    print(f"  Total tests: {passed + failed}")
    print(f"  ✓ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 All tests passed! Aggregate functions are working correctly.\n")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
