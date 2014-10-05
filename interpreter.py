import lexer
import parser
import evaluator
import sys

# Driver code for entire interpreter.
# Uses lexer, parser and evaluator to interpret input code.

def interpret(program):
    """Interpreter function.
    Lexer feeds tokens to parser, which feeds object to machine."""
    lxr = lexer.Lexer(program)
    prsr = parser.Parser(lxr.lex())
    #Machine is passed an environment, which is a list of two dicts. One holds vars, the other funcs.
    mach = evaluator.Machine(prsr.run(), [{}, {}])
    mach.run()

if(len(sys.argv) > 1):
    file_inp = sys.argv[1]
else:
    file_inp = "./test"

with open(file_inp, 'r') as f:
    interpret(f.read())
