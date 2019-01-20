class Symbol:

	def __init__(self, var_name, type_of_var, type_of_data, function_name, scope, type_size, size, address):
		self.var_name = var_name
		self.type_of_var = type_of_var  # int char float bool
		self.type_of_data = type_of_data  # array temp_var var
		self.function = function_name  # global  or function name
		self.scope = scope  # scope number
		self.type_size = type_size
		self.size = size
		self.address = address  # address


class SymbolTable:
	function = "Global"
	scope = 0
	bitmap = []  # 1 is empty  0 is full
	symbols = []
	symbols_size = {"int": 4, "char": 2, "float": 8, "bool": 1}
	last_temp_address = 100000000

	def get_size(self, type_of_var):
		if type_of_var in self.symbols_size:
			return self.symbols_size[type_of_var]
		return -1

	def get_more_size(self):
		for i in range(100):
			self.bitmap.append(1)

	def make_full_bitmap(self, start, size):
		for i in range(start, start + size):
			self.bitmap[i] = 0

	def find_empty_in_bitmap(self, size):
		empty_counter = 0
		for i in range(0, len(self.bitmap)):
			if self.bitmap[i] == 1:
				empty_counter += 1
				if empty_counter == size:
					return i - size + 1
			else:
				empty_counter = 0
		self.get_more_size()
		return self.find_empty_in_bitmap(size)

	def clear_bitmap(self, start, size):
		for i in range(start, start + size):
			self.bitmap[i] = 1

	def new_temp(self):
		size = 8
		address = self.last_temp_address
		self.last_temp_address += size
		return "_" + str(address)

	def new_array(self, name, type_of_var, array_size):
		type_size = self.get_size(type_of_var)
		size = int(type_size) * int(array_size)
		address = self.find_empty_in_bitmap(size)
		array = Symbol(name, type_of_var, "array", self.function, self.scope, type_size, size, address)
		self.symbols.append(array)
		print("Array ", name, " of type ", type_of_var, " placed in ", address, " with size ", size)
		self.make_full_bitmap(address, size)

	def new_variable(self, name, type_of_var):
		size = self.get_size(type_of_var)
		address = self.find_empty_in_bitmap(size)
		var = Symbol(name, type_of_var, "var", self.function, self.scope, size, size, address)
		print("Variable ", name, " of type ", type_of_var, " placed in ", address, " with size ", size)
		self.symbols.append(var)
		self.make_full_bitmap(address, size)

	def get_in_method(self, func_name):
		self.function = func_name

	def one_scope_in(self):
		self.scope += 1

	def one_scope_out(self):
		for symbol in list(self.symbols):
			if symbol.function == self.function and symbol.scope == self.scope:
				self.clear_bitmap(symbol.start, symbol.size)
				self.symbols.remove(symbol)
		self.scope -= 1
		if self.scope == 0:
			self.function = "Global"

	def get_var(self, var_name):
		best_var_scope = - 1
		best_symbol_address = -1
		var = {}
		for symbol in self.symbols:
			if symbol.var_name == var_name and symbol.function == self.function and symbol.scope > best_var_scope:
				best_symbol_address = symbol.address
				best_var_scope = symbol.scope
				var = symbol
		if best_symbol_address == -1:
			for symbol in self.symbols:
				if symbol.var_name == var_name and symbol.function == "Global":
					var = symbol
		return var

	def get_var_address(self, var_name):
		var = self.get_var(var_name)
		return var.address

	def get_var_type_size(self, var_name):
		var = self.get_var(var_name)
		return var.type_size

	def get_var_size(self, var_name):
		var = self.get_var(var_name)
		return var.size

	def is_var_declared(self, var_name):
		for symbol in self.symbols:
			if symbol.var_name == var_name and symbol.function == self.function and self.scope == symbol.scope:
				return True
		return False
