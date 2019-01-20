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

	def get_address_or_immediate_value(self):
		#TODO
		return

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(self.finalCode.get_pc())

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def push(self):
		return self.semantic_stack.append(self.get_next_token_value())

	def get_next_token_value(self):
		return self.next_token.value

	def get_next_token_type(self):
		return self.next_token.type

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
			self.finalCode.add_rule(["mov", self.symbol_table.get_var_address(name), "#" + self.get_next_token_value()])

	def c_desc_normal_array(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, self.get_next_token_value())

	def c_desc_weird_array(self):
		datas = []
		while self.get_top_semantic_stack() != ']':
			datas.append(self.pop_from_semantic_stack())
		self.pop_from_semantic_stack()
		name = self.pop_from_semantic_stack()
		var_type = self.pop_from_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, len(datas))
		var = self.symbol_table.get_var(name)
		type_size = var.type_size
		address = var.address
		for data in reversed(datas):
			self.finalCode.add_rule(["mov", str(address), "#" + data])
			address += int(type_size)

	def complete_assignment(self):
		oper3_type = str(self.get_next_token_type())
		oper3_value = str(self.get_next_token_value())
		oper3 = ""
		assignment_operator = str(self.pop_from_semantic_stack())
		oper1 = self.symbol_table.get_var_address(self.pop_from_semantic_stack())
		if oper3_type == "identifier":
			oper3 = self.symbol_table.get_var_address(oper3_value)
		elif oper3_type == "number":
			oper3 = "#" + str(oper3_value)

		print("oper1 =", oper1)
		print("oper3 =", oper3)
		print("assignment_operator=", assignment_operator)
		code = []
		right_code = []
		if assignment_operator == "=":
			code.append("mov")
			right_code.append(oper3)
		else:
			right_code.append(oper1)
			right_code.append(oper3)
			if assignment_operator == "+=":
				code.append("add")
			elif assignment_operator == "-=":
				code.append("sub")
			elif assignment_operator == "*=":
				code.append("mult")
			elif assignment_operator == "/=":
				code.append("div")
		code.append(oper1)
		for right in right_code:
			code.append(right)
		self.finalCode.add_rule(code)
		return

	def generate_code(self, semantic_rule, next_token):
		self.next_token = next_token
		print("semantic rule =", semantic_rule)
		# switch case on semantic rule
		if semantic_rule == "@push_pc":
			self.push_pc()
		elif semantic_rule == "@push":
			self.push()
		elif semantic_rule == "@pop":
			self.pop_from_semantic_stack()
		elif semantic_rule == "@c_desc":
			self.c_desc()
		elif semantic_rule == "@c_desc_with_assign":
			self.c_desc_with_assign()
		elif semantic_rule == "@c_desc_normal_array":
			self.c_desc_normal_array()
		elif semantic_rule == "@c_desc_weird_array":
			self.c_desc_weird_array()
		elif semantic_rule == "@complete_assignment":
			self.complete_assignment()
