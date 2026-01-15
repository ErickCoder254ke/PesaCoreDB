"""Expression classes for WHERE clause evaluation."""

from typing import Any, Dict, List
from abc import ABC, abstractmethod
from datetime import datetime, date, time, timedelta
import re


class Expression(ABC):
    """Base class for SQL expressions."""
    
    @abstractmethod
    def evaluate(self, row: Dict[str, Any]) -> Any:
        """Evaluate the expression against a row.
        
        Args:
            row: Dictionary of column_name -> value
        
        Returns:
            Result of the expression evaluation
        """
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        pass


class LiteralExpression(Expression):
    """Represents a literal value (number, string, boolean, NULL)."""
    
    def __init__(self, value: Any):
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> Any:
        return self.value
    
    def __repr__(self) -> str:
        if isinstance(self.value, str):
            return f"'{self.value}'"
        elif self.value is None:
            return "NULL"
        elif isinstance(self.value, bool):
            return "TRUE" if self.value else "FALSE"
        else:
            return str(self.value)


class ColumnExpression(Expression):
    """Represents a column reference."""
    
    def __init__(self, column_name: str):
        self.column_name = column_name
    
    def evaluate(self, row: Dict[str, Any]) -> Any:
        # Try the full column name first
        if self.column_name in row:
            return row[self.column_name]

        # If it contains a dot (table.column syntax), try just the column part
        if '.' in self.column_name:
            unqualified_name = self.column_name.split('.', 1)[1]
            if unqualified_name in row:
                return row[unqualified_name]

        # Column not found - provide helpful error message
        if '.' in self.column_name:
            raise ValueError(
                f"Column '{self.column_name}' not found. "
                f"Try using unqualified column name '{self.column_name.split('.', 1)[1]}' "
                f"when querying a single table."
            )
        raise ValueError(f"Column '{self.column_name}' not found in row")
    
    def __repr__(self) -> str:
        return self.column_name


class ComparisonExpression(Expression):
    """Represents a comparison operation (=, <, >, <=, >=, !=)."""
    
    OPERATORS = {
        '=': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '<>': lambda a, b: a != b,  # Alternative syntax for !=
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,
        '<=': lambda a, b: a <= b,
        '>=': lambda a, b: a >= b,
    }
    
    def __init__(self, operator: str, left: Expression, right: Expression):
        if operator not in self.OPERATORS:
            raise ValueError(f"Invalid comparison operator: {operator}")
        self.operator = operator
        self.left = left
        self.right = right
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        left_val = self.left.evaluate(row)
        right_val = self.right.evaluate(row)
        
        # Handle NULL comparisons
        if left_val is None or right_val is None:
            # In SQL, NULL comparisons are special
            # NULL = NULL is NULL (unknown), not TRUE
            # For now, we'll treat NULL != anything as TRUE (for IS NULL/IS NOT NULL later)
            if self.operator in ('=', '<>', '!='):
                return False if left_val is None and right_val is None else (left_val is None) != (right_val is None)
            return False
        
        # Type coercion for comparisons
        # If comparing different types, try to convert
        if type(left_val) != type(right_val):
            # Try to convert to compatible types
            if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                # Numeric comparison
                pass
            elif isinstance(left_val, str) or isinstance(right_val, str):
                # Convert both to strings for comparison
                left_val = str(left_val)
                right_val = str(right_val)
        
        return self.OPERATORS[self.operator](left_val, right_val)
    
    def __repr__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


class LogicalExpression(Expression):
    """Represents a logical operation (AND, OR, NOT)."""
    
    def __init__(self, operator: str, operands: list):
        """Initialize logical expression.
        
        Args:
            operator: 'AND', 'OR', or 'NOT'
            operands: List of Expression objects (1 for NOT, 2 for AND/OR)
        """
        if operator not in ('AND', 'OR', 'NOT'):
            raise ValueError(f"Invalid logical operator: {operator}")
        
        if operator == 'NOT' and len(operands) != 1:
            raise ValueError("NOT operator requires exactly 1 operand")
        
        if operator in ('AND', 'OR') and len(operands) < 2:
            raise ValueError(f"{operator} operator requires at least 2 operands")
        
        self.operator = operator
        self.operands = operands
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        if self.operator == 'NOT':
            result = self.operands[0].evaluate(row)
            return not result
        
        elif self.operator == 'AND':
            # Short-circuit evaluation
            for operand in self.operands:
                result = operand.evaluate(row)
                if not result:
                    return False
            return True
        
        elif self.operator == 'OR':
            # Short-circuit evaluation
            for operand in self.operands:
                result = operand.evaluate(row)
                if result:
                    return True
            return False
    
    def __repr__(self) -> str:
        if self.operator == 'NOT':
            return f"NOT {self.operands[0]}"
        else:
            operand_strs = [str(op) for op in self.operands]
            return f"({f' {self.operator} '.join(operand_strs)})"


class IsNullExpression(Expression):
    """Represents IS NULL or IS NOT NULL check."""
    
    def __init__(self, expression: Expression, is_not: bool = False):
        """Initialize IS NULL expression.
        
        Args:
            expression: Expression to check for NULL
            is_not: If True, check IS NOT NULL
        """
        self.expression = expression
        self.is_not = is_not
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        value = self.expression.evaluate(row)
        is_null = value is None
        return not is_null if self.is_not else is_null
    
    def __repr__(self) -> str:
        not_str = " NOT" if self.is_not else ""
        return f"({self.expression} IS{not_str} NULL)"


