"""Date/Time function expressions for SQL."""

from typing import Any, Dict, List
from datetime import datetime, date, time, timedelta
from .expressions import Expression


class DateTimeFunctionExpression(Expression):
    """Expression for date/time functions (NOW, DATE_ADD, DATE_DIFF, EXTRACT, etc.)."""

    def __init__(self, function_name: str, arguments: List[Expression] = None):
        """Initialize date/time function expression.

        Args:
            function_name: Name of the function (NOW, DATE_ADD, etc.)
            arguments: List of argument expressions
        """
        self.function_name = function_name.upper()
        self.arguments = arguments or []

    def evaluate(self, row: Dict[str, Any]) -> Any:
        """Evaluate the date/time function.

        Args:
            row: Row dictionary for evaluating argument expressions

        Returns:
            Result of the function

        Raises:
            ValueError: If function is invalid or arguments are incorrect
        """
        if self.function_name == 'NOW':
            # NOW() - returns current datetime
            return datetime.now().isoformat()

        elif self.function_name == 'CURRENT_DATE':
            # CURRENT_DATE() - returns current date
            return date.today().isoformat()

        elif self.function_name == 'CURRENT_TIME':
            # CURRENT_TIME() - returns current time
            return datetime.now().time().isoformat()

        elif self.function_name == 'DATE':
            # DATE(datetime_expr) - extracts date part
            if len(self.arguments) != 1:
                raise ValueError("DATE() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                if isinstance(value, str):
                    # Parse datetime string and extract date
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.date().isoformat()
                return value
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid datetime value for DATE(): {value}")

        elif self.function_name == 'TIME':
            # TIME(datetime_expr) - extracts time part
            if len(self.arguments) != 1:
                raise ValueError("TIME() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                if isinstance(value, str):
                    # Parse datetime string and extract time
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.time().isoformat()
                return value
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid datetime value for TIME(): {value}")

        elif self.function_name == 'YEAR':
            # YEAR(date_expr) - extracts year
            if len(self.arguments) != 1:
                raise ValueError("YEAR() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.year
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid date/datetime value for YEAR(): {value}")

        elif self.function_name == 'MONTH':
            # MONTH(date_expr) - extracts month
            if len(self.arguments) != 1:
                raise ValueError("MONTH() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.month
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid date/datetime value for MONTH(): {value}")

        elif self.function_name == 'DAY':
            # DAY(date_expr) - extracts day
            if len(self.arguments) != 1:
                raise ValueError("DAY() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.day
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid date/datetime value for DAY(): {value}")

        elif self.function_name == 'HOUR':
            # HOUR(time_expr) - extracts hour
            if len(self.arguments) != 1:
                raise ValueError("HOUR() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.hour
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid time/datetime value for HOUR(): {value}")

        elif self.function_name == 'MINUTE':
            # MINUTE(time_expr) - extracts minute
            if len(self.arguments) != 1:
                raise ValueError("MINUTE() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.minute
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid time/datetime value for MINUTE(): {value}")

        elif self.function_name == 'SECOND':
            # SECOND(time_expr) - extracts second
            if len(self.arguments) != 1:
                raise ValueError("SECOND() requires exactly 1 argument")
            
            value = self.arguments[0].evaluate(row)
            if value is None:
                return None
            
            try:
                dt = self._parse_datetime_value(value)
                return dt.second
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid time/datetime value for SECOND(): {value}")

        elif self.function_name == 'DATE_ADD':
            # DATE_ADD(date_expr, INTERVAL value unit)
            # Simplified: DATE_ADD(date_expr, days) - adds days to date
            if len(self.arguments) != 2:
                raise ValueError("DATE_ADD() requires exactly 2 arguments: date and number of days")
            
            date_value = self.arguments[0].evaluate(row)
            days_to_add = self.arguments[1].evaluate(row)
            
            if date_value is None or days_to_add is None:
                return None
            
            try:
                dt = self._parse_datetime_value(date_value)
                days = int(days_to_add)
                new_dt = dt + timedelta(days=days)
                
                # Return same format as input
                if isinstance(dt, datetime):
                    return new_dt.isoformat()
                else:
                    return new_dt.date().isoformat()
            except (ValueError, TypeError) as e:
                raise ValueError(f"DATE_ADD() error: {str(e)}")

        elif self.function_name == 'DATE_SUB':
            # DATE_SUB(date_expr, days) - subtracts days from date
            if len(self.arguments) != 2:
                raise ValueError("DATE_SUB() requires exactly 2 arguments: date and number of days")
            
            date_value = self.arguments[0].evaluate(row)
            days_to_sub = self.arguments[1].evaluate(row)
            
            if date_value is None or days_to_sub is None:
                return None
            
            try:
                dt = self._parse_datetime_value(date_value)
                days = int(days_to_sub)
                new_dt = dt - timedelta(days=days)
                
                # Return same format as input
                if isinstance(dt, datetime):
                    return new_dt.isoformat()
                else:
                    return new_dt.date().isoformat()
            except (ValueError, TypeError) as e:
                raise ValueError(f"DATE_SUB() error: {str(e)}")

        elif self.function_name == 'DATEDIFF':
            # DATEDIFF(date1, date2) - returns difference in days
            if len(self.arguments) != 2:
                raise ValueError("DATEDIFF() requires exactly 2 arguments")
            
            date1_value = self.arguments[0].evaluate(row)
            date2_value = self.arguments[1].evaluate(row)
            
            if date1_value is None or date2_value is None:
                return None
            
            try:
                dt1 = self._parse_datetime_value(date1_value)
                dt2 = self._parse_datetime_value(date2_value)
                
                # Extract just the date part for comparison
                if isinstance(dt1, datetime):
                    dt1 = dt1.date()
                if isinstance(dt2, datetime):
                    dt2 = dt2.date()
                
                diff = (dt1 - dt2).days
                return diff
            except (ValueError, TypeError) as e:
                raise ValueError(f"DATEDIFF() error: {str(e)}")

        else:
            raise ValueError(f"Unknown date/time function: {self.function_name}")

    def _parse_datetime_value(self, value: Any) -> datetime:
        """Parse a datetime value from string or datetime object.

        Args:
            value: Value to parse

        Returns:
            datetime object

        Raises:
            ValueError: If value cannot be parsed
        """
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, date):
            return datetime.combine(value, time())
        
        if isinstance(value, str):
            # Try to parse as datetime
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                # Try to parse as date
                try:
                    return datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Cannot parse datetime value: {value}")
        
        raise ValueError(f"Invalid datetime value type: {type(value)}")

    def __repr__(self) -> str:
        if self.arguments:
            args_str = ', '.join(str(arg) for arg in self.arguments)
            return f"{self.function_name}({args_str})"
        return f"{self.function_name}()"
