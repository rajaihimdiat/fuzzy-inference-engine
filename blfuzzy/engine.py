import skfuzzy as fuzz
from math import isclose
from blfuzzy.constants import NAME, MIN, MAX, VALUE, LEVELS, LEVEL, WEIGHT
from blfuzzy.constants import VARIABLES, RULES, AGGREGATION, DEFUZZIFICATION
from blfuzzy.constants import OPERATOR, IMPLICATION, ANTECEDENT, CONSEQUENT
from blfuzzy.constants import X, FUZZY_VALUES, AGGRMF
from blfuzzy import helper
from blfuzzy.helper import get_var_range, operate, get_mf, get_implication


class FuzzyInferenceEngine(object):
    """This implementation is based on the Mamdani fuzzy inference method.
    :attr aggregation: (str) name membership function aggregation method
    :attr defuzzification: (str) name of defuzzification method
    :attr rules: (list) rule object (Rule)
    """

    def __init__(self, data, missing_values=False):
        """
        :param data: (dict) specification of system and input values
        :param missing_values: (boolean) compute with missing values
        """
        self.aggregation = data[AGGREGATION]
        self.defuzzification = data[DEFUZZIFICATION]
        self.rules = self.input_rules(data)
        if missing_values is False:
            self.check_missing_values()

    def as_dict(self):
        variables = {}
        _vars = {**self.get_input_variables(), **self.get_output_variables()}
        for varname, variable in _vars.items():
            variables[varname] = variable.as_dict()
        rules = []
        for rule in self.rules:
            rules.append(rule.as_dict())
        return {VARIABLES: variables,
                RULES: rules,
                AGGREGATION: self.aggregation,
                DEFUZZIFICATION: self.defuzzification}

    @classmethod
    def input_variables(self, data):
        """Sets the variable object to input.
        :param data: (list) variable data (dict)
        :returns: (dict) variable name (str) -> variable object (Variable)
        """
        ret = {}
        for variable in data:
            ret[variable[NAME]] = Variable(variable)
        return ret

    def input_rules(self, data):
        """Creates the variables and rules. The rules will point to the
        variable objects in antecedent and consequent.
        :param data: (list) of rule data
        :returns: (list) rules objects (Rule)
        """
        variables = self.input_variables(data[VARIABLES])
        ret = []
        for ruledata in data[RULES]:
            antecedent = Antecedent(ruledata[ANTECEDENT], variables)
            consequent = Consequent(ruledata[CONSEQUENT], variables)
            weight = ruledata[WEIGHT]
            ret.append(Rule(antecedent, consequent, weight))
        return ret

    def check_missing_values(self):
        """Checks that input variables have values.
        :raises ValueError: some input variable has no value
        """
        for rule in self.rules:
            for varname, variable in rule.antecedent.variables.items():
                if variable.value is None:
                    raise ValueError('"{}" has no value'.format(variable.name))

    def run(self):
        """Perform fuzzy inference.
            1) evaluete each rule
            2) aggregate all rules' results (implicated membership functions)
            3) defuzzify aggregated membership function to obtain crisp value
        """
        for rule in self.rules:
            rule.evaluate()
        self.aggregate()
        self.defuzzify()

    def aggregate(self):
        """Aggregates all implicated membership functions into one resulting mf.
        """
        variables = self.get_output_variables()
        for varname, variable in variables.items():
            imfs = []
            for rule in self.rules:
                imf = rule.consequent.result[varname]
                if imf is not None:
                    imfs.append(rule.consequent.result[varname])
            variable.aggrmf = helper.aggregate(imfs, self.aggregation)

    def defuzzify(self):
        """Defuzzifies all output variables' implicated membership functions.
        """
        variables = self.get_output_variables()
        for varname, variable in variables.items():
            variable.defuzzify(self.defuzzification)

    def get_input_variables(self):
        """Returns references to input variables.
        Not all rules include all variables, so need to inspect all rules.
        :returns: (dict) variable name (str) -> variable object (Variable)
        """
        ret = {}
        for rule in self.rules:
            for varname, variable in rule.antecedent.variables.items():
                ret[varname] = variable
        return ret

    def get_output_variables(self):
        """Returns references to output variables (usually, only one variable).
        :returns: (dict) variable name (str) -> variable object (Variable)
        """
        return next(iter(self.rules)).consequent.variables

    def get_variable_value(self, varname):
        input_vars = self.get_input_variables()
        output_vars = self.get_output_variables()
        var = input_vars.get(varname)
        if var is not None:
            return var.value
        var = output_vars.get(varname)
        if var is not None:
            return var.value
        raise ValueError('"{}" not found'.format(varname))


