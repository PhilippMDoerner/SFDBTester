import unittest as ut
from sfdbtester.common import utilities


class TestUtilities(ut.TestCase):
    def test_get_resource_filepath_resource_in_project(self):
        test_file = 'empty.sfdb'
        test_filepath = utilities.get_resource_filepath(test_file)

        dir1 = "sfdbtester"
        dir2 = "resources"
        self.assertTrue(dir1 in test_filepath)
        self.assertTrue(dir2 in test_filepath)
        self.assertTrue(test_file in test_filepath)

    def test_get_resource_filepath_nonexistant_resource(self):
        test_file = 'ThisResourceDoesNotExist'
        with self.assertRaises(ValueError):
            utilities.get_resource_filepath(test_file)

    def test_get_resource_filepath_dir(self):
        test_file = 'test_dir'
        test_filepath = utilities.get_resource_filepath(test_file)
        contained_in_expected_output = '/sfdbtester/resources/test_dir'
        self.assertTrue(contained_in_expected_output in test_filepath)


if __name__ == '__main__':
    ut.main()