class BetweenExpression(Expression):
    """Represents BETWEEN operator (value BETWEEN low AND high)."""
    
    def __init__(self, expression: Expression, low: Expression, high: Expression, is_not: bool = False):
        self.expression = expression
        self.low = low
        self.high = high
        self.is_not = is_not
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        value = self.expression.evaluate(row)
        low_val = self.low.evaluate(row)
        high_val = self.high.evaluate(row)
        
        # Handle NULLs
        if value is None or low_val is None or high_val is None:
            return False
        
        result = low_val <= value <= high_val
        return not result if self.is_not else result
    
    def __repr__(self) -> str:
        not_str = " NOT" if self.is_not else ""
        return f"({self.expression}{not_str} BETWEEN {self.low} AND {self.high})"


class InExpression(Expression):
    """Represents IN operator (value IN (list))."""
    
    def __init__(self, expression: Expression, values: list, is_not: bool = False):
        self.expression = expression
        self.values = values  # List of Expression objects
        self.is_not = is_not
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        value = self.expression.evaluate(row)
        
        # Evaluate all values in the list
        value_list = [v.evaluate(row) for v in self.values]
        
        result = value in value_list
        return not result if self.is_not else result
    
    def __repr__(self) -> str:
        not_str = " NOT" if self.is_not else ""
        values_str = ', '.join(str(v) for v in self.values)
        return f"({self.expression}{not_str} IN ({values_str}))"


class LikeExpression(Expression):
    """Represents LIKE operator for pattern matching."""

    def __init__(self, expression: Expression, pattern: str, is_not: bool = False):
        """Initialize LIKE expression.

        Args:
            expression: Expression to match against pattern
            pattern: SQL pattern string (% for any chars, _ for single char)
            is_not: If True, check NOT LIKE
        """
        self.expression = expression
        self.pattern = pattern
        self.is_not = is_not

    def evaluate(self, row: Dict[str, Any]) -> bool:
        value = self.expression.evaluate(row)

        if value is None:
            return False

        # Convert to string
        value_str = str(value)

        # Convert SQL pattern to regex
        import re
        regex_pattern = self.pattern.replace('%', '.*').replace('_', '.')
        regex_pattern = '^' + regex_pattern + '$'

        result = re.match(regex_pattern, value_str, re.IGNORECASE) is not None
        return not result if self.is_not else result

    def __repr__(self) -> str:
        not_str = " NOT" if self.is_not else ""
        return f"({self.expression}{not_str} LIKE '{self.pattern}')"


class AggregateExpression(Expression):
    """Base class for aggregate functions (COUNT, SUM, AVG, MIN, MAX).

    Aggregate expressions work differently from regular expressions:
    - They operate on multiple rows, not a single row
    - They return a single value from a collection of values
    - They are evaluated by the executor, not in row-by-row evaluation
    """

    def __init__(self, function: str, expression: Expression = None, is_star: bool = False):
        """Initialize aggregate expression.

        Args:
            function: Aggregate function name (COUNT, SUM, AVG, MIN, MAX)
            expression: Expression to aggregate (e.g., column name)
            is_star: True for COUNT(*), False otherwise
        """
        self.function = function.upper()
        self.expression = expression
        self.is_star = is_star

        if self.function not in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
            raise ValueError(
                f"Invalid aggregate function: {function}. "
                f"Supported aggregate functions are: COUNT, SUM, AVG, MIN, MAX"
            )

        if self.function == 'COUNT' and not is_star and expression is None:
            raise ValueError(
                f"COUNT requires either * or a column name. "
                f"Usage: COUNT(*) or COUNT(column_name)"
            )

        if self.function != 'COUNT' and expression is None:
            raise ValueError(
                f"{self.function} requires a column name. "
                f"Usage: {self.function}(column_name)"
            )

        if self.function != 'COUNT' and is_star:
            raise ValueError(
                f"{self.function}(*) is not valid. Only COUNT(*) is allowed. "
                f"Use {self.function}(column_name) instead."
            )

    def evaluate(self, row: Dict[str, Any]) -> Any:
        """Aggregate expressions cannot be evaluated on single rows.

        This method should not be called directly. Use aggregate() instead.
        """
        raise NotImplementedError(
            f"Aggregate function {self.function}() cannot be evaluated on a single row. "
            f"Aggregate functions operate on multiple rows and return a single value. "
            f"This is an internal error - please report this issue."
        )

    def aggregate(self, rows: list) -> Any:
        """Aggregate over multiple rows.

        Args:
            rows: List of row dictionaries

        Returns:
            Aggregated value
        """
        if not rows and self.function != 'COUNT':
            return None

        if self.function == 'COUNT':
            if self.is_star:
                # COUNT(*) counts all rows
                return len(rows)
            else:
                # COUNT(column) counts non-NULL values
                count = 0
                for row in rows:
                    try:
                        value = self.expression.evaluate(row)
                        if value is not None:
                            count += 1
                    except (ValueError, KeyError):
                        # Column doesn't exist in this row, skip
                        pass
                return count

        # Extract values for aggregation
        values = []
        for row in rows:
            try:
                value = self.expression.evaluate(row)
                if value is not None:  # Skip NULL values
                    values.append(value)
            except (ValueError, KeyError):
                # Column doesn't exist, skip
                pass

        if not values:
            return None

        if self.function == 'SUM':
            # Sum numeric values
            try:
                return sum(values)
            except TypeError as e:
                raise ValueError(
                    f"SUM requires numeric values. "
                    f"Cannot compute SUM on column with non-numeric data types."
                )

        elif self.function == 'AVG':
            # Average numeric values
            try:
                return sum(values) / len(values)
            except TypeError as e:
                raise ValueError(
                    f"AVG requires numeric values. "
                    f"Cannot compute AVG on column with non-numeric data types."
                )

        elif self.function == 'MIN':
            return min(values)

        elif self.function == 'MAX':
            return max(values)

    def __repr__(self) -> str:
        if self.is_star:
            return f"{self.function}(*)"
        else:
            return f"{self.function}({self.expression})"


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
