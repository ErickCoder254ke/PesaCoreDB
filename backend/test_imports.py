#!/usr/bin/env python3
"""Test script to verify RDBMS imports are working correctly."""

import sys
from pathlib import Path

# Add parent directory to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    print("Testing RDBMS imports...")
    
    from rdbms.engine import Database, Table, ColumnDefinition, DataType
    print("✓ Engine imports successful")
    
    from rdbms.sql import Tokenizer, Parser, Executor
    print("✓ SQL imports successful")
    
    # Test basic functionality
    db = Database()
    print("✓ Database instance created")
    
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(db)
    print("✓ Tokenizer, Parser, Executor initialized")
    
    # Test a simple query
    sql = "CREATE TABLE test (id INT PRIMARY KEY, name STRING)"
    tokens = tokenizer.tokenize(sql)
    command = parser.parse(tokens)
    result = executor.execute(command)
    print(f"✓ Test query executed: {result}")
    
    print("\n🎉 All tests passed! Backend is ready to start.")
    print("\nTo start the server, run:")
    print("  uvicorn server:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease ensure:")
    print("1. You are in the 'backend' directory")
    print("2. The 'rdbms' folder exists in the parent directory")
    print("3. All Python dependencies are installed (pip install -r requirements.txt)")
    sys.exit(1)
