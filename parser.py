from evaluator import *
from tokens import *
import sys

#Parser for program.
#Generates AST based on semantics, then converts to program for test_interp.

# EBNF notation syntax for language:
#
# program = statement EOF
# ;
#
# statement = sequence  //Sequence of two statements.
#     | assign          //Assign variable a value.
#     | donothing       //Null statement - all others reduce to this.
#     | ifstmt          //If-then-else.
#     | whilestmt       //While loop.
#     | returnstmt      //Return a value in function body.
#     | execstmt        //Execute a function on its own line.
#     | importstmt      //Import a file.
# ;
#
# sequence = [assign|donothing|ifstmt|whilestmt|returnstmt|execstmt] statement
# ;
#
# ifstmt = IF expression THEN CLPAREN statement CRPAREN ELSE CLPAREN statement CRPAREN
# ;
#
# whilestmt = WHILE expression CLPAREN statement CRPAREN
# ;
#
# assign = variable ASGN expression EOL
# ;
#
#
# //Execute a function in a statement of its own (eg. 'f(x);')
# execstmt = VAR LPAREN {expression {COMMA expression}*}? RPAREN EOL
# ;
#
# donothing = NULL EOL
# ;
#
# returnstmt = RETURN expression EOL
# ;
#
# //eg. import "test.xx";
# importstmt = IMPORT STR EOL
# ;
#
# variable = VAR
# ;
#
# expression = [atom|execute] OP expression
#     | [atom|execute] COMP expression
#     | LPAREN expression RPAREN
#     | atom
#     | function
#     | execute
# ;
#
# //Execute a function
# execute = VAR LPAREN {expression {COMMA expression}*}? RPAREN
# ;
#
# //Function definition
# function = FUNCTION LPAREN {VAR {COMMA VAR}*}? RPAREN CLPAREN statement CRPAREN
# ;
#
# atom = variable
#     | NUM
#     | BOOL
#     | STR
#     | pair
#     | list
# ;
#
# //Define a list
# list = SLPAREN {expression {COMMA expression}*}? SRPAREN
# ;
#
# //Define a pair
# pair = PAIR SLPAREN expression COMMA expression SRPAREN
# ;
#


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
            error("At " + str(self.i)  + ", expected " + str(toktyp) + " but found " + str(token.val))


#------------------------------------------#
# Define all reduction rules.###############
#------------------------------------------#


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
        | ifstmt
        | whilestmt
        | returnstmt
        | execstmt
        | importstmt
    ;

    sequence = [assign|donothing|ifstmt|whilestmt|returnstmt|execstmt] statement
    ;

    execstmt = execute EOL
    ;
    """
    if tok_ls.found(VAR):
        if(tok_ls.ls[tok_ls.i+1].typ == LPAREN): #must be execute
            temp = ExecStmt(execute())
            tok_ls.consume(EOL)
        else:
            temp = assign()
    elif tok_ls.found(NULL):  temp = donothing()
    elif tok_ls.found(IF):    temp = ifstmt()
    elif tok_ls.found(WHILE): temp = whilestmt()
    elif tok_ls.found(RETURN): temp = returnstmt()
    elif tok_ls.found(IMPORT): temp = importstmt()
    else:
        error("Expected VAR, NULL or IF but found " + str(token.val))

    if not (tok_ls.found(EOF) or tok_ls.found(CRPAREN)): #Sequence, add next statement as child
        return Sequence(temp, statement())
    return temp

def ifstmt():
    """
    ifstmt = IF expression THEN CLPAREN statement CRPAREN ELSE CLPAREN statement CRPAREN
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

def whilestmt():
    """
    whilestmt = WHILE expression CLPAREN statement CRPAREN
    ;
    """
    tok_ls.consume(WHILE)
    cond = expression()
    tok_ls.consume(CLPAREN)
    body = statement()
    tok_ls.consume(CRPAREN)

    return While(cond, body)

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

def returnstmt():
    """
    returnstmt = RETURN expression EOL
    ;
    """
    tok_ls.consume(RETURN)
    result = expression()
    tok_ls.consume(EOL)
    return Return(result)

def donothing():
    """
    donothing = NULL EOL
    ;
    """
    tok_ls.consume(NULL)
    tok_ls.consume(EOL)
    return DoNothing()

