class FinalCode:
	codes = []

	def update_code(self, code_number, operand_number, value):
		self.codes[code_number][operand_number] = value

	def add_code(self, code):
		self.codes.append(code)

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
	switch_stack = []
	loop_continues_destination = []
	loop_continues = []
	loop_breaks = []
	symbol_table = {}
	finalCode = FinalCode()
	parser = {}
	next_token = "-1"
	_WILL_BE_SET_LATER = "%"
	_START_OF_LOOP_CHAR = "^"
	_HAVE_DEFAULT_CHAR = "~"
	_START_OF_IF = "#"
	_START_OF_SWITCH = "!"

	def __init__(self, parser, symbol_table):
		self.symbol_table = symbol_table
		self.parser = parser

	def get_temp(self, size):
		return self.symbol_table.new_temp(size)

	def get_address_or_immediate_value(self, value):
		if value[0] == "_":
			return value[1:]
		if value[0] == "@":
			return value[0] + value[2:]
		try:
			val = int(value)
			return "#" + str(val)
		except ValueError:
			x = self.symbol_table.get_var(value)
			if x.type_of_data == "array":
				return "@" + str(x.address)
			return str(x.address)

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def get_pc(self):
		return self.finalCode.get_pc()

	def add_code(self, code):
		self.finalCode.add_code(code)

	def check_type(self, operand0, operand2, operand3):
		if self.symbol_table.get_var_type(operand2) == "bool" or self.symbol_table.get_var_type(operand2) == "char":
			return -1
		if self.symbol_table.get_var_type(operand2) == self.symbol_table.get_var_type(operand3):
			return self.symbol_table.get_var_type(operand2)
		return -1

	def update_code(self, code_number, operand_number, value):
		self.finalCode.update_code(int(code_number), int(operand_number), value)

	def push_pc(self):
		self.push_to_semantic_stack(self.get_pc())

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
		else:
			return  # TODO error

	def c_desc_with_assign(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)
			operand2 = self.get_address_or_immediate_value(self.get_next_token_value())
			code = ["mov", self.symbol_table.get_var_address(name), operand2]
			self.add_code(code)
		else:
			return  # TODO error

	def c_desc_normal_array(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, self.get_next_token_value())
		else:
			return  # TODO error

	def c_desc_weird_array(self):
		datas = []
		while self.get_top_semantic_stack() != ']':
			datas.append(self.pop_from_semantic_stack())
		self.pop_from_semantic_stack()
		name = self.pop_from_semantic_stack()
		var_type = self.pop_from_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, len(datas))
		else:
			return  # TODO error
		var = self.symbol_table.get_var(name)
		type_size = var.type_size
		address = var.address
		for data in reversed(datas):
			self.add_code(["mov", str(address), self.get_address_or_immediate_value(data)])
			address += int(type_size)

	def complete_assignment(self):
		operand3_var = self.pop_from_semantic_stack()
		operand3 = self.get_address_or_immediate_value(operand3_var)
		assignment_operator = str(self.pop_from_semantic_stack())
		operand1_var = self.pop_from_semantic_stack()
		operand1 = self.get_address_or_immediate_value(operand1_var)
		code = []
		right_code = []
		if self.check_type(assignment_operator, operand1_var, operand3_var) < 0:
			return -1  # TODO error
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
		self.add_code(code)
		return

	def push_start_of_if(self):
		self.semantic_stack.append(self._START_OF_IF)

	def start_of_if(self):
		condition_result = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		code = ["jnz", str(condition_result), self._WILL_BE_SET_LATER]
		self.push_to_semantic_stack(self.get_pc())
		self.add_code(code)

	def if_jump_out(self):
		where_to_update = int(self.pop_from_semantic_stack())
		last_of_stl = self.get_pc()
		self.update_code(where_to_update, 2, int(last_of_stl + 1))
		code = ["jmp", "%"]
		self.push_to_semantic_stack(last_of_stl)
		self.add_code(code)

	def for_jump_out(self):
		condition_result = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		self.push_pc()
		code1 = ["jnz", condition_result, self._WILL_BE_SET_LATER]
		self.add_code(code1)
		self.push_pc()
		code2 = ["jmp", self._WILL_BE_SET_LATER]
		self.add_code(code2)
		self.push_pc()

	def for_go_to_expression(self):
		x = self.pop_from_semantic_stack()
		jmp_out_pc = self.pop_from_semantic_stack()
		jnz_st_pc = self.pop_from_semantic_stack()
		where_jump_now = self.pop_from_semantic_stack()
		code = ["jmp", where_jump_now]
		self.add_code(code)
		self.update_code(jnz_st_pc, 2, self.get_pc())
		self.push_to_semantic_stack(x)
		self.push_to_semantic_stack(jmp_out_pc)

	def complete_for(self):
		jmp_out_need_pc = self.pop_from_semantic_stack()
		where_jump_now = self.pop_from_semantic_stack()
		code = ["jmp", where_jump_now]
		self.add_code(code)
		self.update_code(jmp_out_need_pc, 1, self.get_pc())

	def end_of_all_if(self):
		pc = self.get_pc()
		while str(self.get_top_semantic_stack()) != self._START_OF_IF:
			temp = int(self.pop_from_semantic_stack())
			self.update_code(temp, 1, pc)
		self.pop_from_semantic_stack()

	def do_while_end(self):
		condition_result = self.pop_from_semantic_stack()
		start_of_do_while = self.pop_from_semantic_stack()
		self.add_code(["jnz", str(condition_result), str(start_of_do_while)])

	def start_of_loop(self):
		self.loop_continues.append(self._START_OF_LOOP_CHAR)
		self.loop_breaks.append(self._START_OF_LOOP_CHAR)

	def end_of_loop(self):
		break_destination = self.get_pc()
		continue_destination = self.loop_continues_destination.pop()
		while self.loop_breaks[-1] != self._START_OF_LOOP_CHAR:
			self.update_code(self.loop_breaks.pop(), 1, break_destination)
		while self.loop_continues[-1] != self._START_OF_LOOP_CHAR:
			self.update_code(self.loop_continues.pop(), 1, continue_destination)
		self.loop_continues.pop()
		self.loop_breaks.pop()

	def for_simple_assign(self):
		value = self.get_address_or_immediate_value(self.get_next_token_value())
		destination = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		code = ["mov", value, destination]
		self.add_code(code)

	def for_simple_declaration(self):
		value = self.get_address_or_immediate_value(self.get_next_token_value())
		var_name = self.pop_from_semantic_stack()
		var_type = self.pop_from_semantic_stack()
		if not self.symbol_table.is_var_declared(var_name):
			self.symbol_table.new_variable(var_name, var_type, 1)
			code = ["mov", self.symbol_table.get_var_address(var_name), value]
			self.add_code(code)
		else:
			return  # TODO error

	def id_inc_dec(self):
		operand = self.pop_from_semantic_stack()
		id = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		self.inc_id_dec(operand, id)

	def inc_dec_id(self):
		id = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		operand = self.pop_from_semantic_stack()
		self.inc_id_dec(operand, id)

	def inc_id_dec(self, operand, id):
		code = []
		if operand == "++":
			code.append("add")
		elif operand == "--":
			code.append("sub")
		code.append(id)
		code.append("#1")
		self.add_code(code)

	def push_continue_destination(self):
		self.loop_continues_destination.append(self.get_pc())

	def start_of_while(self):
		condition_result = self.pop_from_semantic_stack()
		self.push_to_semantic_stack(self.get_pc())
		code = ["jz", condition_result, self._WILL_BE_SET_LATER]
		self.add_code(code)

	def end_of_while(self):
		where_dest_should_update = self.pop_from_semantic_stack()
		where_should_jump = self.pop_from_semantic_stack()
		code = ["jmp", where_should_jump]
		self.add_code(code)
		self.update_code(where_dest_should_update, 2, self.get_pc())

	def push_break(self):
		self.loop_breaks.append(self.get_pc())
		self.add_code(["jmp", self._WILL_BE_SET_LATER])

	def mult_expression(self):
		operand0 = "mult"
		self.math_expression_for_all(operand0)

	def divide_expression(self):
		operand0 = "div"
		self.math_expression_for_all(operand0)

	def add_expression(self):
		operand0 = "add"
		self.math_expression_for_all(operand0)

	def sub_expression(self):
		operand0 = "sub"
		self.math_expression_for_all(operand0)

	def math_expression_for_all(self, operand0):
		oper2_var = self.pop_from_semantic_stack()
		oper3_var = self.pop_from_semantic_stack()
		operand2 = self.get_address_or_immediate_value(oper2_var)
		operand3 = self.get_address_or_immediate_value(oper3_var)
		temp_var_type = self.check_type(operand0, oper2_var, oper3_var)
		if temp_var_type < 0:
			# TODO Error
			return
		destination_temp = self.get_temp(temp_var_type)
		operand1 = self.get_address_or_immediate_value(destination_temp)
		code = [operand0, operand1, operand2, operand3]
		self.add_code(code)
		self.push_to_semantic_stack(destination_temp)

	def array(self):
		index = self.get_address_or_immediate_value(self.pop_from_semantic_stack())
		array_name = self.pop_from_semantic_stack()
		array = self.symbol_table.get_var(array_name)
		if array.type_of_data != "array":
			# TODO array
			return
		array_start = array.address
		array_type_size = array.type_size
		temp1_address = self.get_address_or_immediate_value(self.get_temp(4))
		temp2 = self.get_temp(4)
		temp2_address = self.get_address_or_immediate_value(temp2)
		code1 = ["mult", temp1_address, array_type_size, index]
		code2 = ["add", temp2_address, array_start, temp1_address]
		self.add_code(code1)
		self.add_code(code2)
		self.push_to_semantic_stack("@" + str(temp2))

	def push_continue(self):
		self.loop_continues.append(self.get_pc())
		self.add_code(["jmp", self._WILL_BE_SET_LATER])

	def start_of_switch_case(self):
		self.loop_breaks.append(self._START_OF_LOOP_CHAR)
		self.push_pc()
		self.push()
		self.push_to_semantic_stack(self._START_OF_SWITCH)
		code = ["jmp", self._WILL_BE_SET_LATER]
		self.add_code(code)

	def push_default(self):
		self.push_pc()
		self.push_to_semantic_stack(self._HAVE_DEFAULT_CHAR)

	def complete_switch(self):
		default_pc = -1
		here_start_pc = self.get_pc()
		if self.get_top_semantic_stack() == self._HAVE_DEFAULT_CHAR:
			self.pop_from_semantic_stack()
			default_pc = self.pop_from_semantic_stack()
		jeq = []
		while self.get_top_semantic_stack() != self._START_OF_SWITCH:
			jeq.append([self.pop_from_semantic_stack(), self.pop_from_semantic_stack()])
		self.pop_from_semantic_stack()
		var = self.pop_from_semantic_stack()
		start_pc = self.pop_from_semantic_stack()
		for case in reversed(jeq):
			equal_value = self.get_address_or_immediate_value(case[0])
			code = ["jeq", self.get_address_or_immediate_value(var), equal_value, case[1]]
			self.add_code(code)
		self.update_code(start_pc, 1, here_start_pc)
		if default_pc != -1:
			code = ["jmp", default_pc]
			self.add_code(code)
		end_pc = self.get_pc()
		print(start_pc)
		while self.loop_breaks[-1] != self._START_OF_LOOP_CHAR:
			self.update_code(self.loop_breaks.pop(), 1, end_pc)
		self.loop_breaks.pop()

	def generate_code(self, semantic_code, next_token):
		self.next_token = next_token
		# print("semantic code = ", semantic_code)
		getattr(self, semantic_code[1:])()
