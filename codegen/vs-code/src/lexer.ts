export enum TokenType {
    Packet = 'packet',
    Identifier = 'identifier',
    Colon = 'colon',
    LeftBrace = 'leftBrace',
    RightBrace = 'rightBrace',
    Type = 'type',
    Comment = 'comment',
    EOF = 'eof'
  }
  
export interface Token {
    type: TokenType;
    value: string;
    line: number;
    column: number;
  }
  
  export class NSLexer {
    private readonly tokens: Token[] = [];
    private position = 0;
    private line = 1;
    private column = 1;
  
    constructor(private readonly input: string) {}
  
    private isEOF(): boolean {
      return this.position >= this.input.length;
    }
  
    private advance(): string {
      const char = this.input[this.position++];
      if (char === '\n') {
        this.line++;
        this.column = 1;
      } else {
        this.column++;
      }
      return char;
    }
  
    private addToken(type: TokenType, value: string): void {
      this.tokens.push({ type, value, line: this.line, column: this.column });
    }
  
    private skipWhitespace(): void {
      while (!this.isEOF() && /\s/.test(this.input[this.position])) {
        this.advance();
      }
    }
  
    private scanToken(): void {
      const char = this.advance();
  
      switch (char) {
        case ':':
          this.addToken(TokenType.Colon, ':');
          break;
        case '{':
          this.addToken(TokenType.LeftBrace, '{');
          break;
        case '}':
          this.addToken(TokenType.RightBrace, '}');
          break;
        default:
          if (/[a-zA-Z_]/.test(char)) {
            let value = char;
            while (!this.isEOF() && /[a-zA-Z0-9_]/.test(this.input[this.position])) {
              value += this.advance();
            }
            const type = value === 'packet' ? TokenType.Packet : TokenType.Identifier;
            this.addToken(type, value);
          } else if (char === '/' && this.input[this.position] === '/') {
            let value = '//';
            while (!this.isEOF() && this.input[this.position] !== '\n') {
              value += this.advance();
            }
            this.addToken(TokenType.Comment, value);
          } else if (char === '/' && this.input[this.position] === '*') {
            let value = '/*';
            while (!this.isEOF() && !(this.input[this.position] === '*' && this.input[this.position + 1] === '/')) {
              value += this.advance();
            }
            value += this.advance();
            value += this.advance();
            this.addToken(TokenType.Comment, value);
          }
          break;
      }
    }
  
    tokenize(): Token[] {
      while (!this.isEOF()) {
        this.skipWhitespace();
        if (!this.isEOF()) {
          this.scanToken();
        }
      }
      this.addToken(TokenType.EOF, '');
      return this.tokens;
    }
  }