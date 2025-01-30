from expression import *
import numpy as np
from matplotlib import pyplot as plt
from derivatives import *
from evaluation import *
from vectors import *

def myplot(term: myexpr, domain: list, var: str, format = 'b-', **kwargs):
    '''
    Wrapper for plt.plot
    '''
    vals = []
    for i in domain:
        vals.append(calc_eval(term,{var: i}))
    
    plt.plot(domain,vals,format, label = term.str, **kwargs)
    plt.xlabel(var)
    plt.legend()
    plt.show()
    
    return 0

def myscatter(term: myexpr, domain: list, var: str, marker = 'o', alpha = 1, **kwargs):
    '''
    Wrapper for plt.scatter
    '''
    vals = []
    for i in domain:
        vals.append(calc_eval(term,{var: i}))
    
    plt.scatter(domain,vals, marker = marker, alpha = alpha, label = term.str, **kwargs)
    plt.xlabel(var)
    plt.legend()
    plt.show()

    return 0

def my3Dsurface(function: myexpr, domain: dict):
    '''
    Wrapper for plt.plot_trisurf (triangulated surface).
    function is a function R^2 -> R
    domain is a dictionary of two variables as keys
    and two lists as their values, which are the corresponding domains.
    Only works with square domains.
    '''
    #extract the variables
    x = list(domain.keys())[0]
    y = list(domain.keys())[1]

    if len(domain[x]) != len(domain[y]):
        return 'The domains do not match. Please provide equal length lists.'
    
    #grid setup for domain
    x_temp = np.array(domain[x])
    y_temp = np.array(domain[y])

    x_vals, y_vals = np.meshgrid(x_temp,y_temp)
    x_vals = x_vals.flatten()
    y_vals = y_vals.flatten()
    
    #create list of points at which function is to be evaluated
    eval_values = [{x: x_vals[i], y: y_vals[i]} for i in range(len(x_vals))]

    #evaluate the function on the given domains
    z_vals = np.array([calc_eval(function, vals) for vals in eval_values])

    #matplotlib.pyplot setup
    ax = plt.figure().add_subplot(projection='3d')

    ax.plot_trisurf(x_vals, y_vals, z_vals.flatten(), linewidth=0.2, antialiased=True)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(function.str)
   
    plt.show()
    return 0

def myvectfield2D(vect_field: vect, domain: dict, **kwargs):
    '''
    Wrapper for plt.quiver.
    Domain is a dict of the form {'variable': list of vlaues for its domain}.
    '''
    #extract the variables
    x = list(domain.keys())[0]
    y = list(domain.keys())[1]

    #grid set-up for domain
    x_vals, y_vals = np.meshgrid(np.array(domain[x]),np.array(domain[y]))
        
    #create list of points at which vector is to be evaluated
    eval_values = [{x: x_vals[i][j], y: y_vals[i][j]} for i in range(len(domain[y])) for j in range(len(domain[x]))]
    
    #evaluate the vector on the given domains
    z_vals = [vect_eval(vect_field, vals) for vals in eval_values]

    #read out component values
    u = np.array([np.array([z_vals[len(domain[y])*i + j].components[0].worth(0) for j in range(len(domain[y]))]) for i in range(len(domain[x]))])
    v = np.array([np.array([z_vals[len(domain[y])*k + l].components[1].worth(0) for l in range(len(domain[y]))]) for k in range(len(domain[x]))])

    plt.quiver(x_vals,y_vals,u,v,**kwargs)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.show()

    return 0

def myvectfield3D(v_field: vect, domain: dict, **kwargs):
    '''
    3D analogue of myvectfield2D().
    '''
    #extract the variables
    x = list(domain.keys())[0]
    y = list(domain.keys())[1]
    z = list(domain.keys())[2]

    #grid set-up for the domain
    x_vals, y_vals, z_vals = np.meshgrid(np.array(domain[x]), np.array(domain[y]), np.array(domain[z]))

    #create list of points at which the vector is to be evaluated
    eval_values = [{x: x_vals[i][j][k], y: y_vals[i][j][k], z: z_vals[i][j][k]} for i in range(len(domain[y])) for j in range(len(domain[x])) for k in range(len(domain[z]))]

    #evaluate vector
    v_vals = [vect_eval(v_field, vals) for vals in eval_values]

    #read out component values
    u = np.array([np.array([np.array([v_vals[len(domain[x])*len(domain[z])*l + len(domain[z])*k + j].components[0].worth(0) for j in range(len(domain[z]))]) for k in range(len(domain[x]))]) for l in range(len(domain[y]))])
    v = np.array([np.array([np.array([v_vals[len(domain[x])*len(domain[z])*l + len(domain[z])*k + j].components[1].worth(0) for j in range(len(domain[z]))]) for k in range(len(domain[x]))]) for l in range(len(domain[y]))])
    w = np.array([np.array([np.array([v_vals[len(domain[x])*len(domain[z])*l + len(domain[z])*k + j].components[2].worth(0) for j in range(len(domain[z]))]) for k in range(len(domain[x]))]) for l in range(len(domain[y]))]) 

    #plot
    ax = plt.figure().add_subplot(projection='3d')
    ax.quiver(x_vals,y_vals,z_vals,u,v,w,length=0.1,normalize=True,**kwargs)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    
    plt.show()

    return 0