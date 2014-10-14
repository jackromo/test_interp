import operator
import copy

# Small step semantics interpreter.
# Every possible term or combination of terms has a reduce() method.
# This method reduces every term by one 'step'. A compound term may reduce its subterms in this method.
# The main driver code - or machine - iterates over the reduce() method until the program is nonreducible.
# The reduce() method calls may alter the environment, eg. during an assign reduce.


# Data types #####################################


class Null(object):
    """Null data type, ie. None in python. Non reducible."""
    def __init__(self):
        pass
    def to_str(self):
        return "Null"
    def reducible(self):
        return False
    def reduce(self):
        return self

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

class Pair(object):
    """Pair class of two values."""
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
    def to_str(self):
        return "(" + self.car.to_str() + ", " + self.cdr.to_str() + ")"
    def reducible(self):
        """Reducible if car or cdr are reducible."""
        if self.car.reducible() or self.cdr.reducible(): return True
        else: return False
    def reduce(self, envionment):
        """Reduce car and cdr."""
        if self.car.reducible():
            return Pair(self.car.reduce(environment), self.cdr)
        elif self.cdr.reducible():
            return Pair(self.car, self.cdr.reduce(environment))
        else:
            return self

class List(object):
    """List of values. Non reducible if all elements are non reducible."""
    def __init__(self, ls):
        self.ls = ls
    def to_str(self):
        return "[" + ",".join([x.to_str() for x in self.ls]) + "]"
    def reducible(self):
        return any([x.reducible() for x in self.ls])
    def reduce(self, environment):
        """Reduce all elements if any are reducible. Else, return self."""
        if any([x.reducible() for x in self.ls]):
            return List([x.reduce(environment) for x in self.ls])
        else:
            return self

class String(object):
    """String data type, non-reducible."""
    def __init__(self, val):
        self.val = val #String value
    def to_str(self):
        return "\"" + self.val + "\""
    def reducible(self):
        return False
    def reduce(self, environment):
        return self

class Function(object):
    """Function data type.
    Must get closure during reduce(), non-reducible after completed.
    Contains parameters and body."""
    def __init__(self, params, body):
        self.params = params #Names of all params, as strings
        self.body = body
        self.closure = {} #Current environment, remembered for closure
        self.closure_defined = False #If closure is defined or not
    def to_str(self):
        return "function(" + ",".join(self.params) + ") {" + self.body.to_str() + "}"
    def reducible(self):
        """If closure not set, must define closure during reduce(), so reducible.
        Else, is considered as a data type, so not reducible."""
        return not self.closure_defined
    def reduce(self, environment):
        self.closure = copy.deepcopy(environment.get_top_scope())
        self.closure_defined = True
        return self

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
        if environment.contains(self.name):
            return environment.get(self.name)
        else:
            return None


