from finalCode import FinalCode


class CodeGenerator:
	semantic_stack = []

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def push_pc(self):
		self.push_to_semantic_stack(FinalCode.get_pc())

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def generate_code(self, semantic_rule):
		# switch case on semantic rule
		print(self.semantic_stack)
		print(semantic_rule)
