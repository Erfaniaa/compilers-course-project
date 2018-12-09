import sys
import re
import copy as copy

text = open(sys.argv[-1], 'r')


class Parser:
	# parseStack = Stack()
	# semanticStack = Stack()
	grammers = {}
	rules = {}
	grammers2 = {}
	firsts = {}
	variables = []
	tokens = []
	RHST = []
	follows = {}
	predicts = {}
	parseTable = []
	nullables = []

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
		return

	def follow(self):
		return

	def is_null_able(self, var):
		return var in self.nullables

	def find_all_follows(self):
		for var in self.variables:
			self.follows[var] = []
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
								for fi_x in self.firsts[x]:
									if fi_x not in fol:
										fol.append(fi_x)
										update = True
								if not self.is_null_able(x):
									next_one_first_should_be_in_var_follows = False
							if self.is_terminal(x):
								next_one_first_should_be_in_var_follows = False
								if x not in fol:
									fol.append(x)
									update = True
						if not next_one_first_should_be_in_var_follows:
							if x == var:
								next_one_first_should_be_in_var_follows = True
							continue
					if next_one_first_should_be_in_var_follows:
						for x in self.follows[rule[0]]:
							if x not in fol:
								fol.append(x)
								update = True
			if not update:
				break
		for x in self.follows:
			print(str(x) + " = " + str(self.follows[x]))

	first_state = {}

	def find_all_firsts(self):
		for var in self.variables:
			self.firsts[var] = []
		while True:
			update = False
			for var in self.variables:
				for gra in self.grammers[var]:
					for right in gra:
						t = self.firsts[var]
						if self.is_terminal(right) and right != "nill":
							if right not in t:
								t.append(right)
								update = True
						if self.is_variable(right):
							for fi in self.firsts[right]:
								if fi not in t:
									t.append(fi)
									update = True
						self.firsts[var] = t
						if self.is_variable(right) and self.is_null_able(right):
							continue
						break
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
						self.nullables.append(var)
						update = True
			if not update:
				break
		return

	def find_variables(self, g):
		for t in g:
			if self.is_variable(t):
				if t not in self.variables:
					self.variables.append(t)

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
			if len(g) == 3 and g[2] == "nill" and g[0] not in self.nullables:
				self.nullables.append(g[0])
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
		self.find_all_follows()


parser = Parser()
parser.run(text)

# print(text)
