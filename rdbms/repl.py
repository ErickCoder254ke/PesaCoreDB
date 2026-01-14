#!/usr/bin/env python3
"""Interactive REPL for the RDBMS."""

import sys
from engine import DatabaseManager
from sql import Tokenizer, Parser, Executor


def format_table(rows: list, max_width: int = 100) -> str:
    """Format query results as a table.
    
    Args:
        rows: List of row dictionaries
        max_width: Maximum width for each column
    
    Returns:
        Formatted table string
    """
    if not rows:
        return "(0 rows)"
    
    # Get column names
    columns = list(rows[0].keys())
    
    # Calculate column widths
    col_widths = {col: min(len(col), max_width) for col in columns}
    for row in rows:
        for col in columns:
            val_str = str(row[col])
            col_widths[col] = min(max(col_widths[col], len(val_str)), max_width)
    
    # Build header
    header_parts = [col.ljust(col_widths[col]) for col in columns]
    header = " | ".join(header_parts)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    
    # Build rows
    result_lines = [header, separator]
    for row in rows:
        row_parts = []
        for col in columns:
            val_str = str(row[col])
            if len(val_str) > max_width:
                val_str = val_str[:max_width-3] + "..."
            row_parts.append(val_str.ljust(col_widths[col]))
        result_lines.append(" | ".join(row_parts))
    
    result_lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")
    return "\n".join(result_lines)


def main():
    """Run the REPL."""
    print("=" * 60)
    print("RDBMS v2.0 - Relational Database Management System")
    print("=" * 60)
    print("\nSupported Commands:")
    print("  Database:  CREATE DATABASE, DROP DATABASE, USE, SHOW DATABASES")
    print("  Table:     CREATE TABLE, DROP TABLE, SHOW TABLES, DESCRIBE")
    print("  Data:      INSERT, SELECT, UPDATE, DELETE")
    print("\nType 'exit' or 'quit' to exit.\n")
    
    # Initialize database manager and components
    database_manager = DatabaseManager()
    tokenizer = Tokenizer()
    parser = Parser()
    executor = Executor(database_manager)
    
    # Track multi-line input
    command_buffer = []
    
    while True:
        try:
            # Prompt shows current database
            if executor.current_database:
                prompt = f"{executor.current_database}> "
            else:
                prompt = "rdbms> "
            
            # Read input
            line = input(prompt).strip()
            
            # Check for exit
            if line.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            
            # Skip empty lines
            if not line:
                continue
            
            # Add to buffer
            command_buffer.append(line)
            
            # Check if command is complete (ends with semicolon or is a complete statement)
            command = ' '.join(command_buffer)
            
            # If doesn't end with semicolon, continue collecting
            if not command.endswith(';') and not any(command.upper().startswith(kw) for kw in ['SHOW', 'USE', 'DESCRIBE', 'DESC']):
                continue
            
            # Process command
            try:
                tokens = tokenizer.tokenize(command)
                parsed_command = parser.parse(tokens)
                result = executor.execute(parsed_command)
                
                # Display result
                if isinstance(result, list):
                    # SELECT query result or metadata query
                    print(format_table(result))
                else:
                    # Other commands (INSERT, UPDATE, DELETE, CREATE, DROP, USE)
                    print(result)
                
                print()  # Blank line after result
            
            except Exception as e:
                # Display error
                print(f"Error: {e}")
                print()
            
            # Clear buffer after processing
            command_buffer = []
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        
        except EOFError:
            print("\nGoodbye!")
            break
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            command_buffer = []
            print()


if __name__ == "__main__":
    main()
