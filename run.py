from codeGenerator import FinalCode
from parser import Parser
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS
from scanner import Scanner
import resource, sys

resource.setrlimit(resource.RLIMIT_STACK, (2 ** 29, -1))
sys.setrecursionlimit(10 ** 6)

GRAMMAR_FILE_PATH = "grammar.in"
source_code_file_path = "test.cpp"
if not source_code_file_path or source_code_file_path == "":
	exit()
text = open(source_code_file_path, 'r').read()
scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
scanner_result = scanner.run()
parser = Parser("PROGRAM")
parser_run_result = parser.run(open(GRAMMAR_FILE_PATH, 'r'))
parser_match_result = parser.match(scanner_result)
print("No Syntax Error")
FinalCode.print_codes(FinalCode())
