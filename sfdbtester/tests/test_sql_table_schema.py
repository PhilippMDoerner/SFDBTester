import unittest as ut
from sfdbtester.sfdb.sql_table_schema import SQLTableSchema


class TestSQLTableSchema(ut.TestCase):
    def setUp(self):
        self.test_schema = SQLTableSchema('TEST_SCHEMA')

    def test_columns(self):
        expected_columns = ['COLUMN1', 'COLUMN2', 'COLUMN3', 'COLUMN4',
                            'COLUMN5', 'COLUMN6', 'COLUMN7', 'COLUMN8']
        self.assertEqual(expected_columns, self.test_schema.columns)

        wrong_columns = ['COLUMN1', 'COLUMN2', 'COLUMN3', 'COLUMN4',
                         'COLUMN5', 'COLUMN6', 'COLUMN7', 'COLUMN9']
        self.assertNotEqual(wrong_columns, self.test_schema.columns)

    def test_is_full_schema(self):
        self.assertTrue(self.test_schema.is_full_schema())

        wrong_schema = SQLTableSchema('Schema is not in KNOWN_SFDB_FILES')
        self.assertFalse(wrong_schema.is_full_schema())

    def test_get_datatype_regex_pattern(self):
        with self.assertRaises(ValueError):
            self.test_schema.get_datatype_regex_pattern('COLUMN9')

        nvarchar10_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN1')
        self.assertIsNotNone(nvarchar10_pattern.search('AnX._?0 /#'))

        bit1_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN2')
        self.assertIsNotNone(bit1_pattern.search('0'))
        self.assertIsNotNone(bit1_pattern.search('1'))
        self.assertIsNone(bit1_pattern.search('23456789'))
        self.assertIsNone(bit1_pattern.search('aA,;.:-_\'#+*`´?=)(/&%$§"!°^'))

        int10_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN3')
        self.assertIsNotNone(int10_pattern.search('1'))
        self.assertIsNotNone(int10_pattern.search('23456789'))
        self.assertIsNone(int10_pattern.search('aA,;.:-_\'#+*`´?=)(/&%$§"!°^'))

        datetime10_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN4')
        self.assertIsNotNone(datetime10_pattern.search('2017-05-22'))
        self.assertIsNone(datetime10_pattern.search('17-05-22'))
        self.assertIsNone(datetime10_pattern.search('22-05-2017'))
        self.assertIsNone(datetime10_pattern.search('22-05-17'))
        self.assertIsNone(datetime10_pattern.search('2017-22-05'))

        datetime210_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN5')
        self.assertIsNotNone(datetime210_pattern.search('2017-05-22'))
        self.assertIsNone(datetime210_pattern.search('17-05-22'))
        self.assertIsNone(datetime210_pattern.search('22-05-2017'))
        self.assertIsNone(datetime210_pattern.search('22-05-17'))
        self.assertIsNone(datetime210_pattern.search('2017-22-05'))

        datetime220_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN6')
        self.assertIsNotNone(datetime10_pattern.search('2017-05-22'))
        self.assertIsNone(datetime220_pattern.search('17-05-22'))
        self.assertIsNone(datetime220_pattern.search('22-05-2017'))
        self.assertIsNone(datetime220_pattern.search('22-05-17'))
        self.assertIsNone(datetime220_pattern.search('2017-22-05'))

        bool1_pattern = self.test_schema.get_datatype_regex_pattern('COLUMN7')
        self.assertIsNotNone(bool1_pattern.search('0'))
        self.assertIsNotNone(bool1_pattern.search('1'))
        self.assertIsNone(bool1_pattern.search('23456789'))
        self.assertIsNone(bool1_pattern.search('aA,;.:-_\'#+*`´?=)(/&%$§"!°^'))


if __name__ == '__main__':
    ut.main()
