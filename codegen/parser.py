import re
from enum import Enum
from typing import List, Optional
import sys

class TokenType(Enum):
    PACKET = 'PACKET'
    IDENTIFIER = 'IDENTIFIER'
    COLON = 'COLON'
    LEFT_BRACE = 'LEFT_BRACE'
    RIGHT_BRACE = 'RIGHT_BRACE'
    COMMENT = 'COMMENT'
    EOF = 'EOF'

class Token:
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

class ASTNode:
    pass

class PacketNode(ASTNode):
    def __init__(self, name: str, fields: List['FieldNode'], parent: Optional['PacketNode'] = None):
        self.name = name
        self.fields = fields
        self.parent = parent

class FieldNode(ASTNode):
    def __init__(self, name: str, data_type: str):
        self.name = name
        self.data_type = data_type

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[PacketNode]:
        packets = []
        while not self.is_at_end():
            self.skip_comments()
            packet = self.parse_packet()
            if packet:
                if any(p.name == packet.name for p in packets):
                    raise RuntimeError(f"Packet with name '{packet.name}' already exists (line: {self.peek().line}, column: {self.peek().column})")

                packets.append(packet)
        return packets

    def parse_packet(self) -> Optional[PacketNode]:
        if self.match(TokenType.PACKET):
            packet_token = self.previous()
            name = self.consume(TokenType.IDENTIFIER, "Ожидается имя пакета").value
            parent = None
            if self.match(TokenType.COLON):
                self.skip_comments()
                parent_name = self.consume(TokenType.IDENTIFIER, "Ожидается имя родительского пакета").value
                parent = PacketNode(parent_name, [])
            self.skip_comments()
            self.consume(TokenType.LEFT_BRACE, "Ожидается '{' после имени пакета")
            fields = self.parse_fields()
            self.consume(TokenType.RIGHT_BRACE, "Ожидается '}' после полей пакета")
            return PacketNode(name, fields, parent)
        return None

    def parse_fields(self) -> List[FieldNode]:
        fields = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.skip_comments()
            if self.check(TokenType.IDENTIFIER):
                name = self.consume(TokenType.IDENTIFIER, "Ожидается имя поля").value
                self.consume(TokenType.COLON, "Ожидается ':' после имени поля")
                data_type = self.parse_data_type()
                fields.append(FieldNode(name, data_type))
            else:
                break
        return fields

    def parse_data_type(self) -> str:
        self.skip_comments()
        if self.match(TokenType.IDENTIFIER):
            return self.previous().value
        else:
            raise RuntimeError(f"Expected data type name (line: {self.peek().line}, column: {self.peek().column})")

    def skip_comments(self):
        while self.match(TokenType.COMMENT):
            pass

    def match(self, token_type: TokenType) -> bool:
        if self.check(token_type):
            self.advance()
            return True
        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise RuntimeError(f'{message} (line: {self.peek().line}, column: {self.peek().column})')

def tokenize(code: str) -> List[Token]:
    tokens = []
    line = 1
    column = 1
    current = 0

    while current < len(code):
        char = code[current]

        if char.isspace():
            if char == '\n':
                line += 1
                column = 1
            else:
                column += 1
            current += 1
        elif char == '{':
            tokens.append(Token(TokenType.LEFT_BRACE, '{', line, column))
            column += 1
            current += 1
        elif char == '}':
            tokens.append(Token(TokenType.RIGHT_BRACE, '}', line, column))
            column += 1
            current += 1
        elif char == ':':
            tokens.append(Token(TokenType.COLON, ':', line, column))
            column += 1
            current += 1
        elif char == '/' and current + 1 < len(code):
            if code[current + 1] == '/':
                start = current
                while current < len(code) and code[current] != '\n':
                    current += 1
                comment = code[start:current]
                tokens.append(Token(TokenType.COMMENT, comment, line, column))
                column += len(comment)
            elif code[current + 1] == '*':
                start = current
                current += 2
                while current < len(code) and not (code[current] == '*' and current + 1 < len(code) and code[current + 1] == '/'):
                    if code[current] == '\n':
                        line += 1
                        column = 1
                    else:
                        column += 1
                    current += 1
                current += 2
                comment = code[start:current]
                tokens.append(Token(TokenType.COMMENT, comment, line, column))
                column += len(comment)
            else:
                raise RuntimeError(f"Unexpected character '/' (line: {line}, column: {column})")
        elif re.match(r'[a-zA-Z_]', char):
            start = current
            while current < len(code) and (re.match(r'[a-zA-Z0-9_]', code[current])):
                current += 1
            value = code[start:current]
            if value == 'packet':
                tokens.append(Token(TokenType.PACKET, value, line, column))
            else:
                tokens.append(Token(TokenType.IDENTIFIER, value, line, column))
            column += len(value)
        else:
            raise RuntimeError(f"Unexpected character '{char}' (line: {line}, column: {column})")

    tokens.append(Token(TokenType.EOF, '', line, column))
    return tokens

def parse(code: str) -> List[PacketNode]:
    tokens = tokenize(code)
    parser = Parser(tokens)
    return parser.parse()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python parser.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        code = f.read()
        try:
            packets = parse(code)
            for packet in packets:
                print(f"Packet: {packet.name}")
                for field in packet.fields:
                    print(f"  Field: {field.name} ({field.data_type})")
        except RuntimeError as e:
            print(e)
        except Exception as e:
            print(f"An error occurred: {e}")
