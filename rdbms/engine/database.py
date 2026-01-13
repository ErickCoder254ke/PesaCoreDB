"""Database management."""

import json
from typing import Dict, Optional, Any, List
from .table import Table, ColumnDefinition
from .row import Row, DataType


class Database:
    """In-memory relational database with persistence."""

    def __init__(self, name: str = "default"):
        """Initialize an empty database.

        Args:
            name: Database name (used for persistence)
        """
        self.name = name
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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize database to dictionary.

        Returns:
            Dictionary representation of the database
        """
        tables_data = {}

        for table_name, table in self.tables.items():
            # Serialize columns
            columns_data = []
            for col in table.columns:
                col_data = {
                    'name': col.name,
                    'type': col.data_type.value,
                    'is_primary_key': col.is_primary_key,
                    'is_unique': col.is_unique
                }
                if col.foreign_key_table:
                    col_data['foreign_key_table'] = col.foreign_key_table
                    col_data['foreign_key_column'] = col.foreign_key_column
                columns_data.append(col_data)

            # Serialize rows
            rows_data = []
            for row in table.rows:
                rows_data.append(row.to_dict())

            tables_data[table_name] = {
                'columns': columns_data,
                'rows': rows_data
            }

        return {
            'name': self.name,
            'tables': tables_data
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Database':
        """Deserialize database from dictionary.

        Args:
            data: Dictionary representation of the database

        Returns:
            Database instance

        Raises:
            ValueError: If deserialization fails
        """
        db_name = data.get('name', 'default')
        db = Database(name=db_name)

        tables_data = data.get('tables', {})

        for table_name, table_data in tables_data.items():
            # Deserialize columns
            columns = []
            columns_data = table_data.get('columns', [])

            for col_data in columns_data:
                col = ColumnDefinition(
                    name=col_data['name'],
                    data_type=DataType.from_string(col_data['type']),
                    is_primary_key=col_data.get('is_primary_key', False),
                    is_unique=col_data.get('is_unique', False),
                    foreign_key_table=col_data.get('foreign_key_table'),
                    foreign_key_column=col_data.get('foreign_key_column')
                )
                columns.append(col)

            # Create table
            table = Table(table_name, columns)

            # Deserialize and insert rows
            rows_data = table_data.get('rows', [])
            for row_values in rows_data:
                # Insert without triggering uniqueness checks during load
                row = Row(table.schema, row_values)
                table.rows.append(row)

            # Rebuild indexes after loading all rows
            table._rebuild_indexes()

            # Add table to database
            db.tables[table_name] = table

        return db

    def save_to_disk(self, file_path: str):
        """Save database to disk as JSON.

        Args:
            file_path: Path to save the database file

        Raises:
            IOError: If file write fails
        """
        data = self.to_dict()

        # Write to temp file first, then rename (atomic operation)
        temp_path = f"{file_path}.tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Rename temp file to actual file (atomic on most systems)
            import os
            if os.path.exists(file_path):
                os.replace(temp_path, file_path)
            else:
                os.rename(temp_path, file_path)
        except Exception as e:
            # Clean up temp file if it exists
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Failed to save database to disk: {e}")

    @staticmethod
    def load_from_disk(file_path: str) -> 'Database':
        """Load database from disk.

        Args:
            file_path: Path to the database file

        Returns:
            Database instance

        Raises:
            IOError: If file read fails
            ValueError: If deserialization fails
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Database.from_dict(data)
        except FileNotFoundError:
            raise IOError(f"Database file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise IOError(f"Invalid database file format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load database: {e}")

    def __repr__(self) -> str:
        return f"Database(name='{self.name}', tables={len(self.tables)})"
