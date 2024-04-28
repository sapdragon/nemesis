import * as vscode from 'vscode';
import { NSLexer, Token, TokenType } from './lexer';

class NSValidator {
  private tokens: Token[];
  private currentIndex: number;

  constructor(tokens: Token[]) {
    this.tokens = tokens;
    this.currentIndex = 0;
  }

  private get currentToken(): Token {
    return this.tokens[this.currentIndex];
  }

  private moveNext(): void {
    this.currentIndex++;
  }

  private match(type: TokenType): boolean {
    if (this.currentToken && this.currentToken.type === type) {
      this.moveNext();
      return true;
    }
    return false;
  }

  private createDiagnostic(message: string, token: Token): vscode.Diagnostic {
    const range = new vscode.Range(
      new vscode.Position(token.line - 1, token.column - 1),
      new vscode.Position(token.line - 1, token.column + token.value.length)
    );
    return new vscode.Diagnostic(range, message, vscode.DiagnosticSeverity.Error);
  }

  private validatePacket(diagnostics: vscode.Diagnostic[]): void {
    if (!this.match(TokenType.Packet)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected "packet" keyword', this.currentToken));
      }
      return;
    }

    if (!this.match(TokenType.Identifier)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected packet name', this.currentToken));
      }
      return;
    }

    if (!this.match(TokenType.LeftBrace)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected "{"', this.currentToken));
      }
      return;
    }

    while (this.currentToken && this.currentToken.type !== TokenType.RightBrace) {
      this.validateField(diagnostics);
    }

    if (!this.match(TokenType.RightBrace)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected "}"', this.currentToken));
      }
    }
  }

  private validateField(diagnostics: vscode.Diagnostic[]): void {
    if (!this.match(TokenType.Identifier)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected field name', this.currentToken));
      }
      return;
    }

    if (!this.match(TokenType.Colon)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected ":"', this.currentToken));
      }
      return;
    }

    if (!this.match(TokenType.Identifier)) {
      if (this.currentToken) {
        diagnostics.push(this.createDiagnostic('Expected field type', this.currentToken));
      }
    }
  }

  public validate(document: vscode.TextDocument): vscode.Diagnostic[] {
    const diagnostics: vscode.Diagnostic[] = [];

    while (this.currentToken) {
      this.validatePacket(diagnostics);

      while (this.currentToken && this.currentToken.type !== TokenType.Packet) {
        this.moveNext();
      }
    }

    return diagnostics;
  }
}

function refreshDiagnostics(document: vscode.TextDocument, collection: vscode.DiagnosticCollection): void {
	const text = document.getText();
	const lexer = new NSLexer(text);
	const tokens = lexer.tokenize();
  
	const validator = new NSValidator(tokens);
	const diagnostics = validator.validate(document);
  
	collection.set(document.uri, diagnostics);
  }
  
  export function subscribeToDocumentChanges(context: vscode.ExtensionContext, diagnostics: vscode.DiagnosticCollection): void {
	if (vscode.window.activeTextEditor) {
	  refreshDiagnostics(vscode.window.activeTextEditor.document, diagnostics);
	}
  
	context.subscriptions.push(
	  vscode.window.onDidChangeActiveTextEditor(editor => {
		if (editor) {
		  refreshDiagnostics(editor.document, diagnostics);
		}
	  })
	);
  
	context.subscriptions.push(
	  vscode.workspace.onDidChangeTextDocument(e => refreshDiagnostics(e.document, diagnostics))
	);
  
	context.subscriptions.push(
	  vscode.workspace.onDidCloseTextDocument(doc => diagnostics.delete(doc.uri))
	);
  }
  
  export function activate(context: vscode.ExtensionContext) {
	const diagnosticCollection = vscode.languages.createDiagnosticCollection('ns');
  
	subscribeToDocumentChanges(context, diagnosticCollection);

  }