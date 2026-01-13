#!/usr/bin/env python3
"""Interactive REPL for the RDBMS."""

import sys
from engine import Database
from sql import Tokenizer, Parser, Executor


def format_table(rows: list) -> str:
    """Format query results as a table.
    
    Args:
        rows: List of row dictionaries
    
    Returns:
        Formatted table string
    """
    if not rows:
        return "(0 rows)"
    
    # Get column names
    columns = list(rows[0].keys())
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            val_str = str(row[col])
            col_widths[col] = max(col_widths[col], len(val_str))
    
    # Build header
    header_parts = [col.ljust(col_widths[col]) for col in columns]
    header = " | ".join(header_parts)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    
    # Build rows
    result_lines = [header, separator]
    for row in rows:
        row_parts = [str(row[col]).ljust(col_widths[col]) for col in columns]
        result_lines.append(" | ".join(row_parts))
    
    result_lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")
    return "\n".join(result_lines)


def main():
    """Run the REPL."""
    print("RDBMS v1.0 - Relational Database Management System")
    print("Type SQL commands or 'exit' to quit.\n")
    
    # Initialize database and components
    database = Database()
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(database)
    
    while True:
        try:
            # Read input
            command = input("db> ").strip()
            
            # Check for exit
            if command.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            
            # Skip empty lines
            if not command:
                continue
            
            # Process command
            tokens = tokenizer.tokenize(command)
            parsed_command = parser.parse(tokens)
            result = executor.execute(parsed_command)
            
            # Display result
            if isinstance(result, list):
                # SELECT query result
                print(format_table(result))
            else:
                # Other commands (INSERT, UPDATE, DELETE, CREATE TABLE)
                print(result)
            
            print()  # Blank line after result
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        
        except EOFError:
            print("\nGoodbye!")
            break
        
        except Exception as e:
            print(f"Error: {e}")
            print()


if __name__ == "__main__":
    main()
