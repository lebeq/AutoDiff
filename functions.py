'''
This is a custom class for symbolic function manipulation, with the main goal being automatic differentiation of functions.
Standard functions, e.g. trig functions, are taken from SymPy. The plotting routines are from MatPLotLib.
Multivariate function will be added in the future.

When creating an instance of the class the user must input the variable and then either a mathematical expression in infix notation
or just a name for the function. All inputs have to strings.

e.g. test('x', '2*x**2 + (sin(3*(x**2 - 1)))(x + 1)')
will be an instance with variable 'x', expression '2*x**2 + (sin(3*(x**2 - 1)))(x + 1)' and name None.
Note, that special functinos, such as trig functions, have to be bracketed as in the example.

The expression can be turned into a sympy symbolic expression via the test.symbify method.
Arithmetic operations between intances of test are possible usign the test.{add,substr,mul} methods.
Evaluation at a number is possible with the test.myeval method.

Differentiation of user input is possible via the test.symbify_diff method.
This returns a sympy symbolic expression.
'''

import sympy as sp
import numpy as np
import re

class test:

    functs = ['tan', 'cos', 'sin', 'sec', 'exp'] #the special functions we have defined as methods for our class
    token_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'] #tokens used for parsing, differentiating

    def __init__(self, var: str, expression: str, name = None, dim = 1):
        #self.t = t  #type of function, e.g. polynomial, trig etc
        self.dim = dim #for adding multivariate functions later, for now irrelevant
        self.var = var #variable, specified by user input
        self.expression = expression #user input, eg. '2*x**3 + cos(x)'
        self.name = name #user input, if the function is not specified, e.g. f
    
######## some standard functions from SymPy #############
    def sin(arg=None):
        if arg == None:
            x = sp.Symbol('x')
        elif isinstance(arg, sp.Expr):
            #if we get sin(3x+5) then the Argument is already
            #a symbolic expression, so don't convert to symbol
            #SymPy takes care of concatenation in this case
            return sp.sin(arg)
        else:
            #preserves the given variable name
            x = sp.Symbol(f'{arg}')
        return sp.sin(x)
    
    def cos(arg=None):
        if arg == None:
            x = sp.Symbol('x')
        elif isinstance(arg, sp.Expr):
            #if we get sin(3x+5) then the Argument is already
            #a symbolic expression, so don't convert to symbol
            #SymPy takes care of concatenation in this case
            return sp.cos(arg)
        else:
            #preserves the given variable name
            x = sp.Symbol(f'{arg}')
        return sp.cos(x)

    def tan(arg=None):
        if arg == None:
            x = sp.Symbol('x')
        elif isinstance(arg, sp.Expr):
            #if we get sin(3x+5) then the Argument is already
            #a symbolic expression, so don't convert to symbol
            #SymPy takes care of concatenation in this case
            return sp.tan(arg)
        else:
            #preserves the given variable name
            x = sp.Symbol(f'{arg}')
        return sp.tan(x)
    
    def sec(arg=None):
        if arg == None:
            x = sp.Symbol('x')
        elif isinstance(arg, sp.Expr):
            return sp.sec(arg)
        else:
            x = sp.Symbol(f'{arg}')
        return sp.sec(x)
    
    def exp(arg=None):
        if arg == None:
            x = sp.Symbol('x')
        elif isinstance(arg, sp.Expr):
            #if we get sin(3x+5) then the Argument is already
            #a symbolic expression, so don't convert to symbol
            #SymPy takes care of concatenation in this case
            return sp.exp(arg)
        else:
            #preserves the given variable name
            x = sp.Symbol(f'{arg}')
        return sp.exp(x)

