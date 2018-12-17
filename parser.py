from utils import add_element_to_set, add_list_of_elements_to_set
import copy
import re
import sys


class Parser:
	_ARROW_STRING = "->"
	_NIL_STRING = "nil"
	_INVALID = -1
	_SEMANTIC_RULE_CHARACTER = '@'
	_END_OF_FILE_CHARACTER = '$'


	@staticmethod
	def is_variable(s):
		if len(s) == 0:
			return False
		if s == Parser._NIL_STRING:
			return False
		pattern = r'[^\.a-zA-Z]'
		if re.search(pattern, s):
			return False
		if s == Parser._ARROW_STRING:
			return False
		if s == s.upper() and s[0] != Parser._SEMANTIC_RULE_CHARACTER:
			return True
		return False


	@staticmethod
	def is_semantic_rule(s):
		if len(s) == 0:
			return False
		if s == Parser._ARROW_STRING:
			return False
		if s[0] == Parser._SEMANTIC_RULE_CHARACTER:
			return True
		return False


	@staticmethod
	def is_terminal(s):
		if len(s) == 0:
			return False
		if s == Parser._NIL_STRING:
			return False
		if s == Parser._ARROW_STRING:
			return False
		if s == s.lower() and s[0] != Parser._SEMANTIC_RULE_CHARACTER:
			return True
		return False


	def __init__(self, start_variable):
		self.clear()
		self.set_start_variable(start_variable)


	def clear(self):
		self._variables = []
		self._nullable_variables = []
		self._terminals = []
		self._variable_rules = {}
		self._variable_rules_with_id = {}
		self._rules = []
		self._firsts = {}
		self._follows = {}
		self._predicts = {}
		self._parse_table = {}


	def set_start_variable(self, start_variable):
		self._start_variable = start_variable


	def _is_nullable_variable(self, variable):
		return variable in self._nullable_variables


	def _parse_code(self):
		return

	def match(self, seq):
		seq.append(self._END_OF_FILE_CHARACTER)
		idx = 0
		parse_stack = [self._END_OF_FILE_CHARACTER, self._start_variable]
		top = self._start_variable
		while top != self._END_OF_FILE_CHARACTER:
			if top == seq[idx]:
				idx = idx + 1
				parse_stack.pop()
			elif (self.is_terminal(top)):
				return False
			else:
				try:
					product_idx = self._parse_table[top][seq[idx]]
					product = self._rules[product_idx][1:]
					parse_stack.pop()
					if product != [self._NIL_STRING]:
						parse_stack.extend(reversed(product))
				except KeyError:
					return (False, "Error: Not able to find derivation of {0} on `{1}`".format(top, seq[idx]))
			top = parse_stack[-1]
		return (True, "Sequence matched successfully.")


	def _fill_parse_table(self):
		for variable in self._variables:
			self._parse_table[variable] = {}
			for terminal in self._terminals:
				self._parse_table[variable][terminal] = Parser._INVALID
		for rule_id in range(len(self._rules)):
			variable = self._rules[rule_id][0]
			for terminal in self._terminals:
				if terminal in self._predicts[rule_id]:
					if self._parse_table[variable][terminal] != Parser._INVALID:
						return (False, "The grammar is not LL1. Variable: " + str(variable) + " Terminal: " + str(terminal))
					else:
						self._parse_table[variable][terminal] = rule_id
		return (True, "Parse table filled successfully.")


	def _find_all_predicts(self):
		for rule_id in range(len(self._rules)):
			self._predicts[rule_id] = set()
			idx = 0
			is_right_nullable = True
			for right in self._rules[rule_id]:
				idx += 1
				if idx == 1:
					continue
				if self.is_terminal(right):
					self._predicts[rule_id].add(right)
					is_right_nullable = False
					break
				if self.is_variable(right):
					self._predicts[rule_id] |= set(self._firsts[right])
					if not self._is_nullable_variable(right):
						is_right_nullable = False
						break
			if is_right_nullable:
				self._predicts[rule_id] |= set(self._follows[self._rules[rule_id][0]])


	def _find_all_follows(self):
		for variable in self._variables:
			self._follows[variable] = set()
		while True:
			follows_updated = False
			for variable in self._variables:
				for rule in self._rules:
					next_one_first_should_be_in_var_follows = False
					idx = 0
					for x in rule:
						idx += 1
						if idx == 1:
							continue
						if next_one_first_should_be_in_var_follows:
							if self.is_variable(x):
								follows_updated |= add_list_of_elements_to_set(self._follows[variable], self._firsts[x])
								if not self._is_nullable_variable(x):
									next_one_first_should_be_in_var_follows = False
							if self.is_terminal(x):
								next_one_first_should_be_in_var_follows = False
								follows_updated |= add_element_to_set(self._follows[variable], x)
						if not next_one_first_should_be_in_var_follows:
							if x == variable:
								next_one_first_should_be_in_var_follows = True
							continue
					if next_one_first_should_be_in_var_follows:
						follows_updated |= add_list_of_elements_to_set(self._follows[variable], self._follows[rule[0]])
			if not follows_updated:
				break


	def _find_all_firsts(self):
		for variable in self._variables:
			self._firsts[variable] = set()
		while True:
			firsts_updated = False
			for variable in self._variables:
				for rule in self._variable_rules[variable]:
					for right in rule:
						if self.is_terminal(right) and right != Parser._NIL_STRING:
							firsts_updated |= add_element_to_set(self._firsts[variable], right)
						if self.is_variable(right):
							firsts_updated |= add_list_of_elements_to_set(self._firsts[variable], self._firsts[right])
						if self.is_variable(right) and self._is_nullable_variable(right):
							continue
						break
			if not firsts_updated:
				break


	def _find_all_nullable_variables(self):
		while True:
			update = False
			for variable in self._variables:
				if variable in self._nullable_variables:
					continue
				for rule in self._variable_rules[variable]:
					all_nullables = True
					for right in rule:
						if self.is_terminal(right):
							all_nullables = False
						elif self.is_variable(right) and right not in self._nullable_variables:
							all_nullables = False
						if not all_nullables:
							break
					if not all_nullables:
						continue
					elif variable not in self._nullable_variables:
						self._nullable_variables.append(variable)
						update = True
			if not update:
				break
		return


	def _update_variables(self, l):
		for x in l:
			if self.is_variable(x) and x not in self._variables:
				self._variables.append(x)


	def _update_terminals(self, l):
		for x in l:
			if self.is_terminal(x) and x not in self._terminals:
				self._terminals.append(x)


	def _update_grammar(self, rule_text):
		idx = len(self._rules)
		rule_text_tokens = rule_text.split(" ")
		self._update_variables(rule_text_tokens)
		self._update_terminals(rule_text_tokens)
		if len(rule_text_tokens) < 3:
			return (False, "Error in rule number " + str(idx))
		if not self.is_variable(rule_text_tokens[0]) or rule_text_tokens[1] != Parser._ARROW_STRING:
			return (False, "Error in rule number " + str(idx))
		if len(rule_text_tokens) == 3 and rule_text_tokens[2] == Parser._NIL_STRING and rule_text_tokens[0] not in self._nullable_variables:
			self._nullable_variables.append(rule_text_tokens[0])
		key = rule_text_tokens[0]
		del rule_text_tokens[1]
		self._rules.append(copy.deepcopy(rule_text_tokens))
		del rule_text_tokens[0]
		temp_list = []
		if key in self._variable_rules:
			temp_list = self._variable_rules[key]
		temp_list.append(rule_text_tokens)
		if key not in self._variable_rules_with_id:
			self._variable_rules_with_id[key] = {}
		self._variable_rules_with_id[key][idx] = rule_text_tokens
		self._variable_rules[key] = temp_list
		return (True, "Grammar updated successfully.")


	def _make_grammar_from_text(self, rules_text):
		lines = []
		while True:
			line = rules_text.readline().strip()
			if not line or line == "":
				break
			else:
				if not self._update_grammar(line):
					return (False, "Error in making grammar")
		return (True, "Grammar made successfully.")


	def run(self, rules_text):
		self.clear()
		if not self._make_grammar_from_text(rules_text)[0]:
			return (False, "Error in making grammar")
		self._find_all_nullable_variables()
		self._find_all_firsts()
		self._find_all_follows()
		self._find_all_predicts()
		if not self._fill_parse_table()[0]:
			return (False, "Error in filling parse table")
		return (True, "Parser ran successfully.")


	def get_start(self):
		return self._start


	def get_firsts(self):
		return self._firsts


	def get_follows(self):
		return self._follows


	def get_variables(self):
		return self._variables


	def get_terminals(self):
		return self._terminals


	def get_parse_table(self):
		return self._parse_table


	def get_rules(self):
		return self._rules


	def get_variable_rules(self):
		return self._variable_rules


	def get_variable_rules_with_id(self):
		return self._variable_rules_with_id


	def get_nullable_variables(self):
		return self._nullable_variables


parser = Parser("S")
text = open(sys.argv[-1], 'r')
if parser.run(text):
	print(parser.get_firsts())
	print(parser.get_follows())
	print(parser.get_variables())
	print(parser.get_parse_table())
	print(parser.get_rules())
	print(parser.get_variable_rules())
	print(parser.get_variable_rules_with_id())

	print(parser.match(["b", "d", "b"]))