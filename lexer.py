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
        """
        1. Remove all comments.
        2. Separate program into list of substrings, each could represent a token.
        3. Convert into list of actual tokens, or TokenList().
        4. Append EOF and return.
        """
        #These regexes defines all comments: (//comment\n).
        #Anything (.*) can go in comment, including nothing (hence * instead of +).
        comment_reg = '//.*\n'
        #Split prog around non-comment sections, then join to remove comments.
        new_inp = "".join(re.split(comment_reg, self.inp))
        #Separate into list called 'items' of strings which will become tokens
        items = re.findall('\w+|[,+*/(){}\[\];-]|[<=>]+|"[^\'\r\n]*"', new_inp)
        tokens = TokenList([self.choose_tok(x) for x in items])
        tokens.ls.append(Token(EOF, "eof")) #no end-of-file in string input
        return tokens
    def choose_tok(self, item):
        """re.findall() call above separates program into sections.
        Each section is a possible token. This finds which one it is."""
        if re.search('if', item): return Token(IF, item)
        elif re.search('then', item): return Token(THEN, item)
        elif re.search('else', item): return Token(ELSE, item)
        elif re.search('while', item): return Token(WHILE, item)
        elif re.search('return', item): return Token(RETURN, item)
        elif re.search('function', item): return Token(FUNCTION, item)
        elif re.search('true', item): return Token(BOOL, True)
        elif re.search('false', item): return Token(BOOL, False)
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
        #Strings are defined as: quote (anything not a quote or newline)* quote
        elif re.search('"[^\r\n\']*"', item): return Token(STR, item[1: len(item)-1]) #Cut off quot marks
        elif re.search('[0-9]+', item): return Token(NUM, int(item))
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
