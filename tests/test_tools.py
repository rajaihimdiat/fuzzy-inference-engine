import unittest
import numpy as np
from blfuzzy.constants import TRIANGLE
from blfuzzy.helper import get_default_mf_params, get_default_mf_unit_params
from blfuzzy.helper import map_0_1_range_to_arbitrary_range, get_var_range


class TestCases(unittest.TestCase):

    def test_default_mf_params(self):
        xmin = 0
        xmax = 10
        levels = 3
        index = 0
        mf_type = TRIANGLE
        expect = np.array([0.0, 0.0, 5.0])
        actual = get_default_mf_params(xmin, xmax, levels, index, mf_type)
        assert(np.allclose(actual, expect))

    def test_get_default_mf_unit_params(self):
        levels = 3
        level_index = 0
        mf_type = TRIANGLE
        expect = np.array([0.0, 0.0, 0.5])
        actual = get_default_mf_unit_params(levels, level_index, mf_type)
        assert(np.allclose(actual, expect))

    def test_map_0_1_range_to_arbitrary_range(self):
        xmin = 3
        xmax = 32
        array = np.array([0.0, 0.5, 1.0])
        expect = np.array([3.0, 17.5, 32.0])
        actual = map_0_1_range_to_arbitrary_range(xmin, xmax, array)
        assert(np.allclose(actual, expect))

    def test_get_var_range_long(self):
        xmin = 3
        xmax = 17
        intervals = 14
        expect = np.array(
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
        actual = get_var_range(xmin, xmax, intervals)
        assert(np.allclose(actual, expect))

    def test_get_var_range_short(self):
        xmin = 3
        xmax = 7
        intervals = 10
        expect = np.array([3, 3.4, 3.8, 4.2, 4.6, 5, 5.4, 5.8, 6.2, 6.6, 7])
        actual = get_var_range(xmin, xmax, intervals)
        assert(np.allclose(actual, expect))


if __name__ == '__main__':
    unittest.main()
