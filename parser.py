from evaluator import *
import sys

#Parser for program.
#Generates AST based on semantics, then converts to program for test_interp.

# EBNF notation syntax for language:
#
# program = statement EOF
# ;
#
# statement = sequence
#     | assign
#     | donothing
#     | block
# ;
#
# sequence = [assign|donothing|block] statement
# ;
#
# block = IF expression THEN CLPAREN statement CRPAREN ELSE CLPAREN statement CRPAREN
# ;
#
# assign = variable ASGN expression EOL
# ;
#
# donothing = NULL EOL
# ;
#
# variable = VAR
# ;
#
# expression = atom OP expression
#     | conditional
#     | LPAREN expression RPAREN
#     | atom
# ;
#
# conditional = expression COMP expression
# ;
#
# atom = variable
#     | NUM
#     | BOOL
# ;
# """


#------------------------------------------#
# Define all token types ###################
# Each is a unique int #####################
#------------------------------------------#


NULL = 0
NUM = 1
BOOL = 2
OP = 3  #Operator (+, -, *, /)
        #(- = + with negative augend, / = * with reciprocal of multiplicand)
COMP = 4 #Comparator (<, >, ==)
ASGN = 5 #Assign
VAR = 6 #Variable
IF = 7
THEN = 8
ELSE = 9
EOL = 10 #End of line (;)
LPAREN = 11
RPAREN = 12
EOF = 13 #End of file
CLPAREN = 14 #Curly left parenthesis ({)
CRPAREN = 15 #Curly right parenthesis (})


#------------------------------------------#
# Define error code.########################
#------------------------------------------#


def error(msg):
    print "Error at token " + str(token.val) + " : " + msg
    sys.exit(0)


#------------------------------------------#
# Define tokens and token list.#############
#------------------------------------------#


class Token(object):
    """Token. Contains type and value of token."""
    def __init__(self, typ, val):
        self.typ = typ
        self.val = val

tok_ls = None #List of tokens.
token = None #Current token checked.

class TokenList(object):
    """List of all tokens being parsed, in order."""
    def __init__(self, ls):
        global token
        self.ls = ls #List of all tokens in program
        self.i = 0 #Index of current token
        token = self.ls[self.i]
    def getToken(self):
        """Set global 'token' var to next token in ls."""
        global token
        if self.i < len(self.ls)-1:
            self.i+=1
            token = self.ls[self.i]
        elif self.i == len(self.ls)-1:
            token = self.ls[self.i]
        else:
            error("Attempted to access more tokens than present")
    def found(self, toktyp):
        """Current token is of type 'toktyp'."""
        global token
        return toktyp == token.typ
    def foundOneOf(self, toktyps):
        """Takes list of possible types. Checks if found one of."""
        for t in toktyps:
            if self.found(t): return True
        return False
    def consume(self, toktyp):
        """Consume token of type 'toktyp' and get next one.
        If not of same type, give error."""
        global token
        if toktyp == token.typ:
            self.getToken()
        else:
            error("Expected " + str(toktyp) + " but found " + str(token.val))


#------------------------------------------#
# Define all reduction rules.###############
#-----------------------------------------#


def program():
    """
    program = statement EOF
    ;
    """
    result = statement()
    tok_ls.consume(EOF)
    return result

def statement():
    """
    statement = sequence
        | assign
        | donothing
        | block
    ;

    sequence = [assign|donothing|block] statement
    ;
    """
    temp = None

    if tok_ls.found(VAR):    temp = assign()
    elif tok_ls.found(NULL): temp = donothing()
    elif tok_ls.found(IF):   temp = block()
    else:
        error("Expected VAR, NULL or IF but found " + str(token.val))

    if not (tok_ls.found(EOF) or tok_ls.found(CRPAREN)): #Sequence, add next statement as child
        return Sequence(temp, statement())
    return temp

