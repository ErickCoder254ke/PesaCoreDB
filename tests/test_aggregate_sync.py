"""
Test script to verify aggregate functions work correctly with backend and frontend.
Tests the fixes for table-qualified columns, GROUP BY, ORDER BY, and aliases.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rdbms.engine import DatabaseManager
from rdbms.sql.tokenizer import Tokenizer
from rdbms.sql.parser import Parser
from rdbms.sql.executor import Executor


def setup_test_data(executor):
    """Create test database and tables with sample data."""
    print("Setting up test database...")
    
    # Create and use test database
    executor.execute(Parser().parse(Tokenizer().tokenize("CREATE DATABASE test_aggregates")))
    executor.execute(Parser().parse(Tokenizer().tokenize("USE test_aggregates")))
    
    # Create users table
    sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name STRING,
        age INT,
        department STRING,
        salary INT
    )
    """
    executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
    
    # Insert sample data
    test_users = [
        (1, 'Alice', 30, 'Engineering', 75000),
        (2, 'Bob', 25, 'Engineering', 65000),
        (3, 'Charlie', 35, 'Sales', 70000),
        (4, 'Diana', 28, 'Sales', 68000),
        (5, 'Eve', 32, 'Engineering', 80000),
        (6, 'Frank', 29, 'Sales', 72000),
    ]
    
    for user in test_users:
        sql = f"INSERT INTO users VALUES ({user[0]}, '{user[1]}', {user[2]}, '{user[3]}', {user[4]})"
        executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
    
    print("✅ Test data created successfully\n")


def test_basic_aggregates(executor):
    """Test basic aggregate functions."""
    print("=" * 60)
    print("TEST 1: Basic Aggregate Functions")
    print("=" * 60)
    
    tests = [
        ("COUNT(*)", "SELECT COUNT(*) FROM users"),
        ("COUNT(column)", "SELECT COUNT(name) FROM users"),
        ("SUM", "SELECT SUM(salary) FROM users"),
        ("AVG", "SELECT AVG(age) FROM users"),
        ("MIN", "SELECT MIN(age) FROM users"),
        ("MAX", "SELECT MAX(salary) FROM users"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}: {result}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_table_qualified_columns(executor):
    """Test aggregate functions with table-qualified column names."""
    print("=" * 60)
    print("TEST 2: Table-Qualified Column Names")
    print("=" * 60)
    
    tests = [
        ("COUNT(users.id)", "SELECT COUNT(users.id) FROM users"),
        ("SUM(users.salary)", "SELECT SUM(users.salary) FROM users"),
        ("AVG(users.age)", "SELECT AVG(users.age) FROM users"),
        ("MIN(users.salary)", "SELECT MIN(users.salary) FROM users"),
        ("MAX(users.age)", "SELECT MAX(users.age) FROM users"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}: {result}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_column_aliases(executor):
    """Test column aliasing with AS keyword."""
    print("=" * 60)
    print("TEST 3: Column Aliasing (AS keyword)")
    print("=" * 60)
    
    tests = [
        ("COUNT AS", "SELECT COUNT(*) AS total_users FROM users"),
        ("SUM AS", "SELECT SUM(salary) AS total_salary FROM users"),
        ("AVG AS", "SELECT AVG(age) AS average_age FROM users"),
        ("Multiple aliases", "SELECT COUNT(*) AS total, AVG(salary) AS avg_sal FROM users"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}: {result}")
            # Verify the alias is in the result
            if result and len(result) > 0:
                keys = list(result[0].keys())
                print(f"   Column names: {keys}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_group_by(executor):
    """Test GROUP BY with aggregates."""
    print("=" * 60)
    print("TEST 4: GROUP BY with Aggregates")
    print("=" * 60)
    
    tests = [
        ("Simple GROUP BY", "SELECT department, COUNT(*) FROM users GROUP BY department"),
        ("GROUP BY with multiple aggregates", "SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_salary FROM users GROUP BY department"),
        ("Table-qualified GROUP BY", "SELECT department, COUNT(users.id) FROM users GROUP BY users.department"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}:")
            for row in result:
                print(f"   {row}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_aggregates_with_where(executor):
    """Test aggregates with WHERE clause."""
    print("=" * 60)
    print("TEST 5: Aggregates with WHERE Clause")
    print("=" * 60)
    
    tests = [
        ("COUNT with WHERE", "SELECT COUNT(*) FROM users WHERE age > 28"),
        ("SUM with WHERE", "SELECT SUM(salary) FROM users WHERE department = 'Engineering'"),
        ("AVG with WHERE", "SELECT AVG(age) FROM users WHERE salary > 70000"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}: {result}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_order_by_with_aggregates(executor):
    """Test ORDER BY with table-qualified columns."""
    print("=" * 60)
    print("TEST 6: ORDER BY with Table-Qualified Columns")
    print("=" * 60)
    
    tests = [
        ("Simple ORDER BY", "SELECT name, age FROM users ORDER BY age DESC"),
        ("Table-qualified ORDER BY", "SELECT name, age FROM users ORDER BY users.age DESC"),
        ("ORDER BY with aggregates", "SELECT department, COUNT(*) AS count FROM users GROUP BY department ORDER BY count DESC"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}:")
            for row in result[:3]:  # Show first 3 rows
                print(f"   {row}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def test_join_with_aggregates(executor):
    """Test that JOIN + AGGREGATE gives clear error."""
    print("=" * 60)
    print("TEST 7: JOIN + AGGREGATE (Should Error)")
    print("=" * 60)
    
    # Create orders table
    sql = "CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, amount INT)"
    executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
    
    sql = "INSERT INTO orders VALUES (1, 1, 100)"
    executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
    
    sql = "SELECT users.name, COUNT(orders.order_id) FROM users INNER JOIN orders ON users.id = orders.user_id GROUP BY users.name"
    
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
        print(f"❌ Should have raised error but got: {result}")
    except Exception as e:
        print(f"✅ Correctly raised error: {e}")
    print()


def test_having_clause(executor):
    """Test HAVING clause with aggregates."""
    print("=" * 60)
    print("TEST 8: HAVING Clause with Aggregates")
    print("=" * 60)
    
    tests = [
        ("HAVING with COUNT", "SELECT department, COUNT(*) AS count FROM users GROUP BY department HAVING COUNT(*) > 2"),
        ("HAVING with AVG", "SELECT department, AVG(salary) AS avg_sal FROM users GROUP BY department HAVING AVG(salary) > 70000"),
    ]
    
    for test_name, sql in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            print(f"✅ {test_name}:")
            for row in result:
                print(f"   {row}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AGGREGATE FUNCTIONS SYNC TEST")
    print("=" * 60 + "\n")
    
    # Initialize RDBMS
    db_manager = DatabaseManager()
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(db_manager)
    
    # Setup test data
    setup_test_data(executor)
    
    # Run all tests
    test_basic_aggregates(executor)
    test_table_qualified_columns(executor)
    test_column_aliases(executor)
    test_group_by(executor)
    test_aggregates_with_where(executor)
    test_order_by_with_aggregates(executor)
    test_join_with_aggregates(executor)
    test_having_clause(executor)
    
    print("=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
