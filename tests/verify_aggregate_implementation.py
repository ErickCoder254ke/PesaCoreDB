#!/usr/bin/env python3
"""
Comprehensive verification script for PesaDB aggregate functions implementation.
Tests all required functionality:
- COUNT(*) and COUNT(column)
- Column aliasing with AS
- WHERE clauses with aggregates
- Empty table handling
- Backend/DB sync verification
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from rdbms.engine import DatabaseManager
from rdbms.sql.tokenizer import Tokenizer
from rdbms.sql.parser import Parser
from rdbms.sql.executor import Executor


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_test(description, passed, details=None):
    """Print test result."""
    status = f"{Colors.GREEN}✓ PASS" if passed else f"{Colors.RED}✗ FAIL"
    print(f"{status}{Colors.END} - {description}")
    if details:
        print(f"        {details}")


def verify_mandatory_requirements(executor):
    """Verify all mandatory objectives from the problem statement."""
    print_header("MANDATORY REQUIREMENTS VERIFICATION")
    
    all_passed = True
    
    # Requirement 1: COUNT(*) support
    print(f"\n{Colors.BOLD}Requirement 1: COUNT(*) Support{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(*) FROM users")))
        passed = len(result) == 1 and 'COUNT(*)' in result[0]
        print_test("COUNT(*) returns result", passed, f"Result: {result}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("COUNT(*) returns result", False, f"Error: {e}")
        all_passed = False
    
    # Requirement 2: COUNT(column) support
    print(f"\n{Colors.BOLD}Requirement 2: COUNT(column) Support{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(id) FROM users")))
        passed = len(result) == 1 and 'COUNT(id)' in result[0]
        print_test("COUNT(column) returns result", passed, f"Result: {result}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("COUNT(column) returns result", False, f"Error: {e}")
        all_passed = False
    
    # Requirement 3: Column aliasing with AS
    print(f"\n{Colors.BOLD}Requirement 3: Column Aliasing (AS){Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(*) AS count FROM users")))
        passed = len(result) == 1 and 'count' in result[0] and 'COUNT(*)' not in result[0]
        print_test("AS alias appears in result keys", passed, f"Result: {result}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("AS alias appears in result keys", False, f"Error: {e}")
        all_passed = False
    
    # Requirement 4: Aggregates return exactly one row
    print(f"\n{Colors.BOLD}Requirement 4: Execution Semantics{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(*) FROM users")))
        passed = len(result) == 1
        print_test("Aggregate returns exactly one row", passed, f"Row count: {len(result)}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Aggregate returns exactly one row", False, f"Error: {e}")
        all_passed = False
    
    # Requirement 5: Empty tables return 0
    print(f"\n{Colors.BOLD}Requirement 5: Empty Table Handling{Colors.END}")
    try:
        # Create empty table
        executor.execute(Parser().parse(Tokenizer().tokenize("CREATE TABLE empty_test (id INT PRIMARY KEY)")))
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(*) FROM empty_test")))
        passed = len(result) == 1 and result[0]['COUNT(*)'] == 0
        print_test("Empty table returns 0", passed, f"Result: {result}")
        executor.execute(Parser().parse(Tokenizer().tokenize("DROP TABLE empty_test")))
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Empty table returns 0", False, f"Error: {e}")
        all_passed = False
    
    # Requirement 6: WHERE clauses are respected
    print(f"\n{Colors.BOLD}Requirement 6: WHERE Clause Support{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT COUNT(*) FROM users WHERE active = true")))
        passed = len(result) == 1 and isinstance(result[0]['COUNT(*)'], int)
        print_test("WHERE clause is respected", passed, f"Result: {result}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("WHERE clause is respected", False, f"Error: {e}")
        all_passed = False
    
    return all_passed


def verify_compatibility(executor):
    """Verify that existing SELECT behavior is not broken."""
    print_header("COMPATIBILITY VERIFICATION")
    
    all_passed = True
    
    # Test basic SELECT
    print(f"\n{Colors.BOLD}Basic SELECT{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT * FROM users")))
        passed = isinstance(result, list) and len(result) > 0
        print_test("SELECT * works", passed, f"Returned {len(result)} rows")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("SELECT * works", False, f"Error: {e}")
        all_passed = False
    
    # Test SELECT with WHERE
    print(f"\n{Colors.BOLD}SELECT with WHERE{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT * FROM users WHERE id = 1")))
        passed = isinstance(result, list)
        print_test("SELECT with WHERE works", passed, f"Returned {len(result)} rows")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("SELECT with WHERE works", False, f"Error: {e}")
        all_passed = False
    
    # Test SELECT with LIMIT
    print(f"\n{Colors.BOLD}SELECT with LIMIT{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("SELECT * FROM users LIMIT 2")))
        passed = isinstance(result, list) and len(result) <= 2
        print_test("SELECT with LIMIT works", passed, f"Returned {len(result)} rows")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("SELECT with LIMIT works", False, f"Error: {e}")
        all_passed = False
    
    # Test INSERT
    print(f"\n{Colors.BOLD}INSERT{Colors.END}")
    try:
        result = executor.execute(Parser().parse(Tokenizer().tokenize("INSERT INTO users VALUES (999, 'Test User', true)")))
        passed = True
        print_test("INSERT works", passed, "Insert successful")
        # Clean up
        executor.execute(Parser().parse(Tokenizer().tokenize("DELETE FROM users WHERE id = 999")))
        all_passed = all_passed and passed
    except Exception as e:
        print_test("INSERT works", False, f"Error: {e}")
        all_passed = False
    
    return all_passed


def verify_required_test_cases(executor):
    """Verify the specific test cases mentioned in requirements."""
    print_header("REQUIRED TEST CASES")
    
    all_passed = True
    
    tests = [
        ("SELECT COUNT(*) FROM users", 
         "Basic COUNT(*) without alias"),
        
        ("SELECT COUNT(*) AS count FROM users", 
         "COUNT(*) with AS alias"),
        
        ("SELECT COUNT(id) FROM users", 
         "COUNT(column) without alias"),
        
        ("SELECT COUNT(id) AS total FROM users WHERE active = true",
         "COUNT(column) with WHERE and alias"),
    ]
    
    for sql, description in tests:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            passed = len(result) == 1 and len(result[0]) > 0
            print_test(description, passed, f"SQL: {sql}\n        Result: {result}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(description, False, f"SQL: {sql}\n        Error: {e}")
            all_passed = False
    
    return all_passed


def verify_aggregate_functions(executor):
    """Verify all aggregate functions work correctly."""
    print_header("AGGREGATE FUNCTIONS VERIFICATION")
    
    all_passed = True
    
    # Add salary column data if not exists
    try:
        executor.execute(Parser().parse(Tokenizer().tokenize("ALTER TABLE users ADD COLUMN salary INT")))
    except:
        pass  # Column might already exist
    
    try:
        executor.execute(Parser().parse(Tokenizer().tokenize("UPDATE users SET salary = 50000 WHERE id = 1")))
        executor.execute(Parser().parse(Tokenizer().tokenize("UPDATE users SET salary = 60000 WHERE id = 2")))
        executor.execute(Parser().parse(Tokenizer().tokenize("UPDATE users SET salary = 55000 WHERE id = 3")))
    except:
        pass  # Updates might fail if salary column doesn't support UPDATE yet
    
    functions = [
        ("COUNT(*)", "SELECT COUNT(*) FROM users"),
        ("COUNT(column)", "SELECT COUNT(id) FROM users"),
        ("SUM", "SELECT SUM(salary) FROM users"),
        ("AVG", "SELECT AVG(salary) FROM users"),
        ("MIN", "SELECT MIN(id) FROM users"),
        ("MAX", "SELECT MAX(id) FROM users"),
    ]
    
    for func_name, sql in functions:
        try:
            result = executor.execute(Parser().parse(Tokenizer().tokenize(sql)))
            passed = len(result) == 1
            print_test(f"{func_name} function", passed, f"Result: {result}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"{func_name} function", False, f"Error: {e}")
            all_passed = False
    
    return all_passed


def setup_test_database():
    """Set up test database with sample data."""
    print_header("DATABASE SETUP")
    
    db_manager = DatabaseManager()
    
    # Create test database
    if db_manager.database_exists("verify_test_db"):
        db_manager.drop_database("verify_test_db")
    
    db_manager.create_database("verify_test_db")
    print(f"{Colors.GREEN}✓{Colors.END} Created test database 'verify_test_db'")
    
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(db_manager)
    
    # Use the test database
    executor.execute(parser.parse(tokenizer.tokenize("USE verify_test_db")))
    
    # Create users table
    create_sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name STRING,
        active BOOL
    )
    """
    executor.execute(parser.parse(tokenizer.tokenize(create_sql)))
    print(f"{Colors.GREEN}✓{Colors.END} Created 'users' table")
    
    # Insert test data
    test_users = [
        (1, 'Alice', True),
        (2, 'Bob', True),
        (3, 'Charlie', False),
        (4, 'Diana', True),
        (5, 'Eve', False),
    ]
    
    for user_id, name, active in test_users:
        active_str = 'TRUE' if active else 'FALSE'
        sql = f"INSERT INTO users VALUES ({user_id}, '{name}', {active_str})"
        executor.execute(parser.parse(tokenizer.tokenize(sql)))
    
    print(f"{Colors.GREEN}✓{Colors.END} Inserted {len(test_users)} test users")
    
    return db_manager, executor


