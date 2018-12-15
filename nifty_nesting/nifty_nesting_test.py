import attr
import collections
import unittest as test

import nifty_nesting as nest


# namedtuple is part of the structure.
Point = collections.namedtuple('Point', ['x', 'y'])


# attr classes are part of the structure
@attr.s
class Coordinates(object):
    x = attr.ib()
    y = attr.ib()

# Regular classes are not part of the structure.
class Blah:
    def __init__(self):
        self.blah = 'blah'


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
        p = nest.pack_list_into(s, [])
        self.assertEqual(p, None)

    def test_single_element(self):
        s = 'string'
        p = nest.pack_list_into(s, ['expected'])
        self.assertEqual(p, 'expected')

    def test_nested(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        l = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
        p = nest.pack_list_into(s, l)
        e = {'a': 2, 'b': 4, 'c': [6, 8, 10, {12, 14}, (16, 18)], 'd': Point(20, 22), 'e': Coordinates(24, 26)}
        self.assertEqual(p, e)

    def test_atomic(self):
        s = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        l = [[2, 4, 6, 8], [10, 12]]
        p = nest.pack_list_into(s, l, is_atomic=lambda x: isinstance(x, list))
        e = {'a': [2, 4, 6, 8], 'b': [10, 12]}
        self.assertEqual(p, e)


class FilterTest(test.TestCase):

    def test_none(self):
        s = None
        f = nest.filter(lambda x: x, s)
        self.assertEqual(f, None)

    def test_single_element(self):
        s = 'string'
        f = nest.filter(lambda x: x != 'string', s)
        self.assertEqual(f, None)

        f = nest.filter(lambda x: x == 'string', s)
        self.assertEqual(f, s)

    def test_no_true_elements(self):
        s = [1, 2, 3]
        f = nest.filter(lambda x: x > 4, s)
        self.assertEqual(f, [])

    def test_nested(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        f = nest.filter(lambda x: x % 2 == 0, s)
        self.assertEqual(f, {'b': 2, 'c': [4, {6}, (8,)], 'd': Point(10, None), 'e': Coordinates(12, None)})


class AssertSameStructureTest(test.TestCase):

    def test_none(self):
        nest.assert_same_structure(None, None)
        nest.assert_same_structure(3, None)
        with self.assertRaises(AssertionError):
            nest.assert_same_structure([], None)

    def test_single_element(self):
        nest.assert_same_structure(3, 'string')
        with self.assertRaises(AssertionError):
            nest.assert_same_structure(3, [1])
        with self.assertRaises(AssertionError):
            nest.assert_same_structure((1,), 3)

    def test_nested(self):
        s1 = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        s2 = {'a': 'hey', 'b': 4, 'c': [2, 3, 4, {'r', 't'}, ('q', 's')], 'd': Point(0, 1), 'e': Coordinates(1, 2)}
        nest.assert_same_structure(s1, s2)

        s3 = {'a': 'hey', 'b': 4, 'c': [2, 3, 4, {'r', 't'}, ('q', 's', 't')], 'd': Point(0, 1), 'e': Coordinates(1, 2)}
        with self.assertRaises(AssertionError):
            nest.assert_same_structure(s1, s3)
        with self.assertRaises(AssertionError):
            nest.assert_same_structure(s3, s1)

    def test_atomic(self):
        s1 = ([1, 2], [3, 4], [5, 6])
        s2 = ([1], [2], [3])
        nest.assert_same_structure(s1, s2, is_atomic=lambda x: isinstance(x, list))


class ReduceTest(test.TestCase):

    def test_none(self):
        s = nest.reduce(lambda x, y: x*y, None)
        self.assertEqual(s, None)

    def test_single_elements(self):
        s = nest.reduce(lambda x, y: x+y, 3)
        self.assertEqual(s, 3)

    def test_nested(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        r = nest.reduce(lambda x, y: x+y, s)
        self.assertEqual(r, sum(range(14)))

    def test_atomic(self):
        s = {'a': 1, 'b': 2, 'c': [3, 4, 5, {6, 7}, (8, 9)], 'd': Point(10, 11), 'e': Coordinates(12, 13)}
        r = nest.reduce(lambda x, y: x if isinstance(x, Point) else y,
                        s,
                        is_atomic=lambda x: isinstance(x, Point) or nest.is_scalar(x))
        self.assertEqual(r, Point(10, 11))


class AtomicTest(test.TestCase):

    def test_is_scalar(self):
        self.assertTrue(nest.is_scalar(None))
        self.assertTrue(nest.is_scalar(3))
        self.assertTrue(nest.is_scalar('string'))
        self.assertTrue(nest.is_scalar(Blah()))

        self.assertFalse(nest.is_scalar([]))
        self.assertFalse(nest.is_scalar((2, 3)))
        self.assertFalse(nest.is_scalar(Point(2, 3)))
        self.assertFalse(nest.is_scalar(Coordinates(2, 3)))

    def test_has_max_depth(self):
        self.assertTrue(nest.has_max_depth(1)([1, 2]))
        self.assertTrue(nest.has_max_depth(1)((1, 2)))
        self.assertTrue(nest.has_max_depth(1)(Point(1, 2)))
        self.assertTrue(nest.has_max_depth(1)(Coordinates(1, 2)))
        self.assertTrue(nest.has_max_depth(2)({'a': Coordinates(1, 2)}))
        self.assertTrue(nest.has_max_depth(2)(Coordinates(1, (2, 3))))

        self.assertFalse(nest.has_max_depth(1)((1, (1, 2))))
        self.assertFalse(nest.has_max_depth(1)({'a': [1, 2]}))

    def test_has_max_depth_with_lists(self):
        l = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        f = nest.map(lambda x: max(x), l, is_atomic=nest.has_max_depth(1))
        self.assertEqual(f, [3, 6, 9])

    def test_has_max_depth_with_nested(self):
        s = {'a': [1, (3, {4, 5})], 'b': {'c': 1}, 'd': [Point(2, 3), Coordinates(Point(1, 2), 7)]}
        f = nest.flatten(s, is_atomic=nest.has_max_depth(1))
        self.assertEqual(f, [1, 3, {4, 5}, {'c': 1}, Point(2, 3), Point(1, 2), 7])


if __name__ == '__main__':
    test.main()
