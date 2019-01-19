class Symbol:

	def __init__(self, type_of_var, is_array, function_name, scope, size):
		self.type_of_var = type_of_var
		self.is_array = is_array
		self.function = function_name
		self.scope = scope
		self.size = size

	@staticmethod
	def get_size(type_of_var):
		if type_of_var == "int":
			return 4
		elif type_of_var == "char":
			return 2
		elif type_of_var == "float":
			return 8
		elif type_of_var == "bool":
			return 1


class SymbolTable:
	function = "Global"
	scope = 0

	def new_variable(self, size):
		return size

	def get_variable_size(self, var_name):
		return

	def get_in_method(self, func_name):
		self.function = func_name

	def one_scope_in(self):
		self.scope += 1

	def get_var_data(self, var_name):
		return

	def remove_variable(self, var):
		return

	def one_scope_out(self):
		return
