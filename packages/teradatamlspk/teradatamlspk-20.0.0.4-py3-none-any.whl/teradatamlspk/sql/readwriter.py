# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Shravan Jat(shravan.jat@teradata.com)
# Secondary Owner: Pradeep Garre(pradeep.garre@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################
from collections import OrderedDict
import os, pandas as pd
from teradataml import ReadNOS, WriteNOS, read_csv, DataFrame as tdml_DataFrame, copy_to_sql
from teradataml import get_connection, execute_sql, db_list_tables, db_drop_table
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import TeradataConstants
from teradatamlspk.sql.utils import _check_lib


class DataFrameReader:
    def __init__(self, **kwargs):

        # Always
        #   'format' holds the format for file. - parquet, csv, orc etc.
        #   'mode' holds the format for file. - parquet, csv, orc etc.
        self.__params = {**kwargs}

    def format(self, source):
        self.__params.update({"format": source})
        return DataFrameReader(**self.__params)

    def json(self, path, **kwargs):
        from teradatamlspk.sql.dataframe import DataFrame as tdmlspk_DataFrame
        # If user have used 'authorization' call ReadNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            self.__params.update({"location": path, "stored_as": "TEXTFILE"})
            return tdmlspk_DataFrame(ReadNOS(**self.__params).result)
        else:
            pandas_df = pd.read_json(path_or_buf = path, **self.__params)
            # Generate random table name
            new_table_name = UtilFuncs._generate_temp_table_name(
                    prefix="tdmlspk_read_json", gc_on_quit=True)
            copy_to_sql(pandas_df, table_name=new_table_name)
            return tdmlspk_DataFrame(tdml_DataFrame(new_table_name))

    def option(self, key, value):
        self.__params[key] = value
        return DataFrameReader(**self.__params)

    def parquet(self, path, **kwargs):
        from teradatamlspk.sql.dataframe import DataFrame as tdmlspk_DataFrame
        # If user have used 'authorization' call ReadNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            self.__params.update({"location": path, "stored_as": "PARQUET"})
            return tdmlspk_DataFrame(ReadNOS(**self.__params).result)
        else:
            _check_lib("pyarrow", "parquet")
            pandas_df = pd.read_parquet(path = path, **self.__params)
            # Generate random table name
            new_table_name = UtilFuncs._generate_temp_table_name(
                    prefix="tdmlspk_read_parquet", gc_on_quit=True)
            copy_to_sql(pandas_df, table_name=new_table_name, if_exists="replace")
            return tdmlspk_DataFrame(tdml_DataFrame(new_table_name))

    def options(self, **options):
        self.__params.update(**options)
        return DataFrameReader(**self.__params)

    def load(self, path, format = 'parquet', schema = None, **options):
        # If user have used 'authorization' call ReadNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" not in self.__params:
            if self.__params.get("format", None):
                format = self.__params["format"]
                self.__params.pop("format")
            if format == 'csv':
                return self.csv(path = path, schema = schema)
            elif format == 'parquet':
                return self.parquet(path)
            elif format == 'json':
                return self.json(path)
        if not self.__params.get("format"):
            self.__params.update({"stored_as": "PARQUET" if format == 'parquet' else 'TEXTFILE'})
        else:
            self.__params["stored_as"] = "PARQUET" if self.__params.get("format") == 'parquet' else 'TEXTFILE'
            self.__params.pop("format")
        self.__params.update({"location": path})
        from teradatamlspk.sql.dataframe import DataFrame as tdmlspk_DataFrame
        return tdmlspk_DataFrame(ReadNOS(**self.__params).result)

    def csv(self, path, **kwargs):
        from teradatamlspk.sql.dataframe import DataFrame as tdmlspk_DataFrame

        # Check whether to use tdml read_csv or NoS.
        # Check if the specified path is existed in clients machine or not.
        # If yes, do read_csv. Else, use NoS.
        if os.path.exists(path):

            from teradatamlspk.sql.constants import SPARK_TO_TD_TYPES

            # Define the arguments for read_csv.
            _args = {**self.__params}

            schema = kwargs.get("schema")
            if ("types" not in _args) and schema:
                # Generate types argument.
                types = OrderedDict()
                for column in schema.fieldNames():
                    types[column] = SPARK_TO_TD_TYPES[type(schema[column].dataType)]

                _args["types"] = types
            else:
                # Teradata read_csv can not infer the data.
                raise Exception("Schema is mandatory for Teradata Vantage. ")

            table_name = _args.get("table_name")
            if not table_name:
                # Generate a temp table name.
                _args["table_name"] = UtilFuncs._generate_temp_table_name(
                    prefix="tdmlspk_read_csv", gc_on_quit=True)

            _args["filepath"] = path

            # Call read_csv from teradataml.
            res = read_csv(**_args)

            # Result can be tdml DataFrame or a tuple -
            #       first element is teradataml DataFrame.
            #       second element is a dict.
            # Look read_csv documentation for details.
            if isinstance(res, tdml_DataFrame):
                return tdmlspk_DataFrame(res)

            # Now we are here. So, this returns a tuple.
            # Print the warnings and error DataFrame's dict.
            print(res[1])

            # Then return teradatamlspk DataFrame.
            return tdmlspk_DataFrame(res[0])

        self.__params.update({"location": path, "stored_as": "TEXTFILE"})

        return tdmlspk_DataFrame(ReadNOS(**self.__params).result)
    
    def table(self, tableName):
        """ Returns the specified table as a DataFrame. """
        from teradatamlspk.sql.dataframe import DataFrame as tdmlspk_DataFrame
        return tdmlspk_DataFrame(tdml_DataFrame(tableName))

