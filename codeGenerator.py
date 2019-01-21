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
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)

	def c_desc_with_assign(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)
			operand2 = self.get_address_or_immediate_value(self.get_next_token_value())
			code = ["mov", self.symbol_table.get_var_address(name), operand2]
			self.finalCode.add_rule(code)

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
		operand3_type = str(self.get_next_token_type())
		operand3_value = str(self.get_next_token_value())
		operand3 = ""
		assignment_operator = str(self.pop_from_semantic_stack())
		operand1 = self.symbol_table.get_var_address(self.pop_from_semantic_stack())
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
		condition_result = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		code = ["jnz", str(condition_result), self._WILL_BE_SET_LATER]
		self.push_to_semantic_stack(self.finalCode.get_pc())
		self.finalCode.add_rule(code)

	def if_jump_out(self):
		where_to_update = int(self.pop_from_semantic_stack())
		last_of_stl = self.finalCode.get_pc()
		self.finalCode.print_codes()
		self.finalCode.update_rule(where_to_update, 2, int(last_of_stl + 1))
		code = ["jmp", "%"]
		self.push_to_semantic_stack(last_of_stl)
		self.finalCode.add_rule(code)
		return

	def for_jump_out(self):
		condition_result = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		self.push_pc()
		code1 = ["jnz", condition_result, self._WILL_BE_SET_LATER]
		self.finalCode.add_rule(code1)
		self.push_pc()
		code2 = ["jmp", self._WILL_BE_SET_LATER]
		self.finalCode.add_rule(code2)

	def for_go_to_expression(self):
		jmp_out_pc = self.pop_from_semantic_stack()
		jnz_st_pc = self.pop_from_semantic_stack()
		self.finalCode.update_rule([jnz_st_pc], 2, self.finalCode.get_pc())
		where_jump_now = self.pop_from_semantic_stack()
		code = ["jmp", where_jump_now]
		self.finalCode.add_rule(code)
		self.push_to_semantic_stack(self.finalCode.get_pc())
		self.push_to_semantic_stack(jmp_out_pc)

	def complete_for(self):
		jmp_out_need_pc = self.pop_from_semantic_stack()
		where_jump_now = self.pop_from_semantic_stack()
		code = ["jmp", where_jump_now]


	def end_of_all_if(self):
		pc = self.finalCode.get_pc()
		while str(self.get_top_semantic_stack()) != "#":
			temp = int(self.pop_from_semantic_stack())
			self.finalCode.update_rule(temp, 1, pc)
		self.pop_from_semantic_stack()

	def do_while_end(self):
		condition_result = self.pop_from_semantic_stack()
		start_of_do_while = self.pop_from_semantic_stack()
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

	def for_simple_assign(self):
		value = self.get_address_or_immediate_value(self.get_next_token_value())
		destination = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		code = ["mov", value, destination]
		self.finalCode.add_rule(code)

	def for_simple_declaration(self):
		value = self.get_address_or_immediate_value(self.get_next_token_value())
		var_name = self.pop_from_semantic_stack()
		var_type = self.pop_from_semantic_stack()
		if not self.symbol_table.is_var_declared(var_name):
			self.symbol_table.new_variable(var_name, var_type, 1)
			code = ["mov", self.symbol_table.get_var_address(var_name), value]
			self.finalCode.add_rule(code)

	def push_continue_destination(self):
		self.loop_continues_destination.append(self.finalCode.get_pc())

	def start_of_while(self):
		condition_result = self.pop_from_semantic_stack()
		self.push_to_semantic_stack(self.finalCode.get_pc())
		code = ["jz", condition_result, self._WILL_BE_SET_LATER]
		self.finalCode.add_rule(code)

	def end_of_while(self):
		where_dest_should_update = self.pop_from_semantic_stack()
		where_should_jump = self.pop_from_semantic_stack()
		code = ["jmp", where_should_jump]
		self.finalCode.add_rule(code)
		self.finalCode.update_rule(where_dest_should_update, 2, self.finalCode.get_pc())

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
