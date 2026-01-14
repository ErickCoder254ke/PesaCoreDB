"""Audit trail system for tracking database changes."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class AuditAction(Enum):
    """Types of auditable actions."""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE_TABLE = "CREATE_TABLE"
    DROP_TABLE = "DROP_TABLE"
    TRUNCATE = "TRUNCATE"


class AuditEntry:
    """Represents a single audit log entry."""
    
    def __init__(
        self,
        table_name: str,
        action: AuditAction,
        record_id: Any,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        changed_at: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize an audit entry.
        
        Args:
            table_name: Name of the table affected
            action: Type of action performed
            record_id: ID of the record affected (primary key value)
            old_values: Values before the change (for UPDATE, DELETE)
            new_values: Values after the change (for INSERT, UPDATE)
            changed_at: ISO-8601 timestamp (defaults to now)
            user_id: ID of the user who made the change
            metadata: Additional metadata (e.g., IP address, session info)
        """
        self.table_name = table_name
        self.action = action if isinstance(action, AuditAction) else AuditAction[action]
        self.record_id = record_id
        self.old_values = old_values or {}
        self.new_values = new_values or {}
        self.changed_at = changed_at or (datetime.utcnow().isoformat() + 'Z')
        self.user_id = user_id
        self.metadata = metadata or {}
    
    def get_changed_fields(self) -> Dict[str, Dict[str, Any]]:
        """Get fields that changed with their old and new values.
        
        Returns:
            Dictionary mapping field names to {old, new} value dicts
        """
        changed = {}
        
        # Only applicable for UPDATE actions
        if self.action != AuditAction.UPDATE:
            return changed
        
        all_keys = set(self.old_values.keys()) | set(self.new_values.keys())
        
        for key in all_keys:
            old_val = self.old_values.get(key)
            new_val = self.new_values.get(key)
            
            if old_val != new_val:
                changed[key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return changed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary."""
        return {
            'table_name': self.table_name,
            'action': self.action.value,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changed_at': self.changed_at,
            'user_id': self.user_id,
            'metadata': self.metadata,
            'changed_fields': self.get_changed_fields()
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AuditEntry':
        """Create audit entry from dictionary."""
        return AuditEntry(
            table_name=data['table_name'],
            action=data['action'],
            record_id=data['record_id'],
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            changed_at=data.get('changed_at'),
            user_id=data.get('user_id'),
            metadata=data.get('metadata')
        )
    
    def __repr__(self) -> str:
        return f"AuditEntry({self.action.value} on {self.table_name}[{self.record_id}] at {self.changed_at})"


class AuditLog:
    """Manages audit trail entries."""
    
    def __init__(self, max_entries: int = 10000):
        """Initialize audit log.
        
        Args:
            max_entries: Maximum number of entries to keep in memory
        """
        self.entries: List[AuditEntry] = []
        self.max_entries = max_entries
        self.enabled = True
    
    def log(
        self,
        table_name: str,
        action: AuditAction,
        record_id: Any,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log an audit entry.
        
        Args:
            table_name: Name of the table affected
            action: Type of action performed
            record_id: ID of the record affected
            old_values: Values before the change
            new_values: Values after the change
            user_id: ID of the user who made the change
            metadata: Additional metadata
        
        Returns:
            The created audit entry
        """
        if not self.enabled:
            return None
        
        entry = AuditEntry(
            table_name=table_name,
            action=action,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id,
            metadata=metadata
        )
        
        self.entries.append(entry)
        
        # Trim old entries if we exceed max
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        return entry
    
    def get_entries_for_table(self, table_name: str) -> List[AuditEntry]:
        """Get all audit entries for a specific table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of audit entries
        """
        return [e for e in self.entries if e.table_name == table_name]
    
    def get_entries_for_record(self, table_name: str, record_id: Any) -> List[AuditEntry]:
        """Get audit history for a specific record.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
        
        Returns:
            List of audit entries ordered by time
        """
        return [
            e for e in self.entries
            if e.table_name == table_name and e.record_id == record_id
        ]
    
    def get_entries_by_user(self, user_id: str) -> List[AuditEntry]:
        """Get all audit entries by a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of audit entries
        """
        return [e for e in self.entries if e.user_id == user_id]
    
    def get_recent_entries(self, limit: int = 100) -> List[AuditEntry]:
        """Get the most recent audit entries.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of recent audit entries
        """
        return self.entries[-limit:]
    
    def clear(self):
        """Clear all audit entries."""
        self.entries = []
    
    def enable(self):
        """Enable audit logging."""
        self.enabled = True
    
    def disable(self):
        """Disable audit logging."""
        self.enabled = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        return {
            'entries': [e.to_dict() for e in self.entries],
            'max_entries': self.max_entries,
            'enabled': self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AuditLog':
        """Create audit log from dictionary."""
        audit_log = AuditLog(max_entries=data.get('max_entries', 10000))
        audit_log.enabled = data.get('enabled', True)
        
        for entry_data in data.get('entries', []):
            entry = AuditEntry.from_dict(entry_data)
            audit_log.entries.append(entry)
        
        return audit_log
    
    def export_to_json(self, file_path: str):
        """Export audit log to JSON file.
        
        Args:
            file_path: Path to save the JSON file
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def import_from_json(file_path: str) -> 'AuditLog':
        """Import audit log from JSON file.
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            AuditLog instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return AuditLog.from_dict(data)
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __repr__(self) -> str:
        return f"AuditLog(entries={len(self.entries)}, enabled={self.enabled})"


class AuditableTable:
    """Mixin to add audit trail support to tables."""
    
    def __init__(self, *args, audit_log: Optional[AuditLog] = None, **kwargs):
        """Initialize auditable table.
        
        Args:
            audit_log: AuditLog instance to use (creates new if None)
        """
        super().__init__(*args, **kwargs)
        self.audit_log = audit_log or AuditLog()
    
    def _audit_insert(self, values: Dict[str, Any], record_id: Any, user_id: Optional[str] = None):
        """Audit an insert operation."""
        self.audit_log.log(
            table_name=self.name,
            action=AuditAction.INSERT,
            record_id=record_id,
            new_values=values,
            user_id=user_id
        )
    
    def _audit_update(
        self,
        record_id: Any,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Audit an update operation."""
        self.audit_log.log(
            table_name=self.name,
            action=AuditAction.UPDATE,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id
        )
    
    def _audit_delete(self, record_id: Any, old_values: Dict[str, Any], user_id: Optional[str] = None):
        """Audit a delete operation."""
        self.audit_log.log(
            table_name=self.name,
            action=AuditAction.DELETE,
            record_id=record_id,
            old_values=old_values,
            user_id=user_id
        )


__all__ = [
    'AuditAction',
    'AuditEntry',
    'AuditLog',
    'AuditableTable',
]
