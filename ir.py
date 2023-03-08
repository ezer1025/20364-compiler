import uuid
from enum import Enum
from lark import Transformer
from consts import *
from exceptions import CPLException

from symbol_table import SymbolTable, SymbolUndefinedException

class QuadInstruction:
    INSTRUCTION_TRANSLATION_TABLE = {
        ("=", SymbolTable.Types.INT): "IASN",
        ("=", SymbolTable.Types.FLOAT): "RASN",
        ("OUTPUT", SymbolTable.Types.INT): "IPRT",
        ("OUTPUT", SymbolTable.Types.FLOAT): "RPRT",
        ("INPUT", SymbolTable.Types.INT): "IINP",
        ("INPUT", SymbolTable.Types.FLOAT): "RINP",
        ("==", SymbolTable.Types.INT): "IEQL",
        ("==", SymbolTable.Types.FLOAT): "REQL",
        ("!=", SymbolTable.Types.INT): "INQL",
        ("!=", SymbolTable.Types.FLOAT): "RNQL",
        ("<", SymbolTable.Types.INT): "ILSS",
        ("<", SymbolTable.Types.FLOAT): "RLSS",
        (">", SymbolTable.Types.INT): "IGRT",
        (">", SymbolTable.Types.FLOAT): "RGRT",
        ("+", SymbolTable.Types.INT): "IADD",
        ("+", SymbolTable.Types.FLOAT): "RADD",
        ("-", SymbolTable.Types.INT): "ISUB",
        ("-", SymbolTable.Types.FLOAT): "RSUB",
        ("*", SymbolTable.Types.INT): "IMLT",
        ("*", SymbolTable.Types.FLOAT): "RMLT",
        ("/", SymbolTable.Types.INT): "IDIV",
        ("/", SymbolTable.Types.FLOAT): "RDIV",
        ("CAST", SymbolTable.Types.INT): "RTOI",
        ("CAST", SymbolTable.Types.FLOAT): "ITOR",

        ("jump", SymbolTable.Types.INT): "JUMP",
        ("jump_zero", SymbolTable.Types.INT): "JMPZ",
        ("halt", SymbolTable.Types.INT): "HALT",

        ("label", SymbolTable.Types.INT): "label"
    }

    def __init__(self, operator, type, dest, first_operand, second_operand):
        self.operator = operator
        self.type = type
        self.destination = dest
        self.first_operand = first_operand
        self.second_operarnd = second_operand
    
    @property
    def instruction(self):
        return self.INSTRUCTION_TRANSLATION_TABLE[(self.operator, self.type)]

    @property
    def code(self):
        return "{} {} {} {}".format(self.instruction, self.destination, self.first_operand, self.second_operarnd).strip()
    
class TemporaryVariableFactory():
    counter = 0

    @staticmethod
    def reset():
        TemporaryVariableFactory.counter = 0
    
    @staticmethod
    def get():
        name = "t{}".format(TemporaryVariableFactory.counter)
        TemporaryVariableFactory.counter += 1
        return name

class CPLAST2IR(Transformer):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
    
    def start(self, tree):
        return Program(tree)
    
    def stmt_block(self, tree):
        return StatementBlock(tree)

    def stmtlist(self, tree):
        return StatementList(tree)

    def stmt(self, tree):
        return Statement(tree)
    
    def assignment_stmt(self, tree):
        return AssignmentStatement(tree, self.symbol_table)
    
    def expression(self, tree):
        return Expression(tree)
    
    def term(self, tree):
        return Term(tree)
    
    def factor(self, tree):
        return Factor(tree, self.symbol_table)
    
    def boolexpr(self, tree):
        return BoolExpression(tree)
    
    def boolterm(self, tree):
        return BoolTerm(tree)
    
    def boolfactor(self, tree):
        return BoolFactor(tree)
    
    def input_stmt(self, tree):
        return InputStatement(tree, self.symbol_table)
    
    def output_stmt(self, tree):
        return OutputStatement(tree)
    
    def if_stmt(self, tree):
        return IfStatement(tree)
    
    def while_stmt(self, tree):
        return WhileStatement(tree)
    
    def switch_stmt(self, tree):
        return SwitchStatement(tree)
    
    def castlist(self, tree):
        return Caselist(tree)
    
    def break_stmt(self, tree):
        return BreakStatement(tree)
    
    def epsilon(self, tree):
        pass
    

