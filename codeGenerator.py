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
			temp = ""
			for x in code:
				temp += str(x)
				temp += " "
			print(temp)


class CodeGenerator:
	semantic_stack = []
	symbol_table = SymbolTable()
	finalCode = FinalCode()
	parser = {}
	next_token = "-1"

	def __init__(self, parser):
		self.parser = parser

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(self.finalCode.get_pc())

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def push_next_token(self):
		return self.semantic_stack.append(self.next_token.value)

	def get_top_semantic_stack(self):
		return self.semantic_stack[-1]

	def c_desc(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)

	def c_desc_with_assign(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)
			self.finalCode.add_rule(["add", self.symbol_table.get_var_address(name), "#" + self.next_token.value])
			self.finalCode.print_codes()

	def c_desc_normal_array(self):
		return

	def generate_code(self, semantic_rule, next_token):
		self.next_token = next_token
		print("semantic rule =", semantic_rule)
		# switch case on semantic rule
		if semantic_rule == "@push_pc":
			self.push_pc()
		elif semantic_rule == "@push":
			self.push_next_token()
		elif semantic_rule == "@pop":
			self.pop_from_semantic_stack()
		elif semantic_rule == "@c_desc":
			self.c_desc()
		elif semantic_rule == "@c_desc_with_assign":
			self.c_desc_with_assign()
		elif semantic_rule == "@c_desc_normal_array":
			self.c_desc_normal_array()
