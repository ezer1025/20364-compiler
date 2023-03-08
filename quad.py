from ir import QuadInstruction
from symbol_table import SymbolTable


def get_quad(ir):
    line_number = 1
    labels_dictionary = {}

    quad = []

    # removing every label placeholder and registering its line number to alter the jumps
    for instruction in ir:
        if instruction.operator == "label":
            labels_dictionary[instruction.destination] = line_number
        else:
            quad.append(instruction)
            line_number += 1
    
    result = []

    # altering the jumps to have offset instead of label placeholders
    for instruction in quad:
        if instruction.operator == "jump":
            result.append(QuadInstruction("jump", SymbolTable.Types.INT, labels_dictionary[instruction.destination], "", ""))
        elif instruction.operator == "jump_zero":
            result.append(QuadInstruction("jump_zero", SymbolTable.Types.INT, labels_dictionary[instruction.destination], instruction.first_operand, ""))
        else:
            result.append(instruction)
    
    return result