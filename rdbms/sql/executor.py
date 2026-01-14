"""SQL executor for executing parsed commands."""

from typing import List, Dict, Any, Optional
from .parser import (
    ParsedCommand, CreateDatabaseCommand, DropDatabaseCommand, UseDatabaseCommand, 
    ShowDatabasesCommand, CreateTableCommand, DropTableCommand, ShowTablesCommand, 
    DescribeTableCommand, InsertCommand, SelectCommand, UpdateCommand, DeleteCommand
)
from ..engine import Database, Table, DatabaseManager, ColumnDefinition


class ExecutorError(Exception):
    """Exception raised for execution errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TableNotFoundError(ExecutorError):
    """Exception raised when a table is not found."""
    
    def __init__(self, table_name: str):
        super().__init__(f"TableNotFoundError: table '{table_name}' does not exist")


class DatabaseNotFoundError(ExecutorError):
    """Exception raised when a database is not found."""
    
    def __init__(self, database_name: str):
        super().__init__(f"DatabaseNotFoundError: database '{database_name}' does not exist")


class ConstraintViolationError(ExecutorError):
    """Exception raised when a constraint is violated."""
    pass


class Executor:
    """Executes parsed SQL commands against a database."""

    def __init__(self, database_manager: DatabaseManager):
        """Initialize executor with a database manager.

        Args:
            database_manager: DatabaseManager instance
        """
        self.database_manager = database_manager
        self.current_database: Optional[str] = None

    def _validate_foreign_keys(self, table: Table, values_dict: Dict[str, Any], database: Database):
        """Validate foreign key constraints for a row.

        Args:
            table: Table being inserted/updated
            values_dict: Column values to validate
            database: Database instance for looking up referenced tables

        Raises:
            ConstraintViolationError: If foreign key constraint is violated
        """
        for col in table.columns:
            if col.foreign_key_table and col.name in values_dict:
                fk_value = values_dict[col.name]
                fk_table_name = col.foreign_key_table
                fk_column_name = col.foreign_key_column

                # Get referenced table
                try:
                    fk_table = database.get_table(fk_table_name)
                except ValueError:
                    raise ConstraintViolationError(
                        f"Foreign key constraint violation: referenced table '{fk_table_name}' does not exist"
                    )

                # Check if the foreign key column exists in the referenced table
                if fk_column_name not in fk_table.schema:
                    raise ConstraintViolationError(
                        f"Foreign key constraint violation: column '{fk_column_name}' does not exist in table '{fk_table_name}'"
                    )

                # Check if the value exists in the referenced table
                matching_rows = fk_table.select(
                    columns=[fk_column_name],
                    where_col=fk_column_name,
                    where_val=fk_value
                )

                if not matching_rows:
                    raise ConstraintViolationError(
                        f"Foreign key constraint violation: value '{fk_value}' does not exist in "
                        f"{fk_table_name}({fk_column_name})"
                    )

    def execute(self, command: ParsedCommand) -> Any:
        """Execute a parsed command.

        Args:
            command: Parsed command to execute

        Returns:
            Execution result (varies by command type)

        Raises:
            ExecutorError: If execution fails
        """
        # Database management commands (don't require active database)
        if isinstance(command, CreateDatabaseCommand):
            return self._execute_create_database(command)
        elif isinstance(command, DropDatabaseCommand):
            return self._execute_drop_database(command)
        elif isinstance(command, UseDatabaseCommand):
            return self._execute_use_database(command)
        elif isinstance(command, ShowDatabasesCommand):
            return self._execute_show_databases(command)
        
        # All other commands require an active database
        if self.current_database is None:
            raise ExecutorError("No database selected. Use 'USE database_name;' to select a database.")
        
        # Get the current database
        try:
            database = self.database_manager.get_database(self.current_database)
        except ValueError as e:
            raise DatabaseNotFoundError(self.current_database)
        
        # Table management and data manipulation commands
        if isinstance(command, CreateTableCommand):
            return self._execute_create_table(command, database)
        elif isinstance(command, DropTableCommand):
            return self._execute_drop_table(command, database)
        elif isinstance(command, ShowTablesCommand):
            return self._execute_show_tables(command, database)
        elif isinstance(command, DescribeTableCommand):
            return self._execute_describe_table(command, database)
        elif isinstance(command, InsertCommand):
            return self._execute_insert(command, database)
        elif isinstance(command, SelectCommand):
            return self._execute_select(command, database)
        elif isinstance(command, UpdateCommand):
            return self._execute_update(command, database)
        elif isinstance(command, DeleteCommand):
            return self._execute_delete(command, database)
        else:
            raise ExecutorError(f"Unknown command type: {type(command).__name__}")
    
    # Database Management Commands
    
    def _execute_create_database(self, command: CreateDatabaseCommand) -> str:
        """Execute CREATE DATABASE command."""
        try:
            self.database_manager.create_database(command.database_name)
            return f"Database '{command.database_name}' created successfully."
        except ValueError as e:
            raise ExecutorError(str(e))
    
    def _execute_drop_database(self, command: DropDatabaseCommand) -> str:
        """Execute DROP DATABASE command."""
        try:
            # Don't allow dropping the currently active database
            if self.current_database == command.database_name:
                self.current_database = None
            
            self.database_manager.drop_database(command.database_name)
            return f"Database '{command.database_name}' dropped successfully."
        except ValueError:
            raise DatabaseNotFoundError(command.database_name)
    
    def _execute_use_database(self, command: UseDatabaseCommand) -> str:
        """Execute USE DATABASE command."""
        if not self.database_manager.database_exists(command.database_name):
            raise DatabaseNotFoundError(command.database_name)
        
        self.current_database = command.database_name
        return f"Using database '{command.database_name}'."
    
    def _execute_show_databases(self, command: ShowDatabasesCommand) -> List[Dict[str, str]]:
        """Execute SHOW DATABASES command."""
        databases = self.database_manager.list_databases()
        return [{'Database': db_name} for db_name in sorted(databases)]
    
    # Table Management Commands
    
    def _execute_create_table(self, command: CreateTableCommand, database: Database) -> str:
        """Execute CREATE TABLE command."""
        try:
            table = Table(command.table_name, command.columns)
            database.create_table(table)
            
            # Auto-save
            self.database_manager.save_database(self.current_database)
            
            return f"Table '{command.table_name}' created successfully."
        except ValueError as e:
            raise ExecutorError(str(e))
    
    def _execute_drop_table(self, command: DropTableCommand, database: Database) -> str:
        """Execute DROP TABLE command."""
        try:
            database.drop_table(command.table_name)
            
            # Auto-save
            self.database_manager.save_database(self.current_database)
            
            return f"Table '{command.table_name}' dropped successfully."
        except ValueError:
            raise TableNotFoundError(command.table_name)
    
    def _execute_show_tables(self, command: ShowTablesCommand, database: Database) -> List[Dict[str, str]]:
        """Execute SHOW TABLES command."""
        tables = database.list_tables()
        return [{'Table': table_name} for table_name in sorted(tables)]
    
    def _execute_describe_table(self, command: DescribeTableCommand, database: Database) -> List[Dict[str, str]]:
        """Execute DESCRIBE TABLE command."""
        try:
            table = database.get_table(command.table_name)
            
            result = []
            for col in table.columns:
                row = {
                    'Field': col.name,
                    'Type': col.data_type.value,
                    'Key': 'PRI' if col.is_primary_key else ('UNI' if col.is_unique else ''),
                }
                if col.foreign_key_table:
                    row['References'] = f"{col.foreign_key_table}({col.foreign_key_column})"
                result.append(row)
            
            return result
        except ValueError:
            raise TableNotFoundError(command.table_name)
    
    # Data Manipulation Commands
    
    def _execute_insert(self, command: InsertCommand, database: Database) -> str:
        """Execute INSERT command."""
        try:
            table = database.get_table(command.table_name)
        except ValueError:
            raise TableNotFoundError(command.table_name)
        
        try:
            # Build column-value mapping
            if command.columns:
                # INSERT with column specification
                column_names = command.columns
                
                # Validate that all specified columns exist
                table_columns = table.get_column_names()
                for col in column_names:
                    if col not in table_columns:
                        raise ExecutorError(f"ColumnNotFoundError: column '{col}' does not exist in table '{command.table_name}'")
                
                # Validate value count matches column count
                if len(command.values) != len(column_names):
                    raise ExecutorError(
                        f"Value count mismatch: expected {len(column_names)} values for columns {column_names}, "
                        f"got {len(command.values)} values"
                    )
                
                # Build values dict with only specified columns
                values_dict = {col: val for col, val in zip(column_names, command.values)}
                
                # Check if all columns are provided (for now, we require all columns)
                missing_cols = set(table_columns) - set(column_names)
                if missing_cols:
                    raise ExecutorError(f"Missing values for columns: {', '.join(missing_cols)}")
            else:
                # INSERT without column specification (use all columns in order)
                column_names = table.get_column_names()
                
                if len(command.values) != len(column_names):
                    raise ExecutorError(
                        f"Value count mismatch: expected {len(column_names)} values for columns {column_names}, "
                        f"got {len(command.values)} values"
                    )
                
                values_dict = {col: val for col, val in zip(column_names, command.values)}

            # Validate foreign key constraints before insert
            self._validate_foreign_keys(table, values_dict, database)

            # Insert row
            table.insert(values_dict)
            
            # Auto-save
            self.database_manager.save_database(self.current_database)
            
            return f"1 row inserted into '{command.table_name}'."
        
        except ValueError as e:
            # Convert constraint violations to proper error type
            error_msg = str(e)
            if 'constraint' in error_msg.lower() or 'unique' in error_msg.lower():
                raise ConstraintViolationError(error_msg)
            raise ExecutorError(error_msg)

    def _execute_select(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command."""
        if command.join_table:
            return self._execute_select_with_join(command, database)
        else:
            try:
                table = database.get_table(command.table_name)
                return table.select(command.columns, command.where_col, command.where_val)
            except ValueError as e:
                error_msg = str(e)
                if 'does not exist' in error_msg and 'table' in error_msg.lower():
                    raise TableNotFoundError(command.table_name)
                raise ExecutorError(error_msg)
    
    def _execute_select_with_join(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command with INNER JOIN."""
        try:
            # Get both tables
            left_table = database.get_table(command.table_name)
            right_table = database.get_table(command.join_table)
        except ValueError:
            # Determine which table doesn't exist
            try:
                database.get_table(command.table_name)
            except ValueError:
                raise TableNotFoundError(command.table_name)
            raise TableNotFoundError(command.join_table)
        
        # Parse join columns (format: table.column)
        left_join_parts = command.join_left_col.split('.')
        right_join_parts = command.join_right_col.split('.')
        
        if len(left_join_parts) != 2 or len(right_join_parts) != 2:
            raise ExecutorError("JOIN condition must use table.column format")
        
        left_table_name, left_col_name = left_join_parts
        right_table_name, right_col_name = right_join_parts
        
        # Validate table names
        if left_table_name != command.table_name:
            raise ExecutorError(f"Left join table '{left_table_name}' does not match FROM table '{command.table_name}'")
        if right_table_name != command.join_table:
            raise ExecutorError(f"Right join table '{right_table_name}' does not match JOIN table '{command.join_table}'")
        
        # Validate columns exist
        if left_col_name not in left_table.schema:
            raise ExecutorError(f"ColumnNotFoundError: column '{left_col_name}' does not exist in table '{left_table_name}'")
        if right_col_name not in right_table.schema:
            raise ExecutorError(f"ColumnNotFoundError: column '{right_col_name}' does not exist in table '{right_table_name}'")
        
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
                                    raise ExecutorError(f"ColumnNotFoundError: column '{col}' not found in join result")
                            else:
                                # Try to find column in either table
                                left_key = f"{left_table_name}.{col}"
                                right_key = f"{right_table_name}.{col}"
                                
                                if left_key in joined_row:
                                    projected_row[col] = joined_row[left_key]
                                elif right_key in joined_row:
                                    projected_row[col] = joined_row[right_key]
                                else:
                                    raise ExecutorError(f"ColumnNotFoundError: column '{col}' not found in join result")
                        result.append(projected_row)
                    else:
                        result.append(joined_row)
        
        return result
    
    def _execute_update(self, command: UpdateCommand, database: Database) -> str:
        """Execute UPDATE command."""
        try:
            table = database.get_table(command.table_name)
        except ValueError:
            raise TableNotFoundError(command.table_name)

        try:
            # Validate foreign key constraint if updating a FK column
            for col in table.columns:
                if col.name == command.set_col and col.foreign_key_table:
                    # Create a temporary dict with just the FK column for validation
                    temp_values = {command.set_col: command.set_val}
                    self._validate_foreign_keys(table, temp_values, database)
                    break

            count = table.update(command.set_col, command.set_val, command.where_col, command.where_val)
            
            # Auto-save
            self.database_manager.save_database(self.current_database)
            
            return f"{count} row(s) updated in '{command.table_name}'."
        
        except ValueError as e:
            error_msg = str(e)
            if 'constraint' in error_msg.lower() or 'unique' in error_msg.lower():
                raise ConstraintViolationError(error_msg)
            raise ExecutorError(error_msg)
    
    def _execute_delete(self, command: DeleteCommand, database: Database) -> str:
        """Execute DELETE command."""
        try:
            table = database.get_table(command.table_name)
        except ValueError:
            raise TableNotFoundError(command.table_name)
        
        try:
            count = table.delete(command.where_col, command.where_val)
            
            # Auto-save
            self.database_manager.save_database(self.current_database)
            
            return f"{count} row(s) deleted from '{command.table_name}'."
        
        except ValueError as e:
            raise ExecutorError(str(e))
