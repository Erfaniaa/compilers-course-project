from utils import error_handler


class FinalCode:
	codes = []
	_WILL_BE_SET_LATER = "%"

	def update_code(self, code_number, operand_number, value):
		self.codes[code_number][operand_number] = value

	def add_code(self, code):
		self.codes.append(code)

	def get_pc(self):
		return len(self.codes)

	def have_main(self):
		if self.codes[0][1] == self._WILL_BE_SET_LATER:
			return False
		return True

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
	function_return_value = []
	function_return_address = []
	function_signatures = []
	semantic_stack = []
	switch_stack = []
	loop_continues_destination = []
	loop_continues = []
	loop_breaks = []
	symbol_table = {}
	finalCode = FinalCode()
	parser = {}
	function_call_jmp_that_do_not_have_pc = []  # { address,shomare function , shomare signatures }
	next_token = "-1"
	_WILL_BE_SET_LATER = "%"
	_START_OF_LOOP_CHAR = "^"
	_HAVE_DEFAULT_CHAR = "~"
	_START_OF_IF = "#"
	_START_OF_SWITCH = "!"
	_START_OF_FUNCTION = "&"
	_START_OF_FUNCTION_CALL = "*"

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
			error_handler("Syntax Error", "Types does not match")
		if self.symbol_table.get_var_type(operand2) == self.symbol_table.get_var_type(operand3):
			return self.symbol_table.get_var_type(operand2)
		error_handler("Syntax Error", "Types does not match")

	def update_code(self, code_number, operand_number, value):
		self.finalCode.update_code(int(code_number), int(operand_number), value)

	def push_pc(self):
		self.push_to_semantic_stack(self.get_pc())

	def pop(self):
		return self.semantic_stack.pop()

	def pop_from_semantic_stack(self):
		return self.pop()

	def get_type(self, var):
		return self.symbol_table.get_var_type(var)

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
			error_handler("Syntax Error", "variable with name " + name + " has already declared ")

	def c_desc_with_assign(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_variable(name, var_type)
			operand2 = self.get_address_or_immediate_value(self.get_next_token_value())
			code = ["mov", self.symbol_table.get_var_address(name), operand2]
			self.add_code(code)
		else:
			error_handler("Syntax Error", "variable with name " + name + " has already declared ")

	def c_desc_normal_array(self):
		name = self.pop_from_semantic_stack()
		var_type = self.get_top_semantic_stack()
		if not self.symbol_table.is_var_declared(name):
			self.symbol_table.new_array(name, var_type, self.get_next_token_value())
		else:
			error_handler("Syntax Error", "variable with name " + name + " has already declared ")

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
			error_handler("Syntax Error", "variable with name " + name + " has already declared ")
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
		self.check_type(assignment_operator, operand1_var, operand3_var)
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
			error_handler("Syntax Error", "variable with name " + var_name + " has already declared ")

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
		self.math_expression_for_all("mult")

	def divide_expression(self):
		self.math_expression_for_all("div")

	def add_expression(self):
		self.math_expression_for_all("add")

	def sub_expression(self):
		self.math_expression_for_all("sub")

	def math_expression_for_all(self, operand0):
		oper2_var = self.pop_from_semantic_stack()
		oper3_var = self.pop_from_semantic_stack()
		operand2 = self.get_address_or_immediate_value(oper2_var)
		operand3 = self.get_address_or_immediate_value(oper3_var)
		temp_var_type = self.check_type(operand0, oper2_var, oper3_var)
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
			error_handler("Syntax Error", array_name + " is not array")
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
		if self.get_top_semantic_stack() == self._HAVE_DEFAULT_CHAR:
			self.pop_from_semantic_stack()
			default_pc = self.pop_from_semantic_stack()
		jeq = []
		while self.get_top_semantic_stack() != self._START_OF_SWITCH:
			jeq.append([self.pop_from_semantic_stack(), self.pop_from_semantic_stack()])
		self.pop_from_semantic_stack()
		var = self.pop_from_semantic_stack()
		start_pc = self.pop_from_semantic_stack()
		jump_out_pc = self.get_pc()
		code = ["jmp", self._WILL_BE_SET_LATER]
		self.add_code(code)
		here_start_pc = self.get_pc()
		for case in reversed(jeq):
			equal_value = self.get_address_or_immediate_value(case[0])
			code = ["jeq", self.get_address_or_immediate_value(var), equal_value, case[1]]
			self.add_code(code)
		self.update_code(start_pc, 1, here_start_pc)
		if default_pc != -1:
			code = ["jmp", default_pc]
			self.add_code(code)
		end_pc = self.get_pc()
		while self.loop_breaks[-1] != self._START_OF_LOOP_CHAR:
			self.update_code(self.loop_breaks.pop(), 1, end_pc)
		self.loop_breaks.pop()
		self.update_code(jump_out_pc, 1, end_pc)

	def jump_to_main(self):
		code = ["jmp", self._WILL_BE_SET_LATER]
		self.finalCode.add_code(code)

	def start_of_function(self):
		self.push_to_semantic_stack(self._START_OF_FUNCTION)

	def function_declaration(self):
		pushed = []
		while self.get_top_semantic_stack() != self._START_OF_FUNCTION:
			pushed.append(self.pop_from_semantic_stack())
		self.pop_from_semantic_stack()
		if len(pushed) == 2 and pushed[1] == "void" and pushed[0] == "main":
			self.update_code(0, 1, self.get_pc())
		function_return_type = pushed.pop()
		function_name = pushed.pop()
		self.symbol_table.set_function_name(function_name)
		function_starting_point = self.get_pc()
		function_variables_names = []
		function_variables_types = []
		while len(pushed) != 0:
			function_variables_types.append(pushed.pop())
			function_variables_names.append(pushed.pop())
		state = 0
		function_declaration = {}
		signature_index = -1

		for item in self.function_signatures:
			if item['function_name'] != function_name:
				continue
			if item['function_name'] == "main":
				error_handler("Syntax Error", "There is at least 2 main in your code")
			if item['function_return_type'] != function_return_type:
				error_handler("Syntax Error", " function " + function_name + "has declared with different return type ")
			state = 1
			function_declaration = item
			index = 0
			for signature in item['signatures']:
				is_same = True
				if len(signature['var_types']) != len(function_variables_types):
					index += 1
					continue
				for i in range(0, len(function_variables_types)):
					if signature['var_types'][i] != function_variables_types[i]:
						is_same = False
						break
				if is_same:
					if signature['start_point'] != self._WILL_BE_SET_LATER:
						error_handler("Syntax Error",
									  " function " + function_name + " has declared with same signature")
					else:
						state = 2
						signature_index = index
						break

				index += 1

			break
		obj = {"var_types": function_variables_types, "var_names": function_variables_names,
			   "start_point": function_starting_point}
		if state == 0:
			function_declaration['function_return_type'] = function_return_type
			function_declaration['function_name'] = function_name
			function_declaration['signatures'] = [obj]
			self.function_signatures.append(function_declaration)
		elif state == 1:
			function_declaration['signatures'].append(obj)
		elif state == 2:
			function_declaration['signatures'][signature_index] = obj

	def signature_function_declaration(self):
		pushed = []
		while self.get_top_semantic_stack() != self._START_OF_FUNCTION:
			pushed.append(self.pop_from_semantic_stack())
		self.pop_from_semantic_stack()
		if len(pushed) == 2 and pushed[1] == "void" and pushed[0] == "main":
			self.update_code(0, 1, self.get_pc())
		function_return_type = pushed.pop()
		function_name = pushed.pop()
		self.symbol_table.set_function_name(function_name)
		function_variables_names = []
		function_variables_types = []
		while len(pushed) != 0:
			function_variables_types.append(pushed.pop())
			function_variables_names.append(pushed.pop())
		state = 0
		function_declaration = {}
		for item in self.function_signatures:
			if item['function_name'] != function_name:
				continue
			if item['function_name'] == "main":
				error_handler("Syntax Error", "There is at least 2 main in your code")
			if item['function_return_type'] != function_return_type:
				error_handler("Syntax Error", " function " + function_name + "has declared with different return type ")
			state = 1
			function_declaration = item
			for signature in item['signatures']:
				is_same = True
				if len(signature['var_types']) != len(function_variables_types):
					continue
				for i in range(0, len(function_variables_types)):
					if signature['var_types'][i] != function_variables_types[i]:
						is_same = False
						break
				if is_same:
					error_handler("Syntax Error",
								  " function " + function_name + " has declared with same signature")
			break
		obj = {"var_types": function_variables_types, "var_names": function_variables_names,
			   "start_point": self._WILL_BE_SET_LATER}
		if state == 0:
			function_declaration['function_return_type'] = function_return_type
			function_declaration['function_name'] = function_name
			function_declaration['signatures'] = [obj]
			self.function_signatures.append(function_declaration)
		elif state == 1:
			function_declaration['signatures'].append(obj)

	def jump_out_of_function(self):
		return

	def call_function(self):
		self.push_to_semantic_stack(self._START_OF_FUNCTION_CALL)
		return

	def finish_function_call(self):
		pushed = []
		while self.get_top_semantic_stack() != self._START_OF_FUNCTION_CALL:
			pushed.append(self.pop_from_semantic_stack())
		self.pop_from_semantic_stack()
		function_name = pushed.pop()
		pushed = list(reversed(pushed))
		func_id = 0
		sign_id = 0
		start_point_of_jump = -1
		for function_dec in self.function_signatures:
			found = False
			got_in = False
			if function_dec["function_name"] != function_name:
				func_id += 1
				continue
			sign_id = 0
			got_in = True
			for signature in function_dec["signatures"]:
				is_same = True
				if len(signature['var_types']) != len(pushed):
					sign_id += 1
					continue
				for i in range(0, len(pushed)):
					if signature['var_types'][i] != self.get_type(pushed[i]):
						is_same = False
						break
					i += 1
				if is_same:
					found = True
					start_point_of_jump = signature["start_point"]
					break
				sign_id += 1
			if got_in and not found:
				error_handler("Syntax error", "no function with this name and signature")
			if found:
				break
			func_id += 1

		return_address_size = 4
		return_value_size = self.symbol_table.get_size(self.function_signatures[func_id]['function_return_type'])
		var_size = self.symbol_table.get_all_var_size()
		variables = var_size[1]
		pop_code = []
		for var in variables:
			address = var[0]
			now_address = address
			while now_address < (address + var[1]):
				code = ["push", now_address]  # , "-", str(now_address + var[2])
				pop_code.append(["pop", now_address])  # , "-", str(now_address + var[2])
				self.add_code(code)
				now_address += var[2]
		code=["push",]









		pop_code = reversed(pop_code)
		for pop in pop_code:
			self.add_code(pop)
		var_size = var_size

	# print(return_address_size, return_value_size, var_size)

	# return address 4
	# return value  =get signature return type  1 2 4 8
	# temp_size

	# TODO know func_id des_id start_point and sign matched

	def return_not_void(self):
		return

	def return_void(self):
		return

	def check_all_function_have_signature(self):
		for item in self.function_signatures:
			for signature in item['signatures']:
				if signature['start_point'] == self._WILL_BE_SET_LATER:
					error_handler("Syntax Error", " function " + item['function_name'] + " has not declared")
		if not self.finalCode.have_main():
			error_handler("Syntax Error", "There is not int main that have no input variable")

		for item in self.function_call_jmp_that_do_not_have_pc:
			self.finalCode.update_code(item[0], 1,
									   self.function_signatures[item[1]]["signatures"][item[2]]['start_point'])

	def generate_code(self, semantic_code, next_token):
		self.next_token = next_token
		# print("semantic code = ", semantic_code)
		getattr(self, semantic_code[1:])()
