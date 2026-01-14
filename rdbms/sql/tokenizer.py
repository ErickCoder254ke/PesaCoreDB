"""SQL tokenizer for breaking SQL statements into tokens."""

import re
from typing import List


class Token:
    """Represents a single token in a SQL statement."""
    
    def __init__(self, type_: str, value: str, position: int = 0):
        self.type = type_
        self.value = value
        self.position = position
    
    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False


class TokenizerError(Exception):
    """Exception raised for tokenization errors."""
    
    def __init__(self, message: str, position: int = 0, sql: str = ""):
        self.message = message
        self.position = position
        self.sql = sql
        super().__init__(self._format_error())
    
    def _format_error(self) -> str:
        """Format error message with context."""
        if not self.sql:
            return f"SyntaxError: {self.message}"
        
        # Show the problematic part of SQL
        start = max(0, self.position - 20)
        end = min(len(self.sql), self.position + 20)
        context = self.sql[start:end]
        
        return f"SyntaxError: {self.message} at position {self.position}\n  {context}\n  {' ' * (self.position - start)}^"


class Tokenizer:
    """Tokenizes SQL-like statements."""
    
    # Token patterns (order matters!)
    TOKEN_PATTERNS = [
        ('NUMBER', r'-?\d+(?:\.\d+)?'),  # Support decimals for future use
        ('STRING', r"'[^']*'"),
        ('COMPARISON', r'(?:<=|>=|!=|<>|<|>)'),  # Comparison operators
        ('KEYWORD', r'\b(?:CREATE|DROP|USE|SHOW|DESCRIBE|DESC|TABLE|TABLES|DATABASE|DATABASES|INSERT|INTO|VALUES|SELECT|FROM|WHERE|UPDATE|SET|DELETE|INNER|JOIN|ON|PRIMARY|KEY|UNIQUE|REFERENCES|INT|STRING|BOOL|TRUE|FALSE|NULL|AND|OR|NOT|ORDER|BY|ASC|LIMIT|OFFSET)\b'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('EQUALS', r'='),
        ('COMMA', r','),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('SEMICOLON', r';'),
        ('STAR', r'\*'),
        ('DOT', r'\.'),
        ('WHITESPACE', r'\s+'),
    ]
    
    def __init__(self):
        # Compile patterns
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_PATTERNS)
        self.compiled_regex = re.compile(self.token_regex, re.IGNORECASE)
    
    def tokenize(self, sql: str) -> List[Token]:
        """Tokenize a SQL statement.
        
        Args:
            sql: SQL statement string
        
        Returns:
            List of tokens
        
        Raises:
            TokenizerError: If tokenization fails
        """
        tokens = []
        position = 0
        
        for match in self.compiled_regex.finditer(sql):
            token_type = match.lastgroup
            token_value = match.group()
            token_position = match.start()
            
            # Skip whitespace
            if token_type == 'WHITESPACE':
                continue
            
            # Normalize keywords to uppercase
            if token_type == 'KEYWORD':
                token_value = token_value.upper()
            
            # Remove quotes from strings
            if token_type == 'STRING':
                token_value = token_value[1:-1]  # Remove surrounding quotes
            
            tokens.append(Token(token_type, token_value, token_position))
            position = match.end()
        
        # Check if entire string was tokenized
        if position != len(sql):
            remaining = sql[position:].strip()
            if remaining:
                raise TokenizerError(
                    f"Unexpected character '{remaining[0]}'",
                    position,
                    sql
                )
        
        return tokens
    
    def __repr__(self) -> str:
        return "Tokenizer()"