class Variable(object):
    """Variable object.
    :attr name: (str) variable name
    :attr x: (ndarray) variable range: 1d array of evenly spaced values
    :attr value: (float) value
    :attr mfs: (dict) level name (str) -> memebership function (ndarray)
    :attr fuzzy_values: (dict) level name (str) -> fuzzy value (float)
    :attr aggrmf: (ndarray) aggregated membership function resulting from rules
    """

    def __init__(self, data):
        """
        """
        self.name = data[NAME]
        self.input_range(data)
        self.input_value(data[VALUE])
        self.mfs = self.input_levels(data[LEVELS])
        self.fuzzy_values = self.init_fuzzy_values()
        self.aggrmf = None

    def __str__(self):
        return str(self.as_dict())

    def as_dict(self):
        return {
                NAME: self.name,
                X: self.x.tolist(),
                VALUE: self.value,
                LEVELS: self.mfs,
                FUZZY_VALUES: self.fuzzy_values,
                AGGRMF: None if self.aggrmf is None else self.aggrmf.tolist()}

    def input_range(self, data):
        """Input or compute variable range and validate.
        :param data: (dict) variable data
        """
        x = data.get(X)
        if x:
            self.x = x
            current = self.x[0]
            for nextval in self.x[1:]:
                if nextval <= current:
                    raise ValueError('{} not increasing'.format(self.x))
                current = nextval
        else:
            self.x = get_var_range(data[MIN], data[MAX])

    def input_value(self, value):
        """Input value and verify it is within range.
        :param value: (float) input value
        """
        assert(self.x is not None)
        if value is not None:
            if not isclose(value, self.x[0]):
                if not isclose(value, self.x[-1]):
                    if value < self.x[0] or value > self.x[-1]:
                        raise ValueError('{} out of range'.format(value))
            # when the min/max is computed from data, the value, if happens to
            # be min/max, might be slightly off due to rounding.
            if isclose(value, self.x[0]):
                self.value = self.x[0]
            elif isclose(value, self.x[-1]):
                self.value = self.x[-1]
            else:
                self.value = value
        else:
            self.value = value

    def input_levels(self, data):
        """Input level names and assign membership functions to levels.
        :param data: (list) of level data
        :returns: (dict) levelname (str) -> mf (ndarray)
        """
        assert(self.x is not None)
        ret = {}
        n = len(data)
        for i, level in enumerate(data):
            ret[level[NAME]] = get_mf(self.x, n, level, i)
        return ret

    def init_fuzzy_values(self):
        ret = {}
        for levelname, mf in self.mfs.items():
            ret[levelname] = None
        return ret

    def get_fuzzy_value(self, level):
        fuzzy_value = self.fuzzy_values.get(level)
        if fuzzy_value is not None:
            return fuzzy_value
        self.fuzzify(level)
        return self.fuzzy_values[level]

    def fuzzify(self, level):
        """Convert the crisp value of the variable to a degree of membership
        for a given fuzzy set (level).
        :param level: (str) level name
        """
        value = self.value
        if value is None:
            return
        mf = self.mfs.get(level)
        assert(mf is not None)
        assert(self.x is not None)
        assert(value >= self.x[0] and value <= self.x[-1])
        self.fuzzy_values[level] = fuzz.interp_membership(self.x, mf, value)

    def defuzzify(self, method):
        """Compute crisp value from aggregated membership function.
        :param method: (str) name of defuzzification method
        """
        assert(not self.value)
        assert(self.aggrmf is not None)
        self.value = fuzz.defuzz(self.x, self.aggrmf, method)


class Rule(object):
    """Rule definition.
    :attr weight: (float) rule importance (0-1)
    :attr antecedent: (Antecedent) rule antecedent: operator, variable levels
    :attr consequent: (Consequent) rule consequent: implication, variable
                      levels
    """

    def __init__(self, antecedent, consequent, weight=1.0):
        """
        """
        self.weight = weight
        self.antecedent = antecedent
        self.consequent = consequent

    def as_dict(self):
        return {ANTECEDENT: self.antecedent.as_dict(),
                CONSEQUENT: self.consequent.as_dict()}

    def evaluate(self):
        """Evaluates the rule and sets the implicated mfs for each variable.
        """
        self.antecedent.evaluate()
        if self.antecedent.result is not None:
            self.consequent.evaluate(self.antecedent.result * self.weight)


