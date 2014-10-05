import operator
import copy

#Small step semantics interpreter.

# Data types #####################################

class Number(object):
    """Number class. Non reducible."""
    def __init__(self, val=0):
        self.val = int(val)
    def to_str(self):
        return str(self.val)
    def reducible(self):
        return False
    def reduce(self, environment):
        return self

class Boolean(object):
    """Boolean class. Non reducible."""
    def __init__(self, val=False):
        self.val = val
    def to_str(self):
        return str(self.val)
    def reducible(self):
        return False
    def reduce(self, environment):
        return self

def get_op(op):
    """Get operator function from string."""
    return {"+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.div,
            "%": operator.mod,
            "<": operator.lt,
            ">": operator.gt,
            "==": operator.eq,
            "!=": operator.ne
            }[op]

# Compound terms #################################
# Include add, multiply, less than, greater than, equal to.
# Each is a collection of multiple terms.

class Op(object):
    """Operation (+-*/%), returns number."""
    def __init__(self, first, op, second):
        self.first = first
        self.op = op
        self.second = second
    def to_str(self):
        return self.first.to_str() + self.op + self.second.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """If term 1 reduces, reduce it.
        Else, if term 2 reduces, reduce it.
        Else, reduce operation of terms."""
        if(self.first.reducible()):
            return Op(self.first.reduce(environment), self.op, self.second)
        elif(self.second.reducible()):
            return Op(self.first, self.op, self.second.reduce(environment))
        else:
            return Number(get_op(self.op)(self.first.val, self.second.val))

class Comp(object):
    """Comparison (><==), returns boolean."""
    def __init__(self, first, op, second):
        self.first = first
        self.op = op
        self.second = second
    def to_str(self):
        return self.first.to_str() + self.op + self.second.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """If term 1 reduces, reduce it.
        Else, if term 2 reduces, reduce it.
        Else, reduce comparison of terms."""
        if(self.first.reducible()):
            return Op(self.first.reduce(environment), self.op, self.second)
        elif(self.second.reducible()):
            return Op(self.first, self.op, self.second.reduce(environment))
        else:
            return Boolean(get_op(self.op)(self.first.val, self.second.val))


#######################################################

class Variable(object):
    """Variable. Reduces to variable's value."""
    def __init__(self, name):
        self.name = name
    def to_str(self):
        return str(self.name)
    def reducible(self):
        return True
    def reduce(self, environment):
        """Look up value, reduce to that."""
        return environment[self.name]

# Statements ##########################################
# Statements include assignments, if-else, sequences, and null statement.
# Reduce() method returns tuple of expression and environment; environment can be modified.

class DoNothing(object):
    """Empty statement. Non reducible."""
    def __init__(self):
        pass
    def to_str(self):
        return "do_nothing;"
    def reducible(self):
        return False
    def reduce(self, environment):
        """Non reducible, so don't change."""
        return (self, environment)

class Assign(object):
    """Assignment. Reduces to null statement."""
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
    def to_str(self):
        return self.variable.to_str() + "=" + self.value.to_str() + ";"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce value to primitive form before assigning."""
        if self.value.reducible():
            return (Assign(self.variable, self.value.reduce(environment)), environment)
        else:
            environment[self.variable.to_str()] = self.value
            return (DoNothing(), environment)

class Sequence(object):
    """Sequence of two statements. If first reduces, reduce it; if not, reduce to second statement."""
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def to_str(self):
        return self.first.to_str() + " " + self.second.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """If first one reducible, reduce. Otherwise, become second statement."""
        if self.first.reducible():
            #Must alter environment according to statement 1
            self.first, environment = self.first.reduce(environment)
            return (Sequence(self.first, self.second), environment)
        else:
            return (self.second, environment)

class If(object):
    """If statement (if condition then consequence else alternative)"""
    def __init__(self, condition, consequence, alternative):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative
    def to_str(self):
        return "if " + self.condition.to_str() + " {" + self.consequence.to_str() + "} else {" + self.alternative.to_str() + "}"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce condition to boolean/int. Reduce to cons or alt depending on cond."""
        if self.condition.reducible():
            return (If(self.condition.reduce(environment), self.consequence, self.alternative), environment)
        elif self.condition.val:
            return (self.consequence, environment)
        else:
            return (self.alternative, environment)

class While(object):
    """While loop (while condition body)"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def to_str(self):
        return "while " + self.condition.to_str() + " {" + self.body.to_str() + "}"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce to {if condition then sequence(body while_loop) else do_nothing}
        Don't reduce condition or body; reduced in if statement."""
        # copy.deepcopy(self.body) makes copy of body of while statement.
        # This stops reduction of body outside of while loop changing next while loop.
        return (If(self.condition, Sequence(copy.deepcopy(self.body), self), DoNothing()), environment)

class Define(object):
    """Function definition."""
    pass

class Execute(object):
    """Function call."""
    pass

#######################################################

class Machine(object):
    """Reduces and executes small-step semantics of AST from parser."""
    def __init__(self, expression, environment):
        self.expression = expression
        self.environment = environment
        self.i = 0 #Current step
    def step(self):
        #Create string of dict of variables to print environment
        env_str = "[" + ", ".join([x[0] + ":" + x[1].to_str() for x in self.environment.items()]) + "]"
        state_str = self.expression.to_str() + " " + env_str
        #Print current state, comment out to turn off printing state
        print str(self.i+1) + " | " + state_str
        #Increment i to signify step has been taken.
        self.i += 1
        #Reduce expression and update environment.
        self.expression, self.environment = self.expression.reduce(self.environment)
    def run(self):
        while self.expression.reducible():
            self.step()
        self.step() #Display last, non-reducible statement (should be DoNothing)

########################################################
#Test code.

#if_prog = If(LessThan(Number(5), Number(6)), Assign(Variable('x'), Number(5)), Assign(Variable('x'), Number(6)))
#prog = Sequence(Assign(Variable('x'), Number(5)), Assign(Variable('y'), LessThan(Number(5), Number(3))))
#mach = Machine(if_prog, {})
#mach.run()
