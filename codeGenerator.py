class FinalCode:
	codes = []

	def update_rule(self, rule_number, operand_number, value):
		self.codes[rule_number][operand_number] = value

	def add_rule(self, rule):
		self.codes.append(rule)

	def get_pc(self):
		return len(self.codes)

	def print_codes(self):
		idx = 0
		for code in self.codes:
			temp = str(idx) + " "
			for x in code:
				temp += str(x)
				temp += " "
			print(temp)
			idx += 1


class CodeGenerator:
	semantic_stack = []
	loop_continues_destination = []
	loop_continues = []
	loop_breaks = []
	symbol_table = {}
	finalCode = FinalCode()
	parser = {}
	next_token = "-1"
	_WILL_BE_SET_LATER = "%"
	_START_OF_LOOP_CHAR = "^"

	def __init__(self, parser, symbol_table):
		self.symbol_table = symbol_table
		self.parser = parser

	def get_address_or_immediate_value(self, value):
		if value[0] == "_":
			return value[1:]
		try:
			val = int(value)
			return "#" + str(val)
		except ValueError:
			return self.symbol_table.get_var_address(value)

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(self.finalCode.get_pc())

	def pop(self):
		return self.semantic_stack.pop()

	def pop_from_semantic_stack(self):
		return self.pop()

	def push(self):
		return self.semantic_stack.append(self.get_next_token_value())

	def get_next_token_value(self):
		return self.next_token.value

	def get_next_token_type(self):
		return self.next_token.type

	def get_top_semantic_stack(self):
		return self.semantic_stack[-1]

	def c_desc(self):
		name = self.pop()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)

	def c_desc_with_assign(self):
		name = self.pop()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)
			self.finalCode.add_rule(["mov", self.symbol_table.get_var_address(name), "#" + self.get_next_token_value()])

	def c_desc_normal_array(self):
		name = self.pop()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, self.get_next_token_value())

	def c_desc_weird_array(self):
		datas = []
		while self.get_top_semantic_stack() != ']':
			datas.append(self.pop())
		self.pop()
		name = self.pop()
		var_type = self.pop()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, len(datas))
		var = self.symbol_table.get_var(name)
		type_size = var.type_size
		address = var.address
		for data in reversed(datas):
			self.finalCode.add_rule(["mov", str(address), "#" + data])
			address += int(type_size)

	def complete_assignment(self):
		operand3_type = str(self.get_next_token_type())
		operand3_value = str(self.get_next_token_value())
		operand3 = ""
		assignment_operator = str(self.pop())
		operand1 = self.symbol_table.get_var_address(self.pop())
		if operand3_type == "identifier":
			operand3 = self.symbol_table.get_var_address(operand3_value)
		elif operand3_type == "number":
			operand3 = "#" + str(operand3_value)
		code = []
		right_code = []
		if assignment_operator == "=":
			code.append("mov")
			right_code.append(operand3)
		else:
			right_code.append(operand1)
			right_code.append(operand3)
			if assignment_operator == "+=":
				code.append("add")
			elif assignment_operator == "-=":
				code.append("sub")
			elif assignment_operator == "*=":
				code.append("mult")
			elif assignment_operator == "/=":
				code.append("div")
		code.append(operand1)
		for right in right_code:
			code.append(right)
		self.finalCode.add_rule(code)
		return

	def push_start_of_if(self):
		self.semantic_stack.append("#")

	def start_of_if(self):
		condition_result = self.get_address_or_immediate_value(self.pop())
		code = ["jnz", str(condition_result), self._WILL_BE_SET_LATER]
		self.push_to_semantic_stack(self.finalCode.get_pc())
		self.finalCode.add_rule(code)

	def if_jump_out(self):
		where_to_update = int(self.pop())
		last_of_stl = self.finalCode.get_pc()
		self.finalCode.print_codes()
		print(where_to_update, (last_of_stl + 1))
		self.finalCode.update_rule(where_to_update, 2, int(last_of_stl + 1))
		code = ["jmp", "%"]
		self.push_to_semantic_stack(last_of_stl)
		self.finalCode.add_rule(code)
		return

	def end_of_all_if(self):
		pc = self.finalCode.get_pc()
		while str(self.get_top_semantic_stack()) != "#":
			temp = int(self.pop())
			print(temp, pc)
			self.finalCode.update_rule(temp, 1, pc)
		self.pop()

	def do_while_end(self):
		condition_result = self.pop()
		start_of_do_while = self.pop()
		self.finalCode.add_rule(["jnz", str(condition_result), str(start_of_do_while)])

	def start_of_loop(self):
		self.loop_continues.append(self._START_OF_LOOP_CHAR)
		self.loop_breaks.append(self._START_OF_LOOP_CHAR)

	def end_of_loop(self):
		break_destination = self.finalCode.get_pc()
		continue_destination = self.loop_continues_destination.pop()
		while self.loop_breaks[-1] != self._START_OF_LOOP_CHAR:
			self.finalCode.update_rule(self.loop_breaks.pop(), 1, break_destination)
		while self.loop_continues[-1] != self._START_OF_LOOP_CHAR:
			self.finalCode.update_rule(self.loop_continues.pop(), 1, continue_destination)
		self.loop_continues.pop()
		self.loop_breaks.pop()

	def push_continue_destination(self):
		self.loop_continues_destination.append(self.finalCode.get_pc())

	def start_of_while(self):
		condintion_result = self.pop()

		return

	def end_of_while(self):
		return

	def push_break(self):
		self.loop_breaks.append(self.finalCode.get_pc())
		self.finalCode.add_rule(["jmp", self._WILL_BE_SET_LATER])

	def push_continue(self):
		self.loop_continues.append(self.finalCode.get_pc())
		self.finalCode.add_rule(["jmp", self._WILL_BE_SET_LATER])

	def generate_code(self, semantic_rule, next_token):
		self.next_token = next_token
		# print("semantic rule = ", semantic_rule)
		getattr(self, semantic_rule[1:])()
