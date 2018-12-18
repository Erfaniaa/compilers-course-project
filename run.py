from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from parser import Parser
from scanner import Scanner
from scanner import FINAL_STATES, TRANSITIONS, KEYWORDS

GRAMMAR_FILE_PATH = "grammar.in"

def open_file():
	source_code_file_path = askopenfilename(initialdir=".", filetypes =(("C++", "*.cpp"),("All Files","*.*")), title = "Choose a C++ source file.")
	if not source_code_file_path or source_code_file_path == "":
		return
	text = open(source_code_file_path, 'r').read()
	scanner = Scanner(text, 'new_token', FINAL_STATES, TRANSITIONS, KEYWORDS)
	scanner_result = scanner.run()
	print(scanner_result)
	parser = Parser("PROGRAM")
	print(parser.run(open(GRAMMAR_FILE_PATH, 'r')))
	print(parser.get_variables())
	# print(parser.get_nullable_variables())
	# print(parser.get_rules())
	# print(parser.get_firsts())
	# print(parser.get_follows())
	# print(parser.get_predicts())
	# print(parser.get_parse_table())
	parser_result = parser.match(scanner_result)
	label.config(text=parser_result[1])


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