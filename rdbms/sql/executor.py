"""SQL executor for executing parsed commands."""

from typing import List, Dict, Any, Optional, Union
from .parser import (
    ParsedCommand, CreateTableCommand, InsertCommand, SelectCommand,
    UpdateCommand, DeleteCommand
)
from ..engine import Database, Table, DatabaseManager


class Executor:
    """Executes parsed SQL commands against a database."""

    def __init__(self, database_or_manager: Union[Database, DatabaseManager]):
        """Initialize executor with a database or database manager.

        Args:
            database_or_manager: Database instance or DatabaseManager
        """
        if isinstance(database_or_manager, DatabaseManager):
            self.database_manager = database_or_manager
            self.database = None  # Will be set per execute call
        else:
            self.database_manager = None
            self.database = database_or_manager

    def execute(self, command: ParsedCommand, db_name: Optional[str] = None) -> Any:
        """Execute a parsed command.

        Args:
            command: Parsed command to execute
            db_name: Database name (required if using DatabaseManager)

        Returns:
            Execution result (varies by command type)

        Raises:
            ValueError: If execution fails or db_name not provided with DatabaseManager
        """
        # Get the database to execute against
        if self.database_manager is not None:
            if db_name is None:
                raise ValueError("Database name must be provided when using DatabaseManager")
            database = self.database_manager.get_database(db_name)
        else:
            database = self.database

        # Execute command
        if isinstance(command, CreateTableCommand):
            return self._execute_create_table(command, database, db_name)
        elif isinstance(command, InsertCommand):
            return self._execute_insert(command, database, db_name)
        elif isinstance(command, SelectCommand):
            return self._execute_select(command, database)
        elif isinstance(command, UpdateCommand):
            return self._execute_update(command, database, db_name)
        elif isinstance(command, DeleteCommand):
            return self._execute_delete(command, database, db_name)
        else:
            raise ValueError(f"Unknown command type: {type(command)}")
    
    def _execute_create_table(self, command: CreateTableCommand, database: Database, db_name: Optional[str] = None) -> str:
        """Execute CREATE TABLE command."""
        table = Table(command.table_name, command.columns)
        database.create_table(table)

        # Auto-save if using DatabaseManager
        if self.database_manager is not None and db_name is not None:
            self.database_manager.save_database(db_name)

        return f"Table '{command.table_name}' created successfully."

    def _execute_insert(self, command: InsertCommand, database: Database, db_name: Optional[str] = None) -> str:
        """Execute INSERT command."""
        table = database.get_table(command.table_name)

        # Build column-value mapping
        column_names = table.get_column_names()
        if len(command.values) != len(column_names):
            raise ValueError(
                f"Value count mismatch: expected {len(column_names)} values for columns {column_names}, "
                f"got {len(command.values)} values"
            )

        values_dict = {col: val for col, val in zip(column_names, command.values)}
        table.insert(values_dict)

        # Auto-save if using DatabaseManager
        if self.database_manager is not None and db_name is not None:
            self.database_manager.save_database(db_name)

        return f"1 row inserted into '{command.table_name}'."

    def _execute_select(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command."""
        if command.join_table:
            return self._execute_select_with_join(command, database)
        else:
            table = database.get_table(command.table_name)
            return table.select(command.columns, command.where_col, command.where_val)
    
    def _execute_select_with_join(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command with INNER JOIN."""
        # Get both tables
        left_table = database.get_table(command.table_name)
        right_table = database.get_table(command.join_table)
        
        # Parse join columns (format: table.column)
        left_join_parts = command.join_left_col.split('.')
        right_join_parts = command.join_right_col.split('.')
        
        if len(left_join_parts) != 2 or len(right_join_parts) != 2:
            raise ValueError("JOIN condition must use table.column format")
        
        left_table_name, left_col_name = left_join_parts
        right_table_name, right_col_name = right_join_parts
        
        # Validate table names
        if left_table_name != command.table_name:
            raise ValueError(f"Left join table '{left_table_name}' does not match FROM table '{command.table_name}'")
        if right_table_name != command.join_table:
            raise ValueError(f"Right join table '{right_table_name}' does not match JOIN table '{command.join_table}'")
        
        # Validate columns exist
        if left_col_name not in left_table.schema:
            raise ValueError(f"Column '{left_col_name}' does not exist in table '{left_table_name}'")
        if right_col_name not in right_table.schema:
            raise ValueError(f"Column '{right_col_name}' does not exist in table '{right_table_name}'")
        
        # Perform join
        result = []
        left_rows = left_table.select()
        right_rows = right_table.select()
        
        for left_row in left_rows:
            left_join_value = left_row[left_col_name]
            
            for right_row in right_rows:
                right_join_value = right_row[right_col_name]
                
                if left_join_value == right_join_value:
                    # Merge rows with table prefixes
                    joined_row = {}
                    for col, val in left_row.items():
                        joined_row[f"{left_table_name}.{col}"] = val
                    for col, val in right_row.items():
                        joined_row[f"{right_table_name}.{col}"] = val
                    
                    # Project requested columns
                    if command.columns:
                        projected_row = {}
                        for col in command.columns:
                            # Check if column has table prefix
                            if '.' in col:
                                if col in joined_row:
                                    projected_row[col] = joined_row[col]
                                else:
                                    raise ValueError(f"Column '{col}' not found in join result")
                            else:
                                # Try to find column in either table
                                left_key = f"{left_table_name}.{col}"
                                right_key = f"{right_table_name}.{col}"
                                
                                if left_key in joined_row:
                                    projected_row[col] = joined_row[left_key]
                                elif right_key in joined_row:
                                    projected_row[col] = joined_row[right_key]
                                else:
                                    raise ValueError(f"Column '{col}' not found in join result")
                        result.append(projected_row)
                    else:
                        result.append(joined_row)
        
        return result
    
    def _execute_update(self, command: UpdateCommand, database: Database, db_name: Optional[str] = None) -> str:
        """Execute UPDATE command."""
        table = database.get_table(command.table_name)
        count = table.update(command.set_col, command.set_val, command.where_col, command.where_val)

        # Auto-save if using DatabaseManager
        if self.database_manager is not None and db_name is not None:
            self.database_manager.save_database(db_name)

        return f"{count} row(s) updated in '{command.table_name}'."
    
    def _execute_delete(self, command: DeleteCommand, database: Database, db_name: Optional[str] = None) -> str:
        """Execute DELETE command."""
        table = database.get_table(command.table_name)
        count = table.delete(command.where_col, command.where_val)

        # Auto-save if using DatabaseManager
        if self.database_manager is not None and db_name is not None:
            self.database_manager.save_database(db_name)

        return f"{count} row(s) deleted from '{command.table_name}'."
