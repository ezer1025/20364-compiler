from lark import Lark, UnexpectedToken
from lark.lexer import Lexer, Token
from exceptions import CPLException

from lexer import InvalidSymbolException, Tokenizer

class TypeLexer(Lexer):
    def __init__(self):
        pass
    
    def lex(self, data):
        for token, line_number in data:
            if token.name == Tokenizer.INVALID_SYMBOL_NAME:
                continue
            else:
                yield Token(token.name, token.attributes, line=line_number)

class Parser:
    def __init__(self, grammar):
        self.parser = Lark(grammar, parser='lalr', lexer=TypeLexer)
    
    def parse(self, token_list):
        errors = [
            InvalidSymbolException(line_number, token) for token, line_number in token_list if token.name == Tokenizer.INVALID_SYMBOL_NAME
        ]
        
        result = None
        try:
            result = self.parser.parse(token_list)
        except UnexpectedToken as e:
            errors.append(CPLException("Unexpected token. should be {expected}".format(expected=e.expected), e.line))

        return result, errors