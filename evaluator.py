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
        if environment[0][self.name]:
            return environment[0][self.name]
        elif environment[1][self.name]:
            return environment[1][self.name]
        else:
            return None

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
            environment[0][self.variable.to_str()] = self.value
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
    def __init__(self, name, arg_ls, body):
        self.name = name
        self.arg_ls = arg_ls #List of strings, each is name of each arg.
        self.body = body  #Function body. Do NOT reduce.
    def to_str(self):
        return self.name + "(" + ",".join(self.arg_ls) + ") = {" + self.body.to_str() + "}"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Do not reduce body.
        Functions are stored as tuple of parameters and body.
        They are stored in second dict in environment, for functions only."""
        environment[1][self.name] = [self.arg_ls, self.body]
        return (DoNothing(), environment)

class Execute(object):
    """Function call. Contains arguments supplied and name of called function."""
    def __init__(self, name, arg_ls):
        self.name = name
        self.arg_ls = arg_ls
    def to_str(self):
        return self.name + "(" + ",".join([x.to_str() for x in self.arg_ls]) + ")"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce all arguments.
        After, create new machine and run.
        Reduce to '_return_' variable in environment."""
        if any([x.reducible() for x in self.arg_ls]):
            return Execute(self.name, [x.reduce(environment) for x in self.arg_ls])
        else:
            body = environment[1][self.name]
            temp_env = copy.deepcopy(environment)
            for i in range(len(self.arg_ls)):
                #Set function parameters as temporary variables.
                #Remember that function val is stored as tuple of params and body.
                #Thus, temp_env[1][self.name][0][i] accesses i-th param name of function.
                temp_env[0][temp_env[1][self.name][0][i]] = self.arg_ls[i]
            temp_env[0]["_return_"] = Number(0) #Set return value of function to 0 by default.
            #Make machine to run function body separately. Give function body and temp_env.
            temp_mach = Machine(temp_env[1][self.name][1], temp_env)
            return temp_mach.run()[0]["_return_"] #Run function. Return value of '_return_' variable.

class Return(object):
    """Return statement in a function. eg. return 5"""
    def __init__(self, val):
        self.val = val
    def to_str(self):
        return "return " + self.val.to_str()
    def reducible(self):
        return True
    def reduce(self, environment):
        """Set _return_ variable to value of expression."""
        if self.val.reducible():
            return (Return(self.val.reduce(environment)), environment)
        else:
            environment[0]['_return_'] = self.val
            return (DoNothing(), environment)

#######################################################


class Machine(object):
    """Reduces and executes small-step semantics of AST from parser."""
    def __init__(self, expression, environment):
        self.expression = expression
        self.environment = environment #Environment is a list of two dicts, for vars and funcs.
        self.i = 0 #Current step
    def step(self):
        #Create string of dict of variables to print environment
        var_str = "[" + ", ".join([x[0] + ":" + x[1].to_str() for x in self.environment[0].items()]) + "]"
        fnc_str = "[" + ", ".join([x[0] + ":" + x[1][1].to_str() for x in self.environment[1].items()]) + "]"
        state_str = self.expression.to_str() + " " + var_str + " " + fnc_str
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
        return self.environment

########################################################
#Test code.

#if_prog = If(LessThan(Number(5), Number(6)), Assign(Variable('x'), Number(5)), Assign(Variable('x'), Number(6)))
#prog = Sequence(Assign(Variable('x'), Number(5)), Assign(Variable('y'), LessThan(Number(5), Number(3))))
#mach = Machine(if_prog, {})
#mach.run()
