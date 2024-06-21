import sys
import os
from nemesis_parser.lexer import Lexer
from nemesis_parser.parser import Parser
from nemesis_parser.codegen import CGenerator

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_code.py <input_file> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_file, 'r') as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, input_file)
    ast = parser.parse()

    generator = CGenerator(output_dir)
    generator.generate(ast)

    print(f"C code has been generated in {output_dir}")

if __name__ == "__main__":
    main()