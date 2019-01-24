from code_generator import FinalCodes
from parser import Parser
from scanner import Scanner
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS
import resource, sys

resource.setrlimit(resource.RLIMIT_STACK, (2 ** 29, -1))
sys.setrecursionlimit(10 ** 6)

GRAMMAR_FILE_PATH = "grammar.in"
BOOLEAN_EXPRESSION_GRAMMAR_FILE_PATH = "boolean_expression_grammar.in"

try:
	source_code_file_path = sys.argv[1]
except:
	print("No source code files specified")
	exit()

try:
	text = open(source_code_file_path, 'r').read()
except:
	print("Error in reading source code file")
	exit()

scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
scanner_result = scanner.scan()

parser = Parser("PROGRAM")
parser.process_rules(open(GRAMMAR_FILE_PATH, 'r'), open(BOOLEAN_EXPRESSION_GRAMMAR_FILE_PATH, 'r'))
parser.parse(scanner_result)

print("No syntax errors")
FinalCodes.print_codes(FinalCodes())