######### methods for parsing and converting strings to symbolic expressions ###########
    def poly_from_dict(d, arg=None):
        '''
        input: dict of the form {exponent: coefficient}
        output: symbolic polynomial  \sum coefficient*x**exponent
        Used in str_parse.
        Relies on SymPy for the variable.
        '''
        if arg == None:
            x = sp.Symbol('x')
        else:
            x = sp.Symbol(f'{arg}')
        p = 0
        for i in range(len(d)):
            p = p + list(d.values())[i]*x**(list(d.keys())[i])
        return p

    
    def sanitize(s: str):
        '''
        for the specific use in conv_mon, helps extract exponent by removing extra bracketing and the asterisks
        e.g. 2*x**{23} -> 23 (the variable and coefficient are removed in conv_mon)
        '''
        return s.replace('*', '').replace('{', '').replace('}', '').replace('(', '').replace(')', '')
    
    #tokenizer for bracketed input
    def tokenize(var: list, s: str) -> dict:
        '''
        Given a math expression in string format, this assigns tokens to the subexpressions in order of evaluation, i.e. innermost expression first
        For now uses a fixed list of tokens
        Does not convert the expressions to symbolic expressions
        Output is a dict with {str(expression): token}
        '''
        token_list = test.token_list
        tokens = {}
        buff = []
        l = []
        stack = []

        #put brackets around each variable occurence, so that they get their own tokens
        for v in var:
            s = s.replace(v, f'({v})')

        #pu the whole expression in brackets, so we don't loose terms
        s = '(' + s + ')'

        for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            elif ch == ')' and stack:
                beg = stack.pop()
                l.append([len(stack), s[beg+1:i]])
        for j in range(len(l)):
            if buff and prio > l[j][0]:
                for e in buff:
                    tkn = tokens[e]
                    l[j][1] = l[j][1].replace(e, tkn)
                    
                    #go through rest of expressions and replace each instance of current expression with its token
                    for q in range(j+1, len(l)):
                        if e in l[q][1]:
                            l[q][1] = l[q][1].replace(e, tkn)
            
                buff.clear()
            prio = l[j][0]
            #TRANSLATE INTO ATOMS BEFORE APPENDING TO BUFF
            expr = l[j][1]
            buff.append(expr)
            tokens[expr] = token_list[j]
        return tokens

    def conv_mon(self, s: str, coefficients: dict, sign: int) -> dict:
        '''
        Converts str monomials into a dictionary of the form {exponent: coefficient}.
        Used by str_parse.
        poly_from_dict makes the output dict into symbolic polynomial.
        Relies on SymPy for special functions, variables.
        '''
        if re.search(rf'\b{self.var}\b', s): 
            #if there is a variable in the monomial, locate it
            beg, end = re.search(rf'\b{self.var}\b', s).span()
            temp = test.sanitize(s[end:])
            if len(temp) == 0: 
                #if it is the empty string then the exponent is implicitly 1  
                power = 1
            else:
                power = float(s[end:].replace('*', '').replace('{', '').replace('}', '').replace('(', '').replace(')', '')) #extract the exponent
            if not(len(s[:beg].replace('*', '')) == 0) and not(s[:beg].replace('*', '') == '-'): 
                #check if coefficient is implicitly 1, i.e. we have only x with supressed 1 before it
                value = sign*float(s[:beg].replace('*', '')) #if there is a coefficient extract it
            if s[:beg].replace('*', '') == '-': 
                #check if we have -x, if yes, multiply coeff by -1
                s = s[:beg].replace('*', '').replace('-', '-1') + s[beg:]
                value = sign*float(s[:beg+1])
            if len(s[:beg].replace('*', '')) == 0:
                #if no coefficient, then it's implicitly 1
                value = sign*1
            if power in coefficients.keys():
                coefficients[power] += value
            else:
                coefficients[power] = value
        else: 
            #no variable, so monomial is only a constant
            if 0 in coefficients.keys(): #check whether we already have constants to be added to, if not append to dictionary
                coefficients[0] += sign*float(s)
            else:
                coefficients[0] = sign*float(s)
        return coefficients

    def conv_fcts(functdict: dict, arg=None):
        '''
        Converts a dictionary  of the form {function name: argument} into a symbolic expression, which is the sum of the functions.
        Used in str_parse.
        Uses built-in special functions.
        Relies on SymPy for special functions, variables.
        '''
        expr = 0
        for el in list(functdict.keys()):
            if el in test.functs: 
                #check if the function is known
                inner = test.poly_from_dict(functdict[el], arg)
                if el == 'sin':
                    expr += test.sin(inner)
                if el == 'cos':
                    expr += test.cos(inner)
                if el == 'tan':
                    expr += test.tan(inner)
                if el == 'sec':
                    expr += test.sec(inner)
                if el == 'exp':
                    expr += test.exp(inner)
        return expr
    
    def str_parse(self, s: str = None):
        '''
        For internal use, takes a simple string and converts it into symbolic expression using the built-in special functions and poly_from_dict.
        Simple string here means no nested brackets, no parallel brackets, no nested special functions and no sums of monomials inside special functions.
        Used by symbify.
        Relies on SymPy for special functions, variables.
        '''
        vrs = [self.var] #variables, for now only 1-dim functions
        pm = ['+', '-']
        fbuff = '' #buffer for remembering special functions 
        words = re.compile('|'.join(test.functs)) #pattern for the regex search
        coeffs = {} #the dictionary for creating polynomials
        fcoeffs = {} #dictionary for polynomials inside special funcsionts key = function, value = dict of monomial
        if s == None: #if we don't pass an expression we want to use the one given by the instance of test
            g = self.expression #extract expression
        else: 
            g = s
        splitg = g.split() #split according to whitespaces
        sign = 1 #the first monomial has a virtual '+' before it
        
        for i in range(len(splitg)):
            #omit pluses and minuses, remember the sign
            if splitg[i] in pm:
                if splitg[i] == '-':
                    sign = -1
                if splitg[i] == '+':
                    sign = 1
                continue
                
            #check if we hit a special function
            if words.search(splitg[i]):
                qs = splitg[i].split('(')
                fbuff = fbuff + qs[0] #remember which function got removed
                qs.remove(qs[0])
                splitg[i] = qs[0].replace(')', '') #now splitg[i], the argument of the fct, is of the form coeff*x**exponent

                fcoeffs[fbuff] = test.conv_mon(self, splitg[i], {}, sign) #assigns the value of the monomial as a dict
                fbuff = '' #reset buffer
                continue #the monomial has been dealt with, avoids counting it again as stand-alone monomial

            #check if the expression is just a number without x, then we want exponent = 0 and coeff = that number
            if vrs[0] not in splitg[i]: 
                #for now only one variable, will have to tweak in multivariate case
                splitg[i] = splitg[i].replace('*','') #in case we have split 3*(2*x**2+1) into 3* and (2*x**2+1), then we want to sanitize 3*
                powr = 0
                val = float(splitg[i])
                if powr in coeffs.keys(): #check whether we already have constants to be added to, if not append to dictionary
                    coeffs[powr] += val
                else:
                    coeffs[powr] = val
                continue

            #handle monomials of the form coeff*x**exponent
            test.conv_mon(self, splitg[i], coeffs, sign)
        return test.poly_from_dict(coeffs, vrs[0]) + test.conv_fcts(fcoeffs, vrs[0])
    
    def symbify(self, s: str = None):
        '''
        Converts string user input into a symbolic expression.
        Uses tokenize to break input down, and str_parse to convert the atomic expressions
        '''
        words = re.compile('|'.join(test.functs))
        pm = ['+', '-']
        brackets = ['{', '[', '(', ')', ']', '}']
        token_list = test.token_list
        toks = re.compile('|'.join(token_list))
        symb_tokens = {} #dict for converted tokens, {TOKEN: symbolic expr}
        expr = 0
        if s == None:
            tokens = test.tokenize(self.var, self.expression) #dict of tokenized str input, {string expr: TOKEN}
        else:
            tokens = test.tokenize(self.var, s)

        for key, val in tokens.items():
            expr = 0
            sign = 1
            splitkey = key.split()
            for t in splitkey:
                if t in pm:
                    if t == '-':
                        sign = -1
                    if t == '+':
                        sign = 1
                    continue
                if toks.findall(t): 
                    #check for tokens in current expression
                    tkns = toks.findall(t)
                    temp_expr = 1
                    coeff = 1
                    idx = t.find('(')
                    for tkn in tkns:
                        fct_search = words.search(t) #check for special functions
                        if fct_search:
                            beg, end = fct_search.span()
                            if idx == 0: 
                                #then there is no coefficient before the first bracket
                                if fct_search.group(0) == 'sin' and t.find(tkn) == end+1: #make sure the special function takes the current token as argument
                                    temp_expr *= test.sin(symb_tokens[tkn])
                                if fct_search.group(0) == 'cos' and t.find(tkn) == end+1:
                                    temp_expr *= test.cos(symb_tokens[tkn])
                                if fct_search.group(0) == 'tan' and t.find(tkn) == end+1:
                                    temp_expr *= test.tan(symb_tokens[tkn])
                                if fct_search.group(0) == 'sec' and t.find(tkn) == end+1:
                                    temp_expr *= test.sec(symb_tokens[tkn])
                                if fct_search.group(0) == 'exp' and t.find(tkn) == end+1:
                                    temp_expr *= test.exp(symb_tokens[tkn])
                            else: 
                                #we have coefficient
                                if t[:beg] == '':
                                    coeff = 1
                                else:
                                    if t[:beg] == '-':
                                        coeff = -1
                                    else:
                                        coeff = test.str_parse(self, t[:beg-1]) #this assumes thath the coefficient and special function are separated by an asterisk
                                if fct_search.group(0) == 'sin' and t.find(tkn) == end+1: 
                                    temp_expr *= test.sin(symb_tokens[tkn])
                                if fct_search.group(0) == 'cos' and t.find(tkn) == end+1:
                                    temp_expr *= test.cos(symb_tokens[tkn])
                                if fct_search.group(0) == 'tan' and t.find(tkn) == end+1:
                                    temp_expr *= test.tan(symb_tokens[tkn])
                                if fct_search.group(0) == 'exp' and t.find(tkn) == end+1:
                                    temp_expr *= test.exp(symb_tokens[tkn])
                        else:
                            pwr = t.find('**')
                            if pwr > 0:
                                if t[pwr + 2] not in brackets:
                                    exponent = test.str_parse(self, t[pwr+2])
                                else:
                                    exponent = test.str_parse(self, test.sanitize(t[pwr:]))
                            else:
                                exponent = 1
                            if idx == 0: 
                                #no coefficient
                                temp_expr *= symb_tokens[tkn]**exponent
                            elif idx == -1:
                                #no token in brackets, e.g. 3*A
                                tkn_idx = t.find(tkn)
                                if tkn_idx == 0:
                                    #no coefficient, check for exponent
                                    temp_expr *= symb_tokens[tkn]**exponent
                                else:
                                    #there is a coefficient
                                    coeff = test.str_parse(self, t[:tkn_idx-1])
                                    temp_expr *= symb_tokens[tkn]**exponent
                            else:
                                #check if coeff is a token
                                if t[:idx-1] in tkns:
                                    coeff = symb_tokens[t[:idx-1]]
                                    if t[:idx-1] != tkn:
                                        #avoid multiplying by the same token twice
                                        temp_expr *= symb_tokens[tkn]**exponent
                                else:
                                    coeff = test.str_parse(self, t[:idx-1])
                                    temp_expr *= symb_tokens[tkn]**exponent
                    expr += coeff*sign*temp_expr
                else: 
                    #no tokens found, just convert the expression
                    expr += sign*test.str_parse(self, t)
            symb_tokens[val] = expr #assign token as key and symbolic expression as it's value
        return symb_tokens #return the whole expression, this is a sympy symbolic expression

    def diff_mon(self, s:str, var: str = None):
        '''
        Differentiate monomials, input is string of the form coeff*variable**exponent or just coeff
        Checks if variable present, then uses power rule to return differentiated monomial as a symbolic expr, using symbify
        '''
        expr = ''
        if var == None:
            variable = self.var
        else:
            variable = var
        if re.search(rf'\b{variable}\b', s):
            #found variable in the monomial
            beg, end = re.search(rf'\b{variable}\b', s)
            if beg == 1:
                coeff = '1'
            else:
                if s[:beg] == '-':
                    coeff = '-1'
                else:
                    coeff = s[:beg-2]
            if '**' in s:
                power = test.sanitize(s[end:])
            else:
                power = '1'
            new_power = str(float(power)-1)
            if float(power) == 1 and coeff != '':
                expr = power+'*'+coeff
            elif float(power) != 1 and coeff != '':
                expr = power+'*'+coeff+'*'+f'({variable})'+'**'+new_power
            elif float(power) == 1 and coeff == '':
                expr = power
            elif float(power) != 1 and coeff == '':
                expr = power+'*'+f'({variable})'+'**'+new_power
        else:
            expr = '0'
        return test.str_parse(self, expr)
    
    def diff_fct(self, s:str):
        '''
        Differentiate special functions. Hard coded. Also returns argument of functions for chain rule.
        UPDATE IF ADDED SPECIAL FUNCTIONS.
        '''
        words = re.compile('|'.join(test.functs))
        fsearch = words.search(s)
        beg, end = fsearch.span()
        end_brack = s.find(')')
        arg = s[end+1:end_brack] #everythig between opening and closing bracket of the special fct
        temp_expr = ''
        if fsearch.group(0) == 'sin':
            temp_expr = f'(cos({arg}))'
        if fsearch.group(0) == 'cos':
            temp_expr = f'((-1)*sin({arg}))'
        if fsearch.group(0) == 'tan':
            temp_expr = f'(sec({arg})**2)'
        if fsearch.group(0) == 'exp':
            temp_expr = f'(exp({arg}))'
        return (temp_expr, arg)
    
    def tok_prod_rule(self, s: str, tokens_found: list):
        '''
        method for the product rule for expressions involving multiple tokens, e.g. 3*(A)**2(B)(C)**4
        always separates last token and then uses power rule treating the rest as one expression
        e.g.
        s = 3*(A)**2(B)(C)**4, tokens_found = ['A', 'B', 'C']
        (3*(A)**2(B))X(C)**4 -> d/dx{(3*(A)**2(B))}X(C)**4 + (3*(A)**2(B))Xd/dx{(C)**4}
        proceeds recursively until there is only one token in the expresseion. Then uses test.diff_mon
        output is string, 'inner derivagtives' included as dTOKEN
        to be used in creating dict of differentiated tokens
        '''
        token_list = test.token_list
        tokens = re.compile('|'.join(token_list))
        tok_idxs = {}
        temp_expr = ''
        if len(tokens_found) == 1:
            #only one token  left, apply power rule and chain rule, 2*A**3 -> (6*A**2)dA
            return '('+test.diff_mon(self, s, tokens_found[0])+')'+'*'+'(d'+tokens_found[0]+')'
        for t in tokens_found:
            #get index of each token
            idx, nix = re.search(rf'\b{t}\t', s).span()
            tok_idxs[t] = idx
        slice_dict= {} #dict for storing the expr we need for differentiating, stored by token {token: s[:index of that token]}
        for tkn, exp in tok_idxs.items():
            if (tok_idxs[tkn] - 1) <= 0:
                #avoid spilling over index range and starting from the back
                continue
            slice_dict[tkn] = s[:tok_idxs[tkn] - 1]
        last_key = list(slice_dict.keys())[-1]
        last_key_tokens = tokens.findall(slice_dict[last_key])
        exponent = test.sanitize(s[tok_idxs[last_key] + 1:])
        return '('+test.tok_prod_rule(self, slice_dict[last_key], last_key_tokens)+')'+f'({last_key})'+'**'+exponent+' + '+'('+slice_dict[last_key]+')'+'('+test.diff_mon(self, f'({last_key})**{exponent}', last_key)+')'+'*'+'(d'+last_key+')'
    
    def diff_token(self, d: dict) -> dict:
        '''
        Goes through dict of tokens, e.g. the ouput of test.tokenize, and creates dict of derivatives of the tokens
        format: {dTOKEN: differentiated expression as str}
        '''
        functs = test.functs
        token_list = test.token_list
        pm = ['+', '-']
        tokens = re.compile('|'.join(token_list))
        words = re.compile('|'.join(functs))
        diff_token_dict = {}

        for key, val in d.items():
            splitkey = key.split()
            token = val
            expr = ''

            for el in splitkey:
                sign = 1
                if el in pm:
                    if el == '-':
                        sign = -1
                        expr += ' - '
                    if el == '+':
                        sign = 1
                        expr += ' + '
                    continue
                fsearch = words.search(el)
                if fsearch:
                    #found special function
                    #the argument will already have been computed, as it's in brackets
                    fct, arg = test.diff_fct(el)
                    inner_der = diff_token_dict['d'+arg]
                    expr += f'{sign}*({fct})*(d{arg})'
                elif tokens.search(el):
                    #found token
                    toks = tokens.findall(el)
                    if len(toks) > 1:
                        expr += test.tok_prod_rule(el, toks)
                    else:
                        expr += test.diff_mon(el, toks[0])+'*(d'+toks[0]+')'
                else:
                    #no special functions or tokens, just a monomial
                    expr += test.diff_mon(el, self.var)
            diff_token_dict['d'+f'{token}'] = expr
        return diff_token_dict

    def symbify_diff(self, s: str = None) -> dict:
        '''
        Turns the output of diff_token into a symbolic expression, similarly to symbify.
        Output is dictionary of symbolic expressions.

        '''
        words = re.compile('|'.join(test.functs))
        pm = ['+', '-']
        brackets = ['{', '[', '(', ')', ']', '}']
        token_list = test.token_list
        toks = re.compile('|'.join(token_list))
        symb_diff_token_dict = {}
        expr = 0

        if s == None:
            s = self.expression
        
        token_dict = test.tokenize(self.var, s) #tokenize input string
        diff_token_dict = test.diff_token(self, token_dict) #differentiates the expressions
        diff_toks = re.compile('|'.join(list(diff_token_dict.keys())))
        symb_token_dict = test.symbify(self, s) #dict of symbolic expressions {TOKEN: symb expr}
        
        for key, val in diff_token_dict.items():
            expr = 0
            sign = 1
            splitval = val.split()

            for el in splitval:
                if el in pm:
                    if el == '+':
                        sign = 1
                    if el == '-':
                        sign = -1
                    continue
                if not (toks.findall(el) and diff_toks.findall(el)):
                    #no tokens of any kind in the expression
                    expr += test.str_parse(self, el)
                fct_search = words.search(el)
                if fct_search:
                    #found special function
                    beg, end = fct_search.span()
                    if beg == 0 :
                        coeff = 1
                    else:
                        coeff = test.str_parse(self, el[:beg-1])
                    tkn = el[end:end+2] #the token inside the special fct
                    if fct_search.group(0) == 'sin': 
                        expr += coeff*test.sin(symb_token_dict[tkn])*symb_diff_token_dict['d'+tkn]
                    if fct_search.group(0) == 'cos':
                        expr += coeff*test.cos(symb_token_dict[tkn])*symb_diff_token_dict['d'+tkn]
                    if fct_search.group(0) == 'tan':
                        expr += coeff*test.tan(symb_token_dict[tkn])*symb_diff_token_dict['d'+tkn]
                    if fct_search.group(0) == 'sec':
                        expr += coeff*test.sec(symb_token_dict[tkn])*symb_diff_token_dict['d'+tkn]
                    if fct_search.group(0) == 'exp':
                        expr += coeff*test.exp(symb_token_dict[tkn])*symb_diff_token_dict['d'+tkn]
                #FIGURE OUT HOW TO DEAL WITH EXPR OF THE TYPE coeff*TOKEN*dTOKEN etc
            symb_diff_token_dict['d'+tkn] = expr
        return symb_diff_token_dict 





                


    
