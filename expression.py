'''
Contains the basics class for expression.
'''
import numpy as np
tags = ['id', 'const', 'add', 'mul', 'pwr', 'exp', 'sin', 'cos', 'tan', 'log']

class myexpr:
    '''
    the overarching expression class, consists of two objects and an operation
    i.e. (left) OP (right)
    where left and right can be atoms or expressions and op is one of the binary arithmetic operations
    For special functions or just single terms do:
    1. sum of two terms -> myexpr('add',term1,term2) -- multiplication is 'mul'
    2. sin(x) -> myexpr('sin', myexpr('id'))
    3. x^n -> myexpr('pwr', myexpr('id'),myexpr('const','n'))
    4. constants -> myexpr('const', 'value')
    5. e^x -> myexpr('exp', myexpr('id'))

    Upon initializing it creates
    (i) self.worth = lambda x: output -> function that is used for evaluation, x is value at which eval is called, output is dependent on self.op
    (ii) self.str -> string representation for __str__ and __repr__

    To create multiple different variables use explicit variable naming: myexpr('id','VARIABLE NAME').
    '''
    def __init__(self, op, left=None, right=None):
        self.left = left
        self.right = right
        self.op = op
        if self.op not in tags:
            raise Exception(f'Unknown expression type "{self.op}".')
        if self.op == 'id':
            if self.left == None:
                #only one variable, or unnamed
                #default string
                self.left = 'x'
                self.str = 'x'
            else:
                self.str = self.left
            self.worth = lambda x: float(x) #echoes the value at which it is evaluated
        if self.op == 'const':
            self.worth = lambda x: float(self.left)
            self.str = self.left
        if self.op == 'sin':
            self.worth = lambda x: np.sin(self.left.worth(x))
            self.str = 'sin(' + f'{self.left.str}' + ')'
        if self.op == 'cos':
            self.worth = lambda x: np.cos(self.left.worth(x))
            self.str = 'cos(' + f'{self.left.str}' + ')'
        if self.op == 'tan':
            self.worth = lambda x: np.tan(self.left.worth(x))
            self.str = 'tan(' + f'{self.left.str}' + ')'
        if self.op == 'add':
            self.worth = lambda x: self.left.worth(x) + self.right.worth(x)
            self.str = f'{self.left.str} + {self.right.str}'
        if self.op == 'mul':
            self.worth = lambda x: self.left.worth(x)*self.right.worth(x)
            self.str = f'({self.left.str})' + '*' + f'({self.right.str})'
        if self.op == 'pwr':
            self.worth = lambda x: self.left.worth(x)**self.right.worth(x)
            self.str = f'({self.left})' + '^' + f'({self.right})'
        if self.op == 'exp':
            self.worth = lambda x: np.exp(self.left.worth(x))
            self.str = 'exp(' + f'{self.left.str}' + ')'
        if self.op == 'log':
            self.worth = lambda x: np.log(self.left.worth(x))
            self.str = 'log(' + f'{self.left.str}' + ')'
    
    def __str__(self):
        return self.str
    
    def __repr__(self):
        return self.str

