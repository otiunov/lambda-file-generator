import unittest
import main


class TestMainMethods(unittest.TestCase):

    def test_generate_data(self):
        expected_size = 5
        self.assertEqual(len(main.generate_data(expected_size)), expected_size)


if __name__ == '__main__':
    unittest.main()
