Symbol = str
Number = (int, float)
Atom = (Symbol, Number)
List = list
Exp = (Atom, List)

def parse(program: str) -> Exp:
    "Combines the tokenize process and read_from_tokens to read Scheme from string"
    return read_from_tokens(tokenize(program))

def tokenize(chars: str) -> list:
    "converts input command to 'tokens'- a list of chars"
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def read_from_tokens(tokens: list) -> Exp:
    "decides whether char is Exp: '(' -> List or some Atom or SyntaxError"
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)
    
def atom(token: str) -> Atom:
    "if char is Atom, checks if Number or Symbol"
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

"Let's define a more 'Schemey' environment"

import math
import operator as op

def standard_env():
    env = {}
    env.update(vars(math))
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x,list),
        'map':     lambda *args: list(map(*args)),
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()

"can we evaluate some expressions plz?"

def eval(x: Exp, env=global_env) ->  Exp:
    "evaluates the parsed expression"
    if isinstance(x,Symbol):
        return env[x]
    elif isinstance(x, Number):
        return x
    elif x[0] =='quote':
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        "I found the following a little dense- in short, evaluates according to python 'if'"
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp,env)
    elif x[0] == 'define':
        (_, symbol, exp) = x
        env[symbol] = eval(exp, env)
    elif x[0] == 'lambda':
        (_,parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

def repl(prompt='lis.py>'):
    "A prompt-read-eval-print loop - hide these evalparse mofos under the bonnet"
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))

def schemestr(exp):
    "convert python obj to Scheme str"
    if isinstance(exp, List):
        return '(' + ''.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)

from collections import ChainMap as Environment

class Procedure(object):
    "The class for user-defined Scheme procedures- searches local env before global env for var"
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        "Remember: Environment == ChainMap, creates list of dicts to search sequentially"
        "first index is parms:args, second is env where proc def"
        env = Environment(dict(zip(self.parms, args)), self.env)
        return eval(self.body, env)