# Compound terms #################################
# Include add, multiply, less than, greater than, equal to.
# Each is a collection of multiple terms.


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
        Else, reduce operation of terms.
        Remember to make types of operands the same so op works."""
        if(self.first.reducible()):
            return Op(self.first.reduce(environment), self.op, self.second)
        elif(self.second.reducible()):
            return Op(self.first, self.op, self.second.reduce(environment))
        else:
            #Make operand types same so op works.
            if type(self.first) != type(self.second):
                if isinstance(self.first, String):
                    self.second = String(str(self.second.val))
                elif isinstance(self.second, String):
                    self.first = String(str(self.first.val))
            result = get_op(self.op)(self.first.val, self.second.val)
            if(isinstance(self.first, String)):
                return String(result)
            else: #Must be number, not boolean because not comparison
                return Number(result)

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
            environment.put(self.variable.name, self.value)
            return (DoNothing(), environment)

class Sequence(object):
    """Sequence of two statements.
    If first reduces, reduce it; if not, reduce to second statement."""
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
            #Check if predefined function
            if self.name == "car": return PredefFuncs.carReduce(self.arg_ls[0])
            elif self.name == "cdr": return PredefFuncs.cdrReduce(self.arg_ls[0])
            elif self.name == "setcar": return PredefFuncs.setCarReduce(self.arg_ls[0], self.arg_ls[1])
            elif self.name == "setcdr": return PredefFuncs.setCdrReduce(self.arg_ls[0], self.arg_ls[1])
            elif self.name == "print": return PredefFuncs.printReduce(self.arg_ls[0])
            elif self.name == "input": return PredefFuncs.inputReduce(self.arg_ls[0])
            elif self.name == "curry": return PredefFuncs.curryReduce(self.arg_ls[0])
            elif self.name == "elem": return PredefFuncs.elemReduce(self.arg_ls[0], self.arg_ls[1])
            elif self.name == "setelem": return PredefFuncs.setElemReduce(self.arg_ls[0], self.arg_ls[1], self.arg_ls[2])
            #Else, proceed as normal
            else:
                #Functions have params, body attributes and closure, so access each
                params = environment.get(self.name).params
                body = environment.get(self.name).body
                closure = environment.get(self.name).closure
                #Make temporary scope to run function in
                func_scope = {}
                #Copy over environment into scope for closure
                for name,val in closure.items(): func_scope[name] = val
                #Put params into top scope as variables with args as values
                for i in range(len(self.arg_ls)):
                    #Insert variables of param names with argument values for function
                    func_scope[params[i]] = self.arg_ls[i]
                #Return value stored as special var, reduce func to it
                func_scope["_return_"] = Null()
                #Push new scope to environment
                environment.push_scope(func_scope)
                temp_mach = Machine(body, environment)
                #Run function and return value of _return_ variable
                result = temp_mach.run().get("_return_")
                environment.pop_scope()
                return result

class ExecStmt(object):
    """If a function is called alone, eg. 'print(5);', must be considered as a statement.
    ie. must return self and environment."""
    def __init__(self, expr):
        self.expr = expr
    def to_str(self):
        return self.expr.to_str() + ";"
    def reducible(self):
        return True
    def reduce(self, environment):
        """Reduce statement before, then check.
        This means it cannot return a nonreducible value as a statement.
        eg. 'f(5)'; does not reduce to '5;', then 'do_nothing;' - goes straight to 'do_nothing;'."""
        result = self.expr.reduce(environment)
        if result.reducible():
            return (ExecStmt(result), environment)
        else:
            return (DoNothing(), environment)

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
            environment.put('_return_', self.val)
            return (DoNothing(), environment)

class Import(object):
    """Import a file - essentially run it and copy environment."""
    def __init__(self, filename):
        self.filename = filename
    def to_str(self):
        return "import " + self.filename
    def reducible(self):
        return True
    def reduce(self, environment):
        """Open and run file of name 'filename'.
        Concatenate environment created by evaluating imported file
        with own environment's top scope.
        Any conflicting names are overriden by import."""
        from interpreter import file_interp
        #Run imported file. Get environment created.
        import_env = file_interp(self.filename)
        #Get dict of environment to concatenate with own top scope.
        import_scope = import_env.get_dict()
        #Concatenate dicts together.
        environment.get_top_scope().update(import_scope)
        return (DoNothing(), environment)


# Predefined functions and statements ##################
#Includes return, car(), cdr, setcar(), setcdr(), etc.


class PredefFuncs(object):
    """Container for all predefined functions and their reduce() methods."""

    @staticmethod
    def elemReduce(ls, index):
        """Call elem() function on list, return element of specific index in list.
        Equivalent to ls[i] in Python."""
        return ls.ls[index.val]

    @staticmethod
    def setElemReduce(ls, index, new_val):
        """Call setelem() function on list, return list with modified element at index.
        Equivalent to ls[i] = new_val in Python."""
        ls_new = copy.deepcopy(ls.ls)
        ls_new[index.val] = new_val
        return List(ls_new)

    @staticmethod
    def carReduce(pair):
        """Call car() function on pair, returns car value."""
        return pair.car

    @staticmethod
    def cdrReduce(pair):
        """Call cdr() function on pair, returns cdr value."""
        return pair.cdr

    @staticmethod
    def setCarReduce(pair, new):
        """Call setcar() function on pair, returns pair with new car."""
        return Pair(new, pair.cdr)

    @staticmethod
    def setCdrReduce(pair, new):
        """Call setcdr() function on pair, returns pair with new cdr."""
        return Pair(pair.car, new)

    @staticmethod
    def printReduce(val):
        """Call print() function on expression, print result."""
        if isinstance(val, String):
            #If a string, cut off quotation marks on sides when printing
            string = val.to_str()
            print string[1:len(string)-1]
        else:
            #Print everything else (numbers, bools) normally
            print val.to_str()
        return Number(0) #Print function returns number 0 to denote success

    @staticmethod
    def inputReduce(val):
        """Call input() function, print start, take input and reduce to result."""
        if isinstance(val, String):
            #If a string, cut off quotation marks on sides when printing
            string = val.to_str()
            return String(raw_input(string[1:len(string)-1]))
        else:
            #Print everything else (numbers, bools) normally
            return String(raw_input(val.to_str()))

    @staticmethod
    def curryReduce(func):
        """Return the curried version of a function.
        eg. f = function(x,y){return x+y;};
        This becomes f = function(x){ return function(y){return x+y;}; };
        Rule: func(p1, p2, ..., pn){body}
        -> func(p1){ return func(p2) { ... { return func(pn){ body } } ... } }

        Reduces as follows:
        1. Gather all params.
        2. Create a function for each param, taking param as only parameter.
        3. Put body into last param's function.
        4. Starting at last param's function, put each func into prev param's func body.
        5. Reduce to function remaining."""
        temp_funcs = []
        param_ls = func.params
        for p in param_ls:
            temp_funcs.append(Function(p, DoNothing()))
        #Reverse list, since last param's func contains body
        temp_funcs.reverse()
        temp_funcs[0].body = func.body
        #Put functions as return value of each other.
        for i in range(1, len(temp_funcs)): #Don't access first function, since already set
            temp_funcs[i].body = Return(temp_funcs[i-1])

        return temp_funcs[len(temp_funcs)-1] #Result is last func, ie. first param's function


# Define machine to run evaluator.########################


class Machine(object):
    """Reduces and executes small-step semantics of AST from parser."""
    def __init__(self, expression, environment):
        self.expression = expression
        #Environment is a list of two dicts, for vars and funcs.
        self.environment = environment
        self.i = 0 #Current step
    def step(self):
        #Decide indentation for printing to depict current scope.
        indent = "  "*self.environment.get_scope_size()
        #Create string to print environment
        env_str = "[" + ", ".join([x[0] + ":" + x[1].to_str() for x in self.environment.get_dict().items()]) + "]"
        state_str = self.expression.to_str() + "\n" + indent + "  | vars: " + env_str
        #Print current state, comment out to turn off printing state
        print indent + str(self.i+1) + " | " + state_str + "\n"
        #Increment i to signify step has been taken.
        self.i += 1
        #Reduce expression and update environment.
        self.expression, self.environment = self.expression.reduce(self.environment)
    def run(self):
        while self.expression.reducible():
            #If _return_ is defined, stop evaluatingi because function has returned
            if self.environment.contains("_return_"):
                if not isinstance(self.environment.get("_return_"), Null): break
            self.step()
        self.step() #Display last, non-reducible statement (should be DoNothing)
        return self.environment


#class MachStack(object):
#    """Interpreted program functions as stack of machines.
#    When a function is called, new machine pushed onto stack.
#    Uppermost machine is run.
#    When uppermost machine is nonreducible, pop and run next one."""
#    def __init__(self):
#        self.stack = []
#        self.top = None
#    def step_top(self):
#        """Step topmost machine."""
#        self.top.step()
#    def pop(self):
#        self.stack = self.stack[0: len(self.stack)-2]
#        self.top = self.stack[len(self.stack)-1]
#    def push(self, mach):
#        self.stack.append(mach)
#        self.top = mach
#    def run(self):
#        while len(self.stack) > 0:
#            self.step_top()
#    def get_flat_env(self):
#        """Get all environments as a flat dict."""
#        result = {}
#        #Order of environments evaluated is important.
#        #Val of var w/ highest scope overrides others.
#        for x in self.stack:
#            for name,val in x.environment.val.items():
#                result[name] = val
#        return Environment(result)


