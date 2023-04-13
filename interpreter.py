"""
Collection of functions and objects needed to interpret programs.
"""
from collections import ChainMap, namedtuple
from enum import Enum,auto
from Parser import *
from lexer import *

class SymType(Enum):
    FUN_INT = auto()
    FUN_REAL = auto()
    BUILTIN_INT = auto()
    BUILTIN_REAL = auto()
    VAR_INT = auto()
    VAR_REAL = auto()


class SymbolTableEntry:
    """
    Our basic unit of storage
    """
    def __init__(self, sym_type:SymType, sym_value):
        self.sym_type = sym_type
        self.sym_value = sym_value


class Environment:
    """
    A nested environment for storing program variables.
    """
    def __init__(self, parent=None):
        if parent == None:
            self.env = ChainMap({})
        else:
            self.env = ChainMap({}, parent.env)


    def lookup(self, key:str):
        """
        Search for and return the given symbol.
        Returns a reference to SymbolTableEntry. None, if it does not exist.
        """
        # check for the variable
        if key in self.env.keys():
            return self.env[key]
        else:
            return None


    def define(self, name:str, entry:SymbolTableEntry):
        """
        Insert an entry into the current environment.
        """
        self.env[name] = entry


# builtin functions
def builtin_print(args, env):
    """
    Print arguments, return 0.
    """
    if len(args)==1 and type(args[0])==type([]):
            for i in args[0]:
                print(i)
    else:
        print(*args,end=' ')
    return 0


def builtin_readint(args, env):
    """
    Read an integer and return it.
    """
    return int(input())


def builtin_readreal(args, env):
    """
    Read a real and return it.
    """
    return float(input())


# build the global environment
global_env = Environment()
global_env.define('print', SymbolTableEntry(SymType.BUILTIN_INT, builtin_print))
global_env.define('read', SymbolTableEntry(SymType.BUILTIN_INT, builtin_readint))
global_env.define('readreal', SymbolTableEntry(SymType.BUILTIN_REAL, builtin_readreal))

# define a parse node as a named tuple
ParseNode = namedtuple("ParseNode", ("eval", "child"))


# Semantic elements of the language
def eval_function_def(node : ParseNode, env : Environment):
    """
    Evaluation on a function-def.

    child[0] - Type (SymType)
    child[1] - Identifier
    child[2] - List of arguments (type, name)
    child[3] - Block
    """
    env.define(node.child[1], SymbolTableEntry(node.child[0], node))


def eval_block(node : ParseNode, env : Environment):
    """
    Evaluate a block

    The children of the block are the statements
    """
    for statement in node.child:
        statement.eval(statement, env)


def eval_decl(node : ParseNode, env : Environment):
    """
    Evaluate a declaration
    
    child[0] - Type
    child[1] - Identifier
    """
    if '[' in node.child[1]:
        n=node.child[1].split('[')
        iden=n[0]
        n=n[1].split(']')
        env.define(iden, SymbolTableEntry(node.child[0], []))
    else:
        env.define(node.child[1], SymbolTableEntry(node.child[0], 0))

def eval_while(node : ParseNode, env : Environment):
    """
    Evaluate a while loop

    child[0] - Condition
    child[1] - Block / Statement
    """
    while node.child[0].eval(node.child[0], env):
        node.child[1].eval(node.child[1], env)


def eval_if(node : ParseNode, env : Environment):
    """
    Evaluate an if statement

    child[0] - Condition
    child[1] - Block / Statement
    """
    if node.child[0].eval(node.child[0], env):
        node.child[1].eval(node.child[1], env)


def eval_call(node : ParseNode, env : Environment):
    """
    Evaluate a call to a function.

    child[0] - Identifier
    child[1..n] - args
    """

    # get the parts of the call
    name = node.child[0]
    args = node.child[1:]

    # retrieve the function
    entry = env.lookup(name)
    if not entry:
        print("Function Undefined: %s"%(name))
        return 0

    # evaluate the arguments
    for i in range(len(args)):
        args[i] = args[i].eval(args[i], env)
    
    # attempt to call the function
    if entry.sym_type in (SymType.BUILTIN_INT, SymType.BUILTIN_REAL):
        return entry.sym_value(args, env)
    elif entry.sym_type in (SymType.FUN_INT, SymType.FUN_REAL):
        f = entry.sym_value
        params = f.child[2]
        if len(args) != len(params):
            print("Incorrect number of arguments for %s"%(name))
            return 0

        # create the function's local environment
        env = Environment(global_env)
        i = 0
        for t,n in params:
            env.define(n, SymbolTableEntry(t, args[i]))
            i = i + 1

        # call our function
        return f.child[3].eval(f.child[3], env)    
    else:
        print("Error: %s is not a function!"%(name))
        return 0



