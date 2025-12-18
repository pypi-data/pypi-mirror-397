import ast
from inspect import getsource
from teradataml.dataframe.functions import register as tdml_register
from teradatamlspk.sql.column import Column
from teradatamlspk.sql.types import StringType
from teradatamlspk.sql.utils import _get_tdml_type
from teradatamlspk.sql.dataframe_utils import DataFrameUtils as df_utils

class UDFRegistration:
    """
    Wrapper for user-defined function registration.
    """
    def __init__(self, sparkSession):
        self.sparkSession = sparkSession

    def register(self, name, f, returnType=None):
        """ Registers a user defined function (UDF)."""
        func = f() if "udf.<locals>" in f.__qualname__ else f
        # Check if the func is a ColumnExpression object and has a udf.
        if isinstance(func, Column) and func._udf:
            udf_func = df_utils._udf_col_to_tdml_col(func)
        else:
            returnType = StringType() if returnType is None else returnType
            returnType = _get_tdml_type(returnType)
            udf_func = func
            # Check if the udf_func is a lambda function and reconstruct it.
            if udf_func.__name__ == "<lambda>":
                # Extract the source code of the lambda function.
                udf_func  = df_utils._get_lambda_source_code(udf_func, name)
        tdml_register(name, udf_func, returnType)

        