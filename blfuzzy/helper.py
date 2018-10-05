import math
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from blfuzzy.constants import TRIANGLE, OR, AND, MIN, MAX, SUM, AVERAGE
from blfuzzy.constants import NAME, VALUE, LEVEL, LEVELS, WEIGHT
from blfuzzy.constants import MF_TYPE, MF_PARAMS
from blfuzzy.constants import ANTECEDENT, CONSEQUENT, OPERATOR, IMPLICATION
from blfuzzy.constants import DEFAULT_MF_TYPE, INTERVALS, VARIABLES

DEFAULT_MFS = {
        TRIANGLE: [
            [
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 1.0]
            ],
            [
                [0.0, 0.0, 0.5],
                [0.0, 0.5, 1.0],
                [0.5, 1.0, 1.0]
            ],
            [
                [0.0, 0.0, 0.333],
                [0.0, 0.333, 0.666],
                [0.333, 0.666, 1.0],
                [0.666, 1.0, 1.0]
            ],
            [
                [0.0, 0.0, 0.25],
                [0.0, 0.25, 0.5],
                [0.25, 0.5, 0.75],
                [0.5, 0.75, 1.0],
                [0.75, 1.0, 1.0]
            ]
        ]
}

EXCEL_LEVELS = {'H': 'high', 'M': 'medium', 'L': 'low'}


def get_default_mf_params(xmin, xmax, levels, index, mf_type=DEFAULT_MF_TYPE):
    """Get default membership function params for variable level.
    :param xmin: (float) variable lowest possible value
    :param xmax: (float) variable highest possible value
    :param levels: (int) number of variable fuzzy levels (e.g., low, high)
    :param index: (int) index to level (levels go from low - high)
    :param mf_type: (str) type of membership function (e.g., triangle, square)
    :returns: (ndarray) 1d array representation of membership function
    """
    unit_params = get_default_mf_unit_params(levels, index, mf_type)
    return map_0_1_range_to_arbitrary_range(xmin, xmax, unit_params)


def get_default_mf_unit_params(levels, levelindex, mf_type):
    """Gets default membership function params from file.
    :param levels: (int) number of levels
    :param levelindex: (int) index into level
    :param mf_type: (str) type of membership function (e.g., triangle, square)
    :returns: 1d array representation of membership function on (0-1) domain
    """
    defaults = DEFAULT_MFS
    return np.asarray(defaults[mf_type][levels - 2][levelindex])


def map_0_1_range_to_arbitrary_range(xmin, xmax, array):
    """Maps values in [0-1] array to values in [xmin, xmax] domain.
    :param xmin: (float) lowest possible value
    :param xmax: (float) highest possible value
    :param array: (ndarray) array in [0-1] domain
    :returns: (ndarray) 1d array in [xmin, xmax] domain
    """
    slope = xmax - xmin
    return xmin + np.multiply(array, slope)


def get_var_range(xmin, xmax, n=INTERVALS):
    """Generate array of values between min and max, for use by membership
    functions.
    :param n: (int) number of intervals in resulting array
    :param xmin: (float) lowest variable value possible
    :param xmax: (float) highest variable value possible
    :returns: (ndarray) 1d array of 'n' evenly spaced intervals in [min, max]
    """
    if not xmax > xmin:
        raise ValueError('min >= max')
    step = (xmax - xmin) / n
    # if step > 1: step = 1 # resolution no less than 1
    return np.arange(xmin, xmax + step, step)


def get_variables_from_excel(pathname, sheet):
    """Parses variable data.
    :param pathname: (str) path to Excel file
    :param sheet: (str) name of Excel worksheet
    """
    ret = []
    df = pd.read_excel(pathname, sheetname=sheet)
    for index, row in df.iterrows():
        name = row[NAME]
        xmin = check_nan(row[MIN])
        xmax = check_nan(row[MAX])
        value = check_nan(row[VALUE])
        levels = make_levels(row[LEVELS])
        var = {NAME: name, MIN: xmin, MAX: xmax, VALUE: value, LEVELS: levels}
        ret.append(var)
    return ret


def check_nan(value):
    """Returns None if value is nan, otherwise returns the value.
    :param value: (float) value
    :returns: None or value
    """
    if type(value) is str:
        return value
    return None if math.isnan(value) else value


