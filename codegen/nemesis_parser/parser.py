import os
from .ast_nodes import Program, Packet, Field, DataType, Enum, TypeAlias, Import
from .exceptions import ParserError

class Parser:
    def __init__(self, tokens, file_path=None):
        self.tokens = tokens
        self.current = 0
        self.defined_packets = {}
        self.defined_types = set(['u8', 'u16', 'u32', 'u64', 'i8', 'i16', 'i32', 'i64', 'f32', 'f64', 'bool', 'string'])
        self.defined_enums = {}
        self.defined_aliases = {}
        self.current_generic_params = set()
        self.file_path = file_path
        self.imported_files = set()

    def parse(self):
        declarations = []
        while self.current_token.type != 'EOF':
            if self.current_token.type == 'IMPORT':
                declarations.append(self.import_declaration())
            elif self.current_token.type == 'TYPE':
                declarations.append(self.type_alias())
            elif self.current_token.type == 'ENUM':
                declarations.append(self.enum())
            elif self.current_token.type == 'PACKET':
                declarations.append(self.packet())
            else:
                self.error(f"Unexpected token {self.current_token.type}")
        
        self.check_cyclic_dependencies(declarations)
        return Program(declarations)

    def import_declaration(self):
        self.expect('IMPORT')
        path = self.expect('STRING').value.strip('"')
        if self.file_path:
            full_path = os.path.join(os.path.dirname(self.file_path), path)
        else:
            full_path = path
        
        if full_path in self.imported_files:
            return Import(path)  # Skip if already imported
        
        self.imported_files.add(full_path)
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        from .lexer import Lexer  # Import here to avoid circular imports
        lexer = Lexer(content)
        tokens = lexer.tokenize()
        parser = Parser(tokens, full_path)
        imported_program = parser.parse()
        
        # Merge imported declarations
        self.defined_packets.update(parser.defined_packets)
        self.defined_types.update(parser.defined_types)
        self.defined_enums.update(parser.defined_enums)
        self.defined_aliases.update(parser.defined_aliases)
        
        return Import(path, imported_program.declarations)
    

    def parse_default_value(self, data_type):
        if data_type.name in ['u8', 'u16', 'u32', 'u64', 'i8', 'i16', 'i32', 'i64']:
            return self.expect('NUMBER').value
        elif data_type.name in ['f32', 'f64']:
            return float(self.expect('NUMBER').value)
        elif data_type.name == 'bool':
            value = self.expect('IDENTIFIER').value
            if value not in ['true', 'false']:
                self.error(f"Invalid boolean value: {value}")
            return value == 'true'
        elif data_type.name == 'string':
            return self.expect('STRING').value[1:-1]  # Remove quotes
        elif data_type.name in self.defined_enums:
            value = self.expect('IDENTIFIER').value
            if value not in self.defined_enums[data_type.name].values:
                self.error(f"Invalid enum value: {value}")
            return value
        elif data_type.name in self.defined_aliases:
            # Рекурсивно обрабатываем псевдонимы типов
            aliased_type = self.defined_aliases[data_type.name]
            return self.parse_default_value(aliased_type)
        elif data_type.name in self.defined_packets:
            # Для пользовательских пакетов ожидаем конструктор
            self.expect('{')
            packet = self.defined_packets[data_type.name]
            default_values = {}
            while self.current_token.type != '}':
                field_name = self.expect('IDENTIFIER').value
                self.expect(':')
                field = next((f for f in packet.fields if f.name == field_name), None)
                if field is None:
                    self.error(f"Unknown field '{field_name}' in packet '{data_type.name}'")
                default_values[field_name] = self.parse_default_value(field.data_type)
                if self.current_token.type == ',':
                    self.advance()
            self.expect('}')
            return default_values
        else:
            self.error(f"Unsupported type for default value: {data_type.name}")

    def type_alias(self):
        self.expect('TYPE')
        name = self.expect('IDENTIFIER').value
        self.expect('=')
        aliased_type = self.data_type()
        self.defined_aliases[name] = aliased_type
        self.defined_types.add(name)
        return TypeAlias(name, aliased_type)

    def enum(self):
        self.expect('ENUM')
        name = self.expect('IDENTIFIER').value
        self.expect(':')
        enum_type = self.expect('IDENTIFIER').value
        

        if enum_type not in ['u8', 'u16', 'u32', 'u64', 'i8', 'i16', 'i32', 'i64'] and enum_type not in self.defined_types:
            self.error(f"Invalid enum type: {enum_type}. Must be a primitive integer type or a defined type.")
        
        self.expect('{')
        values = []
        while self.current_token.type != '}':
            values.append(self.expect('IDENTIFIER').value)
            if self.current_token.type == ',':
                self.advance()
        self.expect('}')
        
        enum = Enum(name, enum_type, values)
        self.defined_enums[name] = enum
        self.defined_types.add(name)
        return enum

    def packet(self):
        self.expect('PACKET')
        name = self.expect('IDENTIFIER').value

        if name in self.defined_packets:
            self.error(f"Packet '{name}' is already defined")

        generic_params = self.generic_params() if self.current_token.type == '<' else []
        self.current_generic_params = set(generic_params)

        parent = None
        if self.current_token.type == ':':
            self.advance()
            parent = self.expect('IDENTIFIER').value
            if parent not in self.defined_packets:
                self.error(f"Parent packet '{parent}' is not defined")

        self.expect('{')
        fields = []
        while self.current_token.type != '}':
            fields.append(self.field())
        self.expect('}')

        self.check_field_uniqueness(fields, parent)
        packet = Packet(name, fields, generic_params, parent)
        self.defined_packets[name] = packet
        self.current_generic_params.clear()
        return packet

    def field(self):
        name = self.expect('IDENTIFIER').value
        self.expect(':')
        data_type = self.data_type()
        generic_args = self.generic_args() if self.current_token.type == '<' else []
        default_value = None
        bit_size = None

        if self.current_token.type == '=':
            self.advance()
            default_value = self.parse_default_value(data_type)
        
        if self.current_token.type == '[':
            self.advance()
            if self.current_token.value == 'bits':
                self.advance()
                self.expect(':')
                bit_size = self.expect('NUMBER').value
            self.expect(']')

        return Field(name, data_type, generic_args, default_value, bit_size)

    def data_type(self):
        if self.current_token.type == '[':
            return self.array_type()
        elif self.current_token.type == 'IDENTIFIER':
            type_name = self.advance().value
            if type_name not in self.defined_types and type_name not in self.defined_packets and type_name not in self.current_generic_params:
                self.error(f"Undefined type '{type_name}'")
            return DataType(type_name)
        else:
            self.error("Expected data type")

    def array_type(self):
        self.expect('[')
        size = self.advance().value if self.current_token.type == 'NUMBER' else None
        self.expect(']')
        element_type = self.data_type()
        return DataType(element_type.name, is_array=True, array_size=size)

    def generic_params(self):
        params = []
        self.expect('<')
        while True:
            param = self.expect('IDENTIFIER').value
            if param in params:
                self.error(f"Duplicate generic parameter '{param}'")
            params.append(param)
            if self.current_token.type == '>':
                break
            self.expect(',')
        self.expect('>')
        return params

    def generic_args(self):
        args = []
        self.expect('<')
        while True:
            args.append(self.data_type())
            if self.current_token.type == '>':
                break
            self.expect(',')
        self.expect('>')
        return args

    def check_cyclic_dependencies(self, declarations):
        def dfs(packet, visited, stack):
            visited.add(packet.name)
            stack.add(packet.name)
            
            if packet.parent:
                parent = self.defined_packets[packet.parent]
                if parent.name not in visited:
                    if dfs(parent, visited, stack):
                        return True
                elif parent.name in stack:
                    self.error(f"Cyclic inheritance detected: {' -> '.join(stack)} -> {parent.name}")
            
            stack.remove(packet.name)
            return False

        visited = set()
        for decl in declarations:
            if isinstance(decl, Packet) and decl.name not in visited:
                dfs(decl, visited, set())

    def check_field_uniqueness(self, fields, parent):
        field_names = set()
        while parent:
            parent_packet = self.defined_packets[parent]
            for field in parent_packet.fields:
                field_names.add(field.name)
            parent = parent_packet.parent

        for field in fields:
            if field.name in field_names:
                self.error(f"Duplicate field name '{field.name}'")
            field_names.add(field.name)

    def expect(self, token_type):
        if self.current_token.type == token_type:
            return self.advance()
        self.error(f"Expected {token_type}, got {self.current_token.type}")

    def advance(self):
        token = self.current_token
        self.current += 1
        return token

    @property
    def current_token(self):
        return self.tokens[self.current]

    def error(self, message):
        raise ParserError(f"{message} at line {self.current_token.line}, column {self.current_token.column}")