import unittest as test

import nifty_nesting as nest



        

class MapTest(test.TestCase):
    def test_flat_list(self):
        l = [1, 2, 3, '4']
        l2 = nest.map(lambda x: 2*x, l)
        self.assertEqual(l2, [2, 4, 6, '44'])


if __name__ == '__main__':
    test.main()
    
