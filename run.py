from codeGenerator import FinalCode
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from parser import Parser
from scanner import Scanner
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS
import resource, sys

resource.setrlimit(resource.RLIMIT_STACK, (2 ** 29, -1))
sys.setrecursionlimit(10 ** 6)

GRAMMAR_FILE_PATH = "grammar.in"

def open_file():
	source_code_file_path = askopenfilename(initialdir=".", filetypes =(("C++", "*.cpp"),("All Files","*.*")), title = "Choose a C++ source file.")
	if not source_code_file_path or source_code_file_path == "":
		return
	text = open(source_code_file_path, 'r').read()
	scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
	scanner_result = scanner.run()
	parser = Parser("PROGRAM")

	parser_run_result = parser.run(open(GRAMMAR_FILE_PATH, 'r'))
	parser_match_result = parser.match(scanner_result)
	print("No Syntax Error")
	label.config(text="Check codes.out file for the results.")
	FinalCode.print_codes(FinalCode(), open("codes.out", "w"))


root = Tk()
root.geometry("400x300")
Title = root.title("Compiler project")
label = ttk.Label(root, text="Choose a c++ source file.", foreground="black", font=("Helvetica", 16))
label.pack()
menu = Menu(root)
root.config(menu=menu)
file = Menu(menu)
file.add_command(label = 'Open', command = open_file)
file.add_command(label = 'Exit', command = lambda: exit())
menu.add_cascade(label = 'File', menu = file)
root.mainloop()