class GrammarVariable:
    class NODE_TYPES(Enum):
        NODE_TYPE_EXPRESSION = 1
        NODE_TYPE_TERM = 2
        NODE_TYPE_FACTOR = 3
        NODE_TYPE_BOOL_EXPRESSION = 4
        NODE_TYPE_BOOL_TERM = 5
        NODE_TYPE_BOOL_FACTOR = 6

        NODE_TYPE_STATEMENT_LIST = 7
        NODE_TYPE_CASE_LIST = 8

        EPSILON = 9
        
    def __init__(self):
        self.errors = []
        self.breaks = set()
    
    def get_node_type(self):
        try:
            return self.NODE_TYPE
        except:
            return None
    
    def handle_binary(self, tree):
        self.fix_binary_operands_types(tree)            
        self.code.append(QuadInstruction(tree[1].value, self.type, self.value, tree[0].value, tree[2].value))
    
    def fix_binary_operands_types(self, tree):
        # makes sure that both operands are of the same type, and casting one of them if needed

        self.code = tree[0].code
        self.code.extend(tree[2].code)
        self.value = TemporaryVariableFactory.get()

        left_operand = tree[0].value
        right_operand = tree[2].value

        if tree[0].type != tree[2].type:
            # if they are of different types, the result must be FLOAT and one of them must be INT
            self.type = SymbolTable.Types.FLOAT
            temporary_variable = TemporaryVariableFactory.get()

            # choosing the right operand to convert according to its type (INT should be converted to FLOAT)
            conversion_operand = left_operand if tree[0].type == SymbolTable.Types.INT else right_operand
            self.code.append(QuadInstruction("CAST", self.type, temporary_variable, conversion_operand, ""))

            # rewriting the subtrees values according to the converted variable
            tree[0].value, tree[2].value = (temporary_variable, right_operand) if tree[0].type == SymbolTable.Types.INT else (left_operand, temporary_variable)
            tree[0].type = tree[2].type = self.type
        else:
            self.type = tree[0].type

class Program(GrammarVariable):
    def __init__(self, tree):
        super().__init__()

        self.breaks = self.breaks.union(tree[1].breaks)
        self.code = tree[1].code + [QuadInstruction("halt", SymbolTable.Types.INT, "", "", "")]

        # we recorded every appearance of break statement out of while/switch statements and now we need to report their appearance
        for _break in self.breaks:
            self.errors.append(SemanticException("Unexpected 'break' statement (outside of 'while'/'switch' statement)", _break.line))

class StatementBlock(GrammarVariable):
    def __init__(self, tree):
        super().__init__()
        
        self.code = tree[1].code
        self.breaks = self.breaks.union(tree[1].breaks)

