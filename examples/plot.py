import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.rcsetup as rcsetup # backend information

#sys.path.append('..') # so that Python can find the package from this location
from blfuzzy.helper import get_var_range
from blfuzzy.constants import MIN, MAX
from blfuzzy.constants import MF
from blfuzzy.helper import aggregate

NAME = 'name'
LEVELS = 'levels'
COLORS = ['b', 'g', 'r', 'c', 'm', 'k']
LINEWIDTH = 1.5

def list_available_backends():
    """
    Displays list of backends available to your system.
    """
    print(rcsetup.all_backends)

def membership_functions(variables):
    """
    Plots the membership functions of the variables.
    :param variables: (list) list of variables with their specifications
    """
    n = len(variables)
    fig, ax = plt.subplots(nrows=n, figsize=(8, 3 * n))

    # configure plots
    for i in range(n):
        variable = variables[i]
        x = get_var_range(variable[MIN], variable[MAX])
        sets = variable[LEVELS]
        for j in range(len(sets)):
            set_name = sets[j][NAME]
            fuzzy_set_spec = sets[j]
            mf = fuzzy.get_var_mf(variable, fuzzy_set_spec)
            color_index = j % len(COLORS) # circular index
            ax[i].plot(x, mf, COLORS[j], linewidth=LINEWIDTH, label=set_name)
        ax[i].set_title(variable[NAME])
        ax[i].legend()
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['right'].set_visible(False)
        ax[i].get_xaxis().tick_bottom()
        ax[i].get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()

def plot_variable_mfs(engine, varname, pathname):
    """
    Plots the membership functions of the variable.
    :param engine: (FuzzyInferenceEngine) engine with variables
    :param varname: (str) name of variable
    """
    variable = engine.get_input_variables().get(varname)
    if variable is None: variable = engine.get_output_variables().get(varname)
    x = variable.x
    z = np.zeros_like(x)
    n = len(variable.mfs) + 1
    fig, ax = plt.subplots(figsize=(8, 3))
    aggrmf = variable.aggrmf
    for i, (levelname, mf) in enumerate(variable.mfs.items()):
        color = COLORS[i]
        if variable.aggrmf is not None:
            ax.fill_between(x, z, variable.aggrmf, facecolor=color, alpha=0.7)
        ax.plot(x, mf, color, linewidth=0.5, linestyle='--')
    value = variable.value
    ax.plot([value, value], [0, 1], 'k', linewidth=1.5, alpha=0.9)

    ax.set_title(variable.name)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.tight_layout()
    #plt.show()
    fig.savefig(pathname)
    plt.close()
