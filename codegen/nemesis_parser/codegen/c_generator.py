import os
from jinja2 import Environment, FileSystemLoader
from ..ast_nodes import Program, Packet, Enum, TypeAlias, Field, DataType

class CGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.env.globals.update({
            'isinstance': isinstance,
            'Enum': Enum,
            'Packet': Packet,
            'TypeAlias': TypeAlias,
            'Field': Field,
            'DataType': DataType,
            'c_generator': self
        })

    def generate(self, ast: Program):
        self._ensure_output_dir()
        self._generate_header_file(ast)
        self._generate_source_file(ast)

    def _ensure_output_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_header_file(self, ast: Program):
        template = self.env.get_template('packet.h.jinja2')
        output = template.render(program=ast)
        with open(os.path.join(self.output_dir, 'nemesis_packets.h'), 'w') as f:
            f.write(output)

    def _generate_source_file(self, ast: Program):
        template = self.env.get_template('packet.c.jinja2')
        output = template.render(program=ast)
        with open(os.path.join(self.output_dir, 'nemesis_packets.c'), 'w') as f:
            f.write(output)

    @staticmethod
    def c_type(field: Field) -> str:
        if field.data_type.is_array:
            base_type = CGenerator.c_type(Field(name='', data_type=DataType(field.data_type.name)))
            if field.data_type.array_size is not None:
                return f"{base_type} [{field.data_type.array_size}]"
            else:
                return f"{base_type}*"
        if field.data_type.name in ['u8', 'u16', 'u32', 'u64']:
            return f"uint{field.data_type.name[1:]}_t"
        elif field.data_type.name in ['i8', 'i16', 'i32', 'i64']:
            return f"int{field.data_type.name[1:]}_t"
        elif field.data_type.name == 'f32':
            return 'float'
        elif field.data_type.name == 'f64':
            return 'double'
        elif field.data_type.name == 'bool':
            return 'bool'
        elif field.data_type.name == 'string':
            return 'char*'
        else:
            return field.data_type.name

    @staticmethod
    def c_default_value(field: Field) -> str:
        if field.default_value is None:
            return ''
        if isinstance(field.default_value, str):
            return f' = "{field.default_value}"'
        elif isinstance(field.default_value, bool):
            return f' = {"true" if field.default_value else "false"}'
        else:
            return f' = {field.default_value}'

    @staticmethod
    def generic_type_name(packet: Packet) -> str:
        if packet.generic_params:
            return f"{packet.name}_{'_'.join(packet.generic_params)}"
        return packet.name