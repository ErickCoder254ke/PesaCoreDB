"""Database management."""

from typing import Dict, Optional
from .table import Table


class Database:
    """In-memory relational database."""
    
    def __init__(self):
        """Initialize an empty database."""
        self.tables: Dict[str, Table] = {}
    
    def create_table(self, table: Table):
        """Create a new table in the database.
        
        Args:
            table: Table to create
        
        Raises:
            ValueError: If table already exists
        """
        if table.name in self.tables:
            raise ValueError(f"Table '{table.name}' already exists")
        self.tables[table.name] = table
    
    def get_table(self, table_name: str) -> Table:
        """Get a table by name.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Table object
        
        Raises:
            ValueError: If table does not exist
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        return self.tables[table_name]
    
    def drop_table(self, table_name: str):
        """Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
        
        Raises:
            ValueError: If table does not exist
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        del self.tables[table_name]
    
    def list_tables(self) -> list:
        """List all table names in the database."""
        return list(self.tables.keys())
    
    def __repr__(self) -> str:
        return f"Database(tables={len(self.tables)})"