class StatementList(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_STATEMENT_LIST
    def __init__(self, tree):
        super().__init__()

        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_STATEMENT_LIST:
            self.code = tree[0].code + tree[1].code
            self.breaks = self.breaks.union(tree[0].breaks)
            self.breaks = self.breaks.union(tree[1].breaks)
        else:
            self.code = []

class Statement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()

        self.code = tree[0].code
        self.breaks = self.breaks.union(tree[0].breaks)

class AssignmentStatement(GrammarVariable):
    def __init__(self, tree, symbol_table):
        super().__init__()

        # reusing the Factor code to resolve the variable from the symbol table
        id = Factor(tree, symbol_table)

        # cannot assign float to integer variable
        if id.type == SymbolTable.Types.INT and tree[2].type == SymbolTable.Types.FLOAT:
            self.errors = [SemanticException("Unable to assign floating point number to integer variable", tree[1].line)]
            self.code = []
        else:
            self.type = id.type
            self.value = id.value
            left_operand = tree[2].value

            self.code = tree[2].code
            
            # if they are of different type, we should convert the assigned expression to FLOAT
            if id.type == SymbolTable.Types.FLOAT and tree[2].type == SymbolTable.Types.INT:
                temporary_variable = TemporaryVariableFactory.get()
                left_operand = temporary_variable
                self.code.append(QuadInstruction("CAST", id.type, temporary_variable, tree[2].value, ""))

            self.code.append(QuadInstruction("=", self.type, self.value, left_operand, ""))

class InputStatement(GrammarVariable):
    def __init__(self, tree, symbol_table):
        super().__init__()

        # reusing the Factor code to resolve the variable from the symbol table
        tree[2] = Factor([tree[2]], symbol_table)
        self.type = tree[2].type
        self.code = tree[2].code
        self.value = tree[2].value

        self.code.append(QuadInstruction("INPUT", self.type, self.value, "", ""))

class OutputStatement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()

        self.type = tree[2].type
        self.code = tree[2].code
        self.value = tree[2].value

        self.code.append(QuadInstruction("OUTPUT", self.type, self.value, "", ""))

class IfStatement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()

        false_stmt_label = uuid.uuid4().hex
        end_stmt_label = uuid.uuid4().hex

        # adding every break statement which don't belong to while/swith statement
        self.breaks = self.breaks.union(tree[4].breaks)
        self.breaks = self.breaks.union(tree[6].breaks)

        # Appearance list: Condition code, jump to the "Else statement" if the condition does not met, true statement, jump to the end of the if after the true statement
        #   placeholder for the calculation of the "Else statement" conditional jump, "else statement" code and a placeholder for the calculation of the end of the if
        self.code = (
            tree[2].code +
            [QuadInstruction("jump_zero", SymbolTable.Types.INT, false_stmt_label, tree[2].value, "")] +
            tree[4].code +
            [QuadInstruction("jump", SymbolTable.Types.INT, end_stmt_label, "", ""), QuadInstruction("label", SymbolTable.Types.INT, false_stmt_label, "", "")] +
            tree[6].code +
            [QuadInstruction("label", SymbolTable.Types.INT, end_stmt_label, "", "")]
        )

class WhileStatement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()

        condition_label = uuid.uuid4().hex
        end_while_label = uuid.uuid4().hex

        # adding for every appearace of break statement the end of the while placeholding label to be calculated later as the jump offset
        for _break in tree[4].breaks:
            _break.label = end_while_label

        # Appearance list: start of the while placeholder for the calculation of the repeating condition, condition code, conditional jump to the end of the while-loop,
        #   true statement code, jump to the start of the condition code, placeholder for the end of the while-loop
        self.code = (
            [QuadInstruction("label", SymbolTable.Types.INT, condition_label, "", "")] +
            tree[2].code +
            [QuadInstruction("jump_zero", SymbolTable.Types.INT, end_while_label, tree[2].value, "")] +
            tree[4].code +
            [QuadInstruction("jump", SymbolTable.Types.INT, condition_label, "", ""), QuadInstruction("label", SymbolTable.Types.INT, end_while_label, "", "")]
        )

class SwitchStatement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()
        self.code = []

        if tree[2].type != SymbolTable.Types.INT:
            self.errors = [SemanticException("Invalid switch condition - must be of an integer value", tree[0].line)] 
        else:
            # creating placeholders for each condition, the default and the end of the switch
            end_stmt_label = uuid.uuid4().hex
            default_stmt_label = uuid.uuid4().hex
            conditions_labels = { case_number: uuid.uuid4().hex for case_number in tree[5].cases }

            listed_cases = list(tree[5].cases)

            # the condition code
            self.code = tree[2].code

            # temporary variable to check the whether the condition is met
            temporary_variable = TemporaryVariableFactory.get()

            for index, (key, value) in enumerate(tree[5].cases):
                # placeholder of the current condition and a checking if the condition is met
                self.code.extend([QuadInstruction("label", SymbolTable.Types.INT, conditions_labels[key], "", ""), 
                                  QuadInstruction("==", SymbolTable.Types.INT, temporary_variable, tree[2].value, key)])
                
                # if there are more conditions to check, create a conditional jump to the next condition, otherwise to the default condition
                if index + 1 == len(tree[5].cases):
                    self.code.append(QuadInstruction("jump_zero", SymbolTable.Types.INT, default_stmt_label, temporary_variable, ""))
                else:
                    next_key, _ = listed_cases[index + 1]
                    self.code.append(QuadInstruction("jump_zero", SymbolTable.Types.INT, conditions_labels[next_key], "", ""))
                
                # add the case code so if the condition is met, the case code will be executed
                self.code += value.code
            
            # add a placeholder for the default case, the default case code and the end of the switch statement to be jumped by break statements
            self.code += (
                [QuadInstruction("label", SymbolTable.Types.INT, default_stmt_label, "", "")] +
                tree[8].code +
                [QuadInstruction("label", SymbolTable.Types.INT, end_stmt_label, "", "")]
            )

            # update all the break appearances with the placeholder of the end of the switch to be jumped
            for _break in tree[5].breaks.union(tree[8].breaks):
                _break.label = end_stmt_label


class Caselist(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_CASE_LIST

    def __init__(self, tree, symbol_table):
        super().__init__()
        self.code = []
        

        # if the leftmost subtree is caselist, that means that we are not in the caselist->epsilon rule
        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_CASE_LIST:
            self.cases = {}
            self.breaks = self.breaks.union(tree[0].breaks)
            self.breaks = self.breaks.union(tree[4].breaks)

            # reusing the Factor code to resolve the case number
            case_number = Factor([tree[2]], symbol_table)

            if case_number.type != SymbolTable.Types.INT:
                self.errors = [ SemanticException("Invalid switch case number - must be of an integer value", tree[1].line)]
            else:
                self.cases.update(tree[0].cases)

                if case_number.value in self.cases:
                    self.errors = [SemanticException("Invalid switch case number - case already exist", tree[1].line)]
                else:
                    self.cases[case_number.value] = tree[4]
                    self.code = tree[0].code + tree[4].code

class BreakStatement(GrammarVariable):
    def __init__(self, tree):
        super().__init__()
        self.label = None
        self.line = tree[0].line
        self.breaks.add(self)
    
    @property
    def code(self):
        if self.label:
            return [QuadInstruction("jump", SymbolTable.Types.INT, self.label, "", "")]
        else:
            return [self]

class Expression(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_EXPRESSION

    def __init__(self, tree):
        super().__init__()

        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_EXPRESSION:
            self.handle_binary(tree)
        else:
            self.type = tree[0].type
            self.code = tree[0].code
            self.value = tree[0].value

class Term(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_TERM

    def __init__(self, tree):
        super().__init__()

        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_TERM:
            self.handle_binary(tree)
        else:
            self.type = tree[0].type
            self.code = tree[0].code
            self.value = tree[0].value

class Factor(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_FACTOR

    def __init__(self, tree, symbol_table):
        super().__init__()

        if tree[0].type == TOKEN_NAME_ID:
            self._handle_id(tree, symbol_table)
        elif tree[0].type == TOKEN_NAME_NUM:
            self._handle_num(tree)
        elif tree[0].type == TOKEN_NAME_CAST:
            self._handle_cast(tree)
        elif tree[0].type == TOKEN_NAME_LEFT_PRNTSS:
            self.code = tree[1].code
            self.type = tree[1].type
            self.value = tree[1].value

    def _handle_id(self, tree, symbol_table: SymbolTable):
        self.code = []
        try:
            symbol = symbol_table.try_get_symbol(tree[0].value, tree[0].line)
            self.type = symbol.type
            self.value = symbol.name
        except SymbolUndefinedException as e:
            self.errors = [e]
            self.type = None
            self.value = tree[0].value

    def _handle_num(self, tree):
        self.code = []
        self.type = SymbolTable.Types.FLOAT if type(tree[0].value) == float else SymbolTable.Types.INT
        self.value = float(tree[0].value) if self.type == SymbolTable.Types.FLOAT else int(tree[0].value)
    
    def _handle_cast(self, tree):
        self.type = tree[0].value
        self.code = tree[2].code
        self.value = TemporaryVariableFactory.get()

        if self.type != tree[2].type:
            self.code.append(QuadInstruction(tree[0].type, self.type, self.value, tree[2].value, ""))
        else:
            # if they are of the same type, it is just an assignment
            self.code.append(QuadInstruction("=", self.type, self.value, tree[2].value, ""))
                

class BoolExpression(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_BOOL_EXPRESSION

    def __init__(self, tree):
        super().__init__()

        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_BOOL_EXPRESSION:
            self._handle_or(tree)
        else:
            self.type = tree[0].type
            self.code = tree[0].code
            self.value = tree[0].value
        
        self.type = SymbolTable.Types.INT

    def _handle_or(self, tree):
        self.fix_binary_operands_types(tree)

        # to check if one of them is not zero, we can check if their sum isn't zero, all the numbers are non-negative
        self.code.extend([QuadInstruction("+", self.type, self.value, tree[0].value, tree[2].value), 
                          QuadInstruction(">", SymbolTable.Types.INT, self.value, self.value, 0)])

class BoolTerm(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_BOOL_TERM

    def __init__(self, tree):
        super().__init__()

        if tree[0].get_node_type() == GrammarVariable.NODE_TYPES.NODE_TYPE_BOOL_TERM:
            self._handle_and(tree)
        else:
            self.type = tree[0].type
            self.code = tree[0].code
            self.value = tree[0].value
        
        self.type = SymbolTable.Types.INT
    
    def _handle_and(self, tree):
        self.fix_binary_operands_types(tree)
        temporary_variable = TemporaryVariableFactory.get()

        # to check if both aren't zero, we can check if both equal 1
        self.code.extend([QuadInstruction("==", self.type, temporary_variable, tree[0].value, 1), 
                          QuadInstruction("==", self.type, self.value, tree[2].value, temporary_variable)])

class BoolFactor(GrammarVariable):
    NODE_TYPE = GrammarVariable.NODE_TYPES.NODE_TYPE_BOOL_FACTOR

    def __init__(self, tree):
        super().__init__()

        try:
            # if we can get the node type, that means it is an expression, otherwise it is the NOT terminal
            _ = tree[0].get_node_type()

            if tree[1].value == ">=":
                self.fix_binary_operands_types(tree)
                self.value = TemporaryVariableFactory.get()
                temporary_variable = TemporaryVariableFactory.get()
                
                # we check whether they are equal OR (with the same logic of _handle_or) one is bigger than the other
                self.code.extend([
                    QuadInstruction("==", tree[0].type, temporary_variable, tree[0].value, tree[2].value),
                    QuadInstruction(">", tree[0].type, self.value, tree[0].value, tree[2].value),
                    QuadInstruction("+", SymbolTable.Types.INT, self.value, self.value, temporary_variable), 
                    QuadInstruction(">", SymbolTable.Types.INT, self.value, self.value, 0)
                ])
            elif tree[1].value == "<=":
                self.fix_binary_operands_types(tree)
                self.value = TemporaryVariableFactory.get()
                temporary_variable = TemporaryVariableFactory.get()

                # we check whether they are equal OR (with the same logic of _handle_or) one is smaller than the other
                self.code.extend([
                    QuadInstruction("==", tree[0].type, temporary_variable, tree[0].value, tree[2].value),
                    QuadInstruction("<", tree[0].type, self.value, tree[0].value, tree[2].value),
                    QuadInstruction("+", SymbolTable.Types.INT, self.value, self.value, temporary_variable), 
                    QuadInstruction(">", SymbolTable.Types.INT, self.value, self.value, 0)
                ])
            else:
                self.handle_binary(tree)
        except:
            self.type = tree[2].type
            self.code = tree[2].code
            self.value = tree[2].value

            self.code.append(QuadInstruction("!=", self.type, self.value, self.value, "1"))
        
        self.type = SymbolTable.Types.INT
        

def get_ir(ast, symbol_table):
    TemporaryVariableFactory.reset()

    ast_transformer = CPLAST2IR(symbol_table)
    ir_tree = ast_transformer.transform(ast)

    if ast_transformer.errors:
        return ast_transformer.errors, []

    ir = []
    for instruction in ir_tree.code:
        if type(instruction) == BreakStatement:
            ir.append(instruction.code[0])
        else:
            ir.append(instruction)
    
    return None, ir

class SemanticException(CPLException):
    def __init__(self, message, line_number):
        super().__init__("Semantic Exception: {message}".format(message=message), line_number)