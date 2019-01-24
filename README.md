# Compilers Course Project
> Converting a pseudo C++ source code to a pseudo assembly code

For more information, read the PDF files which are located in this repository (they're in Persian language).

## Dependencies

    pip3 install -r requirements.txt
  
  
## Usage

	python3 run.py input_file_name.cpp

**Sample input (pseudo C++ source code):**

Check out [sample.cpp](https://github.com/Erfaniaa/compilers-course-project/blob/master/sample.cpp) in the repository.

    python3 run.py sample.cpp

**Sample output (pseudo assembly codes):**

	No syntax errors
	line number 0: jmp 15 
	line number 1: mov 0 #0 
	line number 2: pop 10000 
	line number 3: mov 4 #47 
    line number 4: push 4 
    line number 5: jmp 10000 
    line number 6: push #0 
    line number 7: jmp 10000 
    line number 8: pop 4 
    line number 9: pop 10000 
    line number 10: add 4 #47 4 
    ...


## Notes

- This project was done by [Ali Mirjahani](https://github.com/alimirjahani7) and [Erfan Alimohammadi](https://github.com/erfaniaa) in 2019 for the [Shahid Beheshti University](http://en.sbu.ac.ir) Compilers Course project.
- You can modify the codes and produce your own programming language. There are not much hard-codes, so editing the language grammar would be easy. Grammar rules files have ".in" extension in the repository.
- There are no switch-case statements in the scanner FSM part. Just draw your DFA graph on a paper, and enter the graph nodes and edges in the scanner; it will work for you!
- This project uses a LL(1) parser (which is implemented by us) and a LALR parser (which is lark-parser, for parsing the boolean expressions). It switches between these two parsers, according to its state.
