"""SQL parser for converting tokens into command objects."""

from typing import List, Optional, Dict, Any, Tuple
from .tokenizer import Token
from ..engine import DataType, ColumnDefinition
from .expressions import (
    Expression, LiteralExpression, ColumnExpression, ComparisonExpression,
    LogicalExpression, IsNullExpression, BetweenExpression, InExpression, LikeExpression,
    AggregateExpression
)
from .datetime_functions import DateTimeFunctionExpression


class ParserError(Exception):
    """Exception raised for parsing errors."""
    
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        super().__init__(self._format_error())
    
    def _format_error(self) -> str:
        """Format error message with context."""
        if self.token:
            return f"SyntaxError: {self.message} near '{self.token.value}'"
        return f"SyntaxError: {self.message}"


class ParsedCommand:
    """Base class for parsed SQL commands."""
    pass


# Database Management Commands
class CreateDatabaseCommand(ParsedCommand):
    """Parsed CREATE DATABASE command."""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
    
    def __repr__(self) -> str:
        return f"CreateDatabaseCommand(database={self.database_name})"


class DropDatabaseCommand(ParsedCommand):
    """Parsed DROP DATABASE command."""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
    
    def __repr__(self) -> str:
        return f"DropDatabaseCommand(database={self.database_name})"


class UseDatabaseCommand(ParsedCommand):
    """Parsed USE DATABASE command."""
    
    def __init__(self, database_name: str):
        self.database_name = database_name
    
    def __repr__(self) -> str:
        return f"UseDatabaseCommand(database={self.database_name})"


class ShowDatabasesCommand(ParsedCommand):
    """Parsed SHOW DATABASES command."""
    
    def __repr__(self) -> str:
        return "ShowDatabasesCommand()"


# Table Management Commands
class CreateTableCommand(ParsedCommand):
    """Parsed CREATE TABLE command."""
    
    def __init__(self, table_name: str, columns: List[ColumnDefinition]):
        self.table_name = table_name
        self.columns = columns
    
    def __repr__(self) -> str:
        return f"CreateTableCommand(table={self.table_name}, columns={len(self.columns)})"


class DropTableCommand(ParsedCommand):
    """Parsed DROP TABLE command."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def __repr__(self) -> str:
        return f"DropTableCommand(table={self.table_name})"


class ShowTablesCommand(ParsedCommand):
    """Parsed SHOW TABLES command."""
    
    def __repr__(self) -> str:
        return "ShowTablesCommand()"


class DescribeTableCommand(ParsedCommand):
    """Parsed DESCRIBE table command."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def __repr__(self) -> str:
        return f"DescribeTableCommand(table={self.table_name})"


# Data Manipulation Commands
class InsertCommand(ParsedCommand):
    """Parsed INSERT command."""
    
    def __init__(self, table_name: str, columns: Optional[List[str]], values: List[Any]):
        self.table_name = table_name
        self.columns = columns
        self.values = values
    
    def __repr__(self) -> str:
        return f"InsertCommand(table={self.table_name}, columns={self.columns}, values={self.values})"


class SelectCommand(ParsedCommand):
    """Parsed SELECT command."""

    def __init__(self, columns: List[str], table_name: str, where_clause: Optional[Expression] = None,
                 join_table: Optional[str] = None, join_left_col: Optional[str] = None,
                 join_right_col: Optional[str] = None, join_type: str = 'INNER',
                 order_by: Optional[List[Tuple[str, str]]] = None,
                 limit: Optional[int] = None, offset: Optional[int] = None,
                 distinct: bool = False,
                 aggregates: Optional[List[Tuple[str, AggregateExpression]]] = None,
                 group_by: Optional[List[str]] = None,
                 having_clause: Optional[Expression] = None,
                 where_col: Optional[str] = None, where_val: Any = None):
        self.columns = columns
        self.table_name = table_name
        self.where_clause = where_clause  # Expression object for WHERE clause
        self.join_table = join_table
        self.join_left_col = join_left_col
        self.join_right_col = join_right_col
        self.join_type = join_type.upper()  # INNER, LEFT, RIGHT, FULL
        self.order_by = order_by  # List of (column_name, direction) tuples
        self.limit = limit  # Max number of rows to return
        self.offset = offset  # Number of rows to skip
        self.distinct = distinct  # Remove duplicate rows
        self.aggregates = aggregates  # List of (alias, AggregateExpression) tuples
        self.group_by = group_by  # List of column names to group by
        self.having_clause = having_clause  # Expression for HAVING clause (filter groups)
        # Backward compatibility
        self.where_col = where_col
        self.where_val = where_val

    def __repr__(self) -> str:
        join_info = f", join_type={self.join_type}" if self.join_table else ""
        return f"SelectCommand(columns={self.columns}, table={self.table_name}{join_info})"


