import re
from collections import namedtuple


class ColumnError(Exception):
    pass


class SQLTableSchema:
    """Part of an SFDB object. Defines the datatypes of the individual columns of an sfdb and the associated conditions
    entries need to fulfill. Datatypes are SQL datatypes."""
    def __init__(self, sql_table_name):
        self.table_name = sql_table_name
        self.column_properties = self._get_column_properties()

    @property
    def columns(self):
        """Returns a list of all columns in this sql_table_scheme"""
        return list(self.column_properties.keys())

    @columns.setter
    def columns(self, column_object_list):
        self.column_properties = column_object_list

    def __len__(self):
        """Return number of columns defined by the schema"""
        return len(self.column_properties)

    def __getitem__(self, column):
        """Return a column defined by the schema"""
        if column not in self.columns:
            raise ColumnError(f'Column {column} does not exist in table {self.table_name}!')
        return self.column_properties[column]

    def _get_column_properties(self):
        """Retrieves the SQL column definitions for the SFDB file based on user
        input if available.

        Returns:
            list: A list of tuples (ColumnName (string), Datatype (string),
                    Length (int), IsNullAllowed (bool))
            None: When users SQL column definitions are not already known to the
                    program (Other)"""
        for table_name, table_column_definitions in KNOWN_SFDB_FILES:
            if table_name == self.table_name:
                return table_column_definitions

    def is_full_schema(self):
        """Checks whether the schema actually defines any columns"""
        return self.column_properties is not None

    def get_datatype_regex_pattern(self, column_name):
        """Generates a Pattern object of a regular expression that can match any
        column entry in an SQL table with this column definition of datatype and
        length. So far only covers nvarchar, int, bool, bit, datetime and datetime2.
        Datetime has not been tested yet.

        Parameters:
            column_name (string): The name of the sfdb column for which the regular expression is generated

        Returns:
            Pattern: Pattern object of a regular expression that matches any column
                        entry with the provided datatype and length
            None: When needed SQL datatype is not hard-coded in this function.
        """
        if column_name not in self.columns:
            raise ValueError('Column not in SQL table schema.')

        datatype = self.column_properties[column_name].datatype.lower()
        length = self.column_properties[column_name].length
        regex_string = None
        if datatype == 'nvarchar':
            regex_string = '.{0,' + str(length) + '}'
        elif datatype == 'int':
            regex_string = r'\d{0,' + str(length) + '}'
        elif datatype == 'bool' or datatype.lower() == 'bit':
            regex_string = '[01]'
        elif datatype == 'datetime2' or datatype.lower() == 'datetime':
            regex_string = r'\d\d\d\d-\d\d-\d\d'

        return re.compile(regex_string, re.IGNORECASE) if regex_string else regex_string


Column = namedtuple('Column', ['datatype', 'length', 'with_null'])

__FULL_TEST_SCHEMA = {'NVARCHAR_WITHOUT_NULL':   Column('nvarchar',  8, True),
                      'NVARCHAR_WITH_NULL':      Column('nvarchar',  8, False),
                      'BIT_WITHOUT_NULL':        Column('bit',       1, True),
                      'BIT_WITH_NULL':           Column('bit',       1, False),
                      'INT_WITHOUT_NULL':        Column('int',       8, True),
                      'INT_WITH_NULL':           Column('int',       8, False),
                      'DATETIME_WITHOUT_NULL':   Column('datetime',  1, True),
                      'DATETIME_WITH_NULL':      Column('datetime',  1, False)}

__SMALL_TEST_SCHEMA = {'COLUMN1': Column('nvarchar', 4, False),
                       'COLUMN2': Column('nvarchar', 4, False)}

__SFI_ICEBOX_MAPPING = {'IM_ALIAS':                  Column('nvarchar', 40,  False),
                        'IM_RECIPIENT_NO':           Column('nvarchar', 8,   False),
                        'IM_CONFIRMATION_MAIL_SEND': Column('bit',      1,   False),
                        'IM_MAILBODY':               Column('nvarchar', 256, True)}

__SFI_CURRENCY_SYMBOL = {'CS_CURRENCY': Column('nvarchar', 3, False),
                         'CS_SYMBOL':   Column('nvarchar', 8, False)}

__SFI_RECIPIENT = {'RE_PK':                       Column('nvarchar', 24,  False),
                   'RE_RECIPIENT_NO':             Column('nvarchar', 24,  False),
                   'RE_ENTITY':                   Column('nvarchar', 8,   True),
                   'RE_SYSTEM':                   Column('nvarchar', 16,  True),
                   'RE_NAME':                     Column('nvarchar', 88,  True),
                   'RE_STREET':                   Column('nvarchar', 88,  True),
                   'RE_COUNTRY':                  Column('nvarchar', 8,   False),
                   'RE_ZIPCODE':                  Column('nvarchar', 16,  True),
                   'RE_CITY':                     Column('nvarchar', 40,  True),
                   'RE_ILN':                      Column('nvarchar', 16,  True),
                   'RE_VAT_ID_NO':                Column('nvarchar', 24,  True),
                   'RE_TAX_ID_NO':                Column('nvarchar', 24,  True),
                   'RE_EMAIL_TEAM_INVOICE':       Column('nvarchar', 64,  True),
                   'RE_EMAIL_TEAM_FREIGHT':       Column('nvarchar', 64,  True),
                   'RE_TEAM_INVOICE':             Column('nvarchar', 64,  True),
                   'RE_TEAM_FREIGHT':             Column('nvarchar', 64,  True),
                   'RE_EMAIL_TEMPLATE':           Column('nvarchar', 200, True),
                   'RE_INSERVICE':                Column('nvarchar', 8,   True),
                   'RE_CONFIRMATION_RECEIPT':     Column('nvarchar', 8,   True),
                   'RE_LANGUAGE_CODE':            Column('nvarchar', 8,   True),
                   'RE_DEFAULT_VAT_REGISTRATION': Column('nvarchar', 8,   True),
                   'RE_TOUCHLESS':                Column('nvarchar', 8,   True)}

KNOWN_SFDB_FILES = [('SFI_ICEBOX_MAPPING',  __SFI_ICEBOX_MAPPING),
                    ('SFI_CURRENCY_SYMBOL', __SFI_CURRENCY_SYMBOL),
                    ('SFI_RECIPIENT',       __SFI_RECIPIENT),
                    ('FULL_TEST',           __FULL_TEST_SCHEMA),
                    ('SMALL_TEST',          __SMALL_TEST_SCHEMA)]
