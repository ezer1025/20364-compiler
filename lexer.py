from collections import namedtuple
import re
from consts import TOKEN_NAME_IGNORE_TOKEN, TOKEN_NAME_INVALID_TOKEN

from exceptions import CPLException

MatchedToken = namedtuple("Token", ["name", "lexeme", "attributes"])

class PatternToken:
    def __init__(self, pattern, handler):
        self.pattern = re.compile(r"^({pattern}).*".format(pattern=pattern), re.MULTILINE)
        self.handler = handler
    
    def _match(self, string):
        match = self.pattern.match(string)
        return match.group(1) if match else None
    
    def match_and_handle(self, string):
        match = self._match(string)
        return self.handler(match) if match is not None else None

class TokenList:
    def __init__(self, token_list):
        self.token_list = token_list
    
    def __iter__(self):
        self.current_token = 0
        return self
    
    def __next__(self):
        if self.current_token >= len(self.token_list):
            raise StopIteration()
        
        token = self.token_list[self.current_token]
        self.current_token += 1

        return token

class Tokenizer:
    def __init__(self):
        self.pattern_tokens = []

        # newlines, empty strings, comments and invalid token 
        self.add_token(PatternToken(r"\n", self._handle_new_line))
        self.add_token(PatternToken(r"\s", self._handle_white_spaces))
        self.add_token(PatternToken(r".{1}", self._handle_invalid_token))
        self.add_token(PatternToken(r"/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/", self._handle_new_line))
    
    def add_token(self, token: PatternToken):
        self.pattern_tokens.append(token)
    
    def tokenize(self, string):
        self.input = string
        self.cursor = 0
        self.line_number = 1

        return TokenList(self._tokenize())

    def _handle_new_line(self, matching_string):
        self.line_number += matching_string.count("\n")
        return MatchedToken(TOKEN_NAME_IGNORE_TOKEN, matching_string, "")

    def _handle_white_spaces(self, matching_string):
        return MatchedToken(TOKEN_NAME_IGNORE_TOKEN, matching_string, "")
    
    def _handle_invalid_token(self, matching_string):
        return MatchedToken(TOKEN_NAME_INVALID_TOKEN, matching_string, "")

    def _tokenize(self):
        match_tokens = []

        while self.cursor < len(self.input):
            current_token_match_list = filter(lambda r: r is not None, map(lambda t: t.match_and_handle(), self.pattern_tokens))
            final_token = max(current_token_match_list, lambda t: len(t.lexeme))

            self.cursor += len(final_token.lexeme)
            if final_token.name != TOKEN_NAME_IGNORE_TOKEN:
                match_tokens.append((final_token, self.line_number))
        
        return match_tokens

class InvalidTokenException(CPLException):
    def __init__(self, line_number, token):
        super().__init__("Invalid token {token}".format(token=token.lexeme), line_number)