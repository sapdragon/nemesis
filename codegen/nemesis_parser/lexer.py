import re
from .exceptions import LexerError

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                self.advance()
            elif self.text[self.pos] == '/' and self.pos + 1 < len(self.text):
                if self.text[self.pos + 1] == '/':
                    self.skip_line_comment()
                elif self.text[self.pos + 1] == '*':
                    self.skip_block_comment()
                else:
                    self.error("Unexpected character")
            else:
                tokens.append(self.get_next_token())
        tokens.append(Token('EOF', None, self.line, self.column))
        return tokens

    def get_next_token(self):
        if self.text[self.pos].isalpha() or self.text[self.pos] == '_':
            return self.identifier()
        elif self.text[self.pos].isdigit():
            return self.number()
        elif self.text[self.pos] == '"':
            return self.string()
        elif self.text[self.pos] in '{}[]<>:,=':
            return self.symbol()
        else:
            self.error(f"Unexpected character: {self.text[self.pos]}")

    def identifier(self):
        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.advance()
        value = self.text[start:self.pos]
        if value in ['packet', 'import', 'type', 'enum']:
            return Token(value.upper(), value, self.line, self.column - (self.pos - start))
        return Token('IDENTIFIER', value, self.line, self.column - (self.pos - start))

    def number(self):
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.advance()
        return Token('NUMBER', int(self.text[start:self.pos]), self.line, self.column - (self.pos - start))

    def string(self):
        start = self.pos
        self.advance()  # Skip opening quote
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            if self.text[self.pos] == '\\':
                self.advance()  # Skip escape character
            self.advance()
        if self.pos >= len(self.text):
            self.error("Unterminated string")
        self.advance()  # Skip closing quote
        return Token('STRING', self.text[start:self.pos], self.line, self.column - (self.pos - start))

    def symbol(self):
        char = self.text[self.pos]
        self.advance()
        return Token(char, char, self.line, self.column - 1)

    def skip_line_comment(self):
        while self.pos < len(self.text) and self.text[self.pos] != '\n':
            self.advance()

    def skip_block_comment(self):
        self.advance(2)  # Skip /*
        while self.pos < len(self.text) - 1:
            if self.text[self.pos] == '*' and self.text[self.pos + 1] == '/':
                self.advance(2)
                return
            self.advance()
        self.error("Unterminated block comment")

    def advance(self, count=1):
        for _ in range(count):
            if self.pos < len(self.text):
                if self.text[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def error(self, message):
        raise LexerError(f"{message} at line {self.line}, column {self.column}")