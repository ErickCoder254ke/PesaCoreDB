"""Row representation with type validation."""

from enum import Enum
from typing import Any, Dict
from datetime import datetime, date, time


class DataType(Enum):
    """Supported data types in the RDBMS."""
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOL = "BOOL"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"

    @staticmethod
    def from_string(type_str: str) -> 'DataType':
        """Convert string to DataType enum.

        Supports aliases:
        - REAL, DOUBLE, DECIMAL -> FLOAT
        - TIMESTAMP -> DATETIME
        """
        type_str = type_str.upper()

        # Handle aliases
        if type_str in ('REAL', 'DOUBLE', 'DECIMAL'):
            return DataType.FLOAT
        if type_str == 'TIMESTAMP':
            return DataType.DATETIME

        try:
            return DataType[type_str]
        except KeyError:
            raise ValueError(f"Unsupported data type: {type_str}. Supported types: INT, FLOAT, STRING, BOOL, DATE, TIME, DATETIME")


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


def parse_date(value: Any) -> str:
    """Parse and validate date value.

    Args:
        value: Date value (string or date object)

    Returns:
        ISO-8601 date string (YYYY-MM-DD)

    Raises:
        ValueError: If format is invalid
    """
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, str):
        try:
            # Parse date string (YYYY-MM-DD)
            parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
            return parsed_date.isoformat()
        except ValueError:
            raise ValueError(
                f"Invalid date format: {value}. Expected format: YYYY-MM-DD (e.g., '2024-01-15')"
            )

    raise ValueError(f"Invalid date value: {value}. Expected string in YYYY-MM-DD format")


def parse_time(value: Any) -> str:
    """Parse and validate time value.

    Args:
        value: Time value (string or time object)

    Returns:
        ISO-8601 time string (HH:MM:SS)

    Raises:
        ValueError: If format is invalid
    """
    if isinstance(value, time):
        return value.isoformat()

    if isinstance(value, str):
        try:
            # Try parsing with microseconds
            parsed_time = datetime.strptime(value, '%H:%M:%S.%f').time()
            return parsed_time.isoformat()
        except ValueError:
            try:
                # Try parsing without microseconds
                parsed_time = datetime.strptime(value, '%H:%M:%S').time()
                return parsed_time.isoformat()
            except ValueError:
                try:
                    # Try parsing HH:MM format
                    parsed_time = datetime.strptime(value, '%H:%M').time()
                    return parsed_time.isoformat()
                except ValueError:
                    raise ValueError(
                        f"Invalid time format: {value}. Expected format: HH:MM:SS or HH:MM (e.g., '14:30:00' or '14:30')"
                    )

    raise ValueError(f"Invalid time value: {value}. Expected string in HH:MM:SS format")


def parse_datetime(value: Any) -> str:
    """Parse and validate datetime value.

    Args:
        value: Datetime value (string or datetime object)

    Returns:
        ISO-8601 datetime string

    Raises:
        ValueError: If format is invalid
    """
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, str):
        try:
            # Handle 'Z' timezone indicator
            normalized_value = value.replace('Z', '+00:00')
            parsed_datetime = datetime.fromisoformat(normalized_value)
            return parsed_datetime.isoformat()
        except ValueError:
            # Try common datetime formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f',
            ]
            for fmt in formats:
                try:
                    parsed_datetime = datetime.strptime(value, fmt)
                    return parsed_datetime.isoformat()
                except ValueError:
                    continue

            raise ValueError(
                f"Invalid datetime format: {value}. Expected ISO-8601 format "
                "(e.g., '2024-01-15T10:30:00' or '2024-01-15 10:30:00')"
            )

    raise ValueError(f"Invalid datetime value: {value}. Expected ISO-8601 formatted string")


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

        elif expected_type == DataType.DATE:
            try:
                return parse_date(value)
            except ValueError as e:
                raise ValueError(f"Column '{col_name}': {str(e)}")

        elif expected_type == DataType.TIME:
            try:
                return parse_time(value)
            except ValueError as e:
                raise ValueError(f"Column '{col_name}': {str(e)}")

        elif expected_type == DataType.DATETIME:
            try:
                return parse_datetime(value)
            except ValueError as e:
                raise ValueError(f"Column '{col_name}': {str(e)}")

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
