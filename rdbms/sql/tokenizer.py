"""SQL tokenizer for breaking SQL statements into tokens."""

import re
from typing import List


class Token:
    """Represents a single token in a SQL statement."""
    
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value
    
    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False


class Tokenizer:
    """Tokenizes SQL-like statements."""
    
    # Token patterns (order matters!)
    TOKEN_PATTERNS = [
        ('NUMBER', r'-?\d+'),
        ('STRING', r"'[^']*'"),
        ('KEYWORD', r'\b(CREATE|TABLE|INSERT|INTO|VALUES|SELECT|FROM|WHERE|UPDATE|SET|DELETE|INNER|JOIN|ON|PRIMARY|KEY|UNIQUE|REFERENCES|INT|STRING|BOOL|TRUE|FALSE)\b'),
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
            ValueError: If tokenization fails
        """
        tokens = []
        position = 0
        
        for match in self.compiled_regex.finditer(sql):
            token_type = match.lastgroup
            token_value = match.group()
            
            # Skip whitespace
            if token_type == 'WHITESPACE':
                continue
            
            # Normalize keywords to uppercase
            if token_type == 'KEYWORD':
                token_value = token_value.upper()
            
            # Remove quotes from strings
            if token_type == 'STRING':
                token_value = token_value[1:-1]  # Remove surrounding quotes
            
            tokens.append(Token(token_type, token_value))
            position = match.end()
        
        # Check if entire string was tokenized
        if position != len(sql):
            remaining = sql[position:].strip()
            if remaining:
                raise ValueError(f"Tokenization failed at position {position}: unexpected '{remaining}'")
        
        return tokens
    
    def __repr__(self) -> str:
        return "Tokenizer()"
