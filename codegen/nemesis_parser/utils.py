def print_ast(node, indent=0):
    print('  ' * indent + type(node).__name__)
    for field in node.__dataclass_fields__:
        value = getattr(node, field)
        if isinstance(value, list):
            print('  ' * (indent + 1) + f"{field}:")
            for item in value:
                if isinstance(item, ASTNode):
                    print_ast(item, indent + 2)
                else:
                    print('  ' * (indent + 2) + str(item))
        elif isinstance(value, ASTNode):
            print('  ' * (indent + 1) + f"{field}:")
            print_ast(value, indent + 2)
        else:
            print('  ' * (indent + 1) + f"{field}: {value}")