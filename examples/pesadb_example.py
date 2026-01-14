"""
PesaDB Example - Using the custom RDBMS with pesadb:// connection URL.

This example demonstrates:
1. Connecting to PesaDB using pesadb:// URL
2. Creating tables with constraints
3. Inserting data
4. Querying data with WHERE clauses
5. Performing INNER JOIN operations
6. Updating and deleting data
"""

import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rdbms.connection import connect
from rdbms.sql import Tokenizer, Parser, Executor


def execute_sql(executor, sql: str, description: str = None):
    """Helper function to execute SQL and print results."""
    if description:
        print(f"\n{'=' * 60}")
        print(f"  {description}")
        print('=' * 60)
    
    print(f"SQL: {sql}")
    
    try:
        tokenizer = Tokenizer()
        parser = Parser()
        
        tokens = tokenizer.tokenize(sql)
        command = parser.parse(tokens)
        result = executor.execute(command)
        
        if isinstance(result, list):
            print(f"Result: {len(result)} row(s)")
            for row in result:
                print(f"  {row}")
        else:
            print(f"Result: {result}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Main example function."""
    
    print("=" * 60)
    print("  PesaDB Example - SQL-based Custom RDBMS")
    print("=" * 60)
    
    # 1. Connect to database using pesadb:// URL
    print("\n1. Connecting to PesaDB...")
    connection_url = "pesadb://localhost/example_db"
    print(f"   URL: {connection_url}")
    
    conn = connect(connection_url)
    db_manager = conn.get_database_manager()
    db_name = conn.get_database_name()
    
    print(f"   ✅ Connected to database: {db_name}")
    print(f"   📁 Data directory: {conn.data_dir}")
    
    # 2. Initialize executor
    executor = Executor(db_manager)
    executor.current_database = db_name
    
    # 3. Create tables
    execute_sql(
        executor,
        """CREATE TABLE users (
            id INT PRIMARY KEY,
            email STRING UNIQUE,
            name STRING,
            is_active BOOL
        )""",
        "Creating 'users' table with constraints"
    )
    
    execute_sql(
        executor,
        """CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            user_id INT REFERENCES users(id),
            amount INT,
            status STRING
        )""",
        "Creating 'orders' table with foreign key"
    )
    
    # 4. Show tables
    execute_sql(executor, "SHOW TABLES", "Listing all tables")
    
    # 5. Describe table schema
    execute_sql(executor, "DESCRIBE users", "Describing 'users' table schema")
    
    # 6. Insert data into users table
    users_data = [
        (1, 'alice@example.com', 'Alice Johnson', True),
        (2, 'bob@example.com', 'Bob Smith', True),
        (3, 'carol@example.com', 'Carol Williams', False),
        (4, 'david@example.com', 'David Brown', True),
        (5, 'eve@example.com', 'Eve Davis', True),
    ]
    
    print("\n" + "=" * 60)
    print("  Inserting users")
    print("=" * 60)
    
    for user_id, email, name, is_active in users_data:
        sql = f"INSERT INTO users VALUES ({user_id}, '{email}', '{name}', {is_active})"
        execute_sql(executor, sql)
    
    # 7. Insert data into orders table
    orders_data = [
        (101, 1, 250, 'completed'),
        (102, 1, 150, 'pending'),
        (103, 2, 500, 'completed'),
        (104, 3, 75, 'cancelled'),
        (105, 4, 320, 'completed'),
        (106, 2, 180, 'pending'),
        (107, 5, 420, 'completed'),
    ]
    
    print("\n" + "=" * 60)
    print("  Inserting orders")
    print("=" * 60)
    
    for order_id, user_id, amount, status in orders_data:
        sql = f"INSERT INTO orders VALUES ({order_id}, {user_id}, {amount}, '{status}')"
        execute_sql(executor, sql)
    
    # 8. Query all users
    execute_sql(executor, "SELECT * FROM users", "Selecting all users")
    
    # 9. Query with WHERE clause
    execute_sql(
        executor,
        "SELECT * FROM users WHERE is_active = TRUE",
        "Selecting active users only"
    )
    
    # 10. Query specific user
    execute_sql(
        executor,
        "SELECT name, email FROM users WHERE id = 1",
        "Selecting specific user by ID"
    )
    
    # 11. Query all orders
    execute_sql(executor, "SELECT * FROM orders", "Selecting all orders")
    
    # 12. INNER JOIN - Get orders with user information
    execute_sql(
        executor,
        """SELECT users.name, users.email, orders.order_id, orders.amount, orders.status
        FROM users
        INNER JOIN orders ON users.id = orders.user_id""",
        "INNER JOIN: Orders with user information"
    )
    
    # 13. INNER JOIN - Get completed orders only
    # Note: WHERE clause after JOIN not fully supported yet, so we filter in application
    result = execute_sql(
        executor,
        """SELECT users.name, orders.amount, orders.status
        FROM users
        INNER JOIN orders ON users.id = orders.user_id""",
        "INNER JOIN: All orders with user names"
    )
    
    if result:
        print("\nFiltering for completed orders (application-side):")
        completed = [r for r in result if r.get('status') == 'completed']
        for order in completed:
            print(f"  {order}")
    
    # 14. UPDATE operation
    execute_sql(
        executor,
        "UPDATE users SET is_active = FALSE WHERE id = 2",
        "Deactivating user with ID 2"
    )
    
    # Verify update
    execute_sql(executor, "SELECT * FROM users WHERE id = 2", "Verifying update")
    
    # 15. DELETE operation
    execute_sql(
        executor,
        "DELETE FROM orders WHERE status = 'cancelled'",
        "Deleting cancelled orders"
    )
    
    # Verify deletion
    execute_sql(executor, "SELECT * FROM orders", "Verifying deletion")
    
    # 16. Show database statistics
    print("\n" + "=" * 60)
    print("  Database Statistics")
    print("=" * 60)
    
    db = conn.get_database()
    tables = db.list_tables()
    print(f"Total tables: {len(tables)}")
    
    for table_name in tables:
        table = db.get_table(table_name)
        print(f"  - {table_name}: {len(table.rows)} rows, {len(table.columns)} columns")
    
    # 17. Close connection
    print("\n" + "=" * 60)
    print("  Closing connection")
    print("=" * 60)
    conn.close()
    print("✅ Connection closed")
    
    print("\n" + "=" * 60)
    print("  Example completed successfully!")
    print("=" * 60)
    print(f"\nDatabase persisted to: {conn.data_dir}/{db_name}.json")
    print(f"You can reconnect using: pesadb://localhost/{db_name}")


if __name__ == "__main__":
    main()
