'''
Functionality for vectors
'''
from expression import *
from evaluation import  *
from derivatives import *
from parsing import *


class vect:
    '''
    Vector with components of myexpr.
    First initiate vector with a given dimension.
    Then add components via add_comp().
    '''
    def __init__(self,dim: int):
        self.dim = dim
        self.components = []

    def add_comp(self, term):
        '''
        Adds components to vector, in index order
        from 0 to dim.
        '''
        self.components.append(term)
    
    def __str__(self):
        s = f'[{self.components[0]}'
        if len(self.components) > 1:
            for el in self.components[1:]:
                s += f', {el.str}' 
        s += ']'
        return s
    
    def __repr__(self):
        s = f'[{self.components[0]}'
        if len(self.components) > 1:
            for el in self.components[1:]:
                s += f', {el.str}' 
        s += ']'
        return s

class matrix:
    '''
    A collection of column vectors.
    U-pon initiation the dimensions as well as a list of 
    column vectors need to be provided.
    '''
    def __init__(self, col_dim, row_dim, columns: list):
        '''
        col_dim = dimension of the column vectors
        row_dim = number of column vectors
        Creates col_dim X row_dim matrix
        Columns should be a list of vects
        '''
        self.col_dim = col_dim
        self.row_dim = row_dim
        self.columns = columns

    def __str__(self):
        s = '[['
        for i in range(self.col_dim):
            for j in range(self.row_dim):
                s += f'  {self.columns[j].components[i]},     '
            s += '\n'
        s += ']]'
        return s
    
    def __repr__(self):
        s = '[['
        for i in range(self.col_dim):
            for j in range(self.row_dim):
                s += f'  {self.columns[j].components[i]},     '
            s += '\n'
        s += ']]'
        return s

################################ vector operations ############################################
def vect_add(v1: vect, v2: vect) -> vect:
    '''
    Vector addition, component-wise.
    '''
    if v1.dim != v2.dim:
        return 'Dimensions do not match'
    else:
        res_v = vect(v1.dim)
        for i in range(res_v.dim):
            res_v.add_comp(myexpr('add',v1.components[i],v2.components[i]))
        return res_v
    
def vect_scalar_mul(v1: vect, coeff: myexpr) -> vect:
    '''
    Scalar multiplication of a vector with a term of myexpr.
    Multiplies the vector by coeff component-wise.
    '''
    res_v = vect(v1.dim)
    for i in range(res_v.dim):
        res_v.add_comp(myexpr('mul',v1.components[i],coeff)) 
    return res_v

def vect_cross_prod(v1: vect, v2: vect) -> vect:
    '''
    Cross product of two 3D vectors.
    '''
    if v1.dim != v2.dim:
        return 'Dimensions do not match'
    elif v1.dim != 3 and v2.dim != 3:
        return 'Not defined outside of 3-dimensional space.'
    else:
        res_v = vect(v1.dim)
        res_v.add_comp(myexpr('add',myexpr('mul',v1.components[1],v2.components[2]),myexpr('mul',myexpr('const','-1'),myexpr('mul',v1.components[2],v2.components[1]))))
        res_v.add_comp(myexpr('add',myexpr('mul',v1.components[2],v2.components[0]),myexpr('mul',myexpr('const','-1'),myexpr('mul',v1.components[0],v2.components[2]))))
        res_v.add_comp(myexpr('add',myexpr('mul',v1.components[0],v2.components[1]),myexpr('mul',myexpr('const','-1'),myexpr('mul',v1.components[1],v2.components[0]))))
        return res_v


def vect_dot_prod(v1: vect, v2: vect) -> myexpr:
    '''
    Dot product of two vectors.
    '''
    if v1.dim != v2.dim:
        return 'Dimensions do not match'
    else:
        sum = myexpr('mul',v1.components[0],v2.components[0])
        for i in range(1,v1.dim):
            temp_expr = myexpr('mul',v1.components[i],v2.components[i])
            sum = myexpr('add',sum,temp_expr)
        return sum

def vect_eval(v: vect, vals: dict) -> vect:
    '''
    Evaluates vector w.r.t. given dict of vars and corr. values.
    '''
    res_v = vect(v.dim)
    for el in v.components:
        val = calc_eval(el,vals)
        if isinstance(val,float):
            res_v.add_comp(myexpr('const',f'{val}'))
        else:
            #since calc_eval returns a string if the expr
            #contains a variable that's not eval'd
            #the output must be parsed back into myexpr
            res_v.add_comp(my_parser(list(vals.keys()),val))
    return res_v

