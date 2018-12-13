import attr
import collections
import unittest as test

import nifty_nesting as nest


Point = collections.namedtuple('Point', ['x', 'y'])


@attr.s
class Coordinates(object):
    x = attr.ib()
    y = attr.ib()
        

class FlattenTest(test.TestCase):

    def test_none(self):
        s = None
        flat = nest.flatten(s)
        self.assertEqual(flat, [])

    def test_single_element(self):
        for s in ["example", 2, False]:
            flat = nest.flatten(s)
            self.assertEqual(flat, [s])

    def test_list_tuple_set_dict(self):
        for s in [(1, 2, 3), [4, 5, 6], {7, 8, 8}]:
            flat = nest.flatten(s)
            self.assertEqual(flat, list(s))

        s = {'a': 1, 'b': 2}
        flat = nest.flatten(s)
        self.assertEqual(flat, [1, 2])

    def test_namedtuple(self):
        p = Point(1, 2)
        flat = nest.flatten(p)
        self.assertEqual(flat, [1, 2])

    def test_attr(self):
        c = Coordinates(1, 2)
        flat = nest.flatten(c)
        self.assertEqual(flat, [1, 2])

    def test_nested(self):
        s = (1, [2, {3, 4, 5}, {'a': 6, 'b': 7}, Coordinates(Point(8, 9), Point(10, 11))])
        flat = nest.flatten(s)
        self.assertEqual(flat, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    def test_atomic(self):
        s = [Point(1, 2), (Point(3, 4), Point(5, 6)), {'a': Point(7, 8)}]
        flat = nest.flatten(s, is_atomic=lambda x: isinstance(x, Point))
        self.assertEqual(flat, [Point(1, 2), Point(3, 4), Point(5, 6), Point(7, 8)])


class MapTest(test.TestCase):

    def test_none(self):
        s = None
        m = nest.map(lambda x: 2*x, s)
        self.assertEqual(m, None)

    def test_single_element(self):
        s = 4
        m = nest.map(lambda x: 2*x, s)
        self.assertEqual(m, 8)

    def test_nested(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, {5, 6}], 'd': Point(7, 8), 'e': Coordinates(9, 10)}
        m = {'a': 2, 'b': 4, 'c': [6, 8, {10, 12}], 'd': Point(14, 16), 'e': Coordinates(18, 20)}
        mapped = nest.map(lambda x: 2*x, s)
        self.assertEqual(mapped, m)

    def test_atomic(self):
        s = {'a': [1, 2, 3], 'b': [4, 5, 6], 'c': ([7, 8, 9], [10, 11, 12])}
        m = {'a': 1, 'b': 4, 'c': (7, 10)}
        mapped = nest.map(lambda x: x[0], s, is_atomic=lambda x: isinstance(x, list))


class PackIntoTest(test.TestCase):

    def test_none(self):
        s = None
        p = nest.pack_into(s, [])
        self.assertEqual(p, None)

    def test_single_element(self):
        s = 'string'
        p = nest.pack_into(s, ['expected'])
        self.assertEqual(p, 'expected')

    def test_nested(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        l = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
        p = nest.pack_into(s, l)
        e = {'a': 2, 'b': 4, 'c': [6, 8, 10, {12, 14}, (16, 18)], 'd': Point(20, 22), 'e': Coordinates(24, 26)}
        self.assertEqual(p, e)

    def test_atomic(self):
        s = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        l = [[2, 4, 6, 8], [10, 12]]
        p = nest.pack_into(s, l, is_atomic=lambda x: isinstance(x, list))
        e = {'a': [2, 4, 6, 8], 'b': [10, 12]}
        self.assertEqual(p, e)


if __name__ == '__main__':
    test.main()
