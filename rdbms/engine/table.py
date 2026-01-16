"""Table structure with schema, constraints, and operations."""

from typing import Any, Dict, List, Optional, Set
from .row import Row, DataType
from .index import Index


class ColumnDefinition:
    """Definition of a table column."""

    def __init__(self, name: str, data_type: DataType, is_primary_key: bool = False, is_unique: bool = False,
                 foreign_key_table: Optional[str] = None, foreign_key_column: Optional[str] = None,
                 on_delete: Optional[str] = None, on_update: Optional[str] = None):
        self.name = name
        self.data_type = data_type
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique
        self.foreign_key_table = foreign_key_table
        self.foreign_key_column = foreign_key_column
        # FK actions: CASCADE, SET NULL, RESTRICT, NO ACTION
        # Default to RESTRICT (prevent delete/update if referenced)
        self.on_delete = on_delete.upper() if on_delete else 'RESTRICT'
        self.on_update = on_update.upper() if on_update else 'RESTRICT'

    def __repr__(self) -> str:
        flags = []
        if self.is_primary_key:
            flags.append("PRIMARY KEY")
        if self.is_unique:
            flags.append("UNIQUE")
        if self.foreign_key_table:
            fk_str = f"REFERENCES {self.foreign_key_table}({self.foreign_key_column})"
            if self.on_delete != 'RESTRICT':
                fk_str += f" ON DELETE {self.on_delete}"
            if self.on_update != 'RESTRICT':
                fk_str += f" ON UPDATE {self.on_update}"
            flags.append(fk_str)
        flag_str = " " + " ".join(flags) if flags else ""
        return f"{self.name} {self.data_type.value}{flag_str}"


