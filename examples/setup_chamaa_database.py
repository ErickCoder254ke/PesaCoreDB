"""
Initialize the Chamaa database with required tables and sample data.

This script creates the 'chamaa' database and sets up the schema for a
Chamaa (community savings group) management system.

Usage:
    python setup_chamaa_database.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import rdbms module
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rdbms.connection import connect
from rdbms.sql import Tokenizer, Parser, Executor

# Load environment variables
ENV_FILE = PROJECT_ROOT / 'backend' / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    print(f"⚠️ Warning: .env file not found at {ENV_FILE}")

# Configuration
PESADB_URL = os.getenv("PESADB_URL", "pesadb://localhost/chamaa")
DB_NAME = "chamaa"  # Explicitly set to chamaa

# Override URL to ensure we're creating chamaa database
CHAMAA_URL = f"pesadb://localhost/{DB_NAME}"

print("=" * 80)
print("CHAMAA DATABASE INITIALIZATION")
print("=" * 80)
print(f"Database: {DB_NAME}")
print(f"Connection URL: {CHAMAA_URL}")
print("=" * 80)

try:
    # Connect to database (will auto-create if it doesn't exist)
    connection = connect(CHAMAA_URL)
    db_manager = connection.get_database_manager()
    db_name = connection.get_database_name()
    
    print(f"✅ Connected to database: {db_name}")
    
    # Initialize SQL components
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(db_manager)
    executor.current_database = db_name
    
    def execute_sql(sql: str, description: str = ""):
        """Execute SQL and print result."""
        try:
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            result = executor.execute(command)
            
            if description:
                print(f"✅ {description}")
            else:
                print(f"✅ {result}")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n📋 Creating database schema...")
    print("-" * 80)
    
    # Create Members table
    execute_sql("""
        CREATE TABLE members (
            id INT PRIMARY KEY,
            name STRING,
            email STRING UNIQUE,
            phone STRING,
            join_date STRING,
            is_active BOOL
        )
    """, "Created 'members' table")
    
    # Create Contributions table
    execute_sql("""
        CREATE TABLE contributions (
            id INT PRIMARY KEY,
            member_id INT REFERENCES members(id),
            amount INT,
            contribution_date STRING,
            payment_method STRING,
            status STRING
        )
    """, "Created 'contributions' table (with FK to members)")
    
    # Create Loans table
    execute_sql("""
        CREATE TABLE loans (
            id INT PRIMARY KEY,
            member_id INT REFERENCES members(id),
            amount INT,
            interest_rate INT,
            issue_date STRING,
            due_date STRING,
            status STRING
        )
    """, "Created 'loans' table (with FK to members)")
    
    # Create Meetings table
    execute_sql("""
        CREATE TABLE meetings (
            id INT PRIMARY KEY,
            meeting_date STRING,
            location STRING,
            attendees_count INT,
            agenda STRING
        )
    """, "Created 'meetings' table")
    
    # Create Expenses table
    execute_sql("""
        CREATE TABLE expenses (
            id INT PRIMARY KEY,
            description STRING,
            amount INT,
            expense_date STRING,
            category STRING,
            approved_by INT REFERENCES members(id)
        )
    """, "Created 'expenses' table (with FK to members)")
    
    print("\n📊 Inserting sample data...")
    print("-" * 80)
    
    # Insert sample members
    members_data = [
        (1, 'Alice Wanjiru', 'alice@example.com', '+254701234567', '2024-01-15', 'TRUE'),
        (2, 'Bob Kamau', 'bob@example.com', '+254702345678', '2024-01-15', 'TRUE'),
        (3, 'Carol Achieng', 'carol@example.com', '+254703456789', '2024-02-01', 'TRUE'),
        (4, 'David Omondi', 'david@example.com', '+254704567890', '2024-02-15', 'TRUE'),
        (5, 'Eve Njeri', 'eve@example.com', '+254705678901', '2024-03-01', 'FALSE'),
    ]
    
    for member in members_data:
        execute_sql(
            f"INSERT INTO members VALUES ({member[0]}, '{member[1]}', '{member[2]}', '{member[3]}', '{member[4]}', {member[5]})",
            f"Inserted member: {member[1]}"
        )
    
    # Insert sample contributions
    contributions_data = [
        (101, 1, 5000, '2024-01-20', 'M-Pesa', 'completed'),
        (102, 2, 5000, '2024-01-20', 'M-Pesa', 'completed'),
        (103, 3, 5000, '2024-02-05', 'Bank Transfer', 'completed'),
        (104, 1, 5000, '2024-02-20', 'M-Pesa', 'completed'),
        (105, 2, 5000, '2024-02-20', 'Cash', 'completed'),
        (106, 4, 5000, '2024-03-05', 'M-Pesa', 'completed'),
        (107, 3, 5000, '2024-03-05', 'M-Pesa', 'pending'),
    ]
    
    for contrib in contributions_data:
        execute_sql(
            f"INSERT INTO contributions VALUES ({contrib[0]}, {contrib[1]}, {contrib[2]}, '{contrib[3]}', '{contrib[4]}', '{contrib[5]}')",
            f"Inserted contribution: KES {contrib[2]} from member {contrib[1]}"
        )
    
    # Insert sample loans
    loans_data = [
        (201, 2, 15000, 10, '2024-02-01', '2024-05-01', 'active'),
        (202, 4, 20000, 10, '2024-03-01', '2024-06-01', 'active'),
    ]
    
    for loan in loans_data:
        execute_sql(
            f"INSERT INTO loans VALUES ({loan[0]}, {loan[1]}, {loan[2]}, {loan[3]}, '{loan[4]}', '{loan[5]}', '{loan[6]}')",
            f"Inserted loan: KES {loan[2]} to member {loan[1]}"
        )
    
    # Insert sample meetings
    meetings_data = [
        (301, '2024-01-15', 'Community Hall', 4, 'Group formation and rules'),
        (302, '2024-02-15', 'Community Hall', 5, 'First contribution cycle'),
        (303, '2024-03-15', 'Community Hall', 4, 'Loan applications review'),
    ]
    
    for meeting in meetings_data:
        execute_sql(
            f"INSERT INTO meetings VALUES ({meeting[0]}, '{meeting[1]}', '{meeting[2]}', {meeting[3]}, '{meeting[4]}')",
            f"Inserted meeting: {meeting[1]} - {meeting[4]}"
        )
    
    # Insert sample expenses
    expenses_data = [
        (401, 'Meeting refreshments', 2000, '2024-01-15', 'Administration', 1),
        (402, 'Record book purchase', 1500, '2024-01-15', 'Stationery', 1),
        (403, 'Meeting refreshments', 2500, '2024-02-15', 'Administration', 2),
    ]
    
    for expense in expenses_data:
        execute_sql(
            f"INSERT INTO expenses VALUES ({expense[0]}, '{expense[1]}', {expense[2]}, '{expense[3]}', '{expense[4]}', {expense[5]})",
            f"Inserted expense: {expense[1]} - KES {expense[2]}"
        )
    
    print("\n" + "=" * 80)
    print("✅ CHAMAA DATABASE INITIALIZATION COMPLETE!")
    print("=" * 80)
    print(f"\nDatabase: {db_name}")
    print(f"Location: data/{db_name}.json")
    print("\nTables created:")
    print("  - members (5 records)")
    print("  - contributions (7 records)")
    print("  - loans (2 records)")
    print("  - meetings (3 records)")
    print("  - expenses (3 records)")
    print("\n📊 Database Statistics:")
    
    # Show some statistics
    members_result = execute_sql("SELECT * FROM members", "")
    if isinstance(members_result, list):
        print(f"  Total members: {len(members_result)}")
    
    contributions_result = execute_sql("SELECT * FROM contributions", "")
    if isinstance(contributions_result, list):
        total_contributions = sum(c['amount'] for c in contributions_result if c.get('status') == 'completed')
        print(f"  Total contributions collected: KES {total_contributions:,}")
    
    loans_result = execute_sql("SELECT * FROM loans", "")
    if isinstance(loans_result, list):
        total_loans = sum(l['amount'] for l in loans_result)
        print(f"  Total loans disbursed: KES {total_loans:,}")
    
    print("\n🎯 Next Steps:")
    print("  1. Update your app's .env file:")
    print("     PESADB_URL=pesadb://localhost/chamaa")
    print("     DB_NAME=chamaa")
    print("\n  2. Start the backend server:")
    print("     cd backend && python server.py")
    print("\n  3. Connect your application using the connection guide")
    print("     See: CLIENT_APP_CONNECTION_GUIDE.md")
    print("\n  4. Test with sample queries:")
    print("     SELECT * FROM members")
    print("     SELECT * FROM contributions WHERE status = 'completed'")
    print("     SELECT m.name, c.amount, c.contribution_date")
    print("     FROM members m INNER JOIN contributions c ON m.id = c.member_id")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
