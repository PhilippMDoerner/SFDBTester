import re
import json
from collections import namedtuple
from sfdbtester.common.utilities import get_resource_filepath


class ColumnError(Exception):
    pass


class SQLTableSchema:
    """Part of an SFDB object. Defines the datatypes of the individual columns of an sfdb and the associated conditions
    entries need to fulfill. Datatypes are SQL datatypes."""
    sfdb_schema_file = get_resource_filepath('sfdb_schemas.json')

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
        known_sfdb_schemas = SQLTableSchema._get_known_sfdb_schemas()
        if self.table_name in known_sfdb_schemas:
            return known_sfdb_schemas[self.table_name]

    @classmethod
    def _get_known_sfdb_schemas(cls):
        """Reads in the provided SFDB schemas and returns them as dictionary"""
        with open(cls.sfdb_schema_file, mode='r') as schema_file:
            sfdb_schemas = json.load(schema_file)

        schemas_dict = {}
        for schema_name, column_infos in sfdb_schemas.items():
            column_properties = {}
            for column_name, column_info in column_infos.items():
                column = Column(column_info['datatype'],
                                column_info['length'],
                                column_info['with_null'])

                column_properties[column_name] = column
            schemas_dict[schema_name] = column_properties
        return schemas_dict

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
            regex_string = '^.{0,' + str(length) + '}$'
        elif datatype == 'int':
            regex_string = r'^\d{1,' + str(length) + '}$'
        elif datatype == 'bool' or datatype.lower() == 'bit':
            regex_string = '^[01]$'
        elif datatype == 'datetime2' or datatype.lower() == 'datetime':
            regex_string = r'^\d\d\d\d-\d\d-\d\d$'

        return re.compile(regex_string, re.IGNORECASE) if regex_string else regex_string


Column = namedtuple('Column', ['datatype', 'length', 'with_null'])
