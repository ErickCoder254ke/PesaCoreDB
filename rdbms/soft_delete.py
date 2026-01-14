"""Soft delete functionality for tables."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from .engine.table import Table


class SoftDeleteMixin:
    """Mixin to add soft delete capability to tables.
    
    Usage:
        When creating a table that should support soft delete,
        include a 'deleted_at' column of type STRING (to store ISO timestamps).
        
        Soft-deleted rows will have a timestamp in deleted_at, active rows will have NULL.
    """
    
    @staticmethod
    def has_soft_delete(table: Table) -> bool:
        """Check if table supports soft delete.
        
        Args:
            table: Table to check
            
        Returns:
            True if table has a deleted_at column
        """
        return 'deleted_at' in table.schema
    
    @staticmethod
    def soft_delete(table: Table, where_col: str, where_val: Any) -> int:
        """Soft delete rows by setting deleted_at timestamp.
        
        Args:
            table: Table to delete from
            where_col: Column for WHERE clause
            where_val: Value for WHERE clause
            
        Returns:
            Number of rows soft-deleted
            
        Raises:
            ValueError: If table doesn't support soft delete
        """
        if not SoftDeleteMixin.has_soft_delete(table):
            raise ValueError(
                f"Table '{table.name}' does not support soft delete. "
                "Add a 'deleted_at STRING' column to enable soft delete."
            )
        
        # Get rows that match and aren't already deleted
        matching_rows = []
        for row in table.rows:
            if row.get(where_col) == where_val and row.get('deleted_at') is None:
                matching_rows.append(row)
        
        # Set deleted_at timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        count = 0
        for row in matching_rows:
            row.set('deleted_at', timestamp)
            count += 1
        
        return count
    
    @staticmethod
    def restore(table: Table, where_col: str, where_val: Any) -> int:
        """Restore soft-deleted rows by clearing deleted_at.
        
        Args:
            table: Table to restore in
            where_col: Column for WHERE clause
            where_val: Value for WHERE clause
            
        Returns:
            Number of rows restored
            
        Raises:
            ValueError: If table doesn't support soft delete
        """
        if not SoftDeleteMixin.has_soft_delete(table):
            raise ValueError(
                f"Table '{table.name}' does not support soft delete. "
                "Add a 'deleted_at STRING' column to enable soft delete."
            )
        
        # Get rows that match and are deleted
        matching_rows = []
        for row in table.rows:
            if row.get(where_col) == where_val and row.get('deleted_at') is not None:
                matching_rows.append(row)
        
        # Clear deleted_at
        count = 0
        for row in matching_rows:
            row.set('deleted_at', None)
            count += 1
        
        return count
    
    @staticmethod
    def select_with_soft_delete(
        table: Table, 
        columns: Optional[List[str]] = None,
        where_col: Optional[str] = None,
        where_val: Any = None,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Select rows with soft delete awareness.
        
        Args:
            table: Table to select from
            columns: Columns to return (None = all)
            where_col: Column for WHERE clause
            where_val: Value for WHERE clause
            include_deleted: Whether to include soft-deleted rows
            
        Returns:
            List of matching rows (excluding deleted by default)
        """
        # Use table's normal select
        all_rows = table.select(columns, where_col, where_val)
        
        # Filter out deleted rows unless requested
        if not include_deleted and SoftDeleteMixin.has_soft_delete(table):
            all_rows = [row for row in all_rows if row.get('deleted_at') is None]
        
        return all_rows
    
    @staticmethod
    def hard_delete(table: Table, where_col: str, where_val: Any) -> int:
        """Permanently delete rows (including soft-deleted ones).
        
        Args:
            table: Table to delete from
            where_col: Column for WHERE clause
            where_val: Value for WHERE clause
            
        Returns:
            Number of rows permanently deleted
        """
        # Use table's normal delete (hard delete)
        return table.delete(where_col, where_val)
    
    @staticmethod
    def count_deleted(table: Table) -> int:
        """Count soft-deleted rows in a table.
        
        Args:
            table: Table to count in
            
        Returns:
            Number of soft-deleted rows
            
        Raises:
            ValueError: If table doesn't support soft delete
        """
        if not SoftDeleteMixin.has_soft_delete(table):
            raise ValueError(
                f"Table '{table.name}' does not support soft delete."
            )
        
        count = 0
        for row in table.rows:
            if row.get('deleted_at') is not None:
                count += 1
        
        return count
    
    @staticmethod
    def purge_deleted(table: Table, older_than_days: int = 30) -> int:
        """Permanently delete rows that were soft-deleted more than N days ago.
        
        Args:
            table: Table to purge
            older_than_days: Delete rows soft-deleted this many days ago
            
        Returns:
            Number of rows permanently deleted
            
        Raises:
            ValueError: If table doesn't support soft delete
        """
        if not SoftDeleteMixin.has_soft_delete(table):
            raise ValueError(
                f"Table '{table.name}' does not support soft delete."
            )
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        # Find rows to purge
        rows_to_delete = []
        for i, row in enumerate(table.rows):
            deleted_at_str = row.get('deleted_at')
            if deleted_at_str:
                try:
                    deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
                    if deleted_at < cutoff_date:
                        rows_to_delete.append(i)
                except (ValueError, AttributeError):
                    # Invalid timestamp, skip
                    pass
        
        # Delete in reverse order to maintain indices
        count = 0
        for row_idx in sorted(rows_to_delete, reverse=True):
            row = table.rows[row_idx]
            
            # Remove from indexes
            for col_name, index in table.indexes.items():
                value = row.get(col_name)
                index.remove(value, row_idx)
            
            # Remove row
            table.rows.pop(row_idx)
            count += 1
        
        return count


# Convenience functions for direct use

def enable_soft_delete_on_table(table: Table) -> None:
    """Enable soft delete on an existing table by adding deleted_at column.
    
    Note: This should be done before any data is inserted.
    
    Args:
        table: Table to enable soft delete on
        
    Raises:
        ValueError: If table already has deleted_at column
    """
    if 'deleted_at' in table.schema:
        raise ValueError(f"Table '{table.name}' already has soft delete enabled")
    
    from .engine.row import DataType
    from .engine.table import ColumnDefinition
    
    # Add deleted_at column
    new_col = ColumnDefinition('deleted_at', DataType.STRING, is_primary_key=False, is_unique=False)
    table.columns.append(new_col)
    table.schema['deleted_at'] = DataType.STRING
    
    # Initialize deleted_at to None for all existing rows
    for row in table.rows:
        row.values['deleted_at'] = None
