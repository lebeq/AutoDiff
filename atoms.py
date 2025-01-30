'''
This is the library for atoms to be used in main file functions.py.
MAKE ATOMS ALL IDENTIFIABLE AS ATOMS; MAYBE SUBCLASS
Give all atoms the same eval method so that add, mul etc can all call it regardless of the atom type
define an add, mult etc object to deal with addition, multiplication etc of atoms

TO-DO:
1. add more special functions
2. figure out product rule
    2.1 how to diff tokens? 
    2.2 recognize type of expr and call appropriate diff method? Maybe need universal diff method, that does not care for type of expression, if even possible?

'''

import numpy as np


class myid:
    '''
    The identity, for the lowest level, x \mapsto x
    '''
    def __init__(self, arg):
        self.arg = arg
        self.name = 'id'

    def eval(self, val):
        return float(val)
    
    def diff(self):
        return self.eval(1)

    def __str__(self):
        return str(self.arg)
    
class myconst:
    '''
    For numbers
    '''
    def __init__(self, arg):
        self.arg = arg
        self.value = float(arg)
        self.name = 'const'

    def eval(self, val):
        #the val is irrelevant, but makes code more streamlined
        return self.value

    def diff(self):
        return myconst('0')

    def __str__(self):
        return str(self.arg)
    
class pwr:
    '''
    For exponents
    '''
    def __init__(self, base, exponent):
        self.base = base
        self.power = exponent
        self.name = 'pwr'

    def eval(self, val):
        return self.base.eval(val)**(self.power.eval(val))
    
    def diff(self):
        return (myconst(self.power), pwr(self.base, myconst))
    
    def __str__(self):
        return f'{self.base}**{self.power}'
    
class token:
    '''
    token object, for the tokenizer method in functions.test
    name = the char representing the token, e.g. 'A'
    expr = the expression which the token represents, made of atoms (possibly also tokens!), e.g. add(mul(myconst('2'), myid('x')), pwr(myid('x'), myconst('4')))) 
    '''
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def eval(self, val):
        return self.expr.eval(val)
    
    def __str__(self):
        return self.name



############ SPECIAL FUNCTIONS ####################

class mysin:
    def __init__(self, arg):
        self.arg = arg
        self.name = 'sin'
    
    def eval(self, val):
        return np.sin(self.arg.eval(val))
    
    def __str__(self):
        return f'sin({self.arg})'
    
class mycos:
    def __init__(self, arg):
        self.arg = arg
        self.name = 'cos'
    
    def eval(self, val):
        return np.cos(self.arg.eval(val))
    
    def __str__(self):
        return f'cos({self.arg})'

class mytan:
    def __init__(self, arg):
        self.arg = arg
        self.name = 'tan'

    def eval(self, val):
        return np.tan(self.arg.eval(val))

    def __str__(self):
        return f'tan({self.arg})'

class mysec:
    def __init__(self, arg):
        self.arg = arg
        self.name = 'sec'

    def eval(self, val):
        return np.sec(self.arg.eval(val))
    
    def __str__(self):
        return f'sec({self.arg})'
    
class myexp:
    def __init__(self, arg):
        self.arg = arg
        self.name = 'exp'

    def eval(self, val):
        return np.exp(self.arg.eval(val))
    
    def __str__(self):
        return f'exp({self.arg})'



############## ARITHMETIC OBJECTS ####################

# class add:
#     '''
#     addition object, has two data pieces, left and right as in left + right
#     '''
#     def __init__(self, left, right):
#         self.left = left
#         self.right = right

#     def eval(self, val):
#         return self.right.eval(val) + self.left.eval(val)
    
#     def __str__(self):
#         return self.left.__str__() +' + '+self.right.__str__()
    
# class mul:
#     '''
#     multiplication object, same data as add
#     '''
#     def __init__(self, left, right):
#         self.left = left
#         self.right = right

#     def eval(self, val):
#         return self.right.eval(val)*self.left.eval(val)
    
#     #def diff(self):
#     #    return add(mul())

#     def __str__(self):
#         return self.left.__str__()+'*'+self.right.__str__()
    
# class sub:
#     '''
#     substraction object, uses add
#     '''
#     def __init__(self, left, right):
#         self.left = left
#         self.right = right

#     def eval(self, val):
#         return add(self.left, mul(myconst('-1'), self.right)).eval(val)
    
#     def __str__(self):
#         return self.left.__str__()+' - '+self.right.__str__()
    
# class div:
#     '''
#     standard division, x/y -> numerator = x, denominator = y
#     '''
#     def __init__(self, numerator, denominator):
#         self.numtor = numerator
#         self.denom = denominator

#     def eval(self, val):
#         return self.numtor.eval(val) / self.denom.eval(val)
    
#     def __str__(self):
#         return f'{self.numtor}/{self.denom}'
    
# class int_div:
#     '''
#     the // division, numerator and denominator same as in div
#     '''
#     def __init__(self, numerator, denominator):
#         self.numtor = numerator
#         self.denom = denominator

#     def eval(self, val):
#         return self.numtor.eval(val) // self.denom.eval(val)
    
#     def __str__(self):
#         return f'{self.numtor}//{self.denom}'

# class diff_id:
#     '''
#     derivative of the identity
#     '''
#     def __init__(self, expr):
#         self.expr = expr
#         self.der = myconst('1')

#     def eval(self, val):
#         return self.der.eval(val)
    
#     def __str__(self):
#         return f'd({self.expr})'
    
# class diff_const:
#     '''
#     derivative of constants
#     '''
#     def __init__(self, expr):
#         self.expr = expr
#         self.der = myconst('0')

#     def eval(self, val):
#         return self.der.eval(val)
    
#     def __str__(self):
#         return f'd({self.expr})'
    
# class diff_pwr:
#     '''
#     derivative of exponents, power rule
#     '''
#     def __init__(self, expr):
#         self.expr = expr
#         self.der = mul(expr.power, pwr(expr.base, sub(expr.power, myconst('1'))))

#     def eval(self, val):
#         return self.der.eval(val)
    
#     def __str__(self):
#         return f'{self.expr.power}*{self.expr.base}**({self.expr.power}-1))'

    
# class diff_mul:
#     '''
#     product rule, the expr is a mul object
#     only options are product of tokens, product of variable and token
#     product of number and token/variable and all of the above but with exponents
#     Tokens should be
#     '''
#     def __init__(self, expr):
#         self.expr = expr
#         if isinstance(expr.left, myconst):
#             self.left_der = diff_const(expr.left)
#         elif isinstance(expr.left, myid):
#             self.left_der = diff_id(expr.left)
#         elif isinstance(expr.left, pwr):
#             self.left_der = diff_pwr(expr.left)
#         if isinstance(expr.right, myconst):
#             self.right_der = diff_const(expr.right)
#         elif isinstance(expr.right, myid):
#             self.right_der = diff_id(expr.right)
#         elif isinstance(expr.right, pwr):
#             self.right_der = diff_pwr(expr.right)
#         self.der = add(mul(self.left_der, self.right), mul(self.left, self.right_der))

#     def eval(self, val):
#         return self.der.eval(val)
    
#     def __str__(self):
#         return f'({self.left_der})*({self.expr.right}) + ({self.expr.left})*({self.right_der})'
    



# class diff:
#     '''
#     Differentiation object
#     '''
#     def __init__(self, expr):
#         self.expr = expr

#     def diff_add(self):
#         '''
#         get add object, return add object
#         e.g.
#         '3*A + x**2' -> add(3*A,x**2) -diff_add-> add(d(3*A), d(x**2))
#         '''