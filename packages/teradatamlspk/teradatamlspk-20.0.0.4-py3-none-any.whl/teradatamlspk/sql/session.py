# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre(pradeep.garre@teradata.com)
# Secondary Owner: Adithya Avvaru(adithya.avvaru@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################
import teradataml, re
import pandas as pd
import numpy as np
from teradataml import create_context, remove_context, configure, display,\
    UtilFuncs, TeradataConstants, copy_to_sql

from teradataml.dataframe.dataframe import DataFrame as tdml_DataFrame
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.sql.catalog import Catalog
from teradatamlspk.sql.readwriter import DataFrameReader
from teradatamlspk.sql.udf import UDFRegistration
from teradatamlspk.conf import RuntimeConfig
from teradatamlspk.sql.utils import SQLquery, _infer_dataframe_types
from teradatamlspk.sql.types import StructType, Row, DecimalType, CharType, VarcharType, TimestampType, TimestampNTZType
from teradatamlspk.sql.constants import SPARK_TO_TD_TYPES, SQL_NAME_TO_SPARK_TYPES
from teradatamlspk.sql.constants import SPARK_ELEM_TO_TD_ARRAY
from teradatasqlalchemy.types import BYTEINT, TIMESTAMP, DECIMAL, VARCHAR, CHAR, ARRAY_TIMESTAMP
import re
import datetime
import numpy as np
import pandas as pd

from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.common.constants import ArrayDefaults, TeradataTypes


display.max_rows = 20