############################# matrix operations #############################
def mat_add(m1: matrix, m2: matrix) -> matrix:
    '''
    Addition of matrices, compoenent-wise.
    '''
    #check if both matrices have same shape
    if m1.col_dim != m2.col_dim or m1.row_dim != m2.row_dim:
        return 'Dimensions do not match.'
    
    res_mat = matrix(m1.col_dim, m1.row_dim, [])

    for i in range(m1.row_dim):
        temp_vect = vect(m1.col_dim)
        for j in range(m1.col_dim):
            temp = myexpr('add', m1.columns[i].components[j], m2.columns[i].components[j])
            temp_vect.add_comp(temp)
        res_mat.columns.append(temp_vect)
    return res_mat

def mat_prod(m1: matrix, m2: matrix) -> matrix:
    '''
    Product of two matrices.
    reads out the row vectors of left matrix.
    The resulting matrix has ij-th entry:
    ((i-th) row of m1 ) ° ((j-th) column od m2)
    and is of dimension (m1.row_dim)x(m2.col_dim).
    Uses vect_dot_prod().
    '''
    #check if matrix dim's are compatible
    if m1.row_dim != m2.col_dim:
        return 'Dimensions do not match.'
    
    res_mat = matrix(m1.row_dim, m2.col_dim, [])
    
    #read out the rows of first matrix into a vector
    m1_rows = []
    for j in range(m1.col_dim):
        row = vect(m1.row_dim)
        for i in range(m1.row_dim):
            row.add_comp(m1.columns[i].components[j])
        m1_rows.append(row)
    
    #multiply rows by columns
    #first row times all the columns etc
    for l in range(m2.col_dim):
        res_col = vect(m2.col_dim)
        for k in range(len(m1_rows)):
            v_prod = vect_dot_prod(m1_rows[k],m2.columns[l])
            res_col.add_comp(v_prod)
        res_mat.columns.append(res_col)
    return res_mat

def mat_vect_prod(mat: matrix, v: vect) -> vect:
    '''
    Matrix times vector.
    Components of resulting vecotr are
    the dot product of matrix row times vector.
    Uses vect_dot_prod().
    '''
    #check dimension compatibility
    if mat.row_dim != v.dim:
        return 'Dimension not compatible.'
    
    res_v = vect(v.dim)
    
    #read out the rows of the matrix into a vector
    mat_rows = []
    for j in range(mat.col_dim):
        row = vect(mat.row_dim)
        for i in range(mat.row_dim):
            row.add_comp(mat.columns[i].components[j])
        mat_rows.append(row)
    
    #compute components
    for l in range(len(mat_rows)):
        res_v.add_comp(vect_dot_prod(mat_rows[l],v))
    
    return res_v

def mat_eval(m: matrix, vals: dict) -> matrix:
    '''
    Evaluates a matrix at given values.
    Uses vect_eval().
    '''
    res_mat = matrix(m.col_dim,m.row_dim,[])

    for col in m.columns:
        res_mat.columns.append(vect_eval(col,vals))
    return res_mat

############################ vector calculus ################################
def vect_diff(v: vect, var: str) -> vect:
    '''
    differentiates a vector component-wise w.r.t. the given variable
    aka vector-by-scalar derivative
    '''
    res_v = vect(v.dim)
    for el in v.components:
        res_v.add_comp(calc_diff(el,var))
    return res_v

def vect_grad(term: myexpr, vars: list) -> vect:
    '''
    Gradient of scalar function f: R^n -> R.
    All variables have to be provided in the vars list.
    '''
    dim = len(vars)
    res_v = vect(dim)
    for i in range(dim):
        res_v.add_comp(calc_diff(term,vars[i]))
    return res_v

def mat_diff(m: matrix, var: str) -> matrix:
    '''
    Component-wise derivative of matrix by scalar.
    Uses vect_diff().
    '''
    res_mat = matrix(m.col_dim,m.row_dim,[])

    for col in m.columns:
        res_mat.columns.append(vect_diff(col,var))
    
    return res_mat
