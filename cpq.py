
from consts import *
from lexer import MatchedToken, PatternToken, Tokenizer
from symbol_table import SymbolTable


def main():
    pass

def compile(input):
    pass

def prelexer(lexer: Tokenizer):
    lexer.add_token(PatternToken("break", lambda _: MatchedToken(TOKEN_NAME_BREAK, "break", "")))
    lexer.add_token(PatternToken("case", lambda _: MatchedToken(TOKEN_NAME_CASE, "case", "")))
    lexer.add_token(PatternToken("default", lambda _: MatchedToken(TOKEN_NAME_DEFAULT, "default", "")))
    lexer.add_token(PatternToken("else", lambda _: MatchedToken(TOKEN_NAME_ELSE, "else", "")))
    lexer.add_token(PatternToken("if", lambda _: MatchedToken(TOKEN_NAME_IF, "if", "")))
    lexer.add_token(PatternToken("input", lambda _: MatchedToken(TOKEN_NAME_INPUT, "input", "")))
    lexer.add_token(PatternToken("output", lambda _: MatchedToken(TOKEN_NAME_OUTPUT, "output", "")))
    lexer.add_token(PatternToken("switch", lambda _: MatchedToken(TOKEN_NAME_SWITCH, "switch", "")))
    lexer.add_token(PatternToken("while", lambda _: MatchedToken(TOKEN_NAME_WHILE, "while", "")))

    lexer.add_token(PatternToken(r"\(", lambda _: MatchedToken(TOKEN_NAME_LEFT_PRNTSS, "(", "")))
    lexer.add_token(PatternToken(r"\)", lambda _: MatchedToken(TOKEN_NAME_RIGHT_PRNTSS, ")", "")))
    lexer.add_token(PatternToken("{", lambda _: MatchedToken(TOKEN_NAME_LEFT_BRCKT, "{", "")))
    lexer.add_token(PatternToken("}", lambda _: MatchedToken(TOKEN_NAME_RIGHT_BRCKT, "}", "")))
    lexer.add_token(PatternToken(",", lambda _: MatchedToken(TOKEN_NAME_COMMA, ",", "")))
    lexer.add_token(PatternToken(":", lambda _: MatchedToken(TOKEN_NAME_COLON, ":", "")))
    lexer.add_token(PatternToken(";", lambda _: MatchedToken(TOKEN_NAME_SEMICOLON, ";", "")))
    lexer.add_token(PatternToken("=", lambda _: MatchedToken(TOKEN_NAME_EQUALS, "=", "")))

    lexer.add_token(PatternToken(r"==|!=|<|>|>=|<=",  lambda matched_string: MatchedToken(TOKEN_NAME_RELOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"\+|-", lambda matched_string: MatchedToken(TOKEN_NAME_ADDOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"\*|\/", lambda matched_string: MatchedToken(TOKEN_NAME_MULOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"\|\|", lambda _: MatchedToken(TOKEN_NAME_OR, "||", "")))
    lexer.add_token(PatternToken("&&", lambda _: MatchedToken(TOKEN_NAME_AND, "&&", "")))
    lexer.add_token(PatternToken("!", lambda _: MatchedToken(TOKEN_NAME_NOT, "!", "")))

    lexer.add_token(PatternToken(r"static_cast<(int|float)>", \
        lambda matched_string: MatchedToken(TOKEN_NAME_CAST, matched_string, SymbolTable.Types.INT if matched_string.find("int") != -1 else SymbolTable.Types.FLOAT)))

    lexer.add_token(PatternToken(r"[a-zA-Z][a-zA-Z0-9]*", lambda matched_string: MatchedToken(TOKEN_NAME_ID, matched_string, matched_string)))
    lexer.add_token(PatternToken("int", lambda _: MatchedToken(TOKEN_NAME_TYPE_INT, "int", "")))
    lexer.add_token(PatternToken("float", lambda _: MatchedToken(TOKEN_NAME_TYPE_FLOAT, "float", "")))

    lexer.add_token(PatternToken(r"\d+", lambda matched_string: MatchedToken(TOKEN_NAME_NUM, matched_string, int(matched_string))))
    lexer.add_token(PatternToken(r"\d+.\d+", lambda matched_string: MatchedToken(TOKEN_NAME_NUM, matched_string, float(matched_string))))


if __name__ == "__main__":
    main()