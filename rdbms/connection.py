"""PesaDB connection URL parser and manager.

Supports the pesadb:// URL scheme for connecting to the custom RDBMS.
Auto-creates databases if they don't exist when specified in the connection URL.
"""

import re
from typing import Dict, Any, Optional
from pathlib import Path
from .engine import DatabaseManager


def parse_connection_url(url: str) -> Dict[str, Any]:
    """Parse pesadb:// connection URL.
    
    Supported formats:
    - pesadb://localhost/database_name
    - pesadb:///database_name (localhost implied)
    - pesadb://localhost/database_name?data_dir=/path/to/data
    
    Args:
        url: Connection URL string in pesadb:// format
        
    Returns:
        Dictionary with parsed connection info containing:
        - database: Database name
        - host: Host (always 'localhost' for file-based DB)
        - data_dir: Directory for database files
        
    Raises:
        ValueError: If URL format is invalid
        
    Examples:
        >>> parse_connection_url("pesadb://localhost/myapp")
        {'database': 'myapp', 'host': 'localhost', 'data_dir': 'data'}
        
        >>> parse_connection_url("pesadb:///myapp")
        {'database': 'myapp', 'host': 'localhost', 'data_dir': 'data'}
    """
    if not url.startswith('pesadb://'):
        raise ValueError(
            f"Invalid connection URL format: {url}. "
            "Expected format: pesadb://localhost/database_name or pesadb:///database_name"
        )
    
    # Parse URL format: pesadb://host/database or pesadb:///database
    # Optional query parameters: ?data_dir=/path/to/data
    pattern = r'^pesadb://(?:([^/]+))?/([^?]+)(?:\?(.+))?$'
    match = re.match(pattern, url)
    
    if not match:
        raise ValueError(
            f"Invalid connection URL format: {url}. "
            "Expected format: pesadb://localhost/database_name or pesadb:///database_name"
        )
    
    host = match.group(1) or 'localhost'
    database = match.group(2).strip()
    query_string = match.group(3)
    
    # Validate database name
    if not database:
        raise ValueError("Database name cannot be empty")
    
    if not all(c.isalnum() or c in '_-' for c in database):
        raise ValueError(
            "Database name can only contain letters, numbers, underscores, and hyphens"
        )
    
    # Parse query parameters
    data_dir = 'data'  # Default
    if query_string:
        params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        if 'data_dir' in params:
            data_dir = params['data_dir']
    
    return {
        'database': database,
        'host': host,
        'data_dir': data_dir
    }


class PesaDBConnection:
    """PesaDB connection manager.
    
    Manages connection to the custom RDBMS using pesadb:// URLs.
    Auto-creates the database if it doesn't exist.
    
    Example:
        >>> from rdbms.connection import connect
        >>> conn = connect("pesadb://localhost/myapp")
        >>> db_manager = conn.get_database_manager()
        >>> db = conn.get_database()
    """
    
    def __init__(self, url: str):
        """Initialize connection from pesadb:// URL.
        
        Args:
            url: Connection URL (e.g., "pesadb://localhost/myapp")
            
        Raises:
            ValueError: If URL format is invalid
        """
        self.connection_info = parse_connection_url(url)
        self.database_name = self.connection_info['database']
        self.data_dir = self.connection_info['data_dir']
        
        # Initialize database manager
        self.database_manager = DatabaseManager(data_dir=self.data_dir)
        
        # Auto-create database if it doesn't exist
        if not self.database_manager.database_exists(self.database_name):
            self.database_manager.create_database(self.database_name)
    
    def get_database_manager(self) -> DatabaseManager:
        """Get the database manager instance.
        
        Returns:
            DatabaseManager instance
        """
        return self.database_manager
    
    def get_database(self):
        """Get the connected database instance.
        
        Returns:
            Database instance
        """
        return self.database_manager.get_database(self.database_name)
    
    def get_database_name(self) -> str:
        """Get the name of the connected database.
        
        Returns:
            Database name
        """
        return self.database_name
    
    def close(self):
        """Close the connection (for API compatibility, no-op for file-based DB)."""
        pass
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
        return False
    
    def __repr__(self) -> str:
        return f"PesaDBConnection(database='{self.database_name}', data_dir='{self.data_dir}')"


def connect(url: str) -> PesaDBConnection:
    """Create a connection to PesaDB using a pesadb:// URL.
    
    The database will be automatically created if it doesn't exist.
    
    Args:
        url: Connection URL in format: pesadb://localhost/database_name
        
    Returns:
        PesaDBConnection instance
        
    Raises:
        ValueError: If URL format is invalid
        
    Example:
        >>> from rdbms.connection import connect
        >>> conn = connect("pesadb://localhost/myapp")
        >>> db_manager = conn.get_database_manager()
        >>> 
        >>> # Use with environment variables
        >>> import os
        >>> conn = connect(os.getenv("PESADB_URL", "pesadb://localhost/default"))
    """
    return PesaDBConnection(url)
