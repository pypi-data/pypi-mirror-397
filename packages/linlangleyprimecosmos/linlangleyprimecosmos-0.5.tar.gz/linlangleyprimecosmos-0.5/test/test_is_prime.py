#!/usr/bin/python
 
import unittest
from primepackage import is_prime
 
class Test_is_prime(unittest.TestCase):
 
    def setUp(self):
        # Set up database, parameters before each method is tested ...
        self.fixture = 10
 
    def tearDown(self):
        # Tear down database, parameters after each method is tested ...
        del self.fixture
 
    def test_numbers(self):
        self.assertEqual(is_prime(2), True)
        self.assertEqual(is_prime(8), False)
        self.assertEqual(is_prime(1), False)
        self.assertEqual(is_prime(83), True)
        self.assertEqual(is_prime(self.fixture), False)
 
    def test_raises(self):
        with self.assertRaises(ValueError):
            is_prime(0)
            is_prime(3.14)
            is_prime('Hello')
 
if __name__ == '__main__':
    unittest.main()
