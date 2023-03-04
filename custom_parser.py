from lark import Lark, UnexpectedToken
from lark.lexer import Lexer, Token

from exceptions import CPLException
from lexer import InvalidTokenException
from consts import TOKEN_NAME_INVALID_TOKEN


class TypeLexer(Lexer):
    def __init__(self):
        pass
    
    def lex(self, data):
        for token, line_number in data:
            if token.name == TOKEN_NAME_INVALID_TOKEN:
                continue
            else:
                yield Token(token.name, token.attributes, line=line_number)

class Parser:
    def __init__(self, grammar):
        self.parser = Lark(grammar, parser='lalr', lexer=TypeLexer)
    
    def parse(self, token_list):
        errors = [
            InvalidTokenException(line_number, token) for token, line_number in token_list if token.name == TOKEN_NAME_INVALID_TOKEN
        ]
        
        result = None
        try:
            result = self.parser.parse(token_list)
        except UnexpectedToken as e:
            errors.append(UnexpectedTokenException(e.token, e.expected, e.line))

        return result, errors

class UnexpectedTokenException(CPLException):
    def __init__(self, found, expected, line_number):
        super().__init__("Unexpected token {unexpected}, should be {expected}".format(unexpected=found, expected=expected), line_number)