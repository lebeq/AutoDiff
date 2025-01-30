'''
Analogous to derivatives.py.
Evaluates myexpr term w.r.t. given variable.
If a variable is not to be evaluated it returns the string of that variable.
All functions then check is an argument is a string.
'''
import numpy as np
from expression import *


def calc_eval(term: myexpr, vars: dict):
    '''
    Evaluates a term using the functions defined below
    and the dict with cases, defined at the end of the document.
    The vars dictionary should be of the form {'variable': value},
    where the value is a float. Multiple variables can be given.
    If a variable is not provided with a value all others are evaluated
    and the result is a string.
    '''
    return cases[term.op](term,vars)

########################### basic evals: constants, id ##################################
def eval_const(term, vars):
    #const always gives it's assigned num const as worth
    #so the aergument of self.worth() is irrelevant    
    return term.worth(0)

def eval_id(term, vars):
    '''
    Checks whether the variable is to be evaluated.
    If not, returns the string.
    '''
    if term.left in list(vars.keys()):
        return term.worth(vars[term.left])
    else:
        return term.str

########################### binary operation evals: add, mul, pwr #######################
def eval_add(term, vars):
    #calc left and right summands
    #to check if string is returned
    left = calc_eval(term.left,vars) 
    right = calc_eval(term.right,vars)

    if isinstance(left,str) and isinstance(right,str):
        return f'{term.left.str} + {term.right.str}'
    elif isinstance(left,str) and not isinstance(right,str):
        return f'{left} + {right}'
    elif not isinstance(left,str) and isinstance(right,str):
        return f'{left} + {right}'
    else:
        return left + right

def eval_mul(term, vars):
    #same idea as eval_add
    left = calc_eval(term.left,vars)
    right = calc_eval(term.right,vars)

    if isinstance(left,str) and isinstance(right,str):
        return f'({term.left.str}) * ({term.right.str})'
    elif isinstance(left,str) and not isinstance(right,str):
        return f'({left}) * ({right})'
    elif not isinstance(left,str) and isinstance(right,str):
        return f'({left}) * ({right})'
    else:
        return left * right

def eval_pwr(term, vars):
    base = calc_eval(term.left,vars)
    exponent = calc_eval(term.right,vars)
    if isinstance(base,str) and isinstance(exponent,str):
        return f'{term.left.str}**{term.right.str}'
    elif isinstance(base,str) and not isinstance(exponent,str):
        return f'{term.left.str}**{exponent}'
    elif not isinstance(base,str) and isinstance(exponent,str):
        return f'{base}**{term.right.str}'
    else:
        return base**exponent

########################## special function evals: exp, trig fcts, log #######################
def eval_exp(term, vars):
    arg = calc_eval(term.left,vars)
    if isinstance(arg,str):
        return f'exp({arg})'
    else:
        return np.exp(arg)
    
def eval_sin(term, vars):
    arg = calc_eval(term.left,vars)
    if isinstance(arg,str):
        return f'sin({arg})'
    else:
        return np.sin(arg)

def eval_cos(term, vars):
    arg = calc_eval(term.left,vars)
    if isinstance(arg,str):
        return f'cos({arg})'
    else:
        return np.cos(arg)
    
def eval_tan(term, vars):
    arg = calc_eval(term.left,vars)
    if isinstance(arg,str):
        return f'tan({arg})'
    else:
        return np.tan(arg)

def eval_log(term, vars):
    arg = calc_eval(term.left,vars)
    if isinstance(arg,str):
        return f'log({arg})'
    else:
        return np.log(arg)


cases = {
        'const': eval_const, 'id': eval_id, 'add': eval_add, 'mul': eval_mul,
        'pwr': eval_pwr, 'exp': eval_exp, 'sin': eval_sin, 'cos': eval_cos,
        'tan': eval_tan, 'log': eval_log
        }