import sys
import re
import copy as copy

text = open(sys.argv[-1], 'r')


class Set:
	data = []

	def push(self, item):
		if item not in self.data:
			self.data.append(item)
			return True
		return False

	def __getitem__(self, index):
		return self.data[index]

	def push_all(self, items):
		update = False
		for x in items:
			update = update or self.push(x)
		return update

	def __len__(self):
		return len(self.data)

	def __str__(self):
		return str(self.data)


class Parser:
	# parseStack = Stack()
	# semanticStack = Stack()
	grammers = {}
	rules = {}
	grammers2 = {}
	firsts = {}
	variables = Set()
	follows = {}
	predicts = {}
	parseTable = []
	nullables = Set()

	@staticmethod
	def log_array_of_set(data):
		for key in data:
			print(key)
			print("->")
			output = ""
			for andis in range(0, len(data[key])):
				output += str(data[key][andis] + " ")
			print(output)

	@staticmethod
	def is_variable(st):
		pattern = r'[^\.a-zA-z]'
		if re.search(pattern, st):
			return False
		if st == '->':
			return False
		if st == st.upper() and '@' != st[0]:
			return True
		return False

	@staticmethod
	def is_semantic_rule(st):
		if st == '->':
			return False
		if '@' == st[0]:
			return True
		return False

	@staticmethod
	def is_terminal(st):
		if st == '->':
			return False
		if st == st.lower() and '@' != st[0]:
			return True
		return False

	def parse_code(self):
		return

	def fill_parse_table(self):
		return

	def find_all_predicts(self):
		for rule_id in self.rules:
			pre = Set()
			idx = 0
			is_right_null_able = True
			for right in self.rules[rule_id]:
				idx += 1
				if idx == 1:
					continue
				if self.is_terminal(right):
					pre.push(right)
					is_right_null_able = False
					break
				if self.is_variable(right):
					pre.push_all(self.firsts[right])
					if not self.is_null_able(right):
						is_right_null_able = False
						break
			if is_right_null_able:
				pre.push_all(self.follows[self.rules[rule_id][0]])
			self.predicts[rule_id] = pre
		return

	def is_null_able(self, var):
		return var in self.nullables

	def find_all_follows(self):
		for var in self.variables:
			self.follows[var] = Set()
		while True:
			update = False
			for var in self.variables:
				fol = self.follows[var]
				for rule_id in self.rules:
					rule = self.rules[rule_id]
					next_one_first_should_be_in_var_follows = False
					idx = 0
					for x in rule:
						idx += 1
						if idx == 1:
							continue
						if next_one_first_should_be_in_var_follows:
							if self.is_variable(x):
								update = update or fol.push_all(self.firsts[x])
								if not self.is_null_able(x):
									next_one_first_should_be_in_var_follows = False
							if self.is_terminal(x):
								next_one_first_should_be_in_var_follows = False
								update = update or fol.push(x)
						if not next_one_first_should_be_in_var_follows:
							if x == var:
								next_one_first_should_be_in_var_follows = True
							continue
					if next_one_first_should_be_in_var_follows:
						update = update or fol.push_all(self.follows[rule[0]])
			if not update:
				break

	def find_all_firsts(self):
		print(self.grammers)
		for var in self.variables:
			self.firsts[var] = Set()
		while True:
			update = False
			for var in self.variables:
				print(var)
				for gra in self.grammers[var]:
					print(gra)

			# 	print(gra)
			# 	for right in gra:
			# 		t = self.firsts[var]
			# 		if self.is_terminal(right) and right != "nill":
			# 			update = update or t.push(right)
			# 		if self.is_variable(right):
			# 			update = update or t.push_all(self.firsts[right])
			# 		self.firsts[var] = t
			# 		if self.is_variable(right) and self.is_null_able(right):
			# 			continue
			# 		break
			if not update:
				break

	def find_all_nullable(self):
		while True:
			update = False
			for var in self.variables:
				if var in self.nullables:
					continue
				for gra in self.grammers[var]:
					all_nullables = True
					for right in gra:
						if self.is_terminal(right):
							all_nullables = False
						elif self.is_variable(right) and right not in self.nullables:
							all_nullables = False
						if not all_nullables:
							break
					if not all_nullables:
						continue
					elif var not in self.nullables:
						self.nullables.push(var)
						update = True
			if not update:
				break
		return

	def find_variables(self, g):
		for t in g:
			if self.is_variable(t):
				self.variables.push(t)

	def make_grammers(self, lines):
		idx = 0
		for gra in lines:
			idx += 1
			g = gra.split(" ")
			self.find_variables(g)
			if len(g) < 3:
				print("not enough word ing grammer " + str(idx))
				return False
			if not self.is_variable(g[0]) or g[1] != '->':
				print("error in grammer " + str(idx))
				return False
			if len(g) == 3 and g[2] == "nill":
				self.nullables.push(g[0])
			key = g[0]
			del g[1]
			self.rules[idx] = copy.deepcopy(g)
			del g[0]
			temp = []
			if key in self.grammers:
				temp = self.grammers[key]
			temp.append(g)
			if key not in self.grammers2:
				self.grammers2[key] = {}
			self.grammers2[key][idx] = g
			self.grammers[key] = temp
		return True

	def read_grammers(self, text):
		lines = []
		while True:
			a = text.readline()
			if "" == a:
				break
			else:
				lines.append(a.strip())
		self.make_grammers(lines)

	def run(self, text):
		self.read_grammers(text)
		self.find_all_nullable()
		self.find_all_firsts()
		print(self.firsts)


# self.find_all_follows()
# print(self.follows)


parser = Parser()
parser.run(text)