class Antecedent(object):
    """Antecedent of a fuzzy rule.
    :attr operator_type: (str) operator type
    :attr variables: (dict) variable name (str) -> variable object (Variable)
    :attr levels: (dict) variable name (str) -> fuzzy level (str)
    :attr result: (float) fuzzy value
    """

    def __init__(self, data, variables):
        """
        :param data: (dict) antecedent data
        :param variables: (dict) input variables
        """
        self.operator_type = data[OPERATOR]
        self.variables = self.input_var_references(data[VARIABLES], variables)
        self.levels = self.input_levels(data[VARIABLES])
        self.result = None

    def as_dict(self):
        ret = {}
        ret['operator_type'] = self.operator_type
        ret['variables'] = self.levels
        ret['fuzzy_values'] = {}
        for varname, variable in self.variables.items():
            ret['fuzzy_values'][varname] = variable.fuzzy_values[
                self.levels[varname]]
        ret['result'] = self.result
        return ret

    @classmethod
    def input_var_references(self, data, variables):
        """
        :param data: (list) of dict: variable name (str) -> level name (str)
        :param variables: (dict) input variables
        """
        ret = {}
        for vardata in data:
            varname = vardata[NAME]
            ret[varname] = variables[varname]
        return ret

    def input_levels(self, data):
        """
        :param data: (list) of dict: variable name (str) -> level name (str)
        """
        ret = {}
        for vardata in data:
            ret[vardata[NAME]] = vardata[LEVEL]
        return ret

    def evaluate(self):
        """Computes antecendent: A single fuzzy value resulting from combining
        the fuzzy values of the operands.
        """
        assert(not self.result)  # should only be called once
        fuzzy_values = []
        for varname, var in self.variables.items():
            level = self.levels[varname]
            fuzzy_value = var.get_fuzzy_value(level)
            if fuzzy_value is None:  # cannot evaluate rule; remains None
                return
            fuzzy_values.append(fuzzy_value)
        self.result = operate(fuzzy_values, self.operator_type)


class Consequent(object):
    """Consequent of a fuzzy rule.
    :attr implication_type: (str) implication method
    :attr variables: (dict) variable name (str) -> variable object (Variable)
    :attr levels: (dict) variable name (str) -> fuzzy level (str)
    :attr result: (dict) variable name (str) -> implicated mf (ndarray)
    """

    def __init__(self, data, variables):
        """
        :param data: (dict) consequent data
        :param variables: (dict) output variables
        """
        self.implication_type = data[IMPLICATION]
        self.variables = self.input_var_references(data[VARIABLES], variables)
        self.levels = self.input_levels(data[VARIABLES])
        self.result = self.init_result()

    def as_dict(self):
        ret = {}
        ret['implication_type'] = self.implication_type
        ret['variables'] = self.levels
        ret['result'] = {}
        for varname, imf in self.result.items():
            ret['result'][varname] = imf.tolist()
        return ret

    def input_var_references(self, data, variables):
        """
        :param data: (list) of dict: variable name (str) -> level name (str)
        :param variables: (dict) input variables
        """
        ret = {}
        for vardata in data:
            varname = vardata[NAME]
            ret[varname] = variables[varname]
        return ret

    def input_levels(self, data):
        """
        :param data: (list) of dict: variable name (str) -> level name (str)
        """
        ret = {}
        for vardata in data:
            ret[vardata[NAME]] = vardata[LEVEL]
        return ret

    def init_result(self):
        ret = {}
        for varname, var in self.variables.items():
            ret[varname] = None
        return ret

    def evaluate(self, antecedent):
        """Computes the implicated mfs for the variables.
        :param antecedent: (float) antecedent fuzzy value
        """
        assert(self.result == self.init_result())  # should only be called once
        implication = get_implication(self.implication_type)
        for varname, var in self.variables.items():
            mf = var.mfs[self.levels[varname]]
            self.result[varname] = implication(mf, antecedent)