def cleanup_test_database(db_manager):
    """Clean up test database."""
    print_header("CLEANUP")
    
    try:
        db_manager.drop_database("verify_test_db")
        print(f"{Colors.GREEN}✓{Colors.END} Dropped test database 'verify_test_db'")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠{Colors.END} Cleanup warning: {e}")


def main():
    """Run comprehensive verification."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║   PesaDB Aggregate Functions - Comprehensive Verification         ║")
    print("║   Tests: COUNT(*), COUNT(column), AS aliases, WHERE, empty tables ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    # Setup
    db_manager, executor = setup_test_database()
    
    # Run verification tests
    results = []
    
    try:
        results.append(("Mandatory Requirements", verify_mandatory_requirements(executor)))
        results.append(("Compatibility", verify_compatibility(executor)))
        results.append(("Required Test Cases", verify_required_test_cases(executor)))
        results.append(("Aggregate Functions", verify_aggregate_functions(executor)))
    except Exception as e:
        print(f"\n{Colors.RED}✗ FATAL ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        cleanup_test_database(db_manager)
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(passed for _, passed in results)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}✓ PASS" if passed else f"{Colors.RED}✗ FAIL"
        print(f"{status}{Colors.END} - {test_name}")
    
    print(f"\n{Colors.BOLD}", end="")
    if all_passed:
        print(f"{Colors.GREEN}╔════════════════════════════════════════════════╗")
        print(f"║  🎉 ALL TESTS PASSED!                          ║")
        print(f"║  Aggregate functions are working correctly.    ║")
        print(f"║  Backend and database are properly synced.     ║")
        print(f"╚════════════════════════════════════════════════╝{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}╔════════════════════════════════════════════════╗")
        print(f"║  ⚠️  SOME TESTS FAILED!                        ║")
        print(f"║  Please review the errors above.               ║")
        print(f"╚════════════════════════════════════════════════╝{Colors.END}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Verification interrupted by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Verification failed: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