def eval_lt(node : ParseNode, env : Environment):
    """ 
    Evaluate <
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left < right


def eval_lte(node : ParseNode, env : Environment):
    """ 
    Evaluate <=
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left <= right


def eval_gt(node : ParseNode, env : Environment):
    """ 
    Evaluate >
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left > right


def eval_gte(node : ParseNode, env : Environment):
    """ 
    Evaluate >=
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)
    print(left,right)
    return left >= right


def eval_equal(node : ParseNode, env : Environment):
    """ 
    Evaluate ==
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left == right


def eval_plus(node : ParseNode, env : Environment):
    """ 
    Evaluate +
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left + right


def eval_minus(node : ParseNode, env : Environment):
    """ 
    Evaluate -
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left - right


def eval_times(node : ParseNode, env : Environment):
    """ 
    Evaluate *
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left * right


def eval_divide(node : ParseNode, env : Environment):
    """ 
    Evaluate /
    """

    # evaluate children
    left = node.child[0].eval(node.child[0], env)
    right = node.child[1].eval(node.child[1], env)

    return left / right


def eval_number(node : ParseNode, env : Environment):
    """
    Evaluate a literal
    """

    return node.child[0] 


def eval_identifier(node : ParseNode, env : Environment):
    """
    Evaluate an identifier.
    """

    entry = env.lookup(node.child[0])
    if not entry:
        print("Error: %s not defined"%(node.child[0]))
        return 0
    return entry.sym_value


def eval_assign(node : ParseNode, env : Environment):
    """
    Evaluate an identifier.
    child[0] - identifier
    child[1] - value
    """

    entry = env.lookup(node.child[0])
    
    if node.child[1].child[0]=='read':
        if not entry:
            #print("Error: %s not defined"%(node.child[0]))
            return None
    
        entry.sym_value = int(input("read "+node.child[0]+" "))
    elif node.child[1].child[0]=='insert':
        if not entry:
            #print("Error: %s not defined"%(node.child[0]))
            return None
        ele = int(input("insert n items"))
        entry.sym_value.append(ele)


    elif node.child[1].child[0]=='bublesort':
        entry.sym_value=sorted(entry.sym_value)
    elif node.child[1].child[0]=='rev':
        entry.sym_value=entry.sym_value[::-1]

    else:
        expr = node.child[1]
        if not entry:
            #print("Error: %s not defined"%(node.child[0]))
            return None
        #print(node.child[1].child)
        entry.sym_value=expr.eval(expr, env)
    return None


def eval_swap(node : ParseNode, env : Environment):
    """
    Evaluate an identifier.
    child[0] - identifier
    child[1] - identifier
    """
    

    entry = env.lookup(node.child[0])
    #print(node.child[1].child[0],entry.sym_value)
    if not entry:
        print("Error: %s not defined"%(node.child[0]))
        return None
    expr = node.child[1]
    temp=entry.sym_value
    #print(entry.sym_value)
    entry.sym_value = expr.eval(expr, env)
    
    entry = env.lookup(node.child[1].child[0])
    if not entry:
        print("Error: %s not defined"%(node.child[1]))
        return None
    #print(entry.sym_value)
    entry.sym_value = temp
    return None

# interpreter program
if __name__ == '__main__':
    import sys
    file = open(sys.argv[1],'r')    # open file specified on command line
    content=file.read()
    
    file = open(sys.argv[1],'w+') 
    file.seek(0)
    file.write("int main()\n"+content)
    file.seek(0)
    
    
    file = open(sys.argv[1])    # open file specified on command line

    # create the lexer and the parser
    try:
        lexer = Lexer(file)
        parser = Parser(lexer)

        # try to parse
        parse_tree = parser.parse()
        if not parse_tree:
            print("Parsing failed with %d errors."%(parser.errors))
        else:
            # run our program
            parse_tree.eval(parse_tree, global_env)
    except:
        pass

    file = open(sys.argv[1],'w+') 
    file.seek(0)
    file.write(content)