#-------------------------------------------#
# Define all token types ####################
# Each is a unique int, essentially an enum #
#-------------------------------------------#

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
WHILE = 16
COMMA = 17
RETURN = 18 #return keyword for function returns
SLPAREN = 19 #square left parenthesis ([)
SRPAREN = 20 #square right parenthesis (])
STR = 21 #string (difference from var identified by lexer)
FUNCTION = 22 #used for lambda functions (eg. function(x){return x+1;})
