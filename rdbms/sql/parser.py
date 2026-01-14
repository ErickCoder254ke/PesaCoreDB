"""SQL parser for converting tokens into command objects."""

from typing import List, Optional, Dict, Any
from .tokenizer import Token
from ..engine import DataType, ColumnDefinition


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
    
    def __init__(self, columns: List[str], table_name: str, where_col: Optional[str] = None,
                 where_val: Any = None, join_table: Optional[str] = None,
                 join_left_col: Optional[str] = None, join_right_col: Optional[str] = None):
        self.columns = columns
        self.table_name = table_name
        self.where_col = where_col
        self.where_val = where_val
        self.join_table = join_table
        self.join_left_col = join_left_col
        self.join_right_col = join_right_col
    
    def __repr__(self) -> str:
        return f"SelectCommand(columns={self.columns}, table={self.table_name})"


class UpdateCommand(ParsedCommand):
    """Parsed UPDATE command."""
    
    def __init__(self, table_name: str, set_col: str, set_val: Any,
                 where_col: Optional[str] = None, where_val: Any = None):
        self.table_name = table_name
        self.set_col = set_col
        self.set_val = set_val
        self.where_col = where_col
        self.where_val = where_val
    
    def __repr__(self) -> str:
        return f"UpdateCommand(table={self.table_name}, set={self.set_col}={self.set_val})"


class DeleteCommand(ParsedCommand):
    """Parsed DELETE command."""
    
    def __init__(self, table_name: str, where_col: Optional[str] = None, where_val: Any = None):
        self.table_name = table_name
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
        
        # Parse columns
        columns = []
        if self.peek() and self.peek().type == 'STAR':
            self.consume('*')
            columns = None  # Select all
        else:
            while True:
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
        
        # Check for JOIN
        join_table = None
        join_left_col = None
        join_right_col = None
        
        if self.peek() and self.peek().value == 'INNER':
            self.consume('INNER')
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
        where_col = None
        where_val = None
        
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            
            col_token = self.consume(expected_type='IDENTIFIER')
            where_col = col_token.value
            
            self.consume('=')
            
            val_token = self.peek()
            if not val_token:
                raise ParserError("Expected value in WHERE clause")
            
            if val_token.type == 'NUMBER':
                self.consume()
                try:
                    where_val = int(val_token.value)
                except ValueError:
                    where_val = float(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            elif val_token.value == 'NULL':
                self.consume()
                where_val = None
            else:
                raise ParserError(f"Unexpected value in WHERE clause", val_token)
        
        self._consume_optional_semicolon()
        
        return SelectCommand(columns, table_name, where_col, where_val, join_table, join_left_col, join_right_col)
    
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
        where_col = None
        where_val = None
        
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            
            col_token = self.consume(expected_type='IDENTIFIER')
            where_col = col_token.value
            
            self.consume('=')
            
            val_token = self.peek()
            if not val_token:
                raise ParserError("Expected value in WHERE clause")
            
            if val_token.type == 'NUMBER':
                self.consume()
                try:
                    where_val = int(val_token.value)
                except ValueError:
                    where_val = float(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            elif val_token.value == 'NULL':
                self.consume()
                where_val = None
            else:
                raise ParserError(f"Unexpected value in WHERE clause", val_token)
        
        self._consume_optional_semicolon()
        
        return UpdateCommand(table_name, set_col, set_val, where_col, where_val)
    
    def _parse_delete(self) -> DeleteCommand:
        """Parse DELETE statement."""
        self.consume('DELETE')
        self.consume('FROM')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        # Check for WHERE
        where_col = None
        where_val = None
        
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            
            col_token = self.consume(expected_type='IDENTIFIER')
            where_col = col_token.value
            
            self.consume('=')
            
            val_token = self.peek()
            if not val_token:
                raise ParserError("Expected value in WHERE clause")
            
            if val_token.type == 'NUMBER':
                self.consume()
                try:
                    where_val = int(val_token.value)
                except ValueError:
                    where_val = float(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            elif val_token.value == 'NULL':
                self.consume()
                where_val = None
            else:
                raise ParserError(f"Unexpected value in WHERE clause", val_token)
        
        self._consume_optional_semicolon()
        
        return DeleteCommand(table_name, where_col, where_val)
    
    def _consume_optional_semicolon(self):
        """Consume optional semicolon at end of statement."""
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