class DataFrameWriterV2:
    def __init__(self, df, table, schema_name=None):
        self._df = df
        self._table_name = table
        self._schema_name = schema_name
        self._partition_by = False
        self._options = {}

    def append(self):
        """ Appends data to table. If table does not exist, function creates the table. """
        if self.__is_table_exists():
            sql = """
            INSERT INTO {}
            {}
            """.format(self._get_table_name(), self._df.show_query())
        else:
            sql = self._build_sql()

        execute_sql(sql)

    def create(self):
        """Function to create a table based from DataFrame."""
        execute_sql(self._build_sql())

    def createOrReplace(self):
        """
        Function replaces the table with DataFrame if table already exists.
        Else, function creates the table with DataFrame.
        """
        try:
            db_drop_table(self._table_name, schema_name=self._schema_name)
        except Exception:
            pass
        execute_sql(self._build_sql())

    def replace(self):
        """Function replaces the table with DataFrame. """
        db_drop_table(self._table_name, schema_name=self._schema_name)
        execute_sql(self._build_sql())

    def partitionedBy(self, col, *cols):
        """
        Function partition the output table created by create,
        createOrReplace, or replace using the given columns or
        transforms.
        """
        self._partition_by = True
        self._partitionCols = (col, ) + cols
        self._partitionCols = [col if isinstance(col, str) else col._tdml_column.compile() for col in self._partitionCols]
        return self

    def options(self, **options):
        """
        Function add options for writeTo
        """
        self._options.update(options)
        return self

    def option(self, key, value):
        """
        Function add option for writeTo
        """
        self._options.update({key:value})
        return self

    def __is_table_exists(self):
        """Internal function to check whether table exists or not. """
        connection = get_connection()
        return connection.dialect.has_table(connection, table_name=self._table_name, schema=self._schema_name)

    def _get_table_name(self):
        return '"{}"."{}"'.format(self._schema_name, self._table_name) if self._schema_name else self._table_name

    def _partition(self):
        """Generate query for PARTITION BY"""
        if not self._options.get("primary_index", None):
            raise Exception("primary_index is required for partitionedBy. Use either option or options")
        return """\nPARTITION BY ({})""".format(", ".join(self._partitionCols))

    def _build_sql(self):
        """Generate sql based on table name, select query, primary index and partition by."""
        sql ="""CREATE MULTISET TABLE {} AS\n({})\nWITH DATA""".format(self._get_table_name(), self._df.show_query())
        if self._options.get("primary_index"):
            _primary_index = self._options.get("primary_index")
            if not isinstance(_primary_index, (list, tuple)):
                _primary_index = [_primary_index]
            _primary_index = [col if isinstance(col, str) else col._tdml_column.compile() for col in _primary_index]
            sql+="""\nPRIMARY INDEX ({})""".format(", ".join(_primary_index))
        else:
            sql+="""\nNO PRIMARY INDEX"""
        if self._partition_by:
            sql+=self._partition()
        return sql


