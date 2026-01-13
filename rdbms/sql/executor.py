"""SQL executor for executing parsed commands."""

from typing import List, Dict, Any
from .parser import (
    ParsedCommand, CreateTableCommand, InsertCommand, SelectCommand,
    UpdateCommand, DeleteCommand
)
from ..engine import Database, Table


class Executor:
    """Executes parsed SQL commands against a database."""
    
    def __init__(self, database: Database):
        """Initialize executor with a database.
        
        Args:
            database: Database instance to execute commands against
        """
        self.database = database
    
    def execute(self, command: ParsedCommand) -> Any:
        """Execute a parsed command.
        
        Args:
            command: Parsed command to execute
        
        Returns:
            Execution result (varies by command type)
        
        Raises:
            ValueError: If execution fails
        """
        if isinstance(command, CreateTableCommand):
            return self._execute_create_table(command)
        elif isinstance(command, InsertCommand):
            return self._execute_insert(command)
        elif isinstance(command, SelectCommand):
            return self._execute_select(command)
        elif isinstance(command, UpdateCommand):
            return self._execute_update(command)
        elif isinstance(command, DeleteCommand):
            return self._execute_delete(command)
        else:
            raise ValueError(f"Unknown command type: {type(command)}")
    
    def _execute_create_table(self, command: CreateTableCommand) -> str:
        """Execute CREATE TABLE command."""
        table = Table(command.table_name, command.columns)
        self.database.create_table(table)
        return f"Table '{command.table_name}' created successfully."
    
    def _execute_insert(self, command: InsertCommand) -> str:
        """Execute INSERT command."""
        table = self.database.get_table(command.table_name)
        
        # Build column-value mapping
        column_names = table.get_column_names()
        if len(command.values) != len(column_names):
            raise ValueError(
                f"Value count mismatch: expected {len(column_names)} values for columns {column_names}, "
                f"got {len(command.values)} values"
            )
        
        values_dict = {col: val for col, val in zip(column_names, command.values)}
        table.insert(values_dict)
        
        return f"1 row inserted into '{command.table_name}'."
    
    def _execute_select(self, command: SelectCommand) -> List[Dict[str, Any]]:
        """Execute SELECT command."""
        if command.join_table:
            return self._execute_select_with_join(command)
        else:
            table = self.database.get_table(command.table_name)
            return table.select(command.columns, command.where_col, command.where_val)
    
    def _execute_select_with_join(self, command: SelectCommand) -> List[Dict[str, Any]]:
        """Execute SELECT command with INNER JOIN."""
        # Get both tables
        left_table = self.database.get_table(command.table_name)
        right_table = self.database.get_table(command.join_table)
        
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
    
    def _execute_update(self, command: UpdateCommand) -> str:
        """Execute UPDATE command."""
        table = self.database.get_table(command.table_name)
        count = table.update(command.set_col, command.set_val, command.where_col, command.where_val)
        return f"{count} row(s) updated in '{command.table_name}'."
    
    def _execute_delete(self, command: DeleteCommand) -> str:
        """Execute DELETE command."""
        table = self.database.get_table(command.table_name)
        count = table.delete(command.where_col, command.where_val)
        return f"{count} row(s) deleted from '{command.table_name}'."
