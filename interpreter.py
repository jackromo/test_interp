import lexer
import parser
import evaluator
import sys


# Functions for interpreting program string and file.


def interpret(program):
    """Interpreter function.
    Lexer feeds tokens to parser, which feeds object to machine."""
    lxr = lexer.Lexer(program)
    prsr = parser.Parser(lxr.lex())
    env = evaluator.Environment()
    #Machine is passed an environment, which is a list of two dicts. One holds vars, the other funcs.
    mach = evaluator.Machine(prsr.run(), env)
    mach.run()
    return env

def file_interp(file_inp):
    """Interpret a file of name 'file_inp'."""
    with open(file_inp, 'r') as f:
        return interpret(f.read())


# Driver code for entire interpreter.
# Uses lexer, parser and evaluator to interpret input code.


if(len(sys.argv) > 1):
    file_inp = sys.argv[1]
else:
    file_inp = "./test"

#Interpret a file as a program
file_interp(file_inp)
