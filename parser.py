import sys
import re

text = open(sys.argv[-1], 'r')


class Parser:
	# parseStack = Stack()
	# semanticStack = Stack()
	grammers = {}
	grammers2 = {}
	variables = []
	tokens = []
	RHST = []
	firsts = {}
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
		if '@' == st.lower() and '@' == st[0]:
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

	def find_all_follows(self):
		return

	def first(self):
		return

	def find_all_firsts(self):
		return

	def find_all_nullable(self):
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
			del g[1]
			key = g[0]
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


parser = Parser()
parser.run(text)

# print(text)
