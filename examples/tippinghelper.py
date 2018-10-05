import os
import sys
import json
import yaml
import math
import argparse
import textwrap
import numpy as np
import pandas as pd

from blfuzzy import FuzzyInferenceEngine
from blfuzzy.constants import NAME, OPERATOR, TRIANGLE, MF_TYPE, MF_PARAMS
from blfuzzy.constants import VALUE, MIN, MAX, LEVEL, LEVELS, AND, OR, SUM
from blfuzzy.constants import VARIABLES, IMPLICATION, AGGREGATION, WEIGHT
from blfuzzy.constants import RULES, ANTECEDENT, CONSEQUENT

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

AGGREGATION_TYPES = {OR, SUM}

def get_command_line_args():
    """
    Handles command-line arguments.
    :returns: (Namespace) processed command-line arguments
    """
    DESCRIPTION = 'Performs fuzzy inference'
    parser = argparse.ArgumentParser(
            description = DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog = textwrap.dedent('''\
            Example Usage
            -------------
            python %(prog)s tipping.yaml
            '''))
    parser.add_argument('spec_pathname', metavar = '<pathname>',
            help='pathname to specification file',
            action=ValidateFileAction)
    parser.add_argument('--debug',
            help='print debug messages', action='store_true')
    parser.add_argument('--plot',
            help='plot membership functions', action='store_true')
    parser.add_argument('--aggr', default=SUM,
            help='specifies aggregation method',
            action=ValidateAggregationAction)
    return parser.parse_args()

class ValidateFileAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ValidateFileAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        pathname = values
        if not os.path.isfile(pathname):
            raise ValueError('{} is not a regular file'.format(pathname))
        setattr(namespace, self.dest, pathname)

class ValidateAggregationAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ValidateAggregationAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        aggregation = values
        if aggregation not in AGGREGATION_TYPES:
            msg = 'invalid aggregation type "{}"; valid types: {}'.format(
                    aggregation, AGGREGATION_TYPES)
            raise ValueError(msg)
        setattr(namespace, self.dest, aggregation)

def read_yaml_file(pathname):
    """Reads yaml file into dict.
    :param pathname: (string) file pathname to yaml file
    :returns: (dict) parsed yaml into dictionary
    """
    with open(pathname, 'r') as fd: return yaml.load(fd)

def write_json_file(pathname, data):
    """Stores dict as json to file.
    :param pathname: (string) pathname to file
    :param data: (dict) json data
    """
    with open(pathname, 'w') as fd: json.dump(data, fd)

def get_variables_definitions(df):
    """Read variables definitions from csv file. The actual variable value, for
    each node, will be read later.
    :param df: (dataframe) values for variables (column) for all nodes (rows)
    :returns: (list) of dictionaries
    """
    ret = []
    for name, values in df.iteritems():
        xmin = np.amin(values)
        if math.isnan(xmin): xmin = 0 # default if not specified
        xmax = np.amax(values)
        if math.isnan(xmax): xmax = 1 # default if not specified
        if math.isclose(xmin, xmax, abs_tol=0.00001):
            xmin = xmin * 0.95 # stretch by 5%
            xmax = xmax * 1.05 # stretch by 5%
            if xmax == 0.0: xmax = 1.0 # when all values == 0
        levels = make_levels('LMH')
        ret.append({NAME: name, MIN: xmin, MAX: xmax, LEVELS: levels})
    return ret

def check_nan(value):
    """Returns None if value is nan, otherwise returns the value.
    :param value: (float) value
    :returns: None or value
    """
    if type(value) is str: return value
    return None if math.isnan(value) else value

def make_levels(codes):
    """Parses level codes and constructs list of levels.
    :param codes: (str) LMH for low, medium, high
    """
    ret = []
    for c in codes:
        ret.append({NAME: EXCEL_LEVELS[c], MF_TYPE: None, MF_PARAMS: None})
    return ret

def get_rules_definitions(pathname, sheet):
    """Parses rule definitions from Excel spreadsheet.
    :param pathname: (str) path to Excel file
    :param sheet: (str) name of Excel worksheet
    :returns: (list) of rules
    """
    df = pd.read_excel(pathname, sheetname=sheet)
    ret = []
    for i in range(len(df.index)):
        varnames = list(df.columns)[:-1]
        antecedent = get_antecedent_from_row(df, i, varnames)
        if antecedent is None: continue # no antecedent variables found
        varnames = [list(df.columns)[-1]]
        consequent = get_consequent_from_row(df, i, varnames)
        ret.append({WEIGHT: 1, ANTECEDENT: antecedent, CONSEQUENT: consequent})
    return ret

def get_antecedent_from_row(df, i, varnames, operator=AND):
    """
    """
    variables = []
    for name in varnames:
        level = check_nan(df.iloc[i][name])
        if level is None: continue # if Excel cell empty, variable not in rule
        variables.append({NAME: name, LEVEL: EXCEL_LEVELS[level]})
    if not variables: return None
    return {OPERATOR: operator, VARIABLES: variables}

def get_consequent_from_row(df, i, varnames, implication=MIN):
    """
    """
    variables = []
    for name in varnames:
        level = df.iloc[i][name]
        variables.append({NAME: name, LEVEL: EXCEL_LEVELS[level]})
    return {IMPLICATION: implication, VARIABLES: variables}

def set_variables_values_for_node(data, df, nodename):
    for variable in data[VARIABLES]:
        variable[VALUE] = check_nan(df.loc[nodename, variable[NAME]])

def update_df_variables_values(df, varname, nodes):
    for nodename, node in nodes.items():
        df.loc[nodename, varname] = node[varname].get_variable_value(varname)
