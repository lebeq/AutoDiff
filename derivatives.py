'''
Library for derivatives.
Contains functions that calculate derivatives using a dictionary
cases = {'name of operation': corresponding callable function}
e.g.
term = myexpr('add', left, right)
-> cases = {'add': diff_add} 
-> derivative(term) calls cases[term.op](term.left, term.right)
-> diff_add returns myexpr('add',derivative(term.left), derivative(term.right))
'''

#import atoms as at
import numpy as np
from expression import *

################## functions calculating derivatives #########################

def calc_diff(term: myexpr, var = None) -> myexpr:
    '''
    Recieves a term and calculates the partial derivative using the functions defined below
    and the dict with cases, defined at the end of the document.
    Var is the variabel w.r.t. which the derivative is to be taken.
    Default is None which is taken to be 'x', else input string, e.g.
    calc_diff(TERM, 'y')
    '''
    return cases[term.op](term,var)

############### derivatives of id, const, special fcts ##############

def diff_const(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of constant = 0
    '''
    return myexpr('const', '0')

def diff_id(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of the identity = 1.
    Checks if it's the desired variable.
    If not, it's zero.
    '''
    if term.left == var:
        return myexpr('const', '1')
    else:
        return myexpr('const', '0')

def diff_add(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of sum: (x+y)'= x' + y'
    '''
    return myexpr('add',calc_diff(term.left,var), calc_diff(term.right,var))

def diff_mul(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of product: (x*y)'= (x')*y + x(y')
    '''
    return myexpr('add', myexpr('mul', calc_diff(term.left,var), term.right), myexpr('mul', term.left, calc_diff(term.right,var)))

def diff_pwr(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of x^n: (x^n)' = n*x^(n-1)
    for clarity the new exponent is calculated first,
    assumes the exponent is constant
    '''
    newp = str(term.power.eval(1)-1)
    return myexpr('mul', myexpr('const',term.power),myexpr('pwr',myexpr('id'),myexpr('const',newp)))

def diff_exp(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of exponential fct: exp(x)'= exp(x)*(x')
    '''
    return myexpr('mul',calc_diff(term.left,var),term)

def diff_sin(term: myexpr, var = None) -> myexpr:
    '''
    Deravitve of sine: cosine
    '''
    return myexpr('mul',myexpr('cos',term.left),calc_diff(term.left,var))

def diff_cos(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of cosine: -sine
    '''
    return myexpr('mul',myexpr('const','-1',None),myexpr('mul',myexpr('sin',term.left),calc_diff(term.left,var)))

def diff_tan(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of tangent: sec^2=1/cos^2
    '''
    return myexpr('mul',myexpr('pwr',myexpr('cos'),myexpr('const','-2')),calc_diff(term.left,var))

def diff_log(term: myexpr, var = None) -> myexpr:
    '''
    Derivative of natural log: (arg'/arg)
    '''
    return myexpr('mul',calc_diff(term.left,var),myexpr('pwr',term.left,myexpr('const','-1')))




cases = {
        'const': diff_const, 'id': diff_id, 'add': diff_add, 'mul': diff_mul,
        'pwr': diff_pwr, 'exp': diff_exp, 'sin': diff_sin, 'cos': diff_cos,
        'tan': diff_tan, 'log': diff_log
        }