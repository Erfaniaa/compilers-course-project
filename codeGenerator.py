class CodeGenerator:
	semantic_stack = []

	def push_to_semantic_stack(self, value):
		self.semantic_stack.append(value)

	def pop_from_semantic_stack(self):
		return self.semantic_stack.pop()

	def generate_code(self, semantic_rule):
		# switch case on semantic rule
		print(self.semantic_stack)
		print(semantic_rule)
