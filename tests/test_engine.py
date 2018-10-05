import os
import yaml
import unittest
import pytest
import numpy as np
import pprint
from math import isclose
from blfuzzy import FuzzyInferenceEngine
from blfuzzy.engine import Rule, Variable, Antecedent, Consequent
from blfuzzy.constants import VALUE
from blfuzzy.constants import VARIABLES, NAME, LEVEL, CENTROID
from blfuzzy.constants import RULES, ANTECEDENT, CONSEQUENT
from blfuzzy.constants import OPERATOR, IMPLICATION
from blfuzzy.constants import AGGREGATION, DEFUZZIFICATION

HERE = os.path.dirname(__file__)
FILENAME = 'data.yaml'
PATHNAME = os.path.join(HERE, FILENAME)

pp = pprint.PrettyPrinter(width=200, compact=True)


class TestCases(unittest.TestCase):

    def setUp(self):
        with open(PATHNAME, 'r') as self.fd:
            self.data = yaml.load(self.fd)

    def test_variable_fully_specified(self):
        data = self.data[VARIABLES][0]
        variable = Variable(data)
        name = 'service'
        self.assertEqual(variable.name, name)
        x = np.array([0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10.])
        assert((variable.x == x).all())
        value = 3
        self.assertEqual(variable.value, value)
        mfs = {
            'poor': np.array(
                [1., 0.8, 0.6, 0.4, 0.2, 0., 0., 0., 0., 0., 0.]),
            'good': np.array(
                [0., 0.2, 0.4, 0.6, 0.8, 1., 0.8, 0.6, 0.4, 0.2, 0.]),
            'excellent': np.array(
                [0., 0., 0., 0., 0., 0., 0.2, 0.4, 0.6, 0.8, 1.])}
        for name, mf in mfs.items():
            variablemf = variable.mfs.get(name)
            self.assertIsNotNone(variablemf)
            assert((variablemf == mf).all())
        self.assertEqual(variable.fuzzy_values,
                         {'poor': None, 'good': None, 'excellent': None})
        self.assertIsNone(variable.aggrmf)
        variable.fuzzify('poor')
        variable.fuzzify('good')
        variable.fuzzify('excellent')
        self.assertEqual(variable.fuzzy_values['poor'], 0.4)
        self.assertEqual(variable.fuzzy_values['good'], 0.6)
        self.assertEqual(variable.fuzzy_values['excellent'], 0.0)

    def test_variable_minimally_specified(self):
        data = self.data['minimal_variable'][0]
        variable = Variable(data)
        name = 'tip'
        self.assertEqual(variable.name, name)
        x = np.array(
            [0., 2.5, 5., 7.5, 10., 12.5, 15., 17.5, 20., 22.5, 25.])
        assert((variable.x == x).all())
        value = None
        self.assertEqual(variable.value, value)
        mfs = {
            'cheap': np.array(
                [1., 0.8, 0.6, 0.4, 0.2, 0., 0., 0., 0., 0., 0.]),
            'average': np.array(
                [0., 0.2, 0.4, 0.6, 0.8, 1., 0.8, 0.6, 0.4, 0.2, 0.]),
            'generous': np.array(
                [0., 0., 0., 0., 0., 0., 0.2, 0.4, 0.6, 0.8, 1.])}
        for name, mf in mfs.items():
            variablemf = variable.mfs.get(name)
            self.assertIsNotNone(variablemf)
            assert((variablemf == mf).all())
        variable.aggrmf = mfs['cheap']
        expect = 4.166666666666667
        variable.defuzzify(CENTROID)
        assert(isclose(variable.value, expect))
        method = 'rubbish'
        with pytest.raises(ValueError) as excinfo:
            variable.value = None
            variable.defuzzify(method)
        exception = excinfo.value
        msg = 'The input for `mode`, {}, was incorrect.'.format(method)
        self.assertEqual(str(exception), msg)

    def test_variable_input_value(self):
        data = self.data[VARIABLES][0]
        variable = Variable(data)
        value = 0.0
        variable.input_value(value)
        self.assertEqual(variable.value, value)
        value = 10.0
        variable.input_value(value)
        self.assertEqual(variable.value, value)
        with pytest.raises(ValueError) as excinfo:
            value = -0.0000001
            variable.input_value(value)
        exception = excinfo.value
        self.assertEqual(str(exception), '{} out of range'.format(value))
        with pytest.raises(ValueError) as excinfo:
            value = 10.0000001
            variable.input_value(value)
        exception = excinfo.value
        self.assertEqual(str(exception), '{} out of range'.format(value))

    def test_antecedent(self):
        data = self.data[VARIABLES]
        variables = FuzzyInferenceEngine.input_variables(data)
        rule = self.data[RULES][0]
        antecedent = Antecedent(rule[ANTECEDENT], variables)
        self.assertEqual(antecedent.operator_type, rule[ANTECEDENT][OPERATOR])
        # for varname, variable in variables.items():
        #    assert(antecedent.variables[varname] is variable)
        levels = antecedent.levels
        self.assertEqual(len(levels), len(rule[ANTECEDENT][VARIABLES]))
        for item in rule[ANTECEDENT][VARIABLES]:
            varname = item[NAME]
            self.assertEqual(levels[varname], item[LEVEL])
        self.assertIsNone(antecedent.result)
        antecedent.evaluate()
        service = variables['service']
        food = variables['food']
        self.assertEqual(service.fuzzy_values['poor'], 0.4)
        self.assertEqual(food.fuzzy_values['rancid'], 0.0)

    def test_consequent(self):
        data = self.data[VARIABLES]
        variables = FuzzyInferenceEngine.input_variables(data)
        rule = self.data[RULES][0]
        consequent = Consequent(rule[CONSEQUENT], variables)
        self.assertEqual(consequent.implication_type,
                         rule[CONSEQUENT][IMPLICATION])
        # for varname, variable in variables.items():
        #    assert(consequent.variables[varname] is variable)
        levels = consequent.levels
        self.assertEqual(len(levels), len(rule[CONSEQUENT][VARIABLES]))
        for item in rule[CONSEQUENT][VARIABLES]:
            varname = item[NAME]
            self.assertEqual(levels[varname], item[LEVEL])
        self.assertEqual(consequent.result, {'tip': None})
        antecedent = 0.4
        consequent.evaluate(antecedent)
        expect = np.array(
            [0.4, 0.4, 0.4, 0.4, 0.2, 0., 0., 0., 0., 0., 0.])
        assert((consequent.result['tip'] == expect).all())

    def test_rule(self):
        data = self.data[VARIABLES]
        variables = FuzzyInferenceEngine.input_variables(data)
        rule = self.data[RULES][0]
        antecedent = Antecedent(rule[ANTECEDENT], variables)
        data = self.data[VARIABLES]
        variables = FuzzyInferenceEngine.input_variables(data)
        consequent = Consequent(rule[CONSEQUENT], variables)
        rule = Rule(antecedent, consequent)
        rule.evaluate()
        expect = np.array(
            [0.4, 0.4, 0.4, 0.4, 0.2, 0., 0., 0., 0., 0., 0.])
        assert((consequent.result['tip'] == expect).all())

    def test_fuzzy_inference_engine(self):
        engine = FuzzyInferenceEngine(self.data)
        self.assertEqual(engine.aggregation, self.data[AGGREGATION])
        self.assertEqual(engine.defuzzification, self.data[DEFUZZIFICATION])
        # keys = []
        # for item in self.data[INPUT]: keys.append(item[NAME])
        # self.assertEqual(list(engine.input.keys()), keys)
        keys = []
        for item in self.data[VARIABLES]:
            if item[VALUE] is None:
                keys.append(item[NAME])
        output = engine.get_output_variables()
        self.assertEqual(list(output.keys()), keys)
        engine.run()
        expect = 13.348484848484848
        self.assertEqual(output['tip'].value, expect)
        value = engine.get_variable_value('food')
        self.assertEqual(value, 8)
        pp.pprint(engine.as_dict())
        # assert(False)

    def tearDown(self):
        self.fd.close()


if __name__ == '__main__':
    unittest.main()
