from expression import *
import re

'''
Methods for turning user string input into symbolic expressions.
Contains a tokenizer and converter to symbolic expression.
For now does not simplify.
'''
functions = ['sin', 'cos', 'tan', 'e', 'log']
functs = re.compile('|'.join(functions))
pm = ['+', '-']

def sanitize(s: str):
        '''
        for the specific use in conv_mon, helps extract exponent by removing extra bracketing and the asterisks
        e.g. 2*x**{23} -> 23 (the variable and coefficient are removed in conv_mon)
        '''
        return s.replace('*', '').replace('{', '').replace('}', '').replace('(', '').replace(')', '').strip()

def token_list():
    '''
    Creates list contianing the uppercase Alphabet A-Z
    from ASCII codes
    '''
    toks = []
    for i in range(65,91):
        toks.append(chr(i))
    return toks

def conv_mon(var: list, s: str, token_dict: dict = None):
    '''
    for use in tokenize, converts expressions of the form: x, x**2, A + 1, sin(B) + C into myexpr
    token_dict is dictionary of known tokens and their corresponding myexpr.

    Checks all the possible cases:
    1. only the variable
    2. something of the form '1+TOKEN', '-3'
    3. a token with a coefficient or power, e.g. 2*(TOKEN)**3
    4. a product of tokens (TOKEN)*(TOKEN)
    5. a special function 'sin(TOKEN)'

    Due to the way tokenize() works, these are the only possible cases.
    ''' 
    split_s = s

    signum = myexpr('const', '1')
    #check if it's a variable
    if s in var:
        #it is only a variable, e.g. 'x' or 'y'
        expr = myexpr('id',s)
        return expr
    #check if addition/substraction is present
    if any(ch in pm for ch in s):
        #there is addition
        #or it's sth like '-3'
        #check which sign is present
        if '-' in s:
            #if minus, then set according coeff
            split_s = s.split('-')
            signum = myexpr('const', '-1')
        if '+' in s:
            split_s = s.split('+')
        #remove whitespaces after splitting
        split_s = [el.strip() for el in split_s]
        #this counter is for differentiating left side from right side in split_s
        counter  = 0
        buff = []
        
        for side in split_s:
            #for '-3' split_s = ['','3']
            if side == '':
                counter += 1
                continue
            elif side != '':
                if not any(t in side for t in token_dict):
                    #no token present, so it must be a const
                    #can't be only the variable since a plus or minus is present
                    if counter == 1:
                        temp_expr = myexpr('mul',signum,myexpr('const',side))
                    else:
                        temp_expr = myexpr('const',side)
                else:
                    #found token, recursive call eavluates the token
                    if counter == 1:
                        temp_temp_expr = conv_mon(var,side,token_dict)
                        temp_expr = myexpr('mul',signum,temp_temp_expr)
                    else:
                        temp_expr = conv_mon(var,side,token_dict)
                buff.append(temp_expr)
            counter += 1
        #if there are two things, add them
        #else it's just sth like '-3'
        if len(buff) == 2:
            expr = myexpr('add',buff[0],buff[1])
        else:
            expr = buff[0]
        
    else:
        #check for special functions
        sp_fct_srch = functs.search(s)
        if sp_fct_srch:
            #separate argument
            beg, end = sp_fct_srch.span()
            lit_arg = s[end+1:end+2]
            #the argument is a token, so extract the expression
            arg = token_dict[lit_arg]
            if s[beg:end] == 'sin':
                expr = myexpr('sin',arg)
            if s[beg:end] == 'cos':
                expr = myexpr('cos',arg)
            if s[beg:end] == 'tan':
                expr = myexpr('tan',arg)
            if s[beg:end] == 'e':
                expr = myexpr('exp',arg)
        #check for tokens
        elif any(t in s for t in list(token_dict.keys())):
            for token in token_dict:
                if token in s:
                    beg, end = re.search(rf'\b{token}\b',s).span() #locate token
                    temp = sanitize(s[end:])
                    #check for division
                    if '/' in temp:
                        #it's TOKEN/temp
                        #remove slash
                        temp = temp.replace('/','')
                        #check if a token is in temp
                        if any(tk in temp for tk in list(token_dict.keys())):
                            denominator = token_dict[temp]
                        else:
                            #convert exponent to myexpr
                            denominator = myexpr('const',temp)
                        expr = myexpr('mul',token_dict[token],myexpr('pwr',denominator,myexpr('const','-1')))
                        return expr
                    #check for multiplication of tokens
                    if len(temp) != 0 and s[end+2:end+3] == '(':
                        #it's of the form (TOKEN)*(TOKEN)
                        expr = myexpr('mul',token_dict[token],token_dict[temp])
                        return expr
                    #check for exponent
                    if len(temp) == 0:
                        #if no exponent, set it it to 1, later we can check for it
                        #avoid unnecessary exponentiation by 1
                        power = 1
                    else:
                        #check if token in exponent
                        if any(tk in temp for tk in list(token_dict.keys())):
                            power = token_dict[temp]
                        else:
                            #convert exponent to myexpr
                            power = myexpr('const',temp)
                    #check for coefficient
                    temp_coeff = sanitize(s[:beg])
                    if len(temp_coeff) == 0:
                        #no coeff found, set to 1, same as power
                        coeff = 1
                    else:
                        #check if coeff is a token
                        if temp_coeff in list(token_dict.keys()):
                            coeff = token_dict[temp_coeff]
                        else:
                            #not a token, not a function -> has to be const
                            coeff = myexpr('const', temp_coeff)
                    #put together
                    #goes through all cases
                    if power == 1:
                        if coeff == 1:
                            expr = token_dict[token]
                            break
                        else:
                            expr = myexpr('mul',coeff,token_dict[token])
                            break
                    else:
                        if coeff == 1:
                            expr = myexpr('pwr',token_dict[token],power)
                            break
                        else:
                            expr = myexpr('mul',coeff,myexpr('pwr',token_dict[token],power))
                            break
        else:
            #it's just a number
            #or a fraction e.g. '2/3'
            if '/' in s:
                beg, end = re.search(r'\b/\b',s).span()
                numerator = myexpr('const',s[:beg])
                denominator = myexpr('const',s[end:])
                expr = myexpr('mul',numerator,myexpr('pwr',denominator,myexpr('const','-1')))
            else:    
                expr = myexpr('const',s)
    return expr

        

