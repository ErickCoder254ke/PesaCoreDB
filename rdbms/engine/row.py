"""Row representation with type validation."""

from enum import Enum
from typing import Any, Dict
from datetime import datetime


class DataType(Enum):
    """Supported data types in the RDBMS."""
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOL = "BOOL"

    @staticmethod
    def from_string(type_str: str) -> 'DataType':
        """Convert string to DataType enum.

        Supports aliases:
        - REAL, DOUBLE, DECIMAL -> FLOAT
        """
        type_str = type_str.upper()

        # Handle aliases
        if type_str in ('REAL', 'DOUBLE', 'DECIMAL'):
            return DataType.FLOAT

        try:
            return DataType[type_str]
        except KeyError:
            raise ValueError(f"Unsupported data type: {type_str}. Supported types: INT, FLOAT, STRING, BOOL")


def validate_iso_datetime(value: str) -> str:
    """Validate ISO-8601 datetime string format.

    Args:
        value: String to validate

    Returns:
        The validated datetime string

    Raises:
        ValueError: If format is invalid
    """
    try:
        # Try to parse the datetime string
        # Handle both with and without timezone
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value
    except (ValueError, AttributeError):
        raise ValueError(
            f"Invalid datetime format: {value}. "
            "Expected ISO-8601 format (e.g., '2024-01-15T10:30:00Z' or '2024-01-15T10:30:00+00:00')"
        )


class Row:
    """Represents a single row in a table."""

    def __init__(self, schema: Dict[str, DataType], values: Dict[str, Any]):
        """Initialize a row with schema validation.

        Args:
            schema: Column name to DataType mapping
            values: Column name to value mapping

        Raises:
            ValueError: If validation fails
        """
        self.schema = schema
        self.values = {}

        # Validate and store values
        for col_name, col_type in schema.items():
            if col_name not in values:
                raise ValueError(f"Missing value for column: {col_name}")

            value = values[col_name]
            validated_value = self._validate_type(col_name, value, col_type)
            self.values[col_name] = validated_value
    
    def _validate_type(self, col_name: str, value: Any, expected_type: DataType) -> Any:
        """Validate and convert value to expected type.

        Args:
            col_name: Column name for error messages
            value: Value to validate
            expected_type: Expected DataType

        Returns:
            Validated and converted value

        Raises:
            ValueError: If type validation fails
        """
        if expected_type == DataType.INT:
            if isinstance(value, bool):
                raise ValueError(f"Column '{col_name}' expects INT, got BOOL")
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Column '{col_name}' expects INT, got '{value}'")

        elif expected_type == DataType.FLOAT:
            if isinstance(value, bool):
                raise ValueError(f"Column '{col_name}' expects FLOAT, got BOOL")
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Column '{col_name}' expects FLOAT, got '{value}'")

        elif expected_type == DataType.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Column '{col_name}' expects STRING, got '{value}'")

            # Validate datetime format for columns with datetime-related names
            if any(suffix in col_name.lower() for suffix in ['_at', '_date', 'timestamp']):
                validate_iso_datetime(value)

            return value

        elif expected_type == DataType.BOOL:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ('true', '1', 'yes'):
                    return True
                elif lower_val in ('false', '0', 'no'):
                    return False
            raise ValueError(f"Column '{col_name}' expects BOOL, got '{value}'")

        raise ValueError(f"Unknown type for column '{col_name}'")
    
    def get(self, col_name: str) -> Any:
        """Get value for a column."""
        return self.values.get(col_name)
    
    def set(self, col_name: str, value: Any):
        """Set value for a column with type validation."""
        if col_name not in self.schema:
            raise ValueError(f"Column '{col_name}' does not exist")
        validated_value = self._validate_type(col_name, value, self.schema[col_name])
        self.values[col_name] = validated_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert row to dictionary."""
        return self.values.copy()
    
    def __repr__(self) -> str:
        return f"Row({self.values})"