def block():
    """
    block = IF conditional THEN CLPAREN statement CRPAREN ELSE CLPAREN statement CRPAREN
    ;
    """
    tok_ls.consume(IF)
    cond = expression()
    tok_ls.consume(THEN)
    tok_ls.consume(CLPAREN)
    then = statement()
    tok_ls.consume(CRPAREN)
    tok_ls.consume(ELSE)
    tok_ls.consume(CLPAREN)
    alt = statement()
    tok_ls.consume(CRPAREN)

    return If(cond, then, alt)

def assign():
    """
    assign = variable ASGN expression EOL
    ;
    """
    var = variable()
    tok_ls.consume(ASGN)
    expr = expression()
    tok_ls.consume(EOL)

    return Assign(var, expr)

def donothing():
    """
    donothing = NULL EOL
    ;
    """
    tok_ls.consume(NULL)
    tok_ls.consume(EOL)
    return DoNothing()

def variable():
    """
    variable = VAR
    ;
    """
    global token
    #current token is VAR
    result = Variable(token.val)
    tok_ls.consume(VAR)
    return result

def expression():
    """
    expression = atom OP expression
        | atom COMP expression
        | LPAREN expression RPAREN
        | atom
    ;
    """
    global token

    if tok_ls.found(LPAREN): #LPAREN expression RPAREN
        tok_ls.consume(LPAREN)
        result = expression()
        tok_ls.consume(RPAREN)
        return result
    elif tok_ls.foundOneOf([NUM, BOOL, VAR]):
        start = atom()
        tok_ls.getToken()
        if tok_ls.found(OP): #atom OP expression
            oper = token.val
            tok_ls.consume(OP)
            if oper == "+": return Add(start, expression())
            elif oper == "*": return Multiply(start, expression())
            else: error("Unknown OP: " + oper)
        elif tok_ls.found(COMP): #atom COMP expression
            oper = token.val
            tok_ls.consume(COMP)
            if oper == "<": return LessThan(start, expression())
            elif oper == ">": return GreaterThan(start, expression())
            elif oper == "==": return EqualTo(start, expression())
            else: error("Unknown COMP: " + oper)
        else: #atom
            return start
    else: error("Expected NUM, BOOL, VAR or LPAREN but found " + token.val)

def atom():
    """
    atom = variable
        | BOOL
        | NUM
    ;
    """
    global token

    if tok_ls.found(NUM): atom = Number(token.val)
    elif tok_ls.found(BOOL): atom = Boolean(token.val)
    elif tok_ls.found(VAR): atom = variable()
    return atom


#------------------------------------------#
# Parser class definition.##################
#------------------------------------------#


class Parser(object):
    """Actual parser. Takes list of tokens and creates AST."""
    def __init__(self, tls):
        global tok_ls
        tok_ls = tls
    def run(self):
        global tok_ls
        prog_ast = program() #Abstract Syntax Tree (AST) of program.
        return prog_ast


#------------------------------------------#
# Driver code for parser.###################
#------------------------------------------#

# Premade token list shown. Will be generated by lexer later.

ls_test = TokenList([
    Token(IF, "if"),
    Token(NUM, 5),
    Token(COMP, "<"),
    Token(NUM, 6),
    Token(THEN, "then"),
    Token(CLPAREN, "{"),
    Token(VAR, "x"),
    Token(ASGN, "="),
    Token(NUM, "5"),
    Token(EOL, ";"),
    Token(VAR, "y"),
    Token(ASGN, "="),
    Token(NUM, "6"),
    Token(EOL, ";"),
    Token(CRPAREN, "}"),
    Token(ELSE, "else"),
    Token(CLPAREN, "{"),
    Token(VAR, "x"),
    Token(ASGN, "="),
    Token(NUM, 6),
    Token(EOL, ";"),
    Token(CRPAREN, "}"),
    Token(EOF, "eof")
    ])

parser = Parser(ls_test)
prog = parser.run()
mach = Machine(prog, {})
mach.run()