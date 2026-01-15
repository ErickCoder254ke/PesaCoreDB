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

    def _apply_column_aliases(self, rows: List[Dict[str, Any]], column_aliases: Dict[str, str]) -> List[Dict[str, Any]]:
        """Apply column aliases to result rows.

        Args:
            rows: List of result rows
            column_aliases: Dict mapping original column name to alias

        Returns:
            List of rows with aliased column names
        """
        if not column_aliases or not rows:
            return rows

        aliased_rows = []
        for row in rows:
            aliased_row = {}
            for col_name, value in row.items():
                # Use alias if available, otherwise keep original name
                aliased_col_name = column_aliases.get(col_name, col_name)
                aliased_row[aliased_col_name] = value
            aliased_rows.append(aliased_row)

        return aliased_rows

    def _execute_select(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command."""
        if command.join_table:
            # Check if this query also has aggregates
            if command.aggregates:
                raise ExecutorError(
                    "Aggregate functions with JOIN queries are not yet supported. "
                    "Workaround: Use separate queries or compute aggregates in your application. "
                    "Example: SELECT COUNT(*) FROM (SELECT * FROM table1 JOIN table2 ...) is not supported."
                )
            return self._execute_select_with_join(command, database)
        else:
            try:
                table = database.get_table(command.table_name)

                # Check if this is an aggregate query
                if command.aggregates:
                    return self._execute_select_with_aggregates(command, table)

                # Use new expression-based WHERE if available, otherwise fall back to legacy
                if command.where_clause:
                    # Get all rows first
                    all_rows = table.select(command.columns)

                    # Filter rows using expression
                    filtered_rows = []
                    for row in all_rows:
                        try:
                            if command.where_clause.evaluate(row):
                                filtered_rows.append(row)
                        except ValueError as e:
                            # Column not found in row
                            raise ExecutorError(str(e))

                    result = filtered_rows
                else:
                    # Legacy: simple equality WHERE or no WHERE
                    result = table.select(command.columns, command.where_col, command.where_val)

                # Apply ORDER BY if specified
                if command.order_by:
                    result = self._apply_order_by(result, command.order_by)

                # Apply DISTINCT if specified
                if command.distinct:
                    result = self._apply_distinct(result)

                # Apply OFFSET and LIMIT
                result = self._apply_limit_offset(result, command.limit, command.offset)

                # Apply column aliases if specified
                if command.column_aliases:
                    result = self._apply_column_aliases(result, command.column_aliases)

                return result

            except ValueError as e:
                error_msg = str(e)
                if 'does not exist' in error_msg and 'table' in error_msg.lower():
                    raise TableNotFoundError(command.table_name)
                raise ExecutorError(error_msg)
    
    def _execute_select_with_join(self, command: SelectCommand, database: Database) -> List[Dict[str, Any]]:
        """Execute SELECT command with JOIN (supports INNER, LEFT, RIGHT, FULL OUTER)."""
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

        # Get all rows from both tables
        left_rows = left_table.select()
        right_rows = right_table.select()

        # Track which rows have been matched (for outer joins)
        matched_left_indices = set()
        matched_right_indices = set()

        # Perform join based on join type
        result = []
        join_type = command.join_type.upper()

        # First pass: Find all matches
        for left_idx, left_row in enumerate(left_rows):
            left_join_value = left_row[left_col_name]
            has_match = False

            for right_idx, right_row in enumerate(right_rows):
                right_join_value = right_row[right_col_name]

                if left_join_value == right_join_value:
                    has_match = True
                    matched_left_indices.add(left_idx)
                    matched_right_indices.add(right_idx)

                    # Create joined row with table prefixes
                    joined_row = self._create_joined_row(
                        left_row, right_row,
                        left_table_name, right_table_name,
                        command.columns
                    )
                    result.append(joined_row)

            # LEFT or FULL OUTER JOIN: Include unmatched left rows with NULL for right columns
            if not has_match and join_type in ('LEFT', 'FULL'):
                joined_row = self._create_joined_row(
                    left_row, None,
                    left_table_name, right_table_name,
                    command.columns
                )
                result.append(joined_row)

        # RIGHT or FULL OUTER JOIN: Include unmatched right rows with NULL for left columns
        if join_type in ('RIGHT', 'FULL'):
            for right_idx, right_row in enumerate(right_rows):
                if right_idx not in matched_right_indices:
                    joined_row = self._create_joined_row(
                        None, right_row,
                        left_table_name, right_table_name,
                        command.columns
                    )
                    result.append(joined_row)

        # Apply ORDER BY if specified
        if command.order_by:
            result = self._apply_order_by(result, command.order_by)

        # Apply DISTINCT if specified
        if command.distinct:
            result = self._apply_distinct(result)

        # Apply OFFSET and LIMIT
        result = self._apply_limit_offset(result, command.limit, command.offset)

        return result

    def _create_joined_row(self, left_row: Optional[Dict[str, Any]], right_row: Optional[Dict[str, Any]],
                          left_table_name: str, right_table_name: str,
                          columns: Optional[List[str]]) -> Dict[str, Any]:
        """Create a joined row from left and right rows (handles NULL for outer joins).

        Args:
            left_row: Left table row (None for unmatched in RIGHT JOIN)
            right_row: Right table row (None for unmatched in LEFT JOIN)
            left_table_name: Name of left table
            right_table_name: Name of right table
            columns: List of columns to project (None for all columns)

        Returns:
            Joined row dictionary
        """
        # Build full joined row with table prefixes
        joined_row = {}

        if left_row:
            for col, val in left_row.items():
                joined_row[f"{left_table_name}.{col}"] = val
        else:
            # Fill with NULLs for unmatched left row
            # We don't know the columns, but we'll handle this in projection
            pass

        if right_row:
            for col, val in right_row.items():
                joined_row[f"{right_table_name}.{col}"] = val
        else:
            # Fill with NULLs for unmatched right row
            pass

        # Project requested columns
        if columns:
            projected_row = {}
            for col in columns:
                # Check if column has table prefix
                if '.' in col:
                    if col in joined_row:
                        projected_row[col] = joined_row[col]
                    else:
                        # Column not found - set to NULL (for outer join)
                        projected_row[col] = None
                else:
                    # Try to find column in either table
                    left_key = f"{left_table_name}.{col}"
                    right_key = f"{right_table_name}.{col}"

                    if left_key in joined_row:
                        projected_row[col] = joined_row[left_key]
                    elif right_key in joined_row:
                        projected_row[col] = joined_row[right_key]
                    else:
                        # Column not found - set to NULL (for outer join)
                        projected_row[col] = None
            return projected_row
        else:
            return joined_row

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

            # Use new expression-based WHERE if available
            if command.where_clause:
                # Get all rows and filter based on expression
                all_rows = table.select()
                count = 0

                for i, row in enumerate(all_rows):
                    try:
                        if command.where_clause.evaluate(row):
                            # Get the primary key column value to identify the row
                            pk_col = table.primary_key_column
                            pk_val = row[pk_col]

                            # Update using primary key
                            table.update(command.set_col, command.set_val, pk_col, pk_val)
                            count += 1
                    except ValueError as e:
                        raise ExecutorError(str(e))
            else:
                # Legacy: simple equality WHERE or no WHERE
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
            # Use new expression-based WHERE if available
            if command.where_clause:
                # Get all rows and filter based on expression
                all_rows = table.select()
                count = 0
                rows_to_delete = []

                # Find all rows that match the WHERE clause
                for row in all_rows:
                    try:
                        if command.where_clause.evaluate(row):
                            # Get the primary key column value to identify the row
                            pk_col = table.primary_key_column
                            pk_val = row[pk_col]
                            rows_to_delete.append(pk_val)
                    except ValueError as e:
                        raise ExecutorError(str(e))

                # Delete rows using primary key (one at a time to maintain integrity)
                for pk_val in rows_to_delete:
                    pk_col = table.primary_key_column
                    table.delete(pk_col, pk_val)
                    count += 1
            else:
                # Legacy: simple equality WHERE or no WHERE
                count = table.delete(command.where_col, command.where_val)

            # Auto-save
            self.database_manager.save_database(self.current_database)

            return f"{count} row(s) deleted from '{command.table_name}'."

        except ValueError as e:
            raise ExecutorError(str(e))

    def _apply_order_by(self, rows: List[Dict[str, Any]], order_by: List[tuple]) -> List[Dict[str, Any]]:
        """Apply ORDER BY clause to result rows.

        Args:
            rows: List of row dictionaries to sort
            order_by: List of (column_name, direction) tuples

        Returns:
            Sorted list of rows

        Raises:
            ExecutorError: If column doesn't exist
        """
        if not rows or not order_by:
            return rows

        # Validate that all ORDER BY columns exist in the result
        for col_name, _ in order_by:
            if col_name not in rows[0]:
                raise ExecutorError(f"ColumnNotFoundError: column '{col_name}' not found in result set")

        # Sort by multiple columns (reverse order for stable sort)
        sorted_rows = rows[:]
        for col_name, direction in reversed(order_by):
            reverse = (direction == 'DESC')

            # Sort with None values at the end
            sorted_rows.sort(
                key=lambda row: (row[col_name] is None, row[col_name]),
                reverse=reverse
            )

        return sorted_rows

    def _apply_distinct(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply DISTINCT to remove duplicate rows.

        Args:
            rows: List of row dictionaries

        Returns:
            List of unique rows (order preserved)
        """
        if not rows:
            return rows

        seen = set()
        unique_rows = []

        for row in rows:
            # Convert row to tuple of items for hashing
            # Sort items to ensure consistent ordering
            row_tuple = tuple(sorted(row.items()))

            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_rows.append(row)

        return unique_rows

    def _apply_limit_offset(self, rows: List[Dict[str, Any]], limit: Optional[int], offset: Optional[int]) -> List[Dict[str, Any]]:
        """Apply LIMIT and OFFSET to result rows.

        Args:
            rows: List of row dictionaries
            limit: Maximum number of rows to return (None = no limit)
            offset: Number of rows to skip (None = no offset)

        Returns:
            Sliced list of rows
        """
        if not rows:
            return rows

        start = offset if offset else 0
        end = start + limit if limit else None

        return rows[start:end]

    def _execute_select_with_aggregates(self, command: SelectCommand, table: Table) -> List[Dict[str, Any]]:
        """Execute SELECT with aggregate functions (COUNT, SUM, AVG, MIN, MAX).

        Args:
            command: SelectCommand with aggregates
            table: Table to query

        Returns:
            List of aggregated result rows
        """
        # Get all rows from table
        all_rows = table.select()

        # Apply WHERE clause to filter rows BEFORE aggregation
        if command.where_clause:
            filtered_rows = []
            for row in all_rows:
                try:
                    if command.where_clause.evaluate(row):
                        filtered_rows.append(row)
                except ValueError as e:
                    raise ExecutorError(str(e))
            all_rows = filtered_rows

        # Check if we have GROUP BY
        if command.group_by:
            # Group rows by GROUP BY columns
            groups = self._group_rows(all_rows, command.group_by)

            # Aggregate each group
            result = []
            for group_key, group_rows in groups.items():
                row_result = {}

                # Add GROUP BY columns to result
                for i, col_name in enumerate(command.group_by):
                    row_result[col_name] = group_key[i]

                # Calculate aggregates for this group
                for alias, agg_expr in command.aggregates:
                    try:
                        agg_value = agg_expr.aggregate(group_rows)
                        row_result[alias] = agg_value
                    except ValueError as e:
                        raise ExecutorError(str(e))

                # Add non-aggregate columns (should be in GROUP BY)
                if command.columns:
                    for col_name in command.columns:
                        if col_name not in row_result and col_name not in command.group_by:
                            raise ExecutorError(
                                f"Column '{col_name}' must appear in GROUP BY clause or be used in an aggregate function"
                            )
                        # Column already added from GROUP BY

                result.append(row_result)

            # Apply HAVING clause to filter groups
            if command.having_clause:
                filtered_result = []
                for row in result:
                    try:
                        if command.having_clause.evaluate(row):
                            filtered_result.append(row)
                    except ValueError as e:
                        raise ExecutorError(str(e))
                result = filtered_result
        else:
            # No GROUP BY - aggregate over all rows
            row_result = {}

            # Calculate aggregates
            for alias, agg_expr in command.aggregates:
                try:
                    agg_value = agg_expr.aggregate(all_rows)
                    row_result[alias] = agg_value
                except ValueError as e:
                    raise ExecutorError(str(e))

            # Add non-aggregate columns (if any - this is technically an error in SQL)
            if command.columns:
                if len(all_rows) > 0:
                    # Take values from first row (arbitrary choice - real SQL would error)
                    for col_name in command.columns:
                        row_result[col_name] = all_rows[0].get(col_name)
                else:
                    for col_name in command.columns:
                        row_result[col_name] = None

            result = [row_result]

        # Apply ORDER BY if specified
        if command.order_by:
            result = self._apply_order_by(result, command.order_by)

        # Apply DISTINCT if specified
        if command.distinct:
            result = self._apply_distinct(result)

        # Apply OFFSET and LIMIT
        result = self._apply_limit_offset(result, command.limit, command.offset)

        # Apply column aliases if specified
        if command.column_aliases:
            result = self._apply_column_aliases(result, command.column_aliases)

        return result

    def _group_rows(self, rows: List[Dict[str, Any]], group_by: List[str]) -> Dict[tuple, List[Dict[str, Any]]]:
        """Group rows by specified columns.

        Args:
            rows: List of row dictionaries
            group_by: List of column names to group by

        Returns:
            Dictionary mapping group_key tuple to list of rows in that group

        Raises:
            ExecutorError: If a GROUP BY column doesn't exist
        """
        groups = {}

        for row in rows:
            # Build group key from GROUP BY columns
            group_key = []
            for col_name in group_by:
                if col_name not in row:
                    raise ExecutorError(f"Column '{col_name}' in GROUP BY does not exist")
                group_key.append(row[col_name])

            group_key = tuple(group_key)

            if group_key not in groups:
                groups[group_key] = []

            groups[group_key].append(row)

        return groups
