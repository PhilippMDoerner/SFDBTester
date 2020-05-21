import unittest as ut

from sfdbtester.sfdb.sql_table_schema import Column
from sfdbtester.sfdb.sql_table_schema import SQLTableSchema


#TODO: Change from hard coding the patterns to writing them into a file in "resources" and reading that file in

def create_test_sqltableschema(column_names=('1', '2'), schema_name='TEST_SCHEMA',
                               column_properties=(Column('nvarchar', 8, True), Column('int', 4, True))):
    schema = SQLTableSchema(schema_name)
    schema.columns = {name: properties for name, properties in zip (column_names, column_properties)}
    return schema


class TestSQLTableSchema(ut.TestCase):
    def setUp(self):
        pass

    def test_columns_valid_columns(self):
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

    def test_get_datatype_regex_pattern_bool1_valid_0_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bool1_pattern = test_schema.get_datatype_regex_pattern('BOOL_WITHOUT_NULL')
        test_string = '0'
        self.assertIsNotNone(bool1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bool1_valid_1_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bool1_pattern = test_schema.get_datatype_regex_pattern('BOOL_WITHOUT_NULL')
        test_string = '1'
        self.assertIsNotNone(bool1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bool1_string_too_long(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bool1_pattern = test_schema.get_datatype_regex_pattern('BOOL_WITHOUT_NULL')
        test_string = '12'
        self.assertIsNone(bool1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bool1_invalid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bool1_pattern = test_schema.get_datatype_regex_pattern('BOOL_WITHOUT_NULL')
        test_string = 'a'
        self.assertIsNone(bool1_pattern.match(test_string))

    def test_get_datatype_regex_pattern_bool1_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        bool1_pattern = test_schema.get_datatype_regex_pattern('BOOL_WITHOUT_NULL')
        test_string = ''
        self.assertIsNone(bool1_pattern.match(test_string))

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

    def test_get_datatype_regex_pattern_datetime_invalid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime_pattern = test_schema.get_datatype_regex_pattern('DATETIME_WITHOUT_NULL')
        test_string = 'An invalid string'
        self.assertIsNone(datetime_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime_pattern = test_schema.get_datatype_regex_pattern('DATETIME_WITHOUT_NULL')
        test_string = ''
        self.assertIsNone(datetime_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime_date_yyyy_mm_dd(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime_pattern = test_schema.get_datatype_regex_pattern('DATETIME_WITHOUT_NULL')
        test_string = '2020-05-14'
        self.assertIsNotNone(datetime_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime_date_dd_mm_yyyy(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime_pattern = test_schema.get_datatype_regex_pattern('DATETIME_WITHOUT_NULL')
        test_string = '14-05-2020'
        self.assertIsNone(datetime_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime_date_yy_mm_dd(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime_pattern = test_schema.get_datatype_regex_pattern('DATETIME_WITHOUT_NULL')
        test_string = '20-05-14'
        self.assertIsNone(datetime_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime2_invalid_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime2_pattern = test_schema.get_datatype_regex_pattern('DATETIME2_WITHOUT_NULL')
        test_string = 'An invalid string'
        self.assertIsNone(datetime2_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime2_empty_string(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime2_pattern = test_schema.get_datatype_regex_pattern('DATETIME2_WITHOUT_NULL')
        test_string = ''
        self.assertIsNone(datetime2_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime2_date_yyyy_mm_dd(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime2_pattern = test_schema.get_datatype_regex_pattern('DATETIME2_WITHOUT_NULL')
        test_string = '2020-05-14'
        self.assertIsNotNone(datetime2_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime2_date_dd_mm_yyyy(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime2_pattern = test_schema.get_datatype_regex_pattern('DATETIME2_WITHOUT_NULL')
        test_string = '14-05-2020'
        self.assertIsNone(datetime2_pattern.match(test_string))

    def test_get_datatype_regex_pattern_datetime2_date_yy_mm_dd(self):
        test_schema = SQLTableSchema('FULL_TEST')
        datetime2_pattern = test_schema.get_datatype_regex_pattern('DATETIME2_WITHOUT_NULL')
        test_string = '20-05-14'
        self.assertIsNone(datetime2_pattern.match(test_string))


if __name__ == '__main__':
    ut.main()
