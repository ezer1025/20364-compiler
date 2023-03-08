
import os
import sys
from consts import *
from custom_parser import Parser
from ir import get_ir
from lexer import MatchedToken, PatternToken, Tokenizer
from quad import get_quad
from symbol_table import SymbolTable


def main():
    if len(sys.argv) != 2:
        print("Usage: python cpq.py <path-to-cpl-source>")
        exit(-1)
    
    input_file_path = sys.argv[1]
    input_file_no_ext = os.path.splitext(input_file_path)[0]
    output_file_path = "{}.qud".format(input_file_no_ext)

    with open(input_file_path, "r") as input_file:
        source = input_file.read()
        errors, result = compile(source)

        if not errors:
            with open(output_file_path, "w") as output_file:
                for instruction in result:
                    output_file.write(instruction.code)
                    output_file.write('\n')
                output_file.write("Enosh Zerahia")
        else:
            for error in errors:
                print("Error in line {line_number}: {message}".format(line_number=error.line_number, message=error.message))
            
            print("Enosh Zerahia")


def compile(input):
    parser = None
    with open(GRAMMAR_FILE_PATH, "r") as grammar_file:
        parser = Parser(grammar_file.read())

    lexer = Tokenizer()
    add_cpl_symbols(lexer)

    tokens = lexer.tokenize(input)

    errors, ast = parser.parse(tokens)
    
    if errors:
        return errors, []
    
    errors, symbol_table = SymbolTable.generate_symbol_table(ast)

    if errors:
        return errors, []
    
    errors, ir = get_ir(ast, symbol_table)

    quad = get_quad(ir)
    
    return [], quad


def add_cpl_symbols(lexer):
    lexer.add_token(PatternToken("break", lambda _: MatchedToken(TOKEN_NAME_BREAK, "break", "")))
    lexer.add_token(PatternToken("case", lambda _: MatchedToken(TOKEN_NAME_CASE, "case", "")))
    lexer.add_token(PatternToken("default", lambda _: MatchedToken(TOKEN_NAME_DEFAULT, "default", "")))
    lexer.add_token(PatternToken("else", lambda _: MatchedToken(TOKEN_NAME_ELSE, "else", "")))
    lexer.add_token(PatternToken("if", lambda _: MatchedToken(TOKEN_NAME_IF, "if", "")))
    lexer.add_token(PatternToken("input", lambda _: MatchedToken(TOKEN_NAME_INPUT, "input", "")))
    lexer.add_token(PatternToken("output", lambda _: MatchedToken(TOKEN_NAME_OUTPUT, "output", "")))
    lexer.add_token(PatternToken("switch", lambda _: MatchedToken(TOKEN_NAME_SWITCH, "switch", "")))
    lexer.add_token(PatternToken("while", lambda _: MatchedToken(TOKEN_NAME_WHILE, "while", "")))

    lexer.add_token(PatternToken(r"(==|!=|>=|<=|>|<)",  lambda matched_string: MatchedToken(TOKEN_NAME_RELOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"(\+|-){1}", lambda matched_string: MatchedToken(TOKEN_NAME_ADDOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"(\*|\/){1}", lambda matched_string: MatchedToken(TOKEN_NAME_MULOP, matched_string, matched_string)))
    lexer.add_token(PatternToken(r"\|\|", lambda _: MatchedToken(TOKEN_NAME_OR, "||", "")))
    lexer.add_token(PatternToken("&&", lambda _: MatchedToken(TOKEN_NAME_AND, "&&", "")))
    lexer.add_token(PatternToken("!", lambda _: MatchedToken(TOKEN_NAME_NOT, "!", "")))

    lexer.add_token(PatternToken(r"\(", lambda _: MatchedToken(TOKEN_NAME_LEFT_PRNTSS, "(", "")))
    lexer.add_token(PatternToken(r"\)", lambda _: MatchedToken(TOKEN_NAME_RIGHT_PRNTSS, ")", "")))
    lexer.add_token(PatternToken("{", lambda _: MatchedToken(TOKEN_NAME_LEFT_BRCKT, "{", "")))
    lexer.add_token(PatternToken("}", lambda _: MatchedToken(TOKEN_NAME_RIGHT_BRCKT, "}", "")))
    lexer.add_token(PatternToken(",", lambda _: MatchedToken(TOKEN_NAME_COMMA, ",", "")))
    lexer.add_token(PatternToken(":", lambda _: MatchedToken(TOKEN_NAME_COLON, ":", "")))
    lexer.add_token(PatternToken(";", lambda _: MatchedToken(TOKEN_NAME_SEMICOLON, ";", "")))
    lexer.add_token(PatternToken("=", lambda _: MatchedToken(TOKEN_NAME_EQUALS, "=", "")))


    lexer.add_token(PatternToken(r"static_cast<(int|float)>", \
        lambda matched_string: MatchedToken(TOKEN_NAME_CAST, matched_string, SymbolTable.Types.INT if matched_string.find("int") != -1 else SymbolTable.Types.FLOAT)))

    lexer.add_token(PatternToken("int", lambda _: MatchedToken(TOKEN_NAME_TYPE_INT, "int", "")))
    lexer.add_token(PatternToken("float", lambda _: MatchedToken(TOKEN_NAME_TYPE_FLOAT, "float", "")))
    lexer.add_token(PatternToken("[a-zA-Z][a-zA-Z0-9]*", lambda matched_string: MatchedToken(TOKEN_NAME_ID, matched_string, matched_string)))

    lexer.add_token(PatternToken(r"\d+", lambda matched_string: MatchedToken(TOKEN_NAME_NUM, matched_string, int(matched_string))))
    lexer.add_token(PatternToken(r"\d+\.\d+", lambda matched_string: MatchedToken(TOKEN_NAME_NUM, matched_string, float(matched_string))))

    lexer.add_token(PatternToken(r"\n", lexer._handle_new_line))
    lexer.add_token(PatternToken(r"\s", lexer._handle_white_spaces))
    lexer.add_token(PatternToken(r"/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/", lexer._handle_new_line))
    lexer.add_token(PatternToken(r".{1}", lexer._handle_invalid_token))

if __name__ == "__main__":
    main()