import re
from enum import Enum
from typing import List, Optional
import sys
import networkx as nx
from graphviz import Digraph
class TokenType(Enum):
    PACKET = 'PACKET'
    IDENTIFIER = 'IDENTIFIER'
    COLON = 'COLON'
    LEFT_BRACE = 'LEFT_BRACE'
    RIGHT_BRACE = 'RIGHT_BRACE'
    COMMENT = 'COMMENT'
    LEFT_ANGLE = 'LEFT_ANGLE'
    RIGHT_ANGLE = 'RIGHT_ANGLE'
    LEFT_SQUARE_BRACKET = 'LEFT_SQUARE_BRACKET'
    RIGHT_SQUARE_BRACKET = 'RIGHT_SQUARE_BRACKET'
    COMMA = 'COMMA'

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
    def __init__(self, name: str, fields: List['FieldNode'], parent: Optional['PacketNode'] = None, generic_arguments: List[str] = []):
        self.name = name
        self.fields = fields
        self.parent = parent
        self.generic_arguments = generic_arguments if generic_arguments else []

'''

    u8 - 8-битное беззнаковое целое
    u16 - 16-битное беззнаковое целое
    u32 - 32-битное беззнаковое целое
    u64 - 64-битное беззнаковое целое
    i8 - 8-битное знаковое целое
    i16 - 16-битное знаковое целое
    i32 - 32-битное знаковое целое
    i64 - 64-битное знаковое целое
    f32 - 32-битное число с плавающей точкой
    f64 - 64-битное число с плавающей точкой
    bool - логическое значение
    string - строка

'''
class FIELD_TYPE(Enum):
    UNSIGNED_BYTE = 'u8'
    UNSIGNED_SHORT = 'u16'
    UNSIGNED_INT = 'u32'
    UNSIGNED_LONG = 'u64'
    SIGNED_BYTE = 'i8'
    SIGNED_SHORT = 'i16'
    SIGNED_INT = 'i32'
    SIGNED_LONG = 'i64'
    FLOAT = 'f32'
    DOUBLE = 'f64'
    BOOLEAN = 'bool'
    ARRAY = 'array'
    OBJECT = 'object'


