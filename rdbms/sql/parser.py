"""SQL parser for converting tokens into command objects."""

from typing import List, Optional, Dict, Any
from .tokenizer import Token
from ..engine import DataType, ColumnDefinition


class ParsedCommand:
    """Base class for parsed SQL commands."""
    pass


class CreateTableCommand(ParsedCommand):
    """Parsed CREATE TABLE command."""
    
    def __init__(self, table_name: str, columns: List[ColumnDefinition]):
        self.table_name = table_name
        self.columns = columns
    
    def __repr__(self) -> str:
        return f"CreateTableCommand(table={self.table_name}, columns={len(self.columns)})"


class InsertCommand(ParsedCommand):
    """Parsed INSERT command."""
    
    def __init__(self, table_name: str, values: List[Any]):
        self.table_name = table_name
        self.values = values
    
    def __repr__(self) -> str:
        return f"InsertCommand(table={self.table_name}, values={self.values})"


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
            ValueError: If parsing fails
        """
        self.tokens = tokens
        self.position = 0
        
        if not tokens:
            raise ValueError("No tokens to parse")
        
        first_token = self.peek()
        
        if first_token.value == 'CREATE':
            return self._parse_create_table()
        elif first_token.value == 'INSERT':
            return self._parse_insert()
        elif first_token.value == 'SELECT':
            return self._parse_select()
        elif first_token.value == 'UPDATE':
            return self._parse_update()
        elif first_token.value == 'DELETE':
            return self._parse_delete()
        else:
            raise ValueError(f"Unexpected command: {first_token.value}")
    
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
            ValueError: If token doesn't match expectations
        """
        if self.position >= len(self.tokens):
            raise ValueError("Unexpected end of statement")
        
        token = self.tokens[self.position]
        
        if expected_value and token.value != expected_value:
            raise ValueError(f"Expected '{expected_value}', got '{token.value}'")
        
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected token type {expected_type}, got {token.type}")
        
        self.position += 1
        return token
    
    def _parse_create_table(self) -> CreateTableCommand:
        """Parse CREATE TABLE statement."""
        self.consume('CREATE')
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
            except ValueError as e:
                raise ValueError(f"Invalid data type: {type_token.value}")
            
            is_primary_key = False
            is_unique = False
            
            # Check for PRIMARY KEY
            if self.peek() and self.peek().value == 'PRIMARY':
                self.consume('PRIMARY')
                self.consume('KEY')
                is_primary_key = True
            # Check for UNIQUE
            elif self.peek() and self.peek().value == 'UNIQUE':
                self.consume('UNIQUE')
                is_unique = True
            
            columns.append(ColumnDefinition(col_name, col_type, is_primary_key, is_unique))
            
            next_token = self.peek()
            if next_token and next_token.value == ',':
                self.consume(',')
            else:
                break
        
        self.consume(')')
        
        # Optional semicolon
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
        
        return CreateTableCommand(table_name, columns)
    
    def _parse_insert(self) -> InsertCommand:
        """Parse INSERT statement."""
        self.consume('INSERT')
        self.consume('INTO')
        
        table_name_token = self.consume(expected_type='IDENTIFIER')
        table_name = table_name_token.value
        
        self.consume('VALUES')
        self.consume('(')
        
        values = []
        while True:
            value_token = self.peek()
            
            if value_token.type == 'NUMBER':
                self.consume()
                values.append(int(value_token.value))
            elif value_token.type == 'STRING':
                self.consume()
                values.append(value_token.value)
            elif value_token.value in ('TRUE', 'FALSE'):
                self.consume()
                values.append(value_token.value == 'TRUE')
            else:
                raise ValueError(f"Unexpected value token: {value_token}")
            
            next_token = self.peek()
            if next_token and next_token.value == ',':
                self.consume(',')
            else:
                break
        
        self.consume(')')
        
        # Optional semicolon
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
        
        return InsertCommand(table_name, values)
    
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
            if val_token.type == 'NUMBER':
                self.consume()
                where_val = int(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            else:
                raise ValueError(f"Unexpected WHERE value: {val_token}")
        
        # Optional semicolon
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
        
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
        if set_val_token.type == 'NUMBER':
            self.consume()
            set_val = int(set_val_token.value)
        elif set_val_token.type == 'STRING':
            self.consume()
            set_val = set_val_token.value
        elif set_val_token.value in ('TRUE', 'FALSE'):
            self.consume()
            set_val = set_val_token.value == 'TRUE'
        else:
            raise ValueError(f"Unexpected SET value: {set_val_token}")
        
        # Check for WHERE
        where_col = None
        where_val = None
        
        if self.peek() and self.peek().value == 'WHERE':
            self.consume('WHERE')
            
            col_token = self.consume(expected_type='IDENTIFIER')
            where_col = col_token.value
            
            self.consume('=')
            
            val_token = self.peek()
            if val_token.type == 'NUMBER':
                self.consume()
                where_val = int(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            else:
                raise ValueError(f"Unexpected WHERE value: {val_token}")
        
        # Optional semicolon
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
        
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
            if val_token.type == 'NUMBER':
                self.consume()
                where_val = int(val_token.value)
            elif val_token.type == 'STRING':
                self.consume()
                where_val = val_token.value
            elif val_token.value in ('TRUE', 'FALSE'):
                self.consume()
                where_val = val_token.value == 'TRUE'
            else:
                raise ValueError(f"Unexpected WHERE value: {val_token}")
        
        # Optional semicolon
        if self.peek() and self.peek().type == 'SEMICOLON':
            self.consume(';')
        
        return DeleteCommand(table_name, where_col, where_val)
