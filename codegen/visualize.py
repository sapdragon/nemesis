import sys
import os
from graphviz import Digraph
from nemesis_parser.lexer import Lexer
from nemesis_parser.parser import Parser
from nemesis_parser.ast_nodes import Program, Packet, Enum, TypeAlias, Import, DataType

def create_graph(ast):
    dot = Digraph(comment='Nemesis Packet Language Structure')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.5')
   
    # Create the root node
    dot.node('root', 'Declarations', shape='box')
   
    all_types = {
        'u8': 'u8', 'u16': 'u16', 'u32': 'u32', 'u64': 'u64',
        'i8': 'i8', 'i16': 'i16', 'i32': 'i32', 'i64': 'i64',
        'f32': 'f32', 'f64': 'f64', 'bool': 'bool', 'string': 'string'
    }
    
    # Source of each type (empty for built-in types)
    type_sources = {k: 'primitive' for k in all_types}
    
    created_nodes = set()

    # First pass: collect all types and their sources
    collect_types(ast.declarations, all_types, type_sources, '')

    # Second pass: create nodes for each declaration
    for declaration in ast.declarations:
        if isinstance(declaration, Packet):
            add_packet_to_graph(dot, declaration, all_types, type_sources, created_nodes)
        elif isinstance(declaration, Enum):
            add_enum_to_graph(dot, declaration, type_sources)
        elif isinstance(declaration, TypeAlias):
            add_type_alias_to_graph(dot, declaration, all_types, type_sources, created_nodes)
        elif isinstance(declaration, Import):
            add_import_to_graph(dot, declaration)
   
    return dot

def collect_types(declarations, all_types, type_sources, source):
    for declaration in declarations:
        if isinstance(declaration, Packet):
            all_types[declaration.name] = declaration.name
            type_sources[declaration.name] = source
        elif isinstance(declaration, Enum):
            all_types[declaration.name] = declaration.name
            type_sources[declaration.name] = source
        elif isinstance(declaration, TypeAlias):
            all_types[declaration.name] = declaration.name
            type_sources[declaration.name] = source
        elif isinstance(declaration, Import):
            collect_types(declaration.imported_declarations, all_types, type_sources, declaration.path)

def add_packet_to_graph(dot, packet, all_types, type_sources, created_nodes):
    packet_node = f"packet_{packet.name}"
    fillcolor = 'lightblue' if type_sources[packet.name] == '' else 'lightgreen'
    dot.node(packet_node, packet.name, shape='box', style='filled', fillcolor=fillcolor)
   
    if packet.parent:
        dot.edge(f"packet_{packet.parent}", packet_node, style='dashed')
    else:
        dot.edge('root', packet_node)
   
    if packet.generic_params:
        generic_node = f"{packet_node}_generic"
        dot.node(generic_node, f"<{', '.join(packet.generic_params)}>", shape='diamond')
        dot.edge(packet_node, generic_node)
   
    for field in packet.fields:
        field_node = f"{packet_node}_{field.name}"
        if field.data_type.is_array:
            data_type = f"[]{field.data_type.name}" if field.data_type.array_size is None else f"[{field.data_type.array_size}]{field.data_type.name}"
        else:
            data_type = field.data_type.name
        
        field_label = f"{field.name}: {data_type}"
        if field.default_value is not None:
            if isinstance(field.default_value, dict):
                default_str = ", ".join(f"{k}: {v}" for k, v in field.default_value.items())
                field_label += f" = {{{default_str}}}"
            else:
                field_label += f" = {field.default_value}"
        if field.bit_size is not None:
            field_label += f" [bits: {field.bit_size}]"
        
        dot.node(field_node, field_label, shape='ellipse')
        dot.edge(packet_node, field_node)
        
        # Добавляем связь с типом поля
        add_type_node(dot, data_type, all_types, type_sources, created_nodes)
        dot.edge(field_node, f"type_{data_type}", style='dotted')
        
        if field.generic_args:
            generic_args_node = f"{field_node}_generic_args"
            dot.node(generic_args_node, f"<{', '.join([arg.name for arg in field.generic_args])}>", shape='diamond')
            dot.edge(field_node, generic_args_node)
            dot.edge(field_node, generic_args_node)

def add_enum_to_graph(dot, enum, type_sources):
    enum_node = f"enum_{enum.name}"
    fillcolor = 'lightyellow' if type_sources[enum.name] == '' else 'lightgreen'
    dot.node(enum_node, f"{enum.name}: {enum.type}", shape='box', style='filled', fillcolor=fillcolor)
    dot.edge('root', enum_node)
   
    for value in enum.values:
        value_node = f"{enum_node}_{value}"
        dot.node(value_node, value, shape='ellipse')
        dot.edge(enum_node, value_node)

def add_type_alias_to_graph(dot, alias, all_types, type_sources, created_nodes):
    alias_node = f"alias_{alias.name}"
    fillcolor = 'lightsalmon' if type_sources[alias.name] == '' else 'lightgreen'
    dot.node(alias_node, f"{alias.name}", shape='box', style='filled', fillcolor=fillcolor)
    dot.edge('root', alias_node)

    real_type = alias.aliased_type.name
    add_type_node(dot, real_type, all_types, type_sources, created_nodes)
    
    # Добавляем стрелку от псевдонима к реальному типу
    dot.edge(alias_node, f"type_{real_type}", label='alias of', style='dashed', color='blue')

def add_import_to_graph(dot, import_decl):
    import_node = f"import_{import_decl.path.replace('.', '_')}"
    dot.node(import_node, f"Import: {import_decl.path}", shape='box', style='filled', fillcolor='lightgray')
    dot.edge('root', import_node)

def add_type_node(dot, type_name, all_types, type_sources, created_nodes):
    if f"type_{type_name}" not in created_nodes:
        fillcolor = 'lightblue' if type_sources.get(type_name, '') == '' else 'lightgreen'
        if type_name in ['u8', 'u16', 'u32', 'u64', 'i8', 'i16', 'i32', 'i64', 'f32', 'f64', 'bool', 'string']:
            fillcolor = 'white'
        dot.node(f"type_{type_name}", type_name, shape='box', style='filled', fillcolor=fillcolor)
        created_nodes.add(f"type_{type_name}")

def visualize_graph(dot, output_file):
    dot.render(output_file, view=True, cleanup=True)

def main():
    if len(sys.argv) != 2:
        print("Usage: python visualize.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
   
    with open(input_file, 'r') as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, input_file)
    ast = parser.parse()

    dot = create_graph(ast)
    output_file = os.path.splitext(input_file)[0] + "_structure"
    visualize_graph(dot, output_file)
    print(f"Graph has been saved as {output_file}.pdf")

if __name__ == "__main__":
    main()