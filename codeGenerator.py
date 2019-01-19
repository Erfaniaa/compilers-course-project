from finalCode import FinalCode


class CodeGenerator:
	semantic_stack = []
	finalCode = FinalCode()
	parser = {}

	def __init__(self, parser):
		self.parser = parser

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(self.finalCode.get_pc())

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def push_top_parse_stack(self):
		self.semantic_stack.append(self.parser.get_top_parse_stack())

	def generate_code(self, semantic_rule):
		# switch case on semantic rule
		if semantic_rule == "push_pc":
			self.push_pc()
		elif semantic_rule == "push_declaration_type":
			self.push_top_parse_stack()

		print(self.semantic_stack)
		print(semantic_rule)
