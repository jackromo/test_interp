import re
from parser import Token, TokenList, Parser
from evaluator import Machine
from tokens import *


#-----------------------------------------#
# Define lexer.############################
#-----------------------------------------#


class Lexer(object):
    """Converts characters into tokens.
    Produces token list for parser."""
    def __init__(self, inp):
        self.inp = inp
    def lex(self):
        items = re.findall('[0-9a-z]+|[,+*/(){}\[\];-]|[<=>]+', self.inp)
        tokens = TokenList([self.choose_tok(x) for x in items])
        tokens.ls.append(Token(EOF, "eof")) #no end-of-file in string input
        return tokens
    def choose_tok(self, item):
        if re.search('if', item): return Token(IF, item)
        elif re.search('then', item): return Token(THEN, item)
        elif re.search('else', item): return Token(ELSE, item)
        elif re.search('while', item): return Token(WHILE, item)
        elif re.search('return', item): return Token(RETURN, item)
        elif re.search('true', item): return Token(BOOL, True)
        elif re.search('false', item): return Token(BOOL, False)
        elif re.search('[0-9]+', item): return Token(NUM, int(item))
        elif re.search('(==|<|>|!=)', item): return Token(COMP, item)
        elif re.search('\=', item): return Token(ASGN, item)
        elif re.search('(\+|\-|\*|\/|%)', item): return Token(OP, item)
        elif re.search('\[', item): return Token(SLPAREN, item)
        elif re.search('\]', item): return Token(SRPAREN, item)
        elif re.search('\(', item): return Token(LPAREN, item)
        elif re.search('\)', item): return Token(RPAREN, item)
        elif re.search('\{', item): return Token(CLPAREN, item)
        elif re.search('\}', item): return Token(CRPAREN, item)
        elif re.search('\;', item): return Token(EOL, item)
        elif re.search('\,', item): return Token(COMMA, item)
        elif re.search('[a-z]+', item): return Token(VAR, item)
        else: raise NameError(item + " is not known")


#-----------------------------------------#
# Test code for lexer.#####################
#-----------------------------------------#


#prog = """
#x = 6;
#if x==false then {
#    y=x;
#    y=x+1;
#} else {
#    y = x;
#    y = x*10;
#}
#"""
#
#prog = raw_input()
#
#lxr = Lexer(prog)
#parser = Parser(lxr.lex())
#mach = Machine(parser.run(), {})
#mach.run()