class UpdateCommand(ParsedCommand):
    """Parsed UPDATE command."""

    def __init__(self, table_name: str, set_col: str, set_val: Any,
                 where_clause: Optional[Expression] = None,
                 where_col: Optional[str] = None, where_val: Any = None):
        self.table_name = table_name
        self.set_col = set_col
        self.set_val = set_val
        self.where_clause = where_clause
        # Backward compatibility
        self.where_col = where_col
        self.where_val = where_val

    def __repr__(self) -> str:
        return f"UpdateCommand(table={self.table_name}, set={self.set_col}={self.set_val})"


class DeleteCommand(ParsedCommand):
    """Parsed DELETE command."""

    def __init__(self, table_name: str, where_clause: Optional[Expression] = None,
                 where_col: Optional[str] = None, where_val: Any = None):
        self.table_name = table_name
        self.where_clause = where_clause
        # Backward compatibility
        self.where_col = where_col
        self.where_val = where_val

    def __repr__(self) -> str:
        return f"DeleteCommand(table={self.table_name})"


class Parser:
    """Parser for SQL-like statements."""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.position = 0
    
    def parse(self, tokens: List[Token]) -> ParsedCommand:
        """Parse tokens into a command object.
        
        Args:
            tokens: List of tokens from tokenizer
        
        Returns:
            Parsed command object
        
        Raises:
            ParserError: If parsing fails
        """
        self.tokens = tokens
        self.position = 0
        
        if not tokens:
            raise ParserError("No tokens to parse")
        
        first_token = self.peek()
        
        # Route to appropriate parser based on first keyword
        if first_token.value == 'CREATE':
            return self._parse_create()
        elif first_token.value == 'DROP':
            return self._parse_drop()
        elif first_token.value == 'USE':
            return self._parse_use()
        elif first_token.value == 'SHOW':
            return self._parse_show()
        elif first_token.value in ('DESCRIBE', 'DESC'):
            return self._parse_describe()
        elif first_token.value == 'INSERT':
            return self._parse_insert()
        elif first_token.value == 'SELECT':
            return self._parse_select()
        elif first_token.value == 'UPDATE':
            return self._parse_update()
        elif first_token.value == 'DELETE':
            return self._parse_delete()
        else:
            raise ParserError(f"Unexpected command: {first_token.value}", first_token)
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at a token without consuming it."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def consume(self, expected_value: Optional[str] = None, expected_type: Optional[str] = None) -> Token:
        """Consume and return the next token.
        
        Args:
            expected_value: Expected token value (optional)
            expected_type: Expected token type (optional)
        
        Returns:
            Consumed token
        
        Raises:
            ParserError: If token doesn't match expectations
        """
        if self.position >= len(self.tokens):
            if expected_value:
                raise ParserError(f"Expected '{expected_value}' but reached end of statement")
            raise ParserError("Unexpected end of statement")
        
        token = self.tokens[self.position]
        
        if expected_value and token.value != expected_value:
            raise ParserError(f"Expected '{expected_value}'", token)
        
        if expected_type and token.type != expected_type:
            raise ParserError(f"Expected {expected_type}", token)
        
        self.position += 1
        return token
    
    def _parse_create(self) -> ParsedCommand:
        """Parse CREATE command (DATABASE or TABLE)."""
        self.consume('CREATE')
        
        next_token = self.peek()
        if not next_token:
            raise ParserError("Expected DATABASE or TABLE after CREATE")
        
        if next_token.value == 'DATABASE':
            self.consume('DATABASE')
            db_name = self.consume(expected_type='IDENTIFIER').value
            self._consume_optional_semicolon()
            return CreateDatabaseCommand(db_name)
        elif next_token.value == 'TABLE':
            return self._parse_create_table()
        else:
            raise ParserError("Expected DATABASE or TABLE after CREATE", next_token)
    
    def _parse_drop(self) -> ParsedCommand:
        """Parse DROP command (DATABASE or TABLE)."""
        self.consume('DROP')
        
        next_token = self.peek()
        if not next_token:
            raise ParserError("Expected DATABASE or TABLE after DROP")
        
        if next_token.value == 'DATABASE':
            self.consume('DATABASE')
            db_name = self.consume(expected_type='IDENTIFIER').value
            self._consume_optional_semicolon()
            return DropDatabaseCommand(db_name)
        elif next_token.value == 'TABLE':
            self.consume('TABLE')
            table_name = self.consume(expected_type='IDENTIFIER').value
            self._consume_optional_semicolon()
            return DropTableCommand(table_name)
        else:
            raise ParserError("Expected DATABASE or TABLE after DROP", next_token)
    
    def _parse_use(self) -> UseDatabaseCommand:
        """Parse USE command."""
        self.consume('USE')
        db_name = self.consume(expected_type='IDENTIFIER').value
        self._consume_optional_semicolon()
        return UseDatabaseCommand(db_name)
    
    def _parse_show(self) -> ParsedCommand:
        """Parse SHOW command (DATABASES or TABLES)."""
        self.consume('SHOW')
        
        next_token = self.peek()
        if not next_token:
            raise ParserError("Expected DATABASES or TABLES after SHOW")
        
        if next_token.value == 'DATABASES':
            self.consume('DATABASES')
            self._consume_optional_semicolon()
            return ShowDatabasesCommand()
        elif next_token.value == 'TABLES':
            self.consume('TABLES')
            self._consume_optional_semicolon()
            return ShowTablesCommand()
        else:
            raise ParserError("Expected DATABASES or TABLES after SHOW", next_token)
    
    def _parse_describe(self) -> DescribeTableCommand:
        """Parse DESCRIBE command."""
        # DESCRIBE or DESC
        self.consume()
        table_name = self.consume(expected_type='IDENTIFIER').value
        self._consume_optional_semicolon()
        return DescribeTableCommand(table_name)
    
    def _parse_create_table(self) -> CreateTableCommand:
        """Parse CREATE TABLE statement."""
        self.consume('TABLE')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        self.consume('(')
        
        columns = []
        while True:
            col_name_token = self.consume(expected_type='IDENTIFIER')
            col_name = col_name_token.value
            
            type_token = self.consume(expected_type='KEYWORD')
            try:
                col_type = DataType.from_string(type_token.value)
            except ValueError:
                raise ParserError(f"Invalid data type '{type_token.value}'. Supported types: INT, STRING, BOOL", type_token)
            
            is_primary_key = False
            is_unique = False
            foreign_key_table = None
            foreign_key_column = None

            # Check for PRIMARY KEY
            if self.peek() and self.peek().value == 'PRIMARY':
                self.consume('PRIMARY')
                self.consume('KEY')
                is_primary_key = True
            # Check for UNIQUE
            elif self.peek() and self.peek().value == 'UNIQUE':
                self.consume('UNIQUE')
                is_unique = True

            # Check for REFERENCES (foreign key)
            if self.peek() and self.peek().value == 'REFERENCES':
                self.consume('REFERENCES')
                fk_table_token = self.consume(expected_type='IDENTIFIER')
                foreign_key_table = fk_table_token.value
                self.consume('(')
                fk_col_token = self.consume(expected_type='IDENTIFIER')
                foreign_key_column = fk_col_token.value
                self.consume(')')

            columns.append(ColumnDefinition(col_name, col_type, is_primary_key, is_unique, foreign_key_table, foreign_key_column))
            
            next_token = self.peek()
            if next_token and next_token.value == ',':
                self.consume(',')
            else:
                break
        
        self.consume(')')
        self._consume_optional_semicolon()
        
        return CreateTableCommand(table_name, columns)
    
    def _parse_insert(self) -> InsertCommand:
        """Parse INSERT statement."""
        self.consume('INSERT')
        self.consume('INTO')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        # Check for optional column specification
        columns = None
        if self.peek() and self.peek().type == 'LPAREN':
            # Could be column list or VALUES
            # Peek ahead to see if there's a VALUES keyword
            lookahead_pos = self.position + 1
            is_column_list = False
            
            # Simple lookahead: if we see identifiers followed by ), assume column list
            while lookahead_pos < len(self.tokens):
                lookahead_token = self.tokens[lookahead_pos]
                if lookahead_token.type == 'RPAREN':
                    # Check if next token is VALUES
                    if lookahead_pos + 1 < len(self.tokens) and self.tokens[lookahead_pos + 1].value == 'VALUES':
                        is_column_list = True
                    break
                elif lookahead_token.type not in ('IDENTIFIER', 'COMMA'):
                    break
                lookahead_pos += 1
            
            if is_column_list:
                self.consume('(')
                columns = []
                while True:
                    col_token = self.consume(expected_type='IDENTIFIER')
                    columns.append(col_token.value)
                    
                    if self.peek() and self.peek().value == ',':
                        self.consume(',')
                    else:
                        break
                self.consume(')')
        
        self.consume('VALUES')
        self.consume('(')
        
        values = []
        while True:
            value_token = self.peek()
            
            if not value_token:
                raise ParserError("Expected value in VALUES clause")
            
            if value_token.type == 'NUMBER':
                self.consume()
                # Try to parse as int first, then float
                try:
                    values.append(int(value_token.value))
                except ValueError:
                    values.append(float(value_token.value))
            elif value_token.type == 'STRING':
                self.consume()
                values.append(value_token.value)
            elif value_token.value in ('TRUE', 'FALSE'):
                self.consume()
                values.append(value_token.value == 'TRUE')
            elif value_token.value == 'NULL':
                self.consume()
                values.append(None)
            else:
                raise ParserError(f"Unexpected value in VALUES clause", value_token)
            
            next_token = self.peek()
            if next_token and next_token.value == ',':
                self.consume(',')
            else:
                break
        
        self.consume(')')
        self._consume_optional_semicolon()
        
        return InsertCommand(table_name, columns, values)
    
    def _parse_select(self) -> SelectCommand:
        """Parse SELECT statement."""
        self.consume('SELECT')

        # Check for DISTINCT
        distinct = False
        if self.peek() and self.peek().value == 'DISTINCT':
            self.consume('DISTINCT')
            distinct = True

        # Parse columns and aggregate functions
        columns = []
        aggregates = []  # List of (alias, AggregateExpression)

        if self.peek() and self.peek().type == 'STAR':
            self.consume('*')
            columns = None  # Select all
        else:
            while True:
                # Check if this is an aggregate function
                if self._is_aggregate_function():
                    alias, agg_expr = self._parse_aggregate_function()
                    aggregates.append((alias, agg_expr))
                else:
                    # Handle table.column syntax
                    col_token = self.consume(expected_type='IDENTIFIER')
                    col_name = col_token.value

                    if self.peek() and self.peek().type == 'DOT':
                        self.consume('.')
                        actual_col_token = self.consume(expected_type='IDENTIFIER')
                        col_name = actual_col_token.value

                    columns.append(col_name)

                if self.peek() and self.peek().value == ',':
                    self.consume(',')
                else:
                    break

        self.consume('FROM')
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value

        # Check for JOIN (INNER, LEFT, RIGHT, FULL OUTER, etc.)
        join_table = None
        join_left_col = None
        join_right_col = None
        join_type = 'INNER'  # Default join type

        next_token = self.peek()
        if next_token and next_token.value in ('INNER', 'LEFT', 'RIGHT', 'FULL', 'JOIN'):
            # Parse join type
            if next_token.value == 'INNER':
                self.consume('INNER')
                join_type = 'INNER'
            elif next_token.value == 'LEFT':
                self.consume('LEFT')
                join_type = 'LEFT'
                # Check for optional OUTER keyword
                if self.peek() and self.peek().value == 'OUTER':
                    self.consume('OUTER')
            elif next_token.value == 'RIGHT':
                self.consume('RIGHT')
                join_type = 'RIGHT'
                # Check for optional OUTER keyword
                if self.peek() and self.peek().value == 'OUTER':
                    self.consume('OUTER')
            elif next_token.value == 'FULL':
                self.consume('FULL')
                join_type = 'FULL'
                # Require OUTER keyword for FULL OUTER JOIN
                self.consume('OUTER')
            elif next_token.value == 'JOIN':
                # Just "JOIN" defaults to INNER JOIN
                join_type = 'INNER'

            self.consume('JOIN')

            join_table_token = self.consume(expected_type='IDENTIFIER')
            join_table = join_table_token.value

            self.consume('ON')

            # Parse left side of join condition
            left_table_token = self.consume(expected_type='IDENTIFIER')
            self.consume('.')
            left_col_token = self.consume(expected_type='IDENTIFIER')
            join_left_col = f"{left_table_token.value}.{left_col_token.value}"

            self.consume('=')

            # Parse right side of join condition
            right_table_token = self.consume(expected_type='IDENTIFIER')
            self.consume('.')
            right_col_token = self.consume(expected_type='IDENTIFIER')
            join_right_col = f"{right_table_token.value}.{right_col_token.value}"

        # Check for WHERE
        where_clause = None
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            where_clause = self._parse_where_expression()

        # Check for GROUP BY
        group_by = None
        if self.peek() and self.peek().value == 'GROUP':
            self.consume('GROUP')
            self.consume('BY')
            group_by = []
            while True:
                col_token = self.consume(expected_type='IDENTIFIER')
                group_by.append(col_token.value)

                if self.peek() and self.peek().value == ',':
                    self.consume(',')
                else:
                    break

        # Check for HAVING
        having_clause = None
        if self.peek() and self.peek().value == 'HAVING':
            self.consume('HAVING')
            having_clause = self._parse_where_expression()

        # Check for ORDER BY
        order_by = self._parse_order_by()

        # Check for LIMIT
        limit = None
        if self.peek() and self.peek().value == 'LIMIT':
            self.consume('LIMIT')
            limit_token = self.consume(expected_type='NUMBER')
            limit = int(limit_token.value)
            if limit < 0:
                raise ParserError("LIMIT must be non-negative", limit_token)

        # Check for OFFSET
        offset = None
        if self.peek() and self.peek().value == 'OFFSET':
            self.consume('OFFSET')
            offset_token = self.consume(expected_type='NUMBER')
            offset = int(offset_token.value)
            if offset < 0:
                raise ParserError("OFFSET must be non-negative", offset_token)

        self._consume_optional_semicolon()

        return SelectCommand(columns, table_name, where_clause=where_clause,
                           join_table=join_table, join_left_col=join_left_col,
                           join_right_col=join_right_col, join_type=join_type,
                           order_by=order_by, limit=limit, offset=offset, distinct=distinct,
                           aggregates=aggregates if aggregates else None,
                           group_by=group_by, having_clause=having_clause)
    
    def _parse_update(self) -> UpdateCommand:
        """Parse UPDATE statement."""
        self.consume('UPDATE')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        self.consume('SET')
        
        set_col_token = self.consume(expected_type='IDENTIFIER')
        set_col = set_col_token.value
        
        self.consume('=')
        
        set_val_token = self.peek()
        if not set_val_token:
            raise ParserError("Expected value in SET clause")
        
        if set_val_token.type == 'NUMBER':
            self.consume()
            try:
                set_val = int(set_val_token.value)
            except ValueError:
                set_val = float(set_val_token.value)
        elif set_val_token.type == 'STRING':
            self.consume()
            set_val = set_val_token.value
        elif set_val_token.value in ('TRUE', 'FALSE'):
            self.consume()
            set_val = set_val_token.value == 'TRUE'
        elif set_val_token.value == 'NULL':
            self.consume()
            set_val = None
        else:
            raise ParserError(f"Unexpected value in SET clause", set_val_token)
        
        # Check for WHERE
        where_clause = None
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            where_clause = self._parse_where_expression()

        self._consume_optional_semicolon()

        return UpdateCommand(table_name, set_col, set_val, where_clause=where_clause)
    
    def _parse_delete(self) -> DeleteCommand:
        """Parse DELETE statement."""
        self.consume('DELETE')
        self.consume('FROM')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        # Check for WHERE
        where_clause = None
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            where_clause = self._parse_where_expression()

        self._consume_optional_semicolon()

        return DeleteCommand(table_name, where_clause=where_clause)
    
    def _consume_optional_semicolon(self):
        """Consume optional semicolon at end of statement."""
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')

    def _parse_where_expression(self) -> Expression:
        """Parse WHERE clause expression with full operator support.

        Returns:
            Expression tree representing the WHERE condition
        """
        return self._parse_or_expression()

    def _parse_or_expression(self) -> Expression:
        """Parse OR expression (lowest precedence)."""
        left = self._parse_and_expression()

        operands = [left]
        while self.peek() and self.peek().value == 'OR':
            self.consume('OR')
            operands.append(self._parse_and_expression())

        if len(operands) == 1:
            return operands[0]
        return LogicalExpression('OR', operands)

    def _parse_and_expression(self) -> Expression:
        """Parse AND expression (higher precedence than OR)."""
        left = self._parse_not_expression()

        operands = [left]
        while self.peek() and self.peek().value == 'AND':
            self.consume('AND')
            operands.append(self._parse_not_expression())

        if len(operands) == 1:
            return operands[0]
        return LogicalExpression('AND', operands)

    def _parse_not_expression(self) -> Expression:
        """Parse NOT expression (highest precedence)."""
        if self.peek() and self.peek().value == 'NOT':
            self.consume('NOT')
            operand = self._parse_not_expression()  # Allow chained NOT
            return LogicalExpression('NOT', [operand])

        return self._parse_comparison_expression()

    def _parse_comparison_expression(self) -> Expression:
        """Parse comparison expression (=, !=, <, >, <=, >=, IS NULL, LIKE, IN, BETWEEN)."""
        left = self._parse_primary_expression()

        next_token = self.peek()
        if not next_token:
            return left

        # Handle IS NULL / IS NOT NULL
        if next_token.value == 'IS':
            self.consume('IS')
            is_not = False
            if self.peek() and self.peek().value == 'NOT':
                self.consume('NOT')
                is_not = True
            self.consume('NULL')
            return IsNullExpression(left, is_not)

        # Handle LIKE / NOT LIKE
        if next_token.value == 'LIKE':
            self.consume('LIKE')
            pattern_token = self.consume(expected_type='STRING')
            return LikeExpression(left, pattern_token.value, is_not=False)

        # Handle NOT LIKE
        if next_token.value == 'NOT':
            lookahead = self.peek(1)
            if lookahead and lookahead.value == 'LIKE':
                self.consume('NOT')
                self.consume('LIKE')
                pattern_token = self.consume(expected_type='STRING')
                return LikeExpression(left, pattern_token.value, is_not=True)

        # Handle IN / NOT IN
        if next_token.value == 'IN':
            self.consume('IN')
            self.consume('(')
            values = []
            while True:
                values.append(self._parse_primary_expression())
                if self.peek() and self.peek().value == ',':
                    self.consume(',')
                else:
                    break
            self.consume(')')
            return InExpression(left, values, is_not=False)

        # Handle NOT IN
        if next_token.value == 'NOT':
            lookahead = self.peek(1)
            if lookahead and lookahead.value == 'IN':
                self.consume('NOT')
                self.consume('IN')
                self.consume('(')
                values = []
                while True:
                    values.append(self._parse_primary_expression())
                    if self.peek() and self.peek().value == ',':
                        self.consume(',')
                    else:
                        break
                self.consume(')')
                return InExpression(left, values, is_not=True)

        # Handle BETWEEN / NOT BETWEEN
        if next_token.value == 'BETWEEN':
            self.consume('BETWEEN')
            low = self._parse_primary_expression()
            self.consume('AND')
            high = self._parse_primary_expression()
            return BetweenExpression(left, low, high, is_not=False)

        # Handle NOT BETWEEN
        if next_token.value == 'NOT':
            lookahead = self.peek(1)
            if lookahead and lookahead.value == 'BETWEEN':
                self.consume('NOT')
                self.consume('BETWEEN')
                low = self._parse_primary_expression()
                self.consume('AND')
                high = self._parse_primary_expression()
                return BetweenExpression(left, low, high, is_not=True)

        # Handle comparison operators (=, !=, <>, <, >, <=, >=)
        if next_token.type == 'COMPARISON' or next_token.type == 'EQUALS':
            operator = next_token.value
            self.consume()
            right = self._parse_primary_expression()
            return ComparisonExpression(operator, left, right)

        # If no operator found, return the left side (single expression)
        return left

    def _parse_primary_expression(self) -> Expression:
        """Parse primary expression (column, literal, or parenthesized expression)."""
        token = self.peek()

        if not token:
            raise ParserError("Expected expression")

        # Handle parentheses
        if token.type == 'LPAREN':
            self.consume('(')
            expr = self._parse_where_expression()
            self.consume(')')
            return expr

        # Handle literals
        if token.type == 'NUMBER':
            self.consume()
            try:
                value = int(token.value)
            except ValueError:
                value = float(token.value)
            return LiteralExpression(value)

        if token.type == 'STRING':
            self.consume()
            return LiteralExpression(token.value)

        if token.value in ('TRUE', 'FALSE'):
            self.consume()
            return LiteralExpression(token.value == 'TRUE')

        if token.value == 'NULL':
            self.consume()
            return LiteralExpression(None)

        # Handle datetime function calls
        if token.type == 'IDENTIFIER' and self._is_datetime_function():
            return self._parse_datetime_function()

        # Handle column reference
        if token.type == 'IDENTIFIER':
            self.consume()
            return ColumnExpression(token.value)

        raise ParserError(f"Unexpected token in expression", token)

    def _parse_order_by(self) -> List[Tuple[str, str]]:
        """Parse ORDER BY clause.

        Returns:
            List of (column_name, direction) tuples where direction is 'ASC' or 'DESC'
        """
        order_by = []

        if self.peek() and self.peek().value == 'ORDER':
            self.consume('ORDER')
            self.consume('BY')

            while True:
                col_token = self.consume(expected_type='IDENTIFIER')
                col_name = col_token.value

                # Check for ASC/DESC
                direction = 'ASC'  # Default
                if self.peek() and self.peek().value in ('ASC', 'DESC'):
                    direction = self.consume().value

                order_by.append((col_name, direction))

                # Check for more columns
                if self.peek() and self.peek().value == ',':
                    self.consume(',')
                else:
                    break

        return order_by if order_by else None

    def _is_aggregate_function(self) -> bool:
        """Check if next tokens form an aggregate function call."""
        token = self.peek()
        # Accept both IDENTIFIER and KEYWORD tokens for aggregate functions
        if not token or token.type not in ('IDENTIFIER', 'KEYWORD'):
            return False

        func_name = token.value.upper()
        if func_name not in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
            return False

        # Check for opening parenthesis
        next_token = self.peek(1)
        return next_token and next_token.type == 'LPAREN'

    def _parse_aggregate_function(self) -> Tuple[str, AggregateExpression]:
        """Parse aggregate function (COUNT, SUM, AVG, MIN, MAX).

        Returns:
            Tuple of (alias, AggregateExpression)
        """
        # Accept both IDENTIFIER and KEYWORD tokens for function name
        func_token = self.consume()
        if func_token.type not in ('IDENTIFIER', 'KEYWORD'):
            raise ParserError(f"Expected aggregate function name", func_token)

        func_name = func_token.value.upper()

        # Validate it's a recognized aggregate function
        if func_name not in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
            raise ParserError(f"Unknown aggregate function: {func_name}", func_token)

        self.consume('(')

        is_star = False
        expression = None

        if self.peek() and self.peek().type == 'STAR':
            # COUNT(*)
            self.consume('*')
            is_star = True
            if func_name != 'COUNT':
                raise ParserError(f"{func_name}(*) is not valid, only COUNT(*) is allowed", func_token)
        else:
            # Parse expression (usually a column)
            expression = self._parse_aggregate_expression_argument()

        self.consume(')')

        # Create aggregate expression
        try:
            agg_expr = AggregateExpression(func_name, expression, is_star)
        except ValueError as e:
            raise ParserError(str(e), func_token)

        # Generate alias (e.g., "COUNT(*)", "SUM(amount)")
        if is_star:
            alias = f"{func_name}(*)"
        else:
            alias = f"{func_name}({expression})"

        return alias, agg_expr

    def _parse_aggregate_expression_argument(self) -> Expression:
        """Parse the argument inside an aggregate function.

        Supports:
        - Simple column names: COUNT(id)
        - Table-qualified columns: COUNT(users.id)
        - Keyword tokens: (in case column names match SQL keywords)
        """
        token = self.peek()

        if not token:
            raise ParserError("Expected column name in aggregate function")

        # Accept both IDENTIFIER and KEYWORD tokens for column names
        if token.type in ('IDENTIFIER', 'KEYWORD'):
            first_token = self.consume()
            first_name = first_token.value

            # Check for table.column syntax
            if self.peek() and self.peek().type == 'DOT':
                self.consume('.')  # Consume the dot
                second_token = self.peek()

                if not second_token or second_token.type not in ('IDENTIFIER', 'KEYWORD'):
                    raise ParserError("Expected column name after '.'", second_token)

                self.consume()
                second_name = second_token.value
                # Return fully qualified column name
                return ColumnExpression(f"{first_name}.{second_name}")

            # Simple column reference
            return ColumnExpression(first_name)

        raise ParserError(f"Unexpected token in aggregate function: {token.value}", token)

    def _is_datetime_function(self) -> bool:
        """Check if next tokens form a datetime function call."""
        token = self.peek()
        if not token or token.type != 'IDENTIFIER':
            return False

        func_name = token.value.upper()
        datetime_functions = (
            'NOW', 'CURRENT_DATE', 'CURRENT_TIME',
            'DATE', 'TIME', 'YEAR', 'MONTH', 'DAY',
            'HOUR', 'MINUTE', 'SECOND',
            'DATE_ADD', 'DATE_SUB', 'DATEDIFF'
        )
        if func_name not in datetime_functions:
            return False

        # Check for opening parenthesis
        next_token = self.peek(1)
        return next_token and next_token.type == 'LPAREN'

    def _parse_datetime_function(self) -> DateTimeFunctionExpression:
        """Parse datetime function (NOW, DATE_ADD, etc.).

        Returns:
            DateTimeFunctionExpression
        """
        func_token = self.consume(expected_type='IDENTIFIER')
        func_name = func_token.value.upper()

        self.consume('(')

        arguments = []

        # Parse arguments
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                arg_expr = self._parse_primary_expression()
                arguments.append(arg_expr)

                if self.peek() and self.peek().value == ',':
                    self.consume(',')
                else:
                    break

        self.consume(')')

        return DateTimeFunctionExpression(func_name, arguments)