class TeradataSession:

    catalog = Catalog()
    conf = RuntimeConfig()

    @property
    def version(self):
        return configure.database_version

    @property
    def teradataContext(self):
        from teradatamlspk import TeradataContext
        return TeradataContext()
    
    @property
    def _jsparkSession(self):
        """ Returns the TeradataSession """
        return self

    class Builder:

        def config(self, key=None, value=None, conf=None, map=None):
            TeradataSession.conf = conf if conf else RuntimeConfig()
            return self

        def enableHiveSupport(self):
            return self

        def getOrCreate(self, **kwargs):
            create_context(**kwargs)
            return TeradataSession()

        def master(self, master):
            return self

        def remote(self, url):
            return self

        def appName(self, name):
            return self

        def create(self, **kwargs):
            create_context(**kwargs)
            return TeradataSession()

    builder = Builder()

    def _parse_ddl_schema(self, ddl_str):
        """
        :param ddl_str: DDL string defining the schema. example: "name STRING, age INT, salary FLOAT"
        :return: Tuple of column names and a mapping of column names to Teradata data types.
        Example
        -------
        >>> columns, type_map = session._parse_ddl_schema("name STRING, age INT, salary FLOAT")
        >>> print(columns)
        ['name', 'age', 'salary']
        >>> print(type_map)
        {'name': 'VARCHAR', 'age': 'INTEGER', 'salary': 'FLOAT'}
        """
        ddl_str = ddl_str.replace(":", " ")
        fields = (f.strip() for f in ddl_str.split(","))
        columns = []
        type_map = {}
        # Regex: match `col name` or col_name, then type.
        pattern = re.compile(r'(`[^`]+`|\w+)\s+(\w+)', re.UNICODE)
        for field in fields:
            match = pattern.match(field)
            if match:
                col_name = match.group(1)
                # Remove backticks if present.
                if col_name.startswith("`") and col_name.endswith("`"):
                    col_name = col_name[1:-1]
                spark_type = match.group(2).upper()  # e.g., "string" -> "STRING"
                spark_type_class = SQL_NAME_TO_SPARK_TYPES.get(spark_type)
                td_type = SPARK_TO_TD_TYPES.get(type(spark_type_class))
                columns.append(col_name)
                type_map[col_name] = td_type
        return columns, type_map

    def createDataFrame(self, data, schema=None):
        """
        :param data: Vantage Table name.
        :return: teradataml DataFrame.
        """
        type_map, columns = None, None

        if isinstance(data, str):
            tdml_df = tdml_DataFrame(data)
            # Update TIMESTAMP types to with timezone for consistency with spark DataFrames.
            for col in tdml_df._metaexpr.c:
                if (col.type == TIMESTAMP) or isinstance(col.type, TIMESTAMP):
                    col.type = TIMESTAMP(timezone=True)
                elif isinstance(col.type, ARRAY_TIMESTAMP):
                    col.type = ARRAY_TIMESTAMP(col.type.scope, col.type.default_null, timezone=True)

            return DataFrame(tdml_df)
        
        # If data is a list of Row objects, extract columns and convert to list of dicts.
        if isinstance(data, list) and data and isinstance(data[0], Row):
                columns = list(getattr(data[0], "__fields__", []))
                data = [row.asDict() for row in data]

        # DDL string schema or StructType schema.
        if schema is not None:
            # If schema is a DDL string or StructType, parse it to get columns and type_map.
            if isinstance(schema, str):
                columns, type_map = self._parse_ddl_schema(schema)
            elif isinstance(schema, StructType):
                # Extract column names and types from StructType.
                columns = [field.name for field in schema.fields]
                type_map = {}
                
                for field in schema.fields:
                    dt_name = field.dataType.__class__.__name__
                    if dt_name == "BooleanType":
                        td_type = BYTEINT
                    elif dt_name == "TimestampNTZType":
                        td_type = TIMESTAMP(timezone=False)
                    elif dt_name == "TimestampType":
                        td_type = TIMESTAMP(timezone=True)
                    elif dt_name == "DecimalType":
                        td_type = DECIMAL(field.dataType.precision, field.dataType.scale)
                    elif dt_name == "ArrayType":
                        # Determine Teradata ARRAY_* type based on Spark element type.
                        elem_type = field.dataType.elementType
                        elem_cls = elem_type.__class__
                        td_array_cls = SPARK_ELEM_TO_TD_ARRAY.get(elem_cls)

                        # Scope (single dimension) default size.
                        default_array_size = _InternalBuffer.get("default_array_size") or \
                                              ArrayDefaults.DEFAULT_ARRAY_SIZE.value
                        scope = f'[{default_array_size}]'

                        # Collect constructor kwargs conditional on element type specifics.
                        array_kwargs = {}

                        # DecimalType -> precision / scale
                        if isinstance(elem_type, DecimalType):
                            array_kwargs['precision'] = getattr(elem_type, 'precision', 38)
                            array_kwargs['scale'] = getattr(elem_type, 'scale', 19)
                            
                        # Timestamp types -> timezone flag.
                        if isinstance(elem_type, TimestampNTZType):
                            array_kwargs['timezone'] = False
                        elif isinstance(elem_type, TimestampType):
                            array_kwargs['timezone'] = True

                        td_type = td_array_cls(scope, **{k: v for k, v in array_kwargs.items() if v is not None})
                    else:
                        td_type_spec = SPARK_TO_TD_TYPES.get(field.dataType.__class__)
                        td_type = td_type_spec() if isinstance(td_type_spec, type) else td_type_spec
                    type_map[field.name] = td_type
            else:
                columns = schema if isinstance(schema, (list, tuple)) else None

        # Non-Pandas raw inputs -> convert then infer.
        if isinstance(data, (list, np.ndarray)) and not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=columns)

        if isinstance(data, pd.DataFrame):
            renamed_df = data.copy()
            renamed_df.columns = [f"col_{i}" if isinstance(i, int) else i for i in renamed_df.columns]
            inferred_types = _infer_dataframe_types(renamed_df)
            return DataFrame(tdml_DataFrame(renamed_df, types=type_map or inferred_types, index=False))

    def getActiveSession(self):
        return self

    def active(self):
        return self

    def newSession(self):
        """ Returns the existing TeradataSession """
        return self

    @property
    def readStream(self):
        raise NotImplemented("The API is not supported in Teradata Vantage.")

    def sql(self, sqlQuery, args=None, kwargs=None):
        if args:
            sqlQuery = sqlQuery.format(**args)
        return SQLquery._execute_query(sqlQuery)

    @property
    def read(self):
        return DataFrameReader()
    
    @property
    def udf(self):
        return UDFRegistration(self)

    @staticmethod
    def stop():
        remove_context()
        return

    @staticmethod
    def streams():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def udtf():
        raise NotImplemented("Not supported yet Teradata Vantage.")

    @staticmethod
    def addArtifact():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def addArtifacts():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def copyFromLocalToFs():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def client():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptAll():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptOperation():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def addTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def removeTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def getTags():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def clearTags():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def table(tableName):
        return DataFrame(tdml_DataFrame(tableName))

    def range(self, start, end=None, step=1, numPartitions = None):
        """ Creates a DataFrame with a range of numbers. """
        from teradataml import td_range
        return DataFrame(td_range(start, end, step))
