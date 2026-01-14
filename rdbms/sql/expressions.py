"""Expression classes for WHERE clause evaluation."""

from typing import Any, Dict
from abc import ABC, abstractmethod


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
        if self.column_name not in row:
            raise ValueError(f"Column '{self.column_name}' not found in row")
        return row[self.column_name]
    
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
            raise ValueError(f"Invalid aggregate function: {function}")

        if self.function == 'COUNT' and not is_star and expression is None:
            raise ValueError("COUNT requires either * or a column")

        if self.function != 'COUNT' and expression is None:
            raise ValueError(f"{self.function} requires a column")

    def evaluate(self, row: Dict[str, Any]) -> Any:
        """Aggregate expressions cannot be evaluated on single rows.

        This method should not be called directly. Use aggregate() instead.
        """
        raise NotImplementedError(
            f"Aggregate function {self.function} cannot be evaluated on a single row. "
            "Use aggregate() method instead."
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
            except TypeError:
                raise ValueError(f"SUM requires numeric values")

        elif self.function == 'AVG':
            # Average numeric values
            try:
                return sum(values) / len(values)
            except TypeError:
                raise ValueError(f"AVG requires numeric values")

        elif self.function == 'MIN':
            return min(values)

        elif self.function == 'MAX':
            return max(values)

    def __repr__(self) -> str:
        if self.is_star:
            return f"{self.function}(*)"
        else:
            return f"{self.function}({self.expression})"
