from symbolTable import SymbolTable


class FinalCode:
	codes = []

	def update_rule(self, rule_number, operand_number, value):
		self.codes[rule_number][operand_number] = value

	def add_rule(self, rule):
		self.codes.append(rule)

	def get_pc(self):
		len(self.codes)

	def print_codes(self):
		for code in self.codes:
			for x in code:
				print(x)


class CodeGenerator:
	semantic_stack = []
	symbol_table = SymbolTable()
	finalCode = FinalCode()
	parser = {}

	def __init__(self, parser):
		self.parser = parser

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(self.finalCode.get_pc())

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def push_top_parse_stack(self):
		self.semantic_stack.append(self.get_top_parse_stack())

	def get_top_parse_stack(self):
		return self.parser.get_top_parse_stack()

	def get_top_semantic_stack(self):
		return self.semantic_stack[-1]

	def c_desc(self):
		name = self.get_top_parse_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type)
			print(self.symbol_table.get_var_address(name))

	def generate_code(self, semantic_rule):
		print("semantic rule =", semantic_rule)
		# switch case on semantic rule
		if semantic_rule == "@push_pc":
			self.push_pc()
		elif semantic_rule == "@push":
			self.push_top_parse_stack()
		elif semantic_rule == "@pop":
			self.pop_from_semantic_stack()
		elif semantic_rule == "@C_DESC":
			self.c_desc()
