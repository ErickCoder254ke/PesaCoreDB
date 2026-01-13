"""Hash-based indexing for fast lookups."""

from typing import Any, Dict, List, Optional


class Index:
    """Hash-based index for a column."""
    
    def __init__(self, column_name: str, is_unique: bool = False):
        """Initialize an index.
        
        Args:
            column_name: Name of the indexed column
            is_unique: Whether the index enforces uniqueness
        """
        self.column_name = column_name
        self.is_unique = is_unique
        # Hash map: value -> list of row indices
        self._index: Dict[Any, List[int]] = {}
    
    def insert(self, value: Any, row_index: int):
        """Insert a value into the index.
        
        Args:
            value: Value to index
            row_index: Index of the row in the table
        
        Raises:
            ValueError: If unique constraint is violated
        """
        if self.is_unique and value in self._index:
            raise ValueError(
                f"UNIQUE constraint violation: Value '{value}' already exists in column '{self.column_name}'"
            )
        
        if value not in self._index:
            self._index[value] = []
        self._index[value].append(row_index)
    
    def lookup(self, value: Any) -> List[int]:
        """Look up row indices for a value.
        
        Args:
            value: Value to look up
        
        Returns:
            List of row indices with this value
        """
        return self._index.get(value, [])
    
    def remove(self, value: Any, row_index: int):
        """Remove a value from the index.
        
        Args:
            value: Value to remove
            row_index: Row index to remove
        """
        if value in self._index:
            if row_index in self._index[value]:
                self._index[value].remove(row_index)
            if not self._index[value]:
                del self._index[value]
    
    def update(self, old_value: Any, new_value: Any, row_index: int):
        """Update index when a value changes.
        
        Args:
            old_value: Previous value
            new_value: New value
            row_index: Row index being updated
        
        Raises:
            ValueError: If unique constraint is violated
        """
        if old_value != new_value:
            if self.is_unique and new_value in self._index:
                raise ValueError(
                    f"UNIQUE constraint violation: Value '{new_value}' already exists in column '{self.column_name}'"
                )
            self.remove(old_value, row_index)
            self.insert(new_value, row_index)
    
    def clear(self):
        """Clear all entries from the index."""
        self._index.clear()
    
    def __repr__(self) -> str:
        return f"Index(column={self.column_name}, unique={self.is_unique}, entries={len(self._index)})"
