from collections import namedtuple
from lark import Visitor
from consts import TOKEN_NAME_ID, TOKEN_NAME_TYPE_INT

from exceptions import CPLException

Symbol = namedtuple("Symbol", ["name", "type", "line"])

class SymbolTableVisitor(Visitor):
    def __init__(self, symbol_table):
        self.errors = []
        self.symbol_table = symbol_table
        self._init_declaration_list()

    def _init_declaration_list(self):
        self.current_declaration_type = None
        self.current_declaration_vars = []
    
    def declaration(self, _):
        for variable in self.current_declaration_vars:
            try:
                self.symbol_table.try_add_symbol(variable.value, self.current_declaration_type, variable.line)
            except SymbolRedefenitionException as e:
                self.errors.append(e)

        self._init_declaration_list()
    
    def idlist(self, tree):
        for variable in tree.children:
            if variable.type == TOKEN_NAME_ID:
                self.current_declaration_vars.append(variable)
    
    def type(self, tree):
        type = tree.children[0]
        if type == TOKEN_NAME_TYPE_INT:
            self.current_declaration_type = SymbolTable.Types.INT
        else:
            self.current_declaration_type = SymbolTable.Types.FLOAT
    

class SymbolTable():
    class Types:
        INT = "Integer"
        FLOAT = "Floating Point"
    
    def __init__(self):
        self.symbols = {}
    
    def try_add_symbol(self, name, type, line_number):
        if name in self.symbols:
            raise SymbolRedefenitionException(self.symbols[name], name, line_number)
        
        self.symbols[name] = Symbol(name, type, line_number)
    
    def try_get_symbol(self, name, line_number):
        if name not in self.symbols:
            raise SymbolUndefinedException(name, line_number)
    
    @classmethod
    def generate_symbol_table(self, ast):
        symbol_table = self()
        visitor = SymbolTableVisitor(symbol_table)
        visitor.visit(ast)
        return visitor.errors, symbol_table
    

class SymbolRedefenitionException(CPLException):
    def __init__(self, first_decl, second_decl, line_number):
        super().__init__("Symbol {redecl_name} has already defined in line {origin_line}".format(redel_name=second_decl, origin_line=first_decl.line), line_number)

class SymbolUndefinedException(CPLException):
    def __init__(self, name, line_number):
        super().__init__("Undefined reference to symbol {name}".format(name), line_number)