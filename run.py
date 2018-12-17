import sys
from parser import Parser
from scanner import Scanner
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS

grammar_rules = open(sys.argv[-2], 'r')
text = open(sys.argv[-1], 'r').read()
scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
scanner_result = scanner.run()

print(scanner_result)

# parser = Parser("PROGRAM")
parser = Parser()
print(parser.run(grammar_rules))
# print(parser.get_variables())
# print(parser.get_nullable_variables())
# print(parser.get_rules())
# print(parser.get_firsts())
# print(parser.get_follows())
# print(parser.get_predicts())
# print(parser.get_parse_table())
# print(parser.match(scanner_result))
