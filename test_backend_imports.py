#!/usr/bin/env python3
"""Test script to verify all backend imports and basic functionality."""

import sys
from pathlib import Path

# Add project root to path (this file is in the root directory)
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def test_imports():
    """Test that all imports work correctly."""
    print("=" * 60)
    print("Testing RDBMS Backend Imports")
    print("=" * 60)
    print()
    
    try:
        print("1. Testing engine imports...")
        from rdbms.engine import Database, Table, ColumnDefinition, DataType, Row, Index
        print("   ✅ Engine imports successful")
        print()
        
        print("2. Testing SQL module imports...")
        from rdbms.sql import Tokenizer, Parser, Executor, Token
        print("   ✅ SQL module imports successful")
        print()
        
        print("3. Creating database instance...")
        db = Database()
        print("   ✅ Database instance created")
        print()
        
        print("4. Initializing SQL components...")
        tokenizer = Tokenizer()
        parser = Parser()
        executor = Executor(db)
        print("   ✅ Tokenizer, Parser, and Executor initialized")
        print()
        
        print("5. Testing a simple CREATE TABLE query...")
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name STRING, age INT)"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        print(f"   ✅ {result}")
        print()
        
        print("6. Testing INSERT query...")
        sql = "INSERT INTO users VALUES (1, 'Alice', 30)"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        print(f"   ✅ {result}")
        print()
        
        print("7. Testing SELECT query...")
        sql = "SELECT * FROM users"
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        print(f"   ✅ Query returned {len(result)} row(s)")
        print(f"   Data: {result}")
        print()
        
        print("8. Verifying table list...")
        tables = db.list_tables()
        print(f"   ✅ Tables in database: {tables}")
        print()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("The backend is ready to start. To run the server:")
        print()
        print("  cd backend")
        print("  python server.py")
        print()
        print("  OR")
        print()
        print("  uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("Then open http://localhost:8000/docs to see the API documentation")
        print()
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nPossible solutions:")
        print("1. Ensure you're running this from the project root directory")
        print("2. Check that all Python files have the correct import statements")
        print("3. Verify the rdbms package structure is correct")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