def importstmt():
    """
    importstmt = IMPORT STR EOL
    ;
    """
    global token

    tok_ls.consume(IMPORT)
    fname = token.val #string
    tok_ls.consume(STR)
    tok_ls.consume(EOL)
    return Import(fname)

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
    expression = [atom|execute] OP expression
        | [atom|execute] COMP expression
        | LPAREN expression RPAREN
        | atom
        | execute
        | function
    ;

    execute = variable LPAREN {expression {COMMA expression}*}? RPAREN
    ;
    """
    global token

    if tok_ls.found(LPAREN): #LPAREN expression RPAREN
        tok_ls.consume(LPAREN)
        result = expression()
        tok_ls.consume(RPAREN)
        return result
    elif tok_ls.foundOneOf([NUM, BOOL, VAR, PAIR, STR, SLPAREN]):
        if tok_ls.found(VAR) and tok_ls.ls[tok_ls.i+1].typ == LPAREN:
            start = execute()
        else:
            start = atom()
        if tok_ls.found(OP): #[atom|execute] OP expression
            oper = token.val
            tok_ls.consume(OP)
            return Op(start, oper, expression())
        elif tok_ls.found(COMP): #[atom|execute] COMP expression
            oper = token.val
            tok_ls.consume(COMP)
            return Comp(start, oper, expression())
        else: #atom|execute
            return start
    elif tok_ls.found(FUNCTION):
        return function()
    else: error("Expected NUM, BOOL, VAR or LPAREN but found " + token.val)

def atom():
    """
    atom = variable
        | BOOL
        | NUM
        | STR
        | pair
        | list
    ;
    """
    global token

    if tok_ls.found(NUM):
        atom = Number(token.val)
        tok_ls.consume(NUM)
    elif tok_ls.found(BOOL):
        atom = Boolean(token.val)
        tok_ls.consume(BOOL)
    elif tok_ls.found(VAR):
        atom = variable()
    elif tok_ls.found(STR):
        atom = String(token.val)
        tok_ls.consume(STR)
    elif tok_ls.found(PAIR):
        atom = pair()
    elif tok_ls.found(SLPAREN):
        atom = listexpr()
    return atom

def pair():
    """
    pair = PAIR SLPAREN expression COMMA expression SRPAREN
    ;
    """
    global token

    tok_ls.consume(PAIR)
    tok_ls.consume(SLPAREN)
    car = expression()
    tok_ls.consume(COMMA)
    cdr = expression()
    tok_ls.consume(SRPAREN)
    return Pair(car, cdr)

def listexpr():
    """
    list = SLPAREN {expression {COMMA expression}*}? SRPAREN
    ;
    """
    global token

    tok_ls.consume(SLPAREN)
    args = []
    while not tok_ls.found(SRPAREN):
        args.append(expression())
        if tok_ls.found(COMMA): tok_ls.consume(COMMA)
        else: break
    tok_ls.consume(SRPAREN)
    return List(args)

def execute():
    """
    execute = variable LPAREN {expression {COMMA expression}*}? RPAREN
    ;
    """
    global token

    name = token.val
    tok_ls.consume(VAR)
    tok_ls.consume(LPAREN)
    args = []
    while not tok_ls.found(RPAREN):
        args.append(expression())
        if tok_ls.found(COMMA): tok_ls.consume(COMMA)
        else: break
    tok_ls.consume(RPAREN)
    return Execute(name, args)

def function():
    """
    function = FUNCTION LPAREN {VAR {COMMA VAR}*}? RPAREN CLPAREN statement CRPAREN
    ;
    """
    global token

    tok_ls.consume(FUNCTION)
    tok_ls.consume(LPAREN)
    args = []
    while not tok_ls.found(RPAREN):
        args.append(token.val)
        tok_ls.consume(VAR)
        if tok_ls.found(COMMA): tok_ls.consume(COMMA)
        else: break
    tok_ls.consume(RPAREN)
    tok_ls.consume(CLPAREN)
    body = statement()
    tok_ls.consume(CRPAREN)

    return Function(args, body)

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
# Test code for parser.#####################
#------------------------------------------#


# Premade token list shown. Will be generated by lexer later.

#ls_test = TokenList([
#    Token(IF, "if"),
#    Token(NUM, 5),
#    Token(COMP, "<"),
#    Token(NUM, 6),
#    Token(THEN, "then"),
#    Token(CLPAREN, "{"),
#    Token(VAR, "x"),
#    Token(ASGN, "="),
#    Token(NUM, "5"),
#    Token(EOL, ";"),
#    Token(VAR, "y"),
#    Token(ASGN, "="),
#    Token(NUM, "6"),
#    Token(EOL, ";"),
#    Token(CRPAREN, "}"),
#    Token(ELSE, "else"),
#    Token(CLPAREN, "{"),
#    Token(VAR, "x"),
#    Token(ASGN, "="),
#    Token(NUM, 6),
#    Token(EOL, ";"),
#    Token(CRPAREN, "}"),
#    Token(EOF, "eof")
#    ])

#parser = Parser(ls_test)
#prog = parser.run()
#mach = Machine(prog, {})
#mach.run()
