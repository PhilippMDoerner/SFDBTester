import unittest as ut

from sfdbtester.sfdb.sql_table_schema import Column
from sfdbtester.sfdb.sql_table_schema import SQLTableSchema


#TODO: Change from hard coding the patterns to writing them into a file in "resources" and reading that file in
#TODO: Ensure that the pattern that is returned from get_datattype_regex_pattern only matches exact matches of the regex, not partial

def create_test_sqltableschema(column_names=('1', '2'), schema_name='TEST_SCHEMA',
                               column_properties=(Column('nvarchar', 8, True), Column('int', 4, True))):
    schema = SQLTableSchema(schema_name)
    schema.columns = {name: properties for name, properties in zip (column_names, column_properties)}
    return schema


class TestSQLTableSchema(ut.TestCase):
    def setUp(self):
        pass

    def test_columns_valid_columns(self): #TODO: Get this running
        test_schema = create_test_sqltableschema()
        expected_columns = ['1', '2']
        self.assertEqual(expected_columns, test_schema.columns)

    def test_columns_invalid_columns(self):
        test_schema = create_test_sqltableschema()
        wrong_columns = ['COLUMN1', 'COLUMN2', 'COLUMN3', 'COLUMN4',
                         'COLUMN5', 'COLUMN6', 'COLUMN7', 'COLUMN9']
        self.assertNotEqual(wrong_columns, test_schema.columns)

    def test_is_full_schema_known_sfdb(self):
        test_schema = SQLTableSchema('SFI_CURRENCY_SYMBOL')
        self.assertTrue(test_schema.is_full_schema())

    def test_is_full_schema_unknown_sfdb(self):
        test_schema_without_known_schema = SQLTableSchema('UNKNOWN_SCHEMA')
        self.assertFalse(test_schema_without_known_schema.is_full_schema())

    # TODO: Split this into individual tests and get them running
    def test_get_datatype_regex_pattern_wrong_column(self):
        test_schema = create_test_sqltableschema()
        with self.assertRaises(ValueError):
            test_schema.get_datatype_regex_pattern('NONEXISTANT_COLUMN')

    def test_get_datatype_regex_pattern_nvarchar8_valid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        test_string = 'An._?0 /'
        nvarchar8_pattern = test_schema.get_datatype_regex_pattern('NVARCHAR_WITHOUT_NULL')
        self.assertIsNotNone(nvarchar8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_nvarchar8_string_too_long(self):
        test_schema = SQLTableSchema('FULL_TEST')
        test_string = '123456789'
        nvarchar8_pattern = test_schema.get_datatype_regex_pattern('NVARCHAR_WITHOUT_NULL')
        self.assertIsNone(nvarchar8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_nvarchar8_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        test_string = ''
        nvarchar8_pattern = test_schema.get_datatype_regex_pattern('NVARCHAR_WITHOUT_NULL')
        self.assertIsNotNone(nvarchar8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bit1_valid_0_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bit1_pattern = test_schema.get_datatype_regex_pattern('BIT_WITHOUT_NULL')
        test_string = '0'
        self.assertIsNotNone(bit1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bit1_valid_1_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bit1_pattern = test_schema.get_datatype_regex_pattern('BIT_WITHOUT_NULL')
        test_string = '1'
        self.assertIsNotNone(bit1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bit1_string_too_long(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bit1_pattern = test_schema.get_datatype_regex_pattern('BIT_WITHOUT_NULL')
        test_string = '12'
        self.assertIsNone(bit1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bit1_invalid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bit1_pattern = test_schema.get_datatype_regex_pattern('BIT_WITHOUT_NULL')
        test_string = 'a'
        self.assertIsNone(bit1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bit1_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bit1_pattern = test_schema.get_datatype_regex_pattern('BIT_WITHOUT_NULL')
        test_string = ''
        self.assertIsNone(bit1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_int8_string_too_long(self):
        test_schema = SQLTableSchema('FULL_TEST')
        int8_pattern = test_schema.get_datatype_regex_pattern('INT_WITHOUT_NULL')
        test_string = '123456789'
        self.assertIsNone(int8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_int8_string_short(self):
        test_schema = SQLTableSchema('FULL_TEST')
        int8_pattern = test_schema.get_datatype_regex_pattern('INT_WITHOUT_NULL')
        test_string = '1'
        self.assertIsNotNone(int8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_int8_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        int8_pattern = test_schema.get_datatype_regex_pattern('INT_WITHOUT_NULL')
        test_string = ''
        self.assertIsNone(int8_pattern.match(test_string))

    def test_get_datatype_regex_pattern_int8_invalid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        int8_pattern = test_schema.get_datatype_regex_pattern('INT_WITHOUT_NULL')
        test_string = 'aA,;.:-)'
        self.assertIsNone(int8_pattern.match(test_string))


"""   def test_get_datatype_regex_pattern_datetime_invalid_string(self):
    def test_get_datatype_regex_pattern_datetime_empty_string(self):
    def test_get_datatype_regex_pattern_datetime_valid_string(self):
    def test_get_datatype_regex_pattern_datetime_string_too_long(self):
    def test_get_datatype_regex_pattern_datetime_invalid_date_format(self):
        
        
     
        datetime10_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN4')
        self.assertIsNotNone(datetime10_pattern.match('2017-05-22'))
        self.assertIsNone(datetime10_pattern.match('17-05-22'))
        self.assertIsNone(datetime10_pattern.match('22-05-2017'))
        self.assertIsNone(datetime10_pattern.match('22-05-17'))
        self.assertIsNone(datetime10_pattern.match('2017-22-05'))

        datetime210_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN5')
        self.assertIsNotNone(datetime210_pattern.match('2017-05-22'))
        self.assertIsNone(datetime210_pattern.match('17-05-22'))
        self.assertIsNone(datetime210_pattern.match('22-05-2017'))
        self.assertIsNone(datetime210_pattern.match('22-05-17'))
        self.assertIsNone(datetime210_pattern.match('2017-22-05'))

        datetime220_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN6')
        self.assertIsNotNone(datetime10_pattern.match('2017-05-22'))
        self.assertIsNone(datetime220_pattern.match('17-05-22'))
        self.assertIsNone(datetime220_pattern.match('22-05-2017'))
        self.assertIsNone(datetime220_pattern.match('22-05-17'))
        self.assertIsNone(datetime220_pattern.match('2017-22-05'))

        bool1_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN7')
        self.assertIsNotNone(bool1_pattern.match('0'))
        self.assertIsNotNone(bool1_pattern.match('1'))
        self.assertIsNone(bool1_pattern.match('23456789'))
        self.assertIsNone(bool1_pattern.match('aA,;.:-_\'#+*`´?=)(/&%$§"!°^'))
"""

if __name__ == '__main__':
    ut.main()
