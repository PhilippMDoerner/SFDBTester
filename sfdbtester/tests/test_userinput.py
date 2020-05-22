import os
import unittest as ut
from unittest import mock
from sfdbtester.common import userinput as ui
from sfdbtester.common.utilities import get_resource_filepath


class TestUserInput(ut.TestCase):
    def setUp(self) -> None:
        pass

    def test_request_regex_pattern_regex_input(self):
        with mock.patch('builtins.input', return_value=r'\d\d'):
            test_pattern = ui.request_regex_pattern('')
            test_string = '01'
            self.assertIsNotNone(test_pattern.match(test_string))

    @mock.patch('builtins.input', return_value=r'\l\d')
    @mock.patch('builtins.print', side_effect=[None, Exception('To Break the Loop!')])
    def test_request_regex_pattern_non_regex_input(self, mocked_input, mocked_print):
        with self.assertRaises(Exception):
            ui.request_regex_pattern('')
            mocked_print.assert_called_with('The input was not valid regular expression')

    @mock.patch('builtins.input', return_value='')
    @mock.patch('builtins.print')
    def test_request_regex_pattern_no_input(self, mocked_print, mocked_input):
        test_pattern = ui.request_regex_pattern('')
        mocked_print.assert_called_with('No Regex provided.')
        self.assertIsNone(test_pattern)

    @mock.patch('builtins.input', return_value='1 2 12')
    def test_request_list_of_int_list_of_int(self, mocked_input):
        int_list = ui.request_list_of_int('')
        expected_output = [1, 2, 12]
        self.assertEqual(expected_output, int_list)

    @mock.patch('builtins.input', return_value='1.3 2.4 12.5')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_list_of_int_list_of_float(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_list_of_int('')
        mocked_print.assert_called_with(f"!WARNING! The following entries are not integers :\n1.3  2.4  12.5")

    @mock.patch('builtins.input', return_value='a bc def')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_list_of_int_list_of_string(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_list_of_int('')
        mocked_print.assert_called_with(f"!WARNING! The following entries are not integers :\na  bc  def")

    @mock.patch('builtins.input', return_value='')
    @mock.patch('builtins.print')
    def test_request_list_of_int_empty_string(self, mocked_print, mocked_input):
        ui.request_list_of_int('')
        mocked_print.assert_called_with(f"No list of numbers provided.")

    @mock.patch('builtins.input', return_value='1 2 3')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_list_of_int_list_of_int_below_min(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_list_of_int('', min_value=2)
        mocked_print.assert_called_with(f"!WARNING! The following entries are below the allowed minimum of 2:\n1")

    @mock.patch('builtins.input', return_value='1 2 3')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_list_of_int_list_of_int_above_max(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_list_of_int('', max_value=2)
        mocked_print.assert_called_with(f"!WARNING! The following entries are above the allowed maximum of 2 :\n3")

    @mock.patch('builtins.input', return_value='1 2 3')
    def test_request_list_of_int_list_of_int_between_min_max(self, mocked_input):
        int_list = ui.request_list_of_int('', min_value=0, max_value=4)
        expected_output = [1, 2, 3]
        self.assertEqual(expected_output, int_list)

    @mock.patch('builtins.input', return_value='a bc def')
    def test_request_items_of_list_valid_items(self, mocked_input):
        test_items = ['a', 'bc', 'gh', 'def']
        item_list = ui.request_items_of_list('', test_items)
        expected_output = ['a', 'bc', 'def']
        self.assertEqual(expected_output, item_list)

    @mock.patch('builtins.input', return_value='')
    def test_request_items_of_list_no_items(self, mocked_input):
        test_items = ['a', 'bc', 'gh', 'def']
        item_list = ui.request_items_of_list('', test_items)
        expected_output = []
        self.assertEqual(expected_output, item_list)

    @mock.patch('builtins.input', return_value='ij')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_items_of_list_invalid_items(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            test_items = ['a', 'bc', 'gh', 'def']
            ui.request_items_of_list('', test_items)
        mocked_print.assert_called_with(f"!WARNING! The following entries are not in the list of possible items:\nij")

    @mock.patch('builtins.input', return_value='')
    def test_request_filepath_empty_string(self, mocked_input):
        filepath = ui.request_filepath('')
        expected_output = ''
        self.assertEqual(expected_output, filepath)

    @mock.patch('builtins.input', return_value='5')
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_filepath_int(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_filepath('')
        mocked_print.assert_called_with(f"5 is not a valid filepath.")

    @mock.patch('builtins.input', return_value=f"{get_resource_filepath('empty.sfdb')}_invalid_path_addition")
    @mock.patch('builtins.print', side_effect=Exception('Break The Loop!'))
    def test_request_invalid_filepath(self, mocked_print, mocked_input):
        with self.assertRaises(Exception):
            ui.request_filepath('')
        mocked_print.assert_called_with(f"{get_resource_filepath('empty.sfdb')}_invalid_path_addition "
                                        f"is not a valid filepath.")

    @mock.patch('builtins.input', return_value=get_resource_filepath('empty.sfdb'))
    def test_request_filepath_valid_filepath(self, mocked_input):
        filepath = ui.request_filepath('')
        expected_output = get_resource_filepath('empty.sfdb')
        self.assertEqual(expected_output, filepath)
        self.assertTrue(os.path.isfile(filepath))


if __name__ == '__main__':
    ut.main()
