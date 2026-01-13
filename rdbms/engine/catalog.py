"""Database catalog for managing multiple databases."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from .database import Database


class DatabaseManager:
    """Manages multiple named databases with persistence."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize database manager.
        
        Args:
            data_dir: Directory to store database files
        """
        self.databases: Dict[str, Database] = {}
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Metadata file to track database names
        self.metadata_file = self.data_dir / "catalog.json"
        
        # Load existing databases
        self._load_catalog()
    
    def _load_catalog(self):
        """Load database catalog from metadata file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    db_names = metadata.get('databases', [])
                    
                    # Load each database
                    for db_name in db_names:
                        try:
                            db = Database.load_from_disk(self._get_db_path(db_name))
                            self.databases[db_name] = db
                        except Exception as e:
                            print(f"Warning: Failed to load database '{db_name}': {e}")
            except Exception as e:
                print(f"Warning: Failed to load catalog metadata: {e}")
    
    def _save_catalog(self):
        """Save database catalog metadata."""
        try:
            metadata = {
                'databases': list(self.databases.keys())
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving catalog metadata: {e}")
            raise
    
    def _get_db_path(self, db_name: str) -> str:
        """Get file path for a database.
        
        Args:
            db_name: Database name
        
        Returns:
            Path to database file
        """
        return str(self.data_dir / f"{db_name}.json")
    
    def create_database(self, db_name: str) -> Database:
        """Create a new database.
        
        Args:
            db_name: Name of the database to create
        
        Returns:
            Created database
        
        Raises:
            ValueError: If database already exists or name is invalid
        """
        if not db_name or not db_name.strip():
            raise ValueError("Database name cannot be empty")
        
        db_name = db_name.strip()
        
        # Validate database name (alphanumeric, underscore, hyphen)
        if not all(c.isalnum() or c in '_-' for c in db_name):
            raise ValueError("Database name can only contain letters, numbers, underscores, and hyphens")
        
        if db_name in self.databases:
            raise ValueError(f"Database '{db_name}' already exists")
        
        # Create new database
        db = Database()
        db.name = db_name  # Set database name for persistence
        self.databases[db_name] = db
        
        # Save catalog and database
        self._save_catalog()
        db.save_to_disk(self._get_db_path(db_name))
        
        return db
    
    def get_database(self, db_name: str) -> Database:
        """Get a database by name.
        
        Args:
            db_name: Name of the database
        
        Returns:
            Database instance
        
        Raises:
            ValueError: If database does not exist
        """
        if db_name not in self.databases:
            raise ValueError(f"Database '{db_name}' does not exist")
        return self.databases[db_name]
    
    def drop_database(self, db_name: str):
        """Drop a database.
        
        Args:
            db_name: Name of the database to drop
        
        Raises:
            ValueError: If database does not exist
        """
        if db_name not in self.databases:
            raise ValueError(f"Database '{db_name}' does not exist")
        
        # Remove from memory
        del self.databases[db_name]
        
        # Delete database file
        db_path = Path(self._get_db_path(db_name))
        if db_path.exists():
            db_path.unlink()
        
        # Update catalog
        self._save_catalog()
    
    def list_databases(self) -> List[str]:
        """List all database names.
        
        Returns:
            List of database names
        """
        return list(self.databases.keys())
    
    def database_exists(self, db_name: str) -> bool:
        """Check if a database exists.
        
        Args:
            db_name: Name of the database
        
        Returns:
            True if database exists, False otherwise
        """
        return db_name in self.databases
    
    def save_database(self, db_name: str):
        """Save a specific database to disk.
        
        Args:
            db_name: Name of the database to save
        
        Raises:
            ValueError: If database does not exist
        """
        if db_name not in self.databases:
            raise ValueError(f"Database '{db_name}' does not exist")
        
        db = self.databases[db_name]
        db.save_to_disk(self._get_db_path(db_name))
    
    def __repr__(self) -> str:
        return f"DatabaseManager(databases={len(self.databases)})"
