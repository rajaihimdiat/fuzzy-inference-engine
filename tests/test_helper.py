import unittest
import numpy as np
from blfuzzy.helper import aggregate
from blfuzzy.constants import OR, AVERAGE


class TestCases(unittest.TestCase):

    def test_aggregate_average(self):
        a = np.array([1, 6, 3, 4, 4])
        b = np.array([5, 7, 2, 5, 1])
        c = np.array([6, 8, 4, 6, 1])
        expect = np.array([4, 7, 3, 5, 2])
        actual = aggregate([a, b, c], method=AVERAGE)
        assert(np.allclose(actual, expect))

    def test_aggregate_average_single(self):
        a = np.array([1, 6, 3, 4, 4])
        expect = np.array([1, 6, 3, 4, 4])
        actual = aggregate([a], method=AVERAGE)
        assert(np.allclose(actual, expect))

    def test_aggregate_or(self):
        a = np.array([1, 6, 3, 4, 4])
        b = np.array([5, 7, 2, 5, 1])
        c = np.array([6, 8, 4, 6, 1])
        expect = np.array([6, 8, 4, 6, 4])
        actual = aggregate([a, b, c], method=OR)
        assert(np.allclose(actual, expect))

    def test_aggregate_or_single(self):
        a = np.array([1, 6, 3, 4, 4])
        expect = np.array([1, 6, 3, 4, 4])
        actual = aggregate([a], method=OR)
        assert(np.allclose(actual, expect))


if __name__ == '__main__':
    unittest.main()