######All the class methods like: arithemtic operations, evaluation, plotting########    
    @classmethod
    def add(cls, f, g):
        '''
        Adds two test objects. If both only have a name, the output is (f+g)(x). The second fcts var gets renamed to match the first.
        If one has an expression, the variable in the second gets renamed to match the first.
        '''
        if f.expression == None and g.expression == None:
            return test(f.var, None, f'{f.name} + {g.name}')
        if f.expression == None and g.expression != None:
            return test(g.var, f'{g.expression} + {f.name}({g.var})', None)
        if g.expression == None and f.expression != None:
            return test(f.var, f'{f.expression} + {g.name}({f.var})', None)
        return test(f.var, f.expression + g.expression.replace(g.var, f.var), None)
    
    @classmethod
    def substr(cls, f, g):
        '''
        Substracts two test objects. Variable name assignement same as in add.
        '''
        if f.expression == None and g.expression == None:
            return test(f.var, None, f'{f.name} - {g.name}')
        if f.expression == None and g.expression != None:
            return test(g.var, f'{g.expression} - {f.name}({g.var})', None)
        if g.expression == None and f.expression != None:
            return test(f.var, f'{f.expression} - {g.name}({f.var})', None)
        return test(f.var, f.expression - g.expression.replace(g.var, f.var), None)
    
    @classmethod
    def mul(cls, f, g):
        '''
        Multiplies two test objects. Variable name assignement same as in add.
        '''
        if f.expression == None and g.expression == None:
            return test(f.var, None, f'{f.name}*{g.name}')
        if f.expression == None and g.expression != None:
            return test(g.var, f'({g.expression})*{f.name}({g.var})')
        if g.expression == None and f.expression != None:
            return test(f.var, f'({f.expression})*{g.name}({f.var})')
        return test(f.var, f'({f.expression})*({g.expression.replace(g.var, f.var)})', None)
    
    @classmethod
    def myeval(cls, f, val):
        '''
        Evaluates a test object. If no expression is given returns name(value).
        Uses symbify to evaluate user input expression.
        '''
        if f.expression == None: #if there is no expression to evaluate, return f(value)
            return f'{f.name}({val})'
        last_key = list(test.symbify(f).keys())[-1]
        return test.symbify(f)[last_key].subs(f.var, val)
    
    @classmethod
    def myplot(cls, f, title=None, xlabel=None, ylabel=None, zlabel=None, aspect_ratio='auto', xlim=None, ylim=None, axis_center='auto', axis=True, xscale='linear', yscale='linear', legend=False, autoscale=True, margin=0, annotations=None, markers=None, rectangles=None, fill=None, backend='default', size=None, **kwargs):
        '''
        Does not work probably.
        '''
        return sp.plot(f, title=title, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, aspect_ratio=aspect_ratio, xlim=xlim, ylim=ylim, axis_center=axis_center, axis=axis, xscale=xscale, yscale=yscale, legend=legend, autoscale=autoscale, margin=margin, annotations=annotations, markers=markers, rectangles=rectangles, fill=fill, backend=backend, size=size, **kwargs).show()
    
    def __str__(self):
        if self.name == None:
            return self.expression
        if self.expression == None:
            return f'{self.name}({self.var})'     
    
    def __repr__(self):
        if self.name == None:
            return f'function object({self.expression})'
        if self.expression == None:
            return f'function object<{self.name}, var = {self.var}, dim = {self.dim}>'