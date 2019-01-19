from parser import Parser
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS
from scanner import Scanner

GRAMMAR_FILE_PATH = "grammar.in"
source_code_file_path = "test.cpp"
if not source_code_file_path or source_code_file_path == "":
	exit()
text = open(source_code_file_path, 'r').read()
scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
scanner_result = scanner.run()
# print(scanner_result)
parser = Parser("PROGRAM")
parser_run_result = parser.run(open(GRAMMAR_FILE_PATH, 'r'))
if not parser_run_result[0]:
	exit()
print("No Syntax Error")
# print("variables:", parser.get_variables())
# print(parser.get_nullable_variables())
# print(parser.get_rules())
# print(parser.get_firsts())
# print(parser.get_follows())
# print(parser.get_predicts())
# print(parser.get_parse_table())
parser_match_result = parser.match(scanner_result)