# Define environment for program to run within. ############


class Environment(object):
    """Environment for code to run within.
    Is a stack of dictionaries, each representing a scope.
    Dictionaries are of names and values. Values can be functions, numbers, etc.
    Scope can contain a _return_ value, holds val of return in function."""
    def __init__(self, val={}):
        self.stack = []
        self.stack.append(val)
    def get_dict(self):
        """Return flat dictionary of all names and vals.
        Higher scopes override lower ones."""
        result = {}
        for x in self.stack:
            #Append lower scope first so higher scopes override it later
            for name,val in x.items():
                result[name] = val
        return result
    def get(self, name):
        """Get value by name in dictonary."""
        return self.get_dict()[name]
    def put(self, name, value):
        """Put value with name and value into highest scope, ie. last in stack list."""
        self.stack[len(self.stack)-1][name] = value
    def contains(self, name):
        """Return True if environment contains name, False if not."""
        return self.get_dict().has_key(name)
    def push_scope(self, scope={}):
        """Create new scope level."""
        self.stack.append(scope)
    def pop_scope(self):
        """Go down one scope level, remove old highest one."""
        self.stack = self.stack[:len(self.stack)-1]
    def get_top_scope(self):
        """Return dictionary of top scope."""
        return self.stack[len(self.stack)-1]
    def get_scope_size(self):
        """Return number of scopes, ie. stack size.
        Used to decide indentation when printing state of machine."""
        return len(self.stack)

########################################################
#Test code.

#if_prog = If(LessThan(Number(5), Number(6)), Assign(Variable('x'), Number(5)), Assign(Variable('x'), Number(6)))
#prog = Sequence(Assign(Variable('x'), Number(5)), Assign(Variable('y'), LessThan(Number(5), Number(3))))
#mach = Machine(if_prog, {})
#mach.run()
