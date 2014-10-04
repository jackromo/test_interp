#Small step semantics interpreter.


# Data types #####################################

class Number(object):
    """Number class. Non reducible."""
    def __init__(self, val=0):
        self.val = val
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

# Compound terms #################################
# Include add, multiply, less than, greater than, equal to.
# Each is a collection of multiple terms.

class Add(object):
    """Addition of two numbers. Reduces to sum or reduced terms."""
    def __init__(self, addend, augend):
        self.addend = addend
        self.augend = augend
    def to_str(self):
        return self.addend.to_str() + "+" + self.augend.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """If term 1 reduces, reduce it. Else, if term 2 reduces, reduce it. Else, reduce to sum of terms."""
        if(self.addend.reducible()):
            return Add(self.addend.reduce(environment), self.augend)
        elif(self.augend.reducible()):
            return Add(self.addend, self.augend.reduce(environment))
        else:
            return Number(self.addend.val + self.augend.val)

class Multiply(object):
    """Multiplication of two numbers. Reduces to product of terms."""
    def __init__(self, multiplier, multiplicand):
        self.multiplier = multiplier
        self.multiplicand = multiplicand
    def to_str(self):
        return self.multiplier.to_str() + "*" + self.multiplicand.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """If term 1 reduces, reduce it. Else, if term 2 reduces, reduce it. Else, reduce to product."""
        if self.multiplier.reducible():
            return Multiply(self.multiplier.reduce(environment), self.multiplicand)
        elif self.multiplicand.reducible():
            return Multiply(self.multiplier, self.multiplicand.reduce(environment))
        else:
            return Number(self.multiplier.val * self.multiplicand.val)

class LessThan(object):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def to_str(self):
        return self.first.to_str() + "<" + self.second.to_str();
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce term 1 first, then term 2, then to a boolean of first < second."""
        if self.first.reducible():
            return LessThan(self.first.reduce(environment), self.second)
        elif self.second.reducible():
            return LessThan(self.first, self.second.reduce(environment))
        else:
            return Boolean(self.first.val < self.second.val)

class GreaterThan(object):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def to_str(self):
        return self.first.to_str() + ">" + self.second.to_str();
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce term 1 first, then term 2, then to a boolean of first > second."""
        if self.first.reducible():
            return GreaterThan(self.first.reduce(environment), self.second)
        elif self.second.reducible():
            return GreaterThan(self.first, self.second.reduce(environment))
        else:
            return Boolean(self.first.val > self.second.val)

class EqualTo(object):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def to_str(self):
        return self.first.to_str() + "==" + self.second.to_str();
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce term 1 first, then term 2, then to a boolean of first == second."""
        if self.first.reducible():
            return EqualTo(self.first.reduce(environment), self.second)
        elif self.second.reducible():
            return EqualTo(self.first, self.second.reduce(environment))
        else:
            return Boolean(self.first.val == self.second.val)


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
    def step(self):
        #Create nice-looking array of variables to print environment
        env_str = "[" + ", ".join([x[0] + ":" + x[1].to_str() for x in self.environment.items()]) + "]"
        print self.expression.to_str() + " " + env_str
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