class Table:
    """Represents a table with schema, data, and indexes."""

    def __init__(self, name: str, columns: List[ColumnDefinition], database=None):
        """Initialize a table.

        Args:
            name: Table name
            columns: List of column definitions
            database: Reference to parent Database instance (for FK validation)

        Raises:
            ValueError: If schema validation fails
        """
        self.name = name
        self.columns = columns
        self.database = database  # Store reference to parent database
        self._validate_schema()

        # Build schema dict
        self.schema: Dict[str, DataType] = {col.name: col.data_type for col in columns}

        # Identify constraints
        self.primary_key_column: Optional[str] = None
        self.unique_columns: Set[str] = set()

        for col in columns:
            if col.is_primary_key:
                self.primary_key_column = col.name
                self.unique_columns.add(col.name)
            elif col.is_unique:
                self.unique_columns.add(col.name)

        # Data storage: list of rows
        self.rows: List[Row] = []

        # Indexes: column name -> Index
        self.indexes: Dict[str, Index] = {}

        # Create indexes for primary key and unique columns
        if self.primary_key_column:
            self.indexes[self.primary_key_column] = Index(self.primary_key_column, is_unique=True)

        for col_name in self.unique_columns:
            if col_name not in self.indexes:
                self.indexes[col_name] = Index(col_name, is_unique=True)

        # Create indexes for foreign key columns for better join performance
        for col in columns:
            if col.foreign_key_table and col.name not in self.indexes:
                self.indexes[col.name] = Index(col.name, is_unique=False)
    
    def _validate_schema(self):
        """Validate table schema.

        Raises:
            ValueError: If schema is invalid
        """
        if not self.columns:
            raise ValueError("Table must have at least one column")

        # Check for duplicate column names
        col_names = [col.name for col in self.columns]
        if len(col_names) != len(set(col_names)):
            raise ValueError("Duplicate column names are not allowed")

        # Check for exactly one primary key
        primary_keys = [col for col in self.columns if col.is_primary_key]
        if len(primary_keys) == 0:
            raise ValueError("Table must have exactly one PRIMARY KEY column")
        if len(primary_keys) > 1:
            raise ValueError("Table can have only one PRIMARY KEY column")

    def check_referential_integrity_for_delete(self, where_col: str, where_val: Any) -> None:
        """Check and enforce referential integrity for delete operations.

        This method handles ON DELETE actions: CASCADE, SET NULL, RESTRICT, NO ACTION.

        Args:
            where_col: Column name being used for deletion
            where_val: Value being deleted

        Raises:
            ValueError: If deletion would violate referential integrity (RESTRICT)
        """
        if self.database is None:
            return

        # Check if this is a primary key column being deleted
        if where_col != self.primary_key_column:
            return

        # Look for tables that reference this table
        for table_name in self.database.list_tables():
            if table_name == self.name:
                continue

            other_table = self.database.get_table(table_name)
            for col in other_table.columns:
                if col.foreign_key_table == self.name and col.foreign_key_column == where_col:
                    # This table references us, check if there are any rows with this FK value
                    referencing_rows = other_table.select(
                        columns=[other_table.primary_key_column, col.name],
                        where_col=col.name,
                        where_val=where_val
                    )

                    if referencing_rows:
                        # Handle ON DELETE action
                        on_delete_action = col.on_delete

                        if on_delete_action == 'CASCADE':
                            # Delete all referencing rows
                            for ref_row in referencing_rows:
                                pk_val = ref_row[other_table.primary_key_column]
                                # Recursively check and handle cascades
                                other_table.check_referential_integrity_for_delete(
                                    other_table.primary_key_column, pk_val
                                )
                                # Delete the row
                                other_table.delete(other_table.primary_key_column, pk_val)

                        elif on_delete_action == 'SET NULL':
                            # Set the FK column to NULL for all referencing rows
                            for ref_row in referencing_rows:
                                pk_val = ref_row[other_table.primary_key_column]
                                other_table.update(col.name, None, other_table.primary_key_column, pk_val)

                        elif on_delete_action in ('RESTRICT', 'NO ACTION'):
                            # Prevent deletion (default behavior)
                            raise ValueError(
                                f"Cannot delete row from '{self.name}' where {where_col}={where_val}: "
                                f"Referenced by {len(referencing_rows)} row(s) in table '{table_name}.{col.name}' "
                                f"(ON DELETE {on_delete_action}). "
                                f"Delete or update referencing rows first, or use ON DELETE CASCADE/SET NULL."
                            )

    def validate_foreign_keys(self, values: Dict[str, Any]) -> None:
        """Validate foreign key constraints.

        Args:
            values: Column name to value mapping

        Raises:
            ValueError: If foreign key constraint is violated
        """
        if self.database is None:
            # Can't validate without database reference
            return

        for col in self.columns:
            if col.foreign_key_table and col.name in values:
                fk_value = values[col.name]

                # Skip validation for NULL values (if supported in future)
                if fk_value is None:
                    continue

                # Get the referenced table from the same database
                try:
                    ref_table = self.database.get_table(col.foreign_key_table)

                    # Check if the foreign key value exists in the referenced table
                    ref_col = col.foreign_key_column
                    matching_rows = ref_table.select(
                        columns=[ref_col],
                        where_col=ref_col,
                        where_val=fk_value
                    )

                    if not matching_rows:
                        raise ValueError(
                            f"Foreign key constraint violation: "
                            f"Value '{fk_value}' in column '{col.name}' "
                            f"does not exist in table '{col.foreign_key_table}.{ref_col}'"
                        )
                except ValueError as e:
                    # Re-raise FK violations
                    if "Foreign key constraint violation" in str(e):
                        raise
                    # Table doesn't exist - this is also a violation
                    raise ValueError(
                        f"Foreign key constraint error: "
                        f"Referenced table '{col.foreign_key_table}' does not exist"
                    )
    
    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a row into the table.

        Args:
            values: Column name to value mapping

        Returns:
            Index of the inserted row

        Raises:
            ValueError: If constraints are violated
        """
        # Validate foreign key constraints first
        self.validate_foreign_keys(values)

        # Create and validate row
        row = Row(self.schema, values)

        # Check constraints before inserting
        row_index = len(self.rows)
        for col_name, index in self.indexes.items():
            value = row.get(col_name)
            index.insert(value, row_index)

        # Insert row
        self.rows.append(row)
        return row_index
    
    def select(self, columns: Optional[List[str]] = None, where_col: Optional[str] = None, 
               where_val: Any = None) -> List[Dict[str, Any]]:
        """Select rows from the table.
        
        Args:
            columns: List of column names to return (None = all columns)
            where_col: Column name for WHERE clause
            where_val: Value for WHERE clause
        
        Returns:
            List of row dictionaries
        
        Raises:
            ValueError: If column names are invalid
        """
        # Validate columns
        if columns is not None:
            for col in columns:
                if col not in self.schema:
                    raise ValueError(f"Column '{col}' does not exist in table '{self.name}'")
        else:
            columns = list(self.schema.keys())
        
        # Find matching rows
        matching_rows = []
        
        if where_col is not None:
            if where_col not in self.schema:
                raise ValueError(f"Column '{where_col}' does not exist in table '{self.name}'")
            
            # Use index if available
            if where_col in self.indexes:
                row_indices = self.indexes[where_col].lookup(where_val)
                matching_rows = [self.rows[i] for i in row_indices]
            else:
                # Full table scan
                matching_rows = [row for row in self.rows if row.get(where_col) == where_val]
        else:
            matching_rows = self.rows
        
        # Project columns
        result = []
        for row in matching_rows:
            row_dict = {col: row.get(col) for col in columns}
            result.append(row_dict)
        
        return result
    
    def check_referential_integrity_for_update(self, set_col: str, old_val: Any, new_val: Any) -> None:
        """Check and enforce referential integrity for update operations.

        This method handles ON UPDATE actions: CASCADE, SET NULL, RESTRICT, NO ACTION.

        Args:
            set_col: Column being updated
            old_val: Old value before update
            new_val: New value after update

        Raises:
            ValueError: If update would violate referential integrity (RESTRICT)
        """
        if self.database is None:
            return

        # Only check if updating a primary key or unique column
        if set_col != self.primary_key_column and set_col not in self.unique_columns:
            return

        # Look for tables that reference this table
        for table_name in self.database.list_tables():
            if table_name == self.name:
                continue

            other_table = self.database.get_table(table_name)
            for col in other_table.columns:
                if col.foreign_key_table == self.name and col.foreign_key_column == set_col:
                    # This table references us, check if there are any rows with the old FK value
                    referencing_rows = other_table.select(
                        columns=[other_table.primary_key_column, col.name],
                        where_col=col.name,
                        where_val=old_val
                    )

                    if referencing_rows:
                        # Handle ON UPDATE action
                        on_update_action = col.on_update

                        if on_update_action == 'CASCADE':
                            # Update all referencing rows with the new value
                            for ref_row in referencing_rows:
                                pk_val = ref_row[other_table.primary_key_column]
                                other_table.update(col.name, new_val, other_table.primary_key_column, pk_val)

                        elif on_update_action == 'SET NULL':
                            # Set the FK column to NULL for all referencing rows
                            for ref_row in referencing_rows:
                                pk_val = ref_row[other_table.primary_key_column]
                                other_table.update(col.name, None, other_table.primary_key_column, pk_val)

                        elif on_update_action in ('RESTRICT', 'NO ACTION'):
                            # Prevent update (default behavior)
                            raise ValueError(
                                f"Cannot update '{self.name}.{set_col}' from {old_val} to {new_val}: "
                                f"Referenced by {len(referencing_rows)} row(s) in table '{table_name}.{col.name}' "
                                f"(ON UPDATE {on_update_action}). "
                                f"Update or delete referencing rows first, or use ON UPDATE CASCADE/SET NULL."
                            )

    def update(self, set_col: str, set_val: Any, where_col: Optional[str] = None,
               where_val: Any = None) -> int:
        """Update rows in the table.

        Args:
            set_col: Column to update
            set_val: New value
            where_col: Column name for WHERE clause
            where_val: Value for WHERE clause

        Returns:
            Number of rows updated

        Raises:
            ValueError: If constraints are violated
        """
        if set_col not in self.schema:
            raise ValueError(f"Column '{set_col}' does not exist in table '{self.name}'")

        # Find matching rows
        if where_col is not None:
            if where_col not in self.schema:
                raise ValueError(f"Column '{where_col}' does not exist in table '{self.name}'")

            if where_col in self.indexes:
                row_indices = self.indexes[where_col].lookup(where_val)
            else:
                row_indices = [i for i, row in enumerate(self.rows) if row.get(where_col) == where_val]
        else:
            row_indices = list(range(len(self.rows)))

        # Update rows
        updated_count = 0
        for row_idx in row_indices:
            row = self.rows[row_idx]
            old_value = row.get(set_col)

            # Check referential integrity for updates to PK/unique columns
            if old_value != set_val:
                self.check_referential_integrity_for_update(set_col, old_value, set_val)

            # Update indexes if column is indexed
            if set_col in self.indexes:
                self.indexes[set_col].update(old_value, set_val, row_idx)

            # Update row
            row.set(set_col, set_val)
            updated_count += 1

        return updated_count
    
    def delete(self, where_col: Optional[str] = None, where_val: Any = None) -> int:
        """Delete rows from the table.

        Args:
            where_col: Column name for WHERE clause
            where_val: Value for WHERE clause

        Returns:
            Number of rows deleted

        Raises:
            ValueError: If column is invalid or referential integrity would be violated
        """
        # Check referential integrity before deletion
        if where_col is not None and where_val is not None:
            self.check_referential_integrity_for_delete(where_col, where_val)

        # Find matching rows
        if where_col is not None:
            if where_col not in self.schema:
                raise ValueError(f"Column '{where_col}' does not exist in table '{self.name}'")

            if where_col in self.indexes:
                row_indices = self.indexes[where_col].lookup(where_val)
            else:
                row_indices = [i for i, row in enumerate(self.rows) if row.get(where_col) == where_val]
        else:
            row_indices = list(range(len(self.rows)))
        
        # Delete in reverse order to maintain indices
        deleted_count = 0
        for row_idx in sorted(row_indices, reverse=True):
            row = self.rows[row_idx]
            
            # Remove from indexes
            for col_name, index in self.indexes.items():
                value = row.get(col_name)
                index.remove(value, row_idx)
            
            # Remove row
            self.rows.pop(row_idx)
            deleted_count += 1
        
        # Rebuild indexes after deletion (indices have changed)
        if deleted_count > 0:
            self._rebuild_indexes()
        
        return deleted_count
    
    def _rebuild_indexes(self):
        """Rebuild all indexes after row deletion."""
        for index in self.indexes.values():
            index.clear()
        
        for row_idx, row in enumerate(self.rows):
            for col_name, index in self.indexes.items():
                value = row.get(col_name)
                index.insert(value, row_idx)
    
    def get_column_names(self) -> List[str]:
        """Get list of column names."""
        return list(self.schema.keys())
    
    def __repr__(self) -> str:
        return f"Table({self.name}, columns={len(self.columns)}, rows={len(self.rows)})"
