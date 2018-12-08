import sys

text = open(sys.argv[-1], 'r')


class Parser:
	# parseStack = Stack()
	# semanticStack = Stack()
	grammers = []
	terminals_none_terminals = []
	variables = []
	tokens = []
	RHST = []
	firsts = {}
	follows = {}
	predicts = {}
	parseTable = []

	@staticmethod
	def is_variable(st):
		if st== '->':
			return False
		if st == st.upper() and '@' != st[0]:
			return True
		return False

	@staticmethod
	def is_semantic_rule(st):
		if st== '->':
			return False
		if '@' == st[0]:
			return True
		return False

	@staticmethod
	def is_terminal(st):
		if st== '->':
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

	def find_variables(self):
		for t in self.terminals_none_terminals:
			if self.is_variable(t):
				self.variables.append(t)
		return

	def read_grammers(self, text):
		while True:
			a = text.readline()
			if "" == a:
				break
			else:
				print(a.strip())
				self.grammers.append(a.strip())
		print(self.grammers)
		for gra in self.grammers:
			g = gra.split(" ")
			for g1 in g:
				self.terminals_none_terminals.append(g1)

			print(g)
		print(self.terminals_none_terminals)
		self.find_variables()
		print(self.variables)
		return

	def run(self, text):
		self.read_grammers(text)
		return


parser = Parser()
parser.run(text)

# print(text)
