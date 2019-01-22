from lark import Lark, Transformer, v_args

BOOLEAN_EXPRESSION_GRAMMAR = """
    ?start: boolean_sum
    
    ?boolean_sum: boolean_product
        | boolean_sum "or" boolean_product -> or_expression

    ?boolean_product: boolean_atom
        | boolean_product "and" boolean_atom -> and_expression

    ?boolean_atom: "false"
         | "true"
         | "(" boolean_sum ")"
         | sum_comparision

    ?sum_comparision: sum "<" sum -> less_comparision
        | sum ">" sum -> greater_comparision
        | sum "==" sum -> equal_comparision
        | sum "!=" sum -> not_equal_comparision
        | sum ">=" sum -> greater_equal_comparision
        | sum "<=" sum -> less_equal_comparision

    ?sum: product
        | sum "+" product -> add_expression
        | sum "-" product -> sub_expression

    ?product: atom
        | product "*" atom -> mult_expression
        | product "/" atom -> div_expression

    ?atom: NUMBER -> number
         | NAME -> identifier
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)
class CalculateBooleanExpressionTree(Transformer):
    def __init__(self, code_generator):
        self._code_generator = code_generator

    def number(self, x):
        try:
            return int(x)
        except ValueError:
            pass
        try:
            return float(x)
        except ValueError:
            pass
        return str(x)

    def identifier(self, x):
        return str(x)

    def and_expression(self, x, y):
        return self.math_expression(x, y, "and")

    def or_expression(self, x, y):
        return self.math_expression(x, y, "or")

    def add_expression(self, x, y):
        return self.math_expression(x, y, "add")

    def mult_expression(self, x, y):
        return self.math_expression(x, y, "mult")

    def sub_expression(self, x, y):
        return self.math_expression(x, y, "sub")

    def div_expression(self, x, y):
        return self.math_expression(x, y, "div")

    def math_expression(self, x, y, operand0):
        self._code_generator.push_to_semantic_stack(x)
        self._code_generator.push_to_semantic_stack(y)
        self._code_generator.math_expression_for_all(operand0)
        return self._code_generator.pop_from_semantic_stack()

    def comparision_expression(self, x, y, jump_type):
        oper2_var = x
        oper3_var = y
        operand2 = self._code_generator.get_address_or_immediate_value(oper2_var)
        operand3 = self._code_generator.get_address_or_immediate_value(oper3_var)
        temp_var_type = self._code_generator.check_type("less", oper2_var, oper3_var)
        temp1 = self._code_generator.get_temp(temp_var_type)
        operand1 = self._code_generator.get_address_or_immediate_value(temp1)
        code1 = ["sub", operand1, operand2, operand3]
        temp_var_type = self._code_generator.check_type("less", oper2_var, oper3_var)
        temp2 = self._code_generator.get_temp("bool")
        code2 = ["mov", str(temp2), "#1"]
        code3 = [jump_type, str(temp1), str(self._code_generator.get_pc() + 3)]
        code4 = ["mov", str(temp2), "#0"]
        self._code_generator.add_code(code1)
        self._code_generator.add_code(code2)
        self._code_generator.add_code(code3)
        self._code_generator.add_code(code4)
        return temp2

    def less_expression(self, x, y):
        return self.comparision_expression(x, y, "jl")

    def greater_expression(self, x, y):
        return self.comparision_expression(x, y, "jg")

    def equal_expression(self, x, y):
        return self.comparision_expression(x, y, "jeq")

    def not_equal_expression(self, x, y):
        return self.comparision_expression(x, y, "jne")

    def less_equal_expression(self, x, y):
        return self.comparision_expression(x, y, "jle")

    def greater_equal_expression(self, x, y):
        return self.comparision_expression(x, y, "jge")


class BooleanExpressionParser:
    def __init__(self, code_generator):
        self._code_generator = code_generator
        self._lark_parser = Lark(BOOLEAN_EXPRESSION_GRAMMAR, parser='lalr', transformer=CalculateBooleanExpressionTree(code_generator))

    def parse(self, tokens):
        token_values_str = " ".join([str(token.value) for token in tokens])
        self._lark_parser.parse(token_values_str)
