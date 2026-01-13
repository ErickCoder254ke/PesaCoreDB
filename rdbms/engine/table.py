"""Table structure with schema, constraints, and operations."""

from typing import Any, Dict, List, Optional, Set
from .row import Row, DataType
from .index import Index


class ColumnDefinition:
    """Definition of a table column."""

    def __init__(self, name: str, data_type: DataType, is_primary_key: bool = False, is_unique: bool = False, foreign_key_table: Optional[str] = None, foreign_key_column: Optional[str] = None):
        self.name = name
        self.data_type = data_type
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique
        self.foreign_key_table = foreign_key_table
        self.foreign_key_column = foreign_key_column
    
    def __repr__(self) -> str:
        flags = []
        if self.is_primary_key:
            flags.append("PRIMARY KEY")
        if self.is_unique:
            flags.append("UNIQUE")
        if self.foreign_key_table:
            flags.append(f"REFERENCES {self.foreign_key_table}({self.foreign_key_column})")
        flag_str = " " + " ".join(flags) if flags else ""
        return f"{self.name} {self.data_type.value}{flag_str}"


class Table:
    """Represents a table with schema, data, and indexes."""
    
    def __init__(self, name: str, columns: List[ColumnDefinition]):
        """Initialize a table.
        
        Args:
            name: Table name
            columns: List of column definitions
        
        Raises:
            ValueError: If schema validation fails
        """
        self.name = name
        self.columns = columns
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
    
    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a row into the table.
        
        Args:
            values: Column name to value mapping
        
        Returns:
            Index of the inserted row
        
        Raises:
            ValueError: If constraints are violated
        """
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
            ValueError: If column is invalid
        """
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
