"""SQL input validation and sanitization utilities."""

import re
from typing import Any


# SQL keywords that should not be used as identifiers
SQL_RESERVED_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
    'DELETE', 'CREATE', 'TABLE', 'DROP', 'ALTER', 'INDEX', 'DATABASE',
    'INNER', 'OUTER', 'LEFT', 'RIGHT', 'JOIN', 'ON', 'ORDER', 'BY',
    'GROUP', 'HAVING', 'UNION', 'AND', 'OR', 'NOT', 'NULL', 'TRUE', 'FALSE',
    'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'CHECK', 'DEFAULT',
    'AS', 'DISTINCT', 'ALL', 'EXISTS', 'IN', 'BETWEEN', 'LIKE', 'IS',
    'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'CAST', 'CONVERT'
}


def validate_identifier(identifier: str, allow_reserved: bool = False) -> str:
    """Validate and sanitize SQL identifier (table name, column name, etc.).
    
    Args:
        identifier: The identifier to validate
        allow_reserved: Whether to allow SQL reserved keywords
    
    Returns:
        The validated identifier
    
    Raises:
        ValueError: If identifier is invalid
    
    Examples:
        >>> validate_identifier("users")
        'users'
        >>> validate_identifier("my_table_123")
        'my_table_123'
        >>> validate_identifier("SELECT")
        ValueError: Invalid identifier: 'SELECT' is a reserved SQL keyword
        >>> validate_identifier("table-name")
        ValueError: Invalid identifier format
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")
    
    # Check length (reasonable limit)
    if len(identifier) > 64:
        raise ValueError(f"Identifier too long (max 64 characters): '{identifier}'")
    
    # Check format: must start with letter or underscore, followed by letters, digits, or underscores
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(
            f"Invalid identifier format: '{identifier}'. "
            "Must start with letter or underscore, followed by letters, digits, or underscores."
        )
    
    # Check for reserved keywords
    if not allow_reserved and identifier.upper() in SQL_RESERVED_KEYWORDS:
        raise ValueError(
            f"Invalid identifier: '{identifier}' is a reserved SQL keyword. "
            "Use a different name or quote the identifier."
        )
    
    return identifier


def sanitize_string_value(value: Any) -> str:
    """Sanitize a string value for SQL.
    
    This function is used when building SQL strings manually.
    However, the preferred approach is to use the tokenizer/parser.
    
    Args:
        value: Value to sanitize
    
    Returns:
        Sanitized string suitable for SQL
    
    Examples:
        >>> sanitize_string_value("test")
        "'test'"
        >>> sanitize_string_value("test's")
        "'test''s'"
        >>> sanitize_string_value("test\\nvalue")
        "'test\\\\nvalue'"
    """
    if value is None:
        return 'NULL'
    
    # Convert to string
    str_value = str(value)
    
    # Escape single quotes by doubling them (SQL standard)
    str_value = str_value.replace("'", "''")
    
    # Escape backslashes
    str_value = str_value.replace("\\", "\\\\")
    
    # Wrap in quotes
    return f"'{str_value}'"


def validate_limit_offset(value: Any, param_name: str = "value") -> int:
    """Validate LIMIT or OFFSET value.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
    
    Returns:
        Validated integer value
    
    Raises:
        ValueError: If value is invalid
    """
    try:
        int_value = int(value)
        if int_value < 0:
            raise ValueError(f"{param_name} must be non-negative, got {int_value}")
        if int_value > 1_000_000:
            raise ValueError(f"{param_name} too large (max 1,000,000): {int_value}")
        return int_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {param_name}: {value}. Must be a non-negative integer.")


def validate_table_name(table_name: str) -> str:
    """Validate table name.
    
    Wrapper around validate_identifier for clarity.
    """
    return validate_identifier(table_name, allow_reserved=False)


def validate_column_name(column_name: str) -> str:
    """Validate column name.
    
    Wrapper around validate_identifier for clarity.
    """
    return validate_identifier(column_name, allow_reserved=False)


def validate_database_name(database_name: str) -> str:
    """Validate database name.
    
    Wrapper around validate_identifier for clarity.
    """
    return validate_identifier(database_name, allow_reserved=False)


__all__ = [
    'validate_identifier',
    'validate_table_name',
    'validate_column_name',
    'validate_database_name',
    'sanitize_string_value',
    'validate_limit_offset',
    'SQL_RESERVED_KEYWORDS',
]
