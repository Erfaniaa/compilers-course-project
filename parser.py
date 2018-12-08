import sys
import re

text = open(sys.argv[-1], 'r')


class Parser:
	# parseStack = Stack()
	# semanticStack = Stack()
	grammers = []
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

	def make_grammers(self):
		idx = 0
		for gra in self.grammers:
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
				continue

		print(self.nullables)
		print(self.variables)
		return True

	def read_grammers(self, text):
		while True:
			a = text.readline()
			if "" == a:
				break
			else:
				self.grammers.append(a.strip())
		self.make_grammers()

	def run(self, text):
		self.read_grammers(text)


parser = Parser()
parser.run(text)

# print(text)
