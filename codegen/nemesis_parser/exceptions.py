class NemesisParserError(Exception):
    pass

class LexerError(NemesisParserError):
    pass

class ParserError(NemesisParserError):
    pass