def make_levels(codes):
    """Parses level codes and constructs list of levels.
    :param codes: (str) LMH for low, medium, high
    """
    ret = []
    for c in codes:
        ret.append({NAME: EXCEL_LEVELS[c], MF_TYPE: None, MF_PARAMS: None})
    return ret


def get_rules_from_excel(pathname, sheet, ante_nvars, cons_nvars):
    """Parses rule definitions from Excel spreadsheet.
    :param pathname: (str) path to Excel file
    :param sheet: (str) name of Excel worksheet
    :param ante_nvars: (int) number of antecedent variables to expect
    :param cons_nvars: (int) number of consequent variables to expect
    :returns: (list) of rules
    """
    df = pd.read_excel(pathname, sheetname=sheet)
    ante_vars = set()
    for i in range(ante_nvars):
        ante_vars.add(df.columns[i])
    cons_vars = set()
    for i in range(cons_nvars):
        cons_vars.add(df.columns[ante_nvars + i])
    ret = []
    rows = len(df.index)
    for i in range(rows):
        antecedent = get_antecedent_from_row(df, i, ante_vars)
        consequent = get_consequent_from_row(df, i, cons_vars)
        ret.append({WEIGHT: 1, ANTECEDENT: antecedent, CONSEQUENT: consequent})
    return ret


def get_antecedent_from_row(df, i, varnames, operator=AND):
    """
    """
    variables = []
    for name in varnames:
        level = check_nan(df.iloc[i][name])
        if level is None:
            continue  # if Excel cell empty, variable not in rule
        variables.append({NAME: name, LEVEL: EXCEL_LEVELS[level]})
    return {OPERATOR: operator, VARIABLES: variables}


def get_consequent_from_row(df, i, varnames, implication=MIN):
    """
    """
    variables = []
    for name in varnames:
        level = df.iloc[i][name]
        variables.append({NAME: name, LEVEL: EXCEL_LEVELS[level]})
    return {IMPLICATION: implication, VARIABLES: variables}


def get_mf(x, levels, level, index):
    """Returns the membership function for the variable fuzzy level,
    as specified in the level data. If not specified, a default membership
    function is returned. Assumes levels are ordered from low to high.
    :param x: (ndarray) variable description: 1d array evenly spaced values
    :params levels: (int) number of levels
    :param level: (dict) level specification: name, mf type, mf params
    :param index: (int) determines the level position within the levels
    :returns: (ndarray) membership function description: 1d array
    """
    typename = level.get(MF_TYPE)
    if typename is None:
        typename = TRIANGLE
    params = level.get(MF_PARAMS)
    if params is None:
        xmin = x[0]
        xmax = x[-1]
        params = get_default_mf_params(xmin, xmax, levels, index, typename)
    if typename == TRIANGLE:
        return fuzz.trimf(x, params)
    assert(False)  # work in progress


def get_implication(typename):
    """
    :param typename: (str) implication type
    """
    if typename == MIN:
        return np.fmin
    assert(False)  # work in progress


def operate(operands, typename):
    """
    :param operands: (list) of float
    :param typename: (str) operator type
    :returns: (float) result
    """
    ret = operands[0]
    if len(operands) < 2:
        return ret
    if typename == OR:
        fn = np.fmax
    if typename == AND:
        fn = np.fmin
    for operand in operands[1:]:
        ret = fn(ret, operand)
    return ret


def aggregate(mfs, method=OR):
    """
    """
    if method == OR:
        return aggregate_or(mfs)
    if method == SUM:
        return aggregate_sum(mfs)
    if method == AVERAGE:
        return aggregate_average(mfs)


def aggregate_or(mfs):
    """
    :param mfs: (list) of membership functions (1darray)
    :returns: (1darray) aggregated membership function
    """
    assert(mfs)
    ret = 0
    for mf in mfs:
        ret = np.fmax(ret, mf)
    return ret


def aggregate_sum(mfs):
    """
    :param mfs: (list) of membership functions (1darray)
    :returns: (1darray) aggregated membership function
    """
    return np.sum(mfs, axis=0)


def aggregate_average(mfs):
    """
    :param mfs: (list) of membership functions (1darray)
    :returns: (1darray) aggregated membership function
    """
    return np.average(mfs, axis=0)
