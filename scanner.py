from enum import Enum
import re
import sys

class Transition:
	def __init__(self, src="", dst="", condition=r""):
		self.src = src
		self.dst = dst
		self.condition = condition

class TokenType(Enum):
	error = -1
	identifier = 0
	number = 1
	special_token = 2
	string = 3
	comment = 4
	keyword = 5
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.name

class Token:
	def __init__(self, token_value, token_type):
		self.value = token_value
		self.type = token_type
	def __str__(self):
		return "(" + self.value + ", " + str(self.type) + ")"
	def __repr__(self):
		return "(" + self.value + ", " + str(self.type) + ")"

KEYWORDS = ['if', 'while', 'do', 'for', 'main', 'return', 'int', 'float', 'double', 'char', 'else']
TRANSITIONS = [
	Transition('new_token', 'parentheses', r'[\(\)]'),
	Transition('new_token', 'comma', r'\,'),
	Transition('new_token', 'plus', r'\+'),
	Transition('plus', 'plus_plus', r'\+'),
	Transition('new_token', 'minus', r'\-'),
	Transition('minus', 'minus_minus', r'\-'),
	Transition('new_token', 'equal', r'\='),
	Transition('equal', 'equal_equal', r'\='),
	Transition('new_token', 'greater', r'\>'),
	Transition('greater', 'greater_equal', r'\='),
	Transition('new_token', 'less', r'\<'),
	Transition('less', 'less_equal', r'\='),
	Transition('new_token', 'not', r'\!'),
	Transition('not', 'not_equal', r'\='),	
	Transition('new_token', 'semicolon', r'\;'),
	Transition('new_token', 'string', r'\"'),
	Transition('string', 'string_special_char', r'\\'),
	Transition('string', 'string', r'[^\"\\]'),
	Transition('string', 'string_end', r'\"'),
	Transition('string_special_char', 'string', r'.'),
	Transition('new_token', 'identifier', r'[a-zA-Z]'),
	Transition('identifier', 'identifier', r'[a-zA-Z0-9_]'),
	Transition('new_token', 'braces', r'[\{\}]'),
	Transition('new_token', 'number_or_dot', r'\.'),
	Transition('number_or_dot', 'number_with_fractions', r'[0-9]'),
	Transition('number_with_fractions', 'number_with_fractions', r'[0-9]'),
	Transition('new_token', 'number_wholes', r'[0-9]'),
	Transition('number_wholes', 'number_wholes', r'[0-9]'),
	Transition('number_wholes', 'number_dot', r'\.'),
	Transition('number_dot', 'number_with_fractions', r'[0-9]'),
	Transition('new_token', 'division_or_comment', r'\/'),
	Transition('division_or_comment', 'comment_line', r'\/'),
	Transition('comment_line', 'comment_line', r'[^\n]'),
	Transition('comment_line', 'comment_end', r'\n'),
	Transition('division_or_comment', 'comment', r'\*'),
	Transition('comment', 'comment', r'[^\*]'),
	Transition('comment', 'comment_end_star', r'\*'),
	Transition('comment_end_star', 'comment', r'[^\*\/]'),
	Transition('comment_end_star', 'comment_end_star', r'\*'),
	Transition('comment_end_star', 'comment_end', r'\/'),
	]
FINAL_STATES = {
	'parentheses': TokenType.special_token,
	'plus': TokenType.special_token,
	'plus_plus': TokenType.special_token,
	'minus': TokenType.special_token,
	'minus_minus': TokenType.special_token,
	'equal': TokenType.special_token,
	'semicolon': TokenType.special_token,
	'identifier': TokenType.identifier,
	'braces': TokenType.special_token,
	'number_or_dot': TokenType.special_token,
	'number_with_fractions': TokenType.number,
	'number_wholes': TokenType.number,
	'string_end': TokenType.string,
	'division_or_comment': TokenType.special_token,
	'comment_end': TokenType.comment,
	'not': TokenType.special_token,
	'not_equal': TokenType.special_token,
	'equal': TokenType.special_token,
	'equal_equal': TokenType.special_token,
	'greater': TokenType.special_token,
	'greater_equal': TokenType.special_token,
	'less': TokenType.special_token,
	'less_equal': TokenType.special_token,
	'comma': TokenType.special_token,
}

class Scanner:
	def __init__(self, text="", initial_state=None, final_states={}, transitions=[], keywords=[]):
		self.text = text
		self.current_char_idx = 0
		self.transitions = {}
		self._add_transitions(transitions)
		self.initial_state = initial_state
		self.final_states = final_states
		self.keywords = keywords
		self.final_states = final_states
	def _get_final_state_token_type(self, state):
		return self.final_states.get(state)
	def _is_final_state(self, state):
		return state in self.final_states.keys()
	def _is_keyword(self, s):
		return s in self.keywords
	def _add_transition(self, transition):
		if not self.transitions.get(transition.src):
			self.transitions[transition.src] = []	
		self.transitions[transition.src].append(transition)
	def _add_transitions(self, transitions_list):
		for transition in transitions_list:
			self._add_transition(transition)
	def _next_token(self):
		self.state = self.initial_state
		ret = ""
		while self.current_char_idx < len(text):
			current_char = text[self.current_char_idx]
			if not self.transitions.get(self.state):
				break
			found = False
			for transition in self.transitions[self.state]:
				if re.match(transition.condition, current_char):
					ret = ret + current_char
					self.state = transition.dst
					self.current_char_idx += 1
					found = True
					break
			if not found:
				break
		if self._is_final_state(self.state):
			if self._is_keyword(ret):
				return Token(ret, TokenType.keyword)
			else:
				return Token(ret, self._get_final_state_token_type(self.state))
		else:
			self.current_char_idx += 1
			return Token(ret, TokenType.error)
	def run(self):
		ret = []
		while self.current_char_idx < len(text):
			token = self._next_token()
			if token and len(token.value) > 0:
				ret.append(token)
		return ret


text = open(sys.argv[-1], 'r').read()
scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
scanner_result = scanner.run()
print(scanner_result)