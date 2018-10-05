#! /usr/bin/env python

import json
import yaml
import pprint
import sys, os

import plot
from tippinghelper import get_command_line_args, read_yaml_file, write_json_file

from blfuzzy import FuzzyInferenceEngine
from blfuzzy import get_rules_from_excel
from blfuzzy import get_variables_from_excel
from blfuzzy import get_default_mf_params
from blfuzzy import VARIABLES, MIN, MAX, LEVELS, AVERAGE
from blfuzzy import RULES, AGGREGATION, DEFUZZIFICATION, OR, CENTROID
from blfuzzy import get_var_range

pp = pprint.PrettyPrinter(width = 200, compact=True)

args = get_command_line_args()

data = read_yaml_file(args.spec_pathname)
pp.pprint(data)

varname = 'tip'
try:
    engine = FuzzyInferenceEngine(data, missing_values=False)
    engine.run()
except ValueError as e:
    print('Program terminated: {}'.format(e))
    exit()

expect = 19.868717948717951
msg = 'pasting scikit-fuzzy website code into ipython gives {}'.format(expect)
print(msg)
output_variables = engine.get_output_variables()
print('our result for tip = {}'.format(output_variables[varname].value))

if args.plot: plot.plot_variable_mfs(engine, varname, '{}.png'.format(varname))
if args.plot: plot.plot_variable_mfs(engine, 'food', '{}.png'.format('food'))
if args.plot: plot.plot_variable_mfs(engine, 'service', '{}.png'.format('service'))
