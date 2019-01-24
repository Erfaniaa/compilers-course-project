import copy, re
from boolean_expression_parser import BooleanExpressionParser
from code_generator import CodeGenerator
from code_generator import FinalCodes
from scanner import TokenType, Token
from symbol_table import SymbolTable
from utils import add_element_to_set, add_list_of_elements_to_set, error_handler


class Parser:
	_ARROW_STRING = "->"
	_RULE_COMMENT_CHARACTER = '#'
	_NIL_STRING = "nil"
	_IDENTIFIER_STRING = "identifier"
	_NUMBER_STRING = "number"
	_STRING_STRING = "string"
	_INVALID = -1
	_SEMANTIC_RULE_CHARACTER = '@'
	_END_OF_FILE_CHARACTER = '$'
	_BOOLEAN_EXPRESSION_STRING = "BOOLEAN_EXPRESSION"


	@staticmethod
	def is_variable(s):
		if len(s) == 0:
			return False
		if s == Parser._NIL_STRING:
			return False
		pattern = r'[^\.a-zA-Z_0-9]'
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
		self.set_final_code(FinalCodes())
		self.set_symbol_table(SymbolTable())
		self.set_code_generator(CodeGenerator(self, self._symbol_table))

	def clear(self):
		self._variables = []
		self._nullable_variables = []
		self._terminals = []
		self._variable_rules = {}
		self._rules = []
		self._firsts = {}
		self._follows = {}
		self._predicts = {}
		self._parse_table = {}
		self._parse_stack = []
		self._final_code = None
		self._symbol_table = None
		self._code_generator = None
		self._boolean_expression_parser = None

	def set_start_variable(self, start_variable):
		self._start_variable = start_variable

	def set_final_code(self, final_code):
		self._final_code = final_code

	def set_symbol_table(self, symbol_table):
		self._symbol_table = symbol_table

	def set_code_generator(self, code_generator):
		self._code_generator = code_generator

	def set_boolean_expression_parser(self, boolean_expression_parser):
		self._boolean_expression_parser = boolean_expression_parser

	def _is_nullable_variable(self, variable):
		return variable in self._nullable_variables

	def _get_parse_stack_top(self):
		while self._parse_stack[-1] == self._NIL_STRING:
			self._parse_stack.pop()
		return self._parse_stack[-1]

	def parse(self, tokens):
		tokens.append(Token('eof', 'keyword'))
		tokens.append(self._END_OF_FILE_CHARACTER)
		last_idx = -1
		idx = 0
		self._parse_stack.append(self._END_OF_FILE_CHARACTER)
		self._parse_stack.append(self._start_variable)
		top = self._start_variable
		loop_counter = 0
		open_parentheses_count = 0
		while top != self._END_OF_FILE_CHARACTER:
			loop_counter += 1
			last_token = tokens[-2]

			if top == self._BOOLEAN_EXPRESSION_STRING and open_parentheses_count == 1 and tokens[idx - 1].value == '(':
				self._parse_stack.pop()
				top = self._get_parse_stack_top()
				boolean_expression_tokens = []
				while open_parentheses_count != 0:
					boolean_expression_tokens.append(tokens[idx])
					if tokens[idx].value == "(":
						open_parentheses_count += 1
					if tokens[idx].value == ")":
						open_parentheses_count -= 1
					idx += 1
				idx -= 1
				open_parentheses_count += 1
				boolean_expression_tokens.pop()
				try:
					self._boolean_expression_parser.parse(boolean_expression_tokens)
				except:
					error_handler("Syntax Error:", " error in boolean expression")
				continue

			elif top == self._BOOLEAN_EXPRESSION_STRING and tokens[idx - 1].value == ';':
				self._parse_stack.pop()
				top = self._get_parse_stack_top()
				boolean_expression_tokens = []
				while tokens[idx].value != ";":
					boolean_expression_tokens.append(tokens[idx])
					if tokens[idx].value == "(":
						open_parentheses_count += 1
					if tokens[idx].value == ")":
						open_parentheses_count -= 1
					idx += 1
				try:
					self._boolean_expression_parser.parse(boolean_expression_tokens)
				except:
					error_handler("Syntax Error:", " error in boolean expression")
				continue

			top = self._get_parse_stack_top()
			if top == self._NIL_STRING:
				top = self._get_parse_stack_top()
				continue
			if self.is_semantic_rule(top):					
				semantic = top
				self._parse_stack.pop()
				top = self._get_parse_stack_top()
				self._code_generator.generate_code(semantic, tokens[idx])
				continue
			if loop_counter > len(tokens) * 20:
				error_handler("Syntax Error:", " (1) next token should not be " + str(tokens[idx]))
			if top == self._IDENTIFIER_STRING:
				if tokens[idx].type == TokenType.identifier:
					idx = idx + 1
					self._parse_stack.pop()
					top = self._get_parse_stack_top()
					continue
				else:
					error_handler("Syntax Error:", " (2) next token should not be " + str(tokens[idx]))
			elif top == self._NUMBER_STRING:
				if tokens[idx].type == TokenType.number:
					idx = idx + 1
					self._parse_stack.pop()
					top = self._get_parse_stack_top()
					continue
				else:
					error_handler("Syntax Error:", " (3) next token should not be " + str(tokens[idx]))
			elif self.is_terminal(top):
				if tokens[idx].value == "(":
					open_parentheses_count += 1
				if tokens[idx].value == ")":
					open_parentheses_count -= 1
				if top == "{":
					self._symbol_table.one_scope_in()
				if top == "}":
					self._symbol_table.one_scope_out()
				if tokens[idx].value == top:
					idx = idx + 1
					self._parse_stack.pop()
					top = self._get_parse_stack_top()
					continue
				else:
					error_handler("Syntax Error:", " (4) next token should not be " + str(tokens[idx]))
			try:
				try:
					nxt = tokens[idx].value
					if tokens[idx].type == TokenType.identifier:
						nxt = self._IDENTIFIER_STRING
					if tokens[idx].type == TokenType.number:
						nxt = self._NUMBER_STRING
					rule_idx = self._parse_table[top][nxt]
					product = self._rules[rule_idx][1:]
					self._parse_stack.pop()
					if product != [self._NIL_STRING]:
						self._parse_stack.extend(reversed(product))
				except:
					error_handler("Syntax Error:", " (5)")
			except KeyError:
				error_handler("Syntax Error:", "6: Unable to find derivation of '{0}' on '{1}'".format(top, nxt))
			top = self._get_parse_stack_top()
		return True

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
						error_handler("Grammer Error",
									  "The grammar is not LL1. Variable: " + str(variable) + " Terminal: " + str(
										  terminal))
					else:
						self._parse_table[variable][terminal] = rule_id

	def _find_all_predicts(self):
		for rule_id in range(len(self._rules)):
			self._predicts[rule_id] = set()
			idx = 0
			is_right_nullable = True
			for right in self._rules[rule_id]:
				idx += 1
				if idx == 1:
					continue
				if self.is_semantic_rule(right):
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
					for right in rule:
						idx += 1
						if idx == 1:
							continue
						if self.is_semantic_rule(right):
							continue
						if next_one_first_should_be_in_var_follows:
							if self.is_variable(right):
								follows_updated |= add_list_of_elements_to_set(self._follows[variable],
																			   self._firsts[right])
								if not self._is_nullable_variable(right):
									next_one_first_should_be_in_var_follows = False
							if self.is_terminal(right):
								next_one_first_should_be_in_var_follows = False
								follows_updated |= add_element_to_set(self._follows[variable], right)
						if not next_one_first_should_be_in_var_follows:
							if right == variable:
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
						if self.is_semantic_rule(right):
							continue
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
						if self.is_semantic_rule(right):
							continue
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
		rule_text_tokens = rule_text.split()
		self._update_variables(rule_text_tokens)
		self._update_terminals(rule_text_tokens)
		if len(rule_text_tokens) < 3:
			error_handler("Grammer Error", "Error in rule number " + str(idx))
		if not self.is_variable(rule_text_tokens[0]) or rule_text_tokens[1] != Parser._ARROW_STRING:
			error_handler("Grammer Error", "Error in rule number " + str(idx))
		if len(rule_text_tokens) == 3 and rule_text_tokens[2] == Parser._NIL_STRING and rule_text_tokens[
			0] not in self._nullable_variables:
			self._nullable_variables.append(rule_text_tokens[0])
		key = rule_text_tokens[0]
		del rule_text_tokens[1]
		self._rules.append(copy.deepcopy(rule_text_tokens))
		del rule_text_tokens[0]
		temp_list = []
		if key in self._variable_rules:
			temp_list = self._variable_rules[key]
		temp_list.append(rule_text_tokens)
		self._variable_rules[key] = temp_list

	def _make_grammar_from_text(self, rules_file, boolean_expression_rules_file):
		while True:
			line = rules_file.readline()
			if not line:
				break
			line = line.strip()
			if line == "":
				continue
			if line[0] == Parser._RULE_COMMENT_CHARACTER:
				continue
			self._update_grammar(line)
		return

	def process_rules(self, rules_file, boolean_expression_rules_file):
		self.set_boolean_expression_parser(BooleanExpressionParser(boolean_expression_rules_file.read(), self._code_generator))
		self._make_grammar_from_text(rules_file, boolean_expression_rules_file)
		self._find_all_nullable_variables()
		self._find_all_firsts()
		self._find_all_follows()
		self._find_all_predicts()
		self._fill_parse_table()

	def get_firsts(self):
		return self._firsts

	def get_follows(self):
		return self._follows

	def get_predicts(self):
		return self._predicts

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

	def get_nullable_variables(self):
		return self._nullable_variables