def tokenize(var: list, s: str) -> dict:
    '''
    Converts user input expression 's' into a dictionary of the form

    {Token: expression}

    where Token comes from token_list() and expression is of the form myexpr(...).
    Uses conv_mon() to convert string to myexpr.

    Runs through string and finds innermost bracket -> the expr inside gets token and prio (int, depth of bracket).
    Replaces all occurences of the expression with its token.
    Goes up one level of prio higher.

    e.g. s='2*x + sin(x*(exp(x)+1))'
    1. brackets around whole expr to not lose the 2*x term: s -> (s)
    2. brackets around ewach occurence of the variable: s -> '(2*(x) + sin((x)*(exp((x))+1)))'
    3. prio levels and expressions would be: [[1,'x'] FROM 2*(x), [2,'x'] FROM sin((x)), [5, 'x'] FROM exp((x))] etc
    4. assigns tokens: tokens = {'A': 'x' ...} 

    last two things happen kinda simultaniously.

    The lit_tokens and lit_buff are saving the str version of tokens and expression.
    This makes it easier to replace all occurances of a token in the given string,
    while simulataneaously converting the expression to myexpr and stroing it separately.
    '''
    t_list = token_list()
    lit_tokens = {}
    tokens = {}
    lit_buff = []
    buff = []
    l = []
    stack = []

    #brackets whole expression to prevent loss of terms
    s = '(' + s + ')'

    #replace 'exp' with 'e' so that if the var is x there is no confusion
    s = s.replace('exp', 'e')

    #bracktes variable(s) so they get their own tokens
    for v in var:
        s = s.replace(v,f'({v})')

    for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            elif ch == ')' and stack:
                beg = stack.pop()
                l.append([len(stack), s[beg+1:i]])
    for j in range(len(l)):
        if lit_buff and prio > l[j][0]:
            for e in lit_buff:
                #get key (token) of the value 'e' (the current expression in str) from lit_token
                tkn = list(lit_tokens.keys())[list(lit_tokens.values()).index(e)]
                l[j][1] = l[j][1].replace(e, tkn)
                
                #go through rest of expressions and replace each instance of current expression with its token
                for q in range(j+1, len(l)):
                    if e in l[q][1]:
                        l[q][1] = l[q][1].replace(e, tkn)
            
            lit_buff.clear()
            buff.clear()
        prio = l[j][0]
        lit_buff.append(l[j][1])

        #tanslate expr into myexpr with conv_mon
        expr = conv_mon(var,l[j][1],tokens)
        buff.append(expr)

        #update myexpr tokens dict
        tokens.update({t_list[j]: expr})
        #update lit tokens dict
        lit_tokens.update({t_list[j]: l[j][1]})

    return tokens      

def my_parser(var: list, s: str):
    '''
    Wrapper for tokenize.
    Parses string to myexpr.
    '''
    res_dict = tokenize(var,s)
    res = list(res_dict.values())
    return res[-1]