class DataFrameWriter:
    """
    teradatamlspk writer class enables users to write DataFrame on aws, azure, google cloud etc.
    using WriteNOS capability in csv or parquet format.
    """
    def __init__(self, **kwargs):
        """Constructor for writer class."""
        self.__params = {**kwargs}

    def format(self, source):
        """Specifies the underlying output data source."""
        self.__params.update({"format": source})
        return DataFrameWriter(**self.__params)

    def orc(self, path, **kwargs):
        """Saves the content of the DataFrame in ORC format at the specified path."""
        _check_lib("pyarrow", "orc")
        _df = self.__params.pop('data')
        _df = _df.to_pandas(all_rows=True, fastexport=True)
        # Reset the index as orc does not support serializing a non-default index for the index.
        _df_reset = _df.reset_index()
        return _df_reset.to_orc(path=path, **self.__params)

    def json(self, path, **kwargs):
        """Saves the content of the DataFrame in JSON format (JSON Lines text format or newline-delimited JSON) at the specified path."""
        # If user have used 'authorization' call WriteNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            self.__params.update({"location": path, "stored_as": "JSON"})
            WriteNOS(**self.__params)
        else:
            _df = self.__params.pop('data')
            _df = _df.to_pandas(all_rows=True, fastexport=True)
            _df.to_json(path_or_buf=path, **self.__params)

    def option(self, key, value):
        """Adds an output option for the underlying data source."option" are same as WriteNOS."""
        self.__params[key] = value
        return DataFrameWriter(**self.__params)

    def parquet(self, path, **options):
        """Saves the content of the DataFrame in Parquet format at the specified path."""
        # If user have used 'authorization' call WriteNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            self.__params.update({"location": path, "stored_as": "PARQUET"})
            WriteNOS(**self.__params)
        else:
            _check_lib("pyarrow", "parquet")
            _df = self.__params.pop('data')
            _df = _df.to_pandas(all_rows=True, fastexport=True)
            _df.to_parquet(path=path, **self.__params)

    def options(self, **options):
        """Adds output options for the underlying data source."options" are same as WriteNOS parameters."""
        self.__params.update(**options)
        return DataFrameWriter(**self.__params)

    def save(self, path, format = None, mode = None, partitionBy = None, **options):
        """
        Saves the contents of the DataFrame to a data source.
        The data source is specified by the format and a set of options.
        """
        # If user have used 'authorization' call WriteNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            if not self.__params.get("format"):
                self.__params.update({"stored_as": format.upper()})
            else:
                self.__params["stored_as"] = self.__params.get("format").upper()
                self.__params.pop("format")
            self.__params.update({"location": path})
            WriteNOS(**self.__params)
        else:
            if self.__params.get("format", None):
                format = self.__params["format"]
                self.__params.pop("format")
            if format == 'orc':
                return self.orc(path)
            elif format == 'csv':
                return self.csv(path)
            elif format == 'json':
                return self.json(path)
            elif format == 'parquet':
                return self.parquet(path)

    def csv(self, path, **kwargs):
        """Saves the content of the DataFrame in CSV format at the specified path."""
        # If user have used 'authorization' call WriteNOS functionality.
        # As authorization is required only for cloud platform
        if "authorization" in self.__params:
            self.__params.update({"location": path, "stored_as": "CSV"})
            WriteNOS(**self.__params)
        else:
            _df = self.__params.pop('data')
            _df = _df.to_pandas(all_rows=True, fastexport=True)
            _df.to_csv(path_or_buf=path, **self.__params)
        
    def mode(self, saveMode):
        """Specifies the behavior when data or table already exists."""
        self.__params.update({"mode": saveMode})
        return DataFrameWriter(**self.__params)

    def saveAsTable(self, name, format = None, mode = 'ignore', partitionBy = None, **options):
        mode_dict ={"ignore": "fail", "overwrite": "replace", "append": "append"}
        _args = {"df": self.__params["data"],
                 "table_name": name,
                 "if_exists": mode_dict[self.__params["mode"]] if self.__params.get("mode", None) else mode_dict[mode]}
        # Supports all copy_to_sql params
        self.__params.pop("data")
        self.__params.pop("mode", None)
        copy_to_sql(**_args, **self.__params)

    def insertInto(self, tableName, overwrite = False):
        _args = {"df": self.__params["data"],
                 "table_name": tableName,
                 "if_exists": ("replace" if self.__params["overwrite"] else "append")
                    if self.__params.get("overwrite", None)
                    else ("replace" if overwrite else "append")}
        # Supports all copy_to_sql params
        self.__params.pop("data")
        self.__params.pop("overwrite", None)
        copy_to_sql(**_args, **self.__params)