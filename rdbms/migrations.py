"""Database migration system for tracking and applying schema changes."""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class Migration:
    """Represents a single database migration."""
    
    def __init__(self, version: int, name: str, up_sql: str, down_sql: str = "", description: str = ""):
        """Initialize a migration.
        
        Args:
            version: Migration version number (must be unique and sequential)
            name: Short name for the migration (e.g., "add_user_table")
            up_sql: SQL to apply the migration
            down_sql: SQL to rollback the migration (optional)
            description: Longer description of what the migration does
        """
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.description = description
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of the migration SQL."""
        content = f"{self.version}:{self.name}:{self.up_sql}:{self.down_sql}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert migration to dictionary."""
        return {
            'version': self.version,
            'name': self.name,
            'up_sql': self.up_sql,
            'down_sql': self.down_sql,
            'description': self.description,
            'checksum': self.checksum
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Migration':
        """Create migration from dictionary."""
        migration = Migration(
            version=data['version'],
            name=data['name'],
            up_sql=data['up_sql'],
            down_sql=data.get('down_sql', ''),
            description=data.get('description', '')
        )
        
        # Verify checksum if provided
        if 'checksum' in data and data['checksum'] != migration.checksum:
            raise ValueError(
                f"Migration checksum mismatch for '{migration.name}' (version {migration.version}). "
                "The migration may have been modified after being applied."
            )
        
        return migration
    
    def __repr__(self) -> str:
        return f"Migration(v{self.version}: {self.name})"


class MigrationHistory:
    """Tracks which migrations have been applied to a database."""
    
    def __init__(self):
        """Initialize empty migration history."""
        self.applied_migrations: List[Dict[str, Any]] = []
    
    def record_migration(self, migration: Migration) -> None:
        """Record that a migration has been applied.
        
        Args:
            migration: The migration that was applied
        """
        record = {
            'version': migration.version,
            'name': migration.name,
            'checksum': migration.checksum,
            'applied_at': datetime.utcnow().isoformat() + 'Z',
            'description': migration.description
        }
        self.applied_migrations.append(record)
    
    def rollback_migration(self, version: int) -> None:
        """Remove a migration from the history.
        
        Args:
            version: Version number of the migration to remove
        """
        self.applied_migrations = [
            m for m in self.applied_migrations if m['version'] != version
        ]
    
    def is_applied(self, version: int) -> bool:
        """Check if a migration version has been applied.
        
        Args:
            version: Migration version number
        
        Returns:
            True if the migration has been applied
        """
        return any(m['version'] == version for m in self.applied_migrations)
    
    def get_latest_version(self) -> int:
        """Get the latest applied migration version.
        
        Returns:
            Latest version number, or 0 if no migrations applied
        """
        if not self.applied_migrations:
            return 0
        return max(m['version'] for m in self.applied_migrations)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            'applied_migrations': self.applied_migrations
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MigrationHistory':
        """Create history from dictionary."""
        history = MigrationHistory()
        history.applied_migrations = data.get('applied_migrations', [])
        return history
    
    def __repr__(self) -> str:
        return f"MigrationHistory(applied={len(self.applied_migrations)}, latest=v{self.get_latest_version()})"


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, database, executor):
        """Initialize migration manager.
        
        Args:
            database: Database instance
            executor: SQL executor instance
        """
        self.database = database
        self.executor = executor
        self.migrations: List[Migration] = []
        self.history = MigrationHistory()
        self._load_history()
    
    def _load_history(self):
        """Load migration history from database metadata."""
        # Migration history is stored in the database's metadata
        # For now, we'll store it as a simple list in the database object
        if not hasattr(self.database, 'migration_history'):
            self.database.migration_history = MigrationHistory()
        self.history = self.database.migration_history
    
    def _save_history(self):
        """Save migration history to database metadata."""
        self.database.migration_history = self.history
    
    def register_migration(self, migration: Migration) -> None:
        """Register a migration.
        
        Args:
            migration: Migration to register
        
        Raises:
            ValueError: If version number is not sequential
        """
        # Check for duplicate versions
        if any(m.version == migration.version for m in self.migrations):
            raise ValueError(f"Migration version {migration.version} is already registered")
        
        # Add to list and sort by version
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of migrations that haven't been applied yet.
        
        Returns:
            List of pending migrations in order
        """
        return [m for m in self.migrations if not self.history.is_applied(m.version)]
    
    def apply_migration(self, migration: Migration, dry_run: bool = False) -> Dict[str, Any]:
        """Apply a single migration.
        
        Args:
            migration: Migration to apply
            dry_run: If True, only validate without applying
        
        Returns:
            Result dictionary with success status and messages
        
        Raises:
            ValueError: If migration fails
        """
        result = {
            'success': False,
            'version': migration.version,
            'name': migration.name,
            'messages': []
        }
        
        # Check if already applied
        if self.history.is_applied(migration.version):
            result['messages'].append(f"Migration v{migration.version} already applied")
            result['success'] = True
            return result
        
        if dry_run:
            result['messages'].append(f"DRY RUN: Would apply migration v{migration.version}: {migration.name}")
            result['success'] = True
            return result
        
        try:
            # Execute the UP SQL
            from .sql import Tokenizer, Parser
            tokenizer = Tokenizer()
            parser = Parser()
            
            # Split by semicolons to handle multiple statements
            statements = [s.strip() for s in migration.up_sql.split(';') if s.strip()]
            
            for sql in statements:
                tokens = tokenizer.tokenize(sql)
                command = parser.parse(tokens)
                self.executor.execute(command)
            
            # Record the migration
            self.history.record_migration(migration)
            self._save_history()
            
            result['success'] = True
            result['messages'].append(f"Successfully applied migration v{migration.version}: {migration.name}")
            
        except Exception as e:
            result['messages'].append(f"Failed to apply migration: {str(e)}")
            raise ValueError(f"Migration v{migration.version} failed: {str(e)}")
        
        return result
    
    def rollback_migration(self, migration: Migration, dry_run: bool = False) -> Dict[str, Any]:
        """Rollback a single migration.
        
        Args:
            migration: Migration to rollback
            dry_run: If True, only validate without rolling back
        
        Returns:
            Result dictionary with success status and messages
        
        Raises:
            ValueError: If rollback fails or no down_sql provided
        """
        result = {
            'success': False,
            'version': migration.version,
            'name': migration.name,
            'messages': []
        }
        
        # Check if migration is applied
        if not self.history.is_applied(migration.version):
            result['messages'].append(f"Migration v{migration.version} is not applied")
            result['success'] = True
            return result
        
        # Check if down_sql exists
        if not migration.down_sql:
            raise ValueError(
                f"Cannot rollback migration v{migration.version}: no down_sql provided"
            )
        
        if dry_run:
            result['messages'].append(f"DRY RUN: Would rollback migration v{migration.version}: {migration.name}")
            result['success'] = True
            return result
        
        try:
            # Execute the DOWN SQL
            from .sql import Tokenizer, Parser
            tokenizer = Tokenizer()
            parser = Parser()
            
            # Split by semicolons to handle multiple statements
            statements = [s.strip() for s in migration.down_sql.split(';') if s.strip()]
            
            for sql in statements:
                tokens = tokenizer.tokenize(sql)
                command = parser.parse(tokens)
                self.executor.execute(command)
            
            # Remove from history
            self.history.rollback_migration(migration.version)
            self._save_history()
            
            result['success'] = True
            result['messages'].append(f"Successfully rolled back migration v{migration.version}: {migration.name}")
            
        except Exception as e:
            result['messages'].append(f"Failed to rollback migration: {str(e)}")
            raise ValueError(f"Migration v{migration.version} rollback failed: {str(e)}")
        
        return result
    
    def migrate_to_latest(self, dry_run: bool = False) -> Dict[str, Any]:
        """Apply all pending migrations.
        
        Args:
            dry_run: If True, only show what would be applied
        
        Returns:
            Summary of migrations applied
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            return {
                'success': True,
                'message': 'Database is up to date',
                'current_version': self.history.get_latest_version(),
                'applied': []
            }
        
        applied = []
        errors = []
        
        for migration in pending:
            try:
                result = self.apply_migration(migration, dry_run=dry_run)
                applied.append(result)
            except Exception as e:
                errors.append({
                    'version': migration.version,
                    'name': migration.name,
                    'error': str(e)
                })
                break  # Stop on first error
        
        return {
            'success': len(errors) == 0,
            'message': f"Applied {len(applied)} migration(s)" if not dry_run else f"Would apply {len(applied)} migration(s)",
            'current_version': self.history.get_latest_version(),
            'applied': applied,
            'errors': errors
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get migration status.
        
        Returns:
            Status information including current version and pending migrations
        """
        pending = self.get_pending_migrations()
        
        return {
            'current_version': self.history.get_latest_version(),
            'total_migrations': len(self.migrations),
            'applied_count': len(self.history.applied_migrations),
            'pending_count': len(pending),
            'pending_migrations': [
                {
                    'version': m.version,
                    'name': m.name,
                    'description': m.description
                }
                for m in pending
            ],
            'applied_migrations': self.history.applied_migrations
        }
    
    def save_migrations_to_file(self, file_path: str):
        """Save registered migrations to a JSON file.
        
        Args:
            file_path: Path to save migrations
        """
        data = {
            'migrations': [m.to_dict() for m in self.migrations]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_migrations_from_file(self, file_path: str):
        """Load migrations from a JSON file.
        
        Args:
            file_path: Path to load migrations from
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for migration_data in data.get('migrations', []):
            migration = Migration.from_dict(migration_data)
            self.register_migration(migration)


__all__ = [
    'Migration',
    'MigrationHistory',
    'MigrationManager',
]