class FieldNode(ASTNode):
    def __init__(self, name: str, data_type_name: str, data_type: FIELD_TYPE, is_generic: bool = False, generic_arguments: List[str] = [], array_type: FIELD_TYPE = None):
        self.name = name
        self.data_type_name = data_type_name
        self.is_generic = is_generic
        self.generic_arguments = generic_arguments if generic_arguments else []
        self.data_type = data_type
        self.array_type = array_type

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
                if packet.parent and not any(p.name == packet.parent.name for p in packets):
                    raise RuntimeError(f"Parent packet with name '{packet.parent.name}' does not exist (line: {self.peek().line}, column: {self.peek().column})")
                
                for field in packet.fields:
                    if field.is_generic:
                        if not any(p.name == field.data_type_name for p in packets):
                            raise RuntimeError(f"Generic argument '{field.data_type_name}' in field '{field.name}' is not a valid packet name (line: {self.peek().line}, column: {self.peek().column})")
                        
                        for generic_packet in packets:
                            if generic_packet.name == field.data_type_name:
                                if len(generic_packet.generic_arguments) != len(field.generic_arguments):
                                    raise RuntimeError(f"Generic packet '{field.data_type_name}' has {len(generic_packet.generic_arguments)} generic arguments, but {field.name} has {len(field.generic_arguments)} (line: {self.peek().line}, column: {self.peek().column})")
                                
                    elif field.data_type == FIELD_TYPE.OBJECT and not any(p.name == field.data_type_name for p in packets) and not packet.generic_arguments:
                        raise RuntimeError(f"Field '{field.name}' has invalid data type '{field.data_type_name}' (line: {self.peek().line}, column: {self.peek().column})")

                packets.append(packet)
        return packets
    
    def parse_packet(self) -> Optional[PacketNode]:
        if self.match(TokenType.PACKET):
            packet_token = self.previous()
            name = self.consume(TokenType.IDENTIFIER, "Ожидается имя пакета").value
            parent = None
            generic_arguments = []
            if self.match(TokenType.COLON):
                self.skip_comments()
                parent_name = self.consume(TokenType.IDENTIFIER, "Ожидается имя родительского пакета").value
                parent = PacketNode(parent_name, [])
            elif self.match(TokenType.LEFT_ANGLE):
                while not self.check(TokenType.RIGHT_ANGLE):
                    self.skip_comments()
                    generic_argument = self.consume(TokenType.IDENTIFIER, "Ожидается имя обобщенного аргумента").value
                    generic_arguments.append(generic_argument)
                    
                    if not self.match(TokenType.COMMA):
                        break

                self.consume(TokenType.RIGHT_ANGLE, "Ожидается '>' после списка обобщенных аргументов")

            self.skip_comments()
            self.consume(TokenType.LEFT_BRACE, "Ожидается '{' после имени пакета")
            fields = self.parse_fields()

            for field in fields:
                if generic_arguments:
                    if not field.data_type_name in generic_arguments:
                        raise RuntimeError(f"Field '{field.name}' has invalid data type. It should be one of the generic arguments: {', '.join(generic_arguments)} (line: {self.peek().line}, column: {self.peek().column})")

            self.consume(TokenType.RIGHT_BRACE, "Ожидается '}' после полей пакета")
            return PacketNode(name, fields, parent, generic_arguments)
        return None

    def parse_fields(self) -> List[FieldNode]:
        fields = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.skip_comments()
            if self.check(TokenType.IDENTIFIER):
                name = self.consume(TokenType.IDENTIFIER, "Ожидается имя поля").value
                self.consume(TokenType.COLON, "Ожидается ':' после имени поля")
                data_type_name = self.parse_data_type_name()
                data_type = self.parse_data_type(data_type_name)
                array_type = None
                if data_type == FIELD_TYPE.ARRAY:
                    data_type_name = data_type_name[:-2]
                    array_type = self.parse_data_type(data_type_name)

                is_generic = False
                generic_arguments = []
                if self.match(TokenType.LEFT_ANGLE):
                    is_generic = True
                    while not self.check(TokenType.RIGHT_ANGLE):
                        self.skip_comments()
                        generic_argument = self.consume(TokenType.IDENTIFIER, "Ожидается имя обобщенного аргумента").value
                        generic_arguments.append(generic_argument)
                        
                        if not self.match(TokenType.COMMA):
                            break

                    self.consume(TokenType.RIGHT_ANGLE, "Ожидается '>' после списка обобщенных аргументов")
                

                for field in fields:
                    if field.name == name:
                        raise RuntimeError(f"Field with name '{name}' already exists (line: {self.peek().line}, column: {self.peek().column})")

                fields.append(FieldNode(name, data_type_name, data_type, is_generic, generic_arguments, array_type))
            else:
                break
        return fields

    def parse_data_type_name(self) -> str:
        self.skip_comments()
        if self.match(TokenType.IDENTIFIER):
            return self.previous().value
        elif self.match(TokenType.LEFT_SQUARE_BRACKET):
            self.consume(TokenType.RIGHT_SQUARE_BRACKET, "Ожидается ']' после имени типа")
            data_type_name = self.parse_data_type_name()
            return data_type_name + '[]'
        else:
            raise RuntimeError(f"Expected data type name (line: {self.peek().line}, column: {self.peek().column})")

    def parse_data_type(self, name: str) -> FIELD_TYPE:
        if name == 'u8':
            return FIELD_TYPE.UNSIGNED_BYTE
        elif name == 'u16':
            return FIELD_TYPE.UNSIGNED_SHORT
        elif name == 'u32':
            return FIELD_TYPE.UNSIGNED_INT
        elif name == 'u64':
            return FIELD_TYPE.UNSIGNED_LONG
        elif name == 'i8':
            return FIELD_TYPE.SIGNED_BYTE
        elif name == 'i16':
            return FIELD_TYPE.SIGNED_SHORT
        elif name == 'i32':
            return FIELD_TYPE.SIGNED_INT
        elif name == 'i64':
            return FIELD_TYPE.SIGNED_LONG
        elif name == 'f32':
            return FIELD_TYPE.FLOAT
        elif name == 'f64':
            return FIELD_TYPE.DOUBLE
        elif name == 'bool':
            return FIELD_TYPE.BOOLEAN
        elif name.endswith('[]'):
            return FIELD_TYPE.ARRAY
        else:
            return FIELD_TYPE.OBJECT

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
        elif char == '<':
            tokens.append(Token(TokenType.LEFT_ANGLE, '<', line, column))
            column += 1
            current += 1
        elif char == '>':
            tokens.append(Token(TokenType.RIGHT_ANGLE, '>', line, column))
            column += 1
            current += 1
        elif char == '[':
            tokens.append(Token(TokenType.LEFT_SQUARE_BRACKET, '[', line, column))
            column += 1
            current += 1
        elif char == ']':
            tokens.append(Token(TokenType.RIGHT_SQUARE_BRACKET, ']', line, column))
            column += 1
            current += 1
        elif char == ',':
            tokens.append(Token(TokenType.COMMA, ',', line, column))
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

                if packet.parent:
                    print(f"  Parent: {packet.parent.name}")
                    parent_packet = next(p for p in packets if p.name == packet.parent.name)
                    for field in parent_packet.fields:
                        print(f"  Parent field: {field.name} ({field.data_type_name})")

                for field in packet.fields:
                    if field.is_generic:
                        print(f"  Generic field: {field.name} ({field.data_type_name}<{', '.join(field.generic_arguments)}>)")
                        
                        for generic_packet in packets:
                            if generic_packet.name == field.data_type_name:
                                generic_args = {}
                                for i, arg in enumerate(generic_packet.generic_arguments):
                                    generic_args[arg] = field.generic_arguments[i]

                                for field in generic_packet.fields:
                                    print(f"    Field: {field.name} ({generic_args.get(field.data_type_name, "UNKNOWN")})")
                                    
                    else:
                        if field.data_type == FIELD_TYPE.ARRAY:
                            print(f"  Field: {field.name} ({field.data_type_name}[]) Type {field.data_type}")
                        else:
                            print(f"  Field: {field.name} ({field.data_type_name}) Type {field.data_type}")
        except RuntimeError as e:
            print(e)
        except Exception as e:
            print(f"An error occurred: {e}")
