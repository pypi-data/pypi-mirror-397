# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pooja Chaudhary(pooja.chaudhary@teradata.com)
# Secondary Owner: Pradeep Garre(pradeep.garre@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################

import warnings
import ast
import json
from inspect import getsource
from teradatamlspk.sql.column import Column
from teradatamlspk.sql.utils import AnalysisException
from teradatamlspk.sql.constants import COMPATIBLE_TYPES
from teradataml.dataframe.sql import _SQLColumnExpression
from teradatamlspk.sql.types import *
from sqlalchemy.sql.sqltypes import NullType
from teradataml.dataframe.dataframe_utils import DataFrameUtils as tdml_DFUtils
from teradataml import DataFrame
from teradataml.dataframe.array import Array
from sqlalchemy.sql import literal_column, literal
from teradataml.dataframe.sql_functions import case
from sqlalchemy.sql.elements import BooleanClauseList, BinaryExpression
import datetime, decimal
from teradatamlspk.sql.types import Row
import re

class DataFrameUtils():

    @staticmethod
    def _tuple_to_list(args, arg_name):
        """
        Converts a tuple of string into list of string and multiple list of strings in a tuple
        to list of strings.

        PARAMETERS:
            args: tuple having list of strings or strings.

        EXAMPLES:
            tuple_to_list(args)

        RETURNS:
            list

        RAISES:
            Value error
        """
        if all(isinstance(value, str) for value in args):
            # Accept only strings in tuple.
            res_list = list(args)
        elif len(args) == 1 and isinstance(args[0], list):
            # Accept one list of strings in tuple.
            res_list = args[0]
        else:
            raise ValueError("'{}' argument accepts only strings or one list of strings".format(arg_name))
        return res_list

    @staticmethod
    def _get_columns_from_tuple_args(args, df_columns):
        """
        Converts a tuple of string, column expression or a list of strings/ column expression in a tuple
        to list of strings.

        PARAMETERS:
            args: tuple having list of strings/ column expression, strings or column expression.
            df_columns: list of column names in the DataFrame.

        EXAMPLES:
            _get_columns_from_tuple_args(args, df_columns)

        RETURNS:
            list
        """
        args = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        columns = []
        for arg in args:
            if arg not in df_columns:
                pass
            else:
                arg = arg if isinstance(arg, str) else arg._tdml_column.name
                columns.append(arg)
        return columns
    
    @staticmethod
    def _udf_col_to_tdml_col(col):
        """
        DESCRIPTION:
            Converts a Column containing UDF expression to teradataml ColumnExpression.

        PARAMETERS:
            col:
                Required Argument.
                Specifies the Column containing UDF expression.
                Types: Column

        RETURNS:
            ColumnExpression
        
        RAISES:
            AnalysisException: If the Column is not present in the DataFrame.

        EXAMPLES:
            >>> _udf_col_to_tdml_col(col)
        """
        args = []
        # Check if the UDF arguments of type Column are present in the DataFrame.
        for arg in col._udf_args:
            if isinstance(arg, Column):
                # Fetch the column name from the Column object.
                col_arg = arg._tdml_column.name
                # If column name is None, it means the Column is not present in the DataFrame and raise an exception.
                if col_arg is None:
                    raise AnalysisException("The derived Column is used by the UDF. Use 'withColumn()' to add the "\
                                            f"derived Column '{arg}' to the DataFrame before using it with UDF.",1)
                # Append the column name to the list of arguments.
                args.append(col_arg)
            else:
                args.append(arg)

        # Check if the UDF is a lambda function and reconstruct it.
        if col._udf and col._udf.__name__ == "<lambda>":
            # Extract the source code of the lambda function.
            col._udf = DataFrameUtils._get_lambda_source_code(col._udf)

        # Converts the Column containing UDF expression to teradataml ColumnExpression.
        from teradatamlspk.sql.utils import _get_tdml_type
        return _SQLColumnExpression(expression=None, udf=col._udf, udf_type=_get_tdml_type(col._udf_type),\
                                    udf_args=args, env_name = col._env_name, delimiter= col._delimiter,\
                                    quotechar=col._quotechar, udf_script = col._udf_script)
    
    @staticmethod
    def _get_lambda_source_code(lambda_udf, lambda_name=None):
        """
        DESCRIPTION:
            Function to extract the source code of a lambda function from 
            the udf() or register() function and reconstruct it.

        PARAMETERS:
            lambda_udf:
                Required Argument.
                Specifies the UDF lambda function.
                Types: function

            lambda_name:
                Optional Argument.
                Specifies the name of the lambda function.
                Types: str
                Default Value: None

        RETURNS:
            Function

        EXAMPLES:
            >>> DataFrameUtils._get_lambda_func_source_code(func)
        """
        # Extract the source code of the lambda function.
        udf_code = getsource(lambda_udf).lstrip()
        # Extract the variable name of the lambda function.
        var_name = udf_code.split('=')[0].strip() if lambda_name is None else lambda_name
        # Get the source code of the lambda function present inside the udf() or register() function.
        # eg. sum = udf(lambda x: x + 1, IntegerType()) -> sum = lambda x: x + 1
        # eg. spark.udf.register("sum", lambda x: x + 1) -> sum = lambda x: x + 1
        tree = ast.parse(udf_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                udf_code = f"{var_name} = {ast.unparse(node)}"
                lambda_udf.__source__ = udf_code
                lambda_udf.__name__ = var_name
                break
        return lambda_udf

    @staticmethod
    def check_value_subset_arg_compatiblity(df, value, column):
        """
        DESCRIPTION:
            Check the type compatibility of value with the DataFrame column.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the value to be checked for compatibility.
                Types: str

            column:
                Required Argument.
                Specifies the column name from the DataFrame.
                Types: str

        EXAMPLES:
            check_value_subset_arg_compatiblity(df, value, column)

        RETURNS:
            bool
        """
        # Check the type of value and assign the compatible type name to val_type.
        val_type = "bool" if isinstance(value, bool) else "int_float" if isinstance(value, (int, float)) else "str"
        # Fetch the column type from the DataFrame schema.
        col_type = df.schema[column].dataType
        # Check the compatibility of value and column type.
        is_compatible = any(isinstance(col_type, t) for t in COMPATIBLE_TYPES[val_type])
        return is_compatible
    
    def raise_duplicate_cols_warnings(only_r_prefix=False):
        """
        DESCRIPTION:
            Raise warnings for duplicate columns in the resultant joined DataFrame.

        PARAMETERS:
            only_r_prefix:
                Optional Argument.
                Specifies whether in the resultant DataFrame only 'r_' prefix is added to the duplicate column names.
                Types: bool
                Default: False

        RETURNS:
            None

        EXAMPLES:
            raise_duplicate_cols_warnings()
        """

        msg = "The DataFrames have common column names. To avoid ambiguity, the duplicate column names "\
              "in the resultant DataFrame from left and right DataFrames are prefixed with 'l_' and 'r_' respectively."
        
        r_msg = "The DataFrames have common column names. To avoid ambiguity, the duplicate column names "\
                "in the resultant DataFrame from right DataFrame are prefixed 'r_'."
        
        message = r_msg if only_r_prefix else msg
        warnings.simplefilter("always", UserWarning)
        warnings.warn(message, UserWarning)

    def _fix_null_type_col(res_df):
        """
        DESCRIPTION:
            Fixes the NullType columns in the DataFrame by inferring the actual column type from the database.
        
        PARAMETERS:
            res_df:
                Required Argument.
                Specifies the DataFrame with potential NullType columns.
                Types: teradatamlspk DataFrame

        RETURNS:
            DataFrame with fixed NullType columns.

        EXAMPLES:
            _fix_null_type_col(res_df)
        """
        # Get the SQL query from the DataFrame
        query = res_df._data.show_query()

        # Use column info from the query metadata for both regular and array columns.
        column_info = tdml_DFUtils._get_column_info_from_query(query)
        # Apply the correct types to NullType columns
        for col in res_df._metaexpr.c:
            if isinstance(col.type, NullType) or (col.type == NullType):
                col.type = column_info[col.name]

        return res_df

    def _handle_concat_operation_common(df, col):
        """
        DESCRIPTION:
            Internal function to handle concat operation for string and array columns by 
            checking the type of the first column and decides whether to perform 
            string concatenation or array concatenation.

        PARAMETERS:
            df:
                Required Argument.
                Specifies DataFrame instance.
                Type: teradataml DataFrame

            col:
                Required Argument.
                Specifies Column string or Column expression.
                Type: Column
        
        RETURNS:
            Tuple of (_SQLColumnExpression, bool)
            1. The resulting tdml column expression.
            2. Boolean flag indicating if the resulting expression currently has a NullType
               (so caller can trigger _fix_null_type_col after assign()).
        """
        # Extract the underlying teradataml column and list of columns to concat.
        first_col = col._tdml_column
        other_cols = col._concat_columns

        # If the first column has a concrete name and exists in the DataFrame's schema,
        # infer its type from DataFrame.dtypes. This allows us to differentiate
        # between string concatenation and array concatenation.
        first_col_name = first_col.name if first_col.name else None
        if first_col_name and first_col_name in df.columns:
            # get the column type from DataFrame schema
            col_type = df[first_col_name]._type

            # If the column's type includes ARRAY, perform element-wise array concatenation.
            if "ARRAY" in str(col_type):
                result = first_col
                for other_col in other_cols:
                    # Use tdml array_concat which merges arrays.
                    result = result.array_concat(other_col)

                is_null = isinstance(result.type, NullType)
                return result, is_null

            # Treat as strings and perform SQL string concatenation by default.
            # This is the common fallback whether we determined the column type
            # explicitly or the first column is unnamed / unknown in the DataFrame.
            concat_expr = first_col.concat("", *other_cols)
            is_null = isinstance(concat_expr.type, NullType)
            return concat_expr, is_null

    def _handle_array_operation(df, col):
        """
        DESCRIPTION:
            Internal function to handle array operation.

        PARAMETERS:
            df:
                Required Argument.
                Specifies DataFrame instance.
                Type: teradataml DataFrame

            col:
                Required Argument.
                Specifies Column string or Column expression.
                Type: Column

        RETURNS:
            _SQLColumnExpression
        """
        # Process the array_col elements
        elements = []

        # Handle PySpark-style single-argument form where the caller passes a list/tuple
        # of column names: array(['col1', 'col2']). In that case col._array_col may be a
        # sequence with one element which itself is a list/tuple. Unwrap it so the rest
        # of the resolution logic treats each inner item as a separate array element.
        array_items = col._array_col
        if len(array_items) == 1 and isinstance(array_items[0], (list)):
            array_items = array_items[0]

        # Resolve each item supplied to the array literal:
        # - If the item is a teraspark `Column` object, extract its underlying tdml column.
        # - If the item is a string, treat it as a column name and get the corresponding tdml column from the DataFrame.
        # - Otherwise treat the item as a literal value (number/boolean/etc.) and convert it
        #   to a SQLAlchemy literal expression wrapped in a tdml _SQLColumnExpression.
        for elem in array_items:
            if isinstance(elem, Column):
                # Column object already wraps a tdml column expression.
                elements.append(elem._tdml_column)
            elif isinstance(elem, str):
                # Column name provided as string.
                elements.append(df[elem])
            else:
                # Literal value (e.g. int/float); convert into a tdml column expression.
                # Inline the simple conversion to a SQL literal instead of calling a tiny helper.
                elements.append(_SQLColumnExpression(literal_column(elem) if isinstance(elem, str) else literal(elem)))
        # Create and return an Array object
        return Array(tuple(elements))

    @staticmethod
    def _prepare_tdml_column(df, col, **kwargs):
        """
        DESCRIPTION:
            Centralized helper to convert a teradatamlspk Column expression into a
            teradataml column expression and flags required by callers.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame to apply the Column expression on.
                Types: teradataml DataFrame

            col:
                Required Argument.
                Specifies the Column expression to convert.
                Types: teradatamlspk Column

            kwargs:
                col_with_null_type:
                    Optional Argument.
                    Specifies whether the resulting expression has NullType.
                    Default Value: None
                    Types: bool
                
                drop_cols:
                    Optional Argument.
                    Specifies whether to drop columns after assign.
                    Default Value: None
                    Types: bool

        RETURNS:
            tuple: (_SQLColumnExpression, bool, bool)
            1. The resulting tdml column expression.
            2. Boolean flag indicating if the resulting expression currently has a NullType.
            3. Boolean flag indicating whether to drop columns after assign.
        """
        col_with_null_type = kwargs.get("col_with_null_type", None)
        drop_cols = kwargs.get("drop_cols", None)

        # Priority: UDF > array_agg > array operations > concat > boolean expr > default
        if col._udf or col._udf_name:
            tdml_column = DataFrameUtils._udf_col_to_tdml_col(col)
            drop_cols = False
        elif col._array_col is not None and col._tdml_column is None:
            tdml_column = DataFrameUtils._handle_array_operation(df, col)
        elif col._concat_columns is not None:
            tdml_column, is_null = DataFrameUtils._handle_concat_operation_common(df, col)
            col_with_null_type = is_null
        elif col._reverse_column is not None:
            tdml_column = DataFrameUtils._handle_reverse_operation(df, col)
        elif DataFrameUtils._check_boolean_expression(col):
            tdml_column = case([(col._tdml_column, 1)], else_=0)
        else:
            # Default: direct tdml column
            tdml_column = col._tdml_column
            if isinstance(tdml_column, _SQLColumnExpression):
                tdml_column = DataFrameUtils._check_udf_array_col(df, tdml_column)
                if tdml_column._type is NullType or isinstance(tdml_column._type, NullType):
                    col_with_null_type = True

        return tdml_column, col_with_null_type, drop_cols

    @staticmethod
    def _check_boolean_expression(col):
        """
        DESCRIPTION:
            Check if the Column expression is a boolean expression.

        PARAMETERS:
            col:
                Required Argument.
                Specifies the Column expression to check.
                Types: Column

        RETURNS:
            bool: True if the Column expression is a boolean expression, False otherwise.
        """
        # Extract tdml column expression from Column
        _expr = col._tdml_column if hasattr(col, '_tdml_column') else None
        if _expr is None or (isinstance(_expr, _SQLColumnExpression) and _expr._udf_args):
            return False

        # Reuse the same heuristics as DataFrame._check_boolean_expression
        try:
            compiled = str(_expr.compile())
        except Exception:
            compiled = str(_expr)

        if isinstance(_expr.expression, BooleanClauseList) \
                or compiled.endswith('IS NULL') \
                or compiled.endswith('IS NOT NULL') \
                or re.search(r'[=<>]\s\d+$', compiled) \
                or re.search(r'= LENGTH\(.+?\) \+ 1$', compiled) \
                or re.search(r'LIKE\s', compiled) \
                or (isinstance(_expr.expression, BinaryExpression)
                    and any(re.search(f'\s{op}>$', str(_expr.expression.operator))
                        for op in ['ne', 'ge', 'gt', 'lt', 'le', 'eq'])):
            return True

        return False
    
    @staticmethod
    def _handle_explode_expr_column(column, df, _assign_expr={}, explode_col_count=None):
        """
        DESCRIPTION:
            Handles explode column expression operations for DataFrame select, withColumn and withColumns method.
        
        PARAMETERS:
            column:
                Required Argument.
                Specifies the Column with explode expression.
                Types: teradatamlspk Column

            df:
                Required Argument.
                Specifies the DataFrame to apply explode on.
                Types: teradataml DataFrame

            _assign_expr:
                Optional Argument.
                Specifies the assign expression dictionary to update with exploded columns.
                Types: dict

            explode_col_count:
                Optional Argument.
                Specifies the default column number for naming.
                Types: int

        RETURNS:
            tuple: (updated_df, updated_assign_expr, explode_col_count)

        EXAMPLES:
            _handle_explode_expr_column(column, df, assign_expr, 1)
        """        
        # The explode column expression is a tuple of (column, ordinality_flag).
        explode_expr = column._explode_col[0]
        ordinality_col = column._explode_col[1]

        # Get the tdml column for explode expression.
        exploded_col = explode_expr if isinstance(explode_expr, str) else explode_expr._tdml_column

        # If alias name is not passed, create a default column name for exploded column and position column.
        alias_exploded_arr = column.alias_name if column.alias_name else f"exploded_col{explode_col_count}"
        alias_pos = f"pos{explode_col_count}"
        if explode_col_count is not None:
            explode_col_count += 1

        # Explode the array column.
        if ordinality_col:
            exp_df = df.unnest(exploded_col, ordinality=True, array_col_alias=alias_exploded_arr, 
                               key_col_alias="tdml_key_col", pos_col_alias=alias_pos)
        else:
            exp_df = df.unnest(exploded_col, array_col_alias=alias_exploded_arr, key_col_alias="tdml_key_col")

        # Drop the temporary key columns.
        updated_df = exp_df.drop(columns=["tdml_key_col"])

        # Assign the exploded column and position column to the assign expression.
        if column._explode_col[1]:
            _assign_expr[alias_pos] = exp_df[alias_pos]-1
        _assign_expr[alias_exploded_arr] = exp_df[alias_exploded_arr]
        
        return updated_df, _assign_expr, explode_col_count
    
    @staticmethod
    def _handle_reverse_operation(df, col):
        """
        DESCRIPTION:
            Internal function to handle reverse operation for array and regular column.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame for reverse operation.
                Type: teradataml DataFrame

            col:
                Required Argument.
                Specifies Column Expression for reverse operation.
                Type: teradatamlspk Column

        RETURNS:
            _SQLColumnExpression
        """
        col = col._tdml_column
        col_name = col.name if col.name else None
        col_type = df[col_name]._type

        # If column is of type ARRAY, call array_reverse, else reverse over string type column.
        if "ARRAY" in str(col_type):
            col._type = col_type
            return col.array_reverse()

        return col.reverse()
    
    @staticmethod
    def _check_udf_array_col(df, tdml_column):
        """
        DESCRIPTION:
            Internal function to check if the tdml column is an udf array column 
            and fix the NullType columns.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the teradataml DataFrame.
                Type: teradataml DataFrame

            tdml_column:
                Required Argument.
                Specifies Column expression.
                Type: teradataml ColumnExpression

        RETURNS:
            _SQLColumnExpression
        """
        # If the teradataml column contains _udf_args, the its array function called using UDF.
        # If its type is NullType, then fetch the column expression from DataFrame to get correct type.
        if tdml_column._udf_args and isinstance(tdml_column._type, NullType):
            # With column name fetch the column expression from DataFrame to get correct type.
            tdml_column._type = df[tdml_column._udf_args[0]]._type
        
        return tdml_column
    
    @staticmethod
    def _convert_str_timestamp_to_timestamp_format(val, drop_tz=False):
        """
        DESCRIPTION:
            Parse a timestamp value using 'datetime.datetime.fromisoformat' only.
            If parsing fails the original value is returned unchanged.
            When 'drop_tz' is True any timezone info on the parsed datetime is removed.

        PARAMETERS:
            val:
                Required Argument.
                Specifies the value to parse (string or datetime).
                Types: str, datetime.

            drop_tz:
                Optional Argument.
                Specifies whether to drop timezone information if present.
                Types: bool
                Default Value: False

        RETURNS:
            datetime or original value when parsing fails.

        EXAMPLES:
            >>> DataFrameUtils._convert_str_timestamp_to_timestamp_format('2024-01-01 10:20:30')
            datetime.datetime(2024, 1, 1, 10, 20, 30)
            >>> DataFrameUtils._convert_str_timestamp_to_timestamp_format('2024-01-01T10:20:30+05:00', drop_tz=True)
            datetime.datetime(2024, 1, 1, 10, 20, 30)
            >>> DataFrameUtils._convert_str_timestamp_to_timestamp_format('2024-01-01T10:20:30+05:00')
            datetime.datetime(2024, 1, 1, 10, 20, 30, tzinfo=datetime.timezone(datetime.timedelta(seconds=18000)))
        """
        if isinstance(val, datetime.datetime):
            # Value already a datetime; optionally drop timezone info.
            return val.replace(tzinfo=None) if drop_tz and val.tzinfo else val
        
        # Parse using fromisoformat which accepts 'YYYY-MM-DD HH:MM:SS[.ffffff][+HH:MM]'
        dt = datetime.datetime.fromisoformat(val.strip())
        # Successfully parsed; drop timezone if requested.
        return dt.replace(tzinfo=None) if drop_tz and dt.tzinfo else dt
    
    @staticmethod
    def _convert_interval_value(dtype, val):
        """
        DESCRIPTION:
            Convert Teradata/driver returned interval literal strings into Spark-like
            Python objects for Row construction.

            - IntervalYearToMonthType  -> int (total number of months)
              Spark behavior: make_ym_interval / ArrayType(YearMonthIntervalType()) yields
              an integer representing total months.
            - IntervalDayToSecondType  -> datetime.timedelta
              Spark behavior: make_dt_interval / ArrayType(DayTimeIntervalType()) yields
              a datetime.timedelta instance.

        PARAMETERS:
            dtype:
                Required Argument.
                Interval data type instance
                Types: IntervalYearToMonthType, IntervalDayToSecondType

            val:
                Required Argument.
                Raw value coming from database / driver.
                Types: str, int, None

        RETURNS:
            Interval type


        EXAMPLES:
            >>> DataFrameUtils._convert_interval_value(IntervalYearToMonthType(), '2-03')
            27
            >>> DataFrameUtils._convert_interval_value(IntervalDayToSecondType(), '1 00:00:00')
            datetime.timedelta(days=1)
        """
        if val is None:
            return None

        # YEAR TO MONTH -> total months as int
        from teradatamlspk.sql.types import IntervalYearToMonthType, IntervalDayToSecondType

        if isinstance(dtype, IntervalYearToMonthType):
            # Expected format: optional sign, YEARS-MONTHS e.g. '2-03', '-2-03'
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                raw = val.strip()
                m = re.fullmatch(r"([+-]?)(\d+)-(\d+)", raw)
                if m:
                    sign, years, months = m.groups()
                    total = int(years) * 12 + int(months)
                    if sign == '-':
                        total = -total
                    return total
            return val  # leave unchanged if it doesn't match expected pattern

        # DAY TO SECOND -> datetime.timedelta
        if isinstance(dtype, IntervalDayToSecondType):
            # Return the timedelta type by calling the existing parser.
            return tdml_DFUtils._parse_interval(val)

        # Not an interval type we recognize.
        return val
  

    # Mapping of Spark-like data types to simple Python conversion callables.
    _TYPE_MAP = {
    TimestampType: lambda v: DataFrameUtils._convert_str_timestamp_to_timestamp_format(v, drop_tz=False),
    TimestampNTZType: lambda v: DataFrameUtils._convert_str_timestamp_to_timestamp_format(v, drop_tz=True),
    DateType: lambda v: v if isinstance(v, datetime.date) else datetime.datetime.strptime(v, "%Y-%m-%d").date(),
    (IntegerType, LongType, ShortType, ByteType): int,
    (FloatType, DoubleType): lambda v: float(v.replace("E ", "E")) if isinstance(v, str) else float(v),
    DecimalType: decimal.Decimal,
    (StringType, CharType, VarcharType): str,
    BooleanType: lambda v: v if isinstance(v, bool) else str(v).lower() in ("1", "true"),
    IntervalYearToMonthType: lambda v: DataFrameUtils._convert_interval_value(IntervalYearToMonthType(), v),
    IntervalDayToSecondType: lambda v: DataFrameUtils._convert_interval_value(IntervalDayToSecondType(), v)
    }
    
    @staticmethod
    def _convert_array_value(data_type, val):
        """
        DESCRIPTION:
            Convert a value (array or scalar). Name keeps 'array' for historical/user preference.
            If data_type is ArrayType, parses and converts each element recursively; otherwise
            applies scalar type mapping from _TYPE_MAP (including NULL / empty normalization).

        PARAMETERS:
            data_type:
                Required Argument.
                Specifies the data type (ArrayType or scalar type).
                Types: DataType.

            val:
                Required Argument.
                Specifies the value to convert.
                Types: any.

        RETURNS:
            Converted Python value (list for arrays)

        EXAMPLES:
            >>> DataFrameUtils._convert_array_value(ArrayType(IntegerType()), '(1,2,3)')
            [1, 2, 3]
            >>> DataFrameUtils._convert_array_value(IntegerType(), 1)
            1
            >>> DataFrameUtils._convert_array_value(TimestampType(), '2024-01-01 10:20:30')
            datetime.datetime(2024, 1, 1, 10, 20, 30)
        """
        # If the data_type is ArrayType, handle array conversion.
        if isinstance(data_type, ArrayType):
            # Normalize raw value into a Python sequence (seq).
            # Convert each element according to the elementType assuming it is scalar.
            # Preserve None (NULL) arrays.
            if val is None:
                return None
            if isinstance(val, (list, tuple)):
                # Already a Python sequence
                seq = val
            elif isinstance(val, str):
                # Database supplied a string representation like '(1,2,3)' or "('a','b')".
                seq = DataFrameUtils._parse_array_representation(val)
            else:
                # Single scalar was given where an array is expected; wrap it.
                seq = [val]
            # Recursively convert each element to its target Python type.
            return [DataFrameUtils._convert_array_value(data_type.elementType, v) for v in seq]

        # For non-array types we map the logical dtype instance to a converter
        # function stored in _TYPE_MAP. The map keys are either a single type
        # class (e.g., TimestampType) or a tuple grouping related numeric types.
        if val is None:
            return None  # Preserve NULL scalars.
        for t, fn in DataFrameUtils._TYPE_MAP.items():
            # Check if data_type is an instance of the mapped type or one of the grouped types.
            if isinstance(data_type, t): 
                # Handle NULL strings and empty strings as None.
                if isinstance(val, str):
                    if val.strip().upper() == 'NULL':  # Only handle 'NULL', not empty strings
                        return None
                return fn(val)
        # No matching data_type mapping found; return value unchanged.
        return val
    
    @staticmethod
    def _parse_array_representation(raw):
        """
        DESCRIPTION:
            Parse a Teradata array string representation '(val1,val2,...)' into a 
            Python list of strings. Surrounding single quotes on individual elements 
            are stripped.

        PARAMETERS:
            raw:
                Required Argument.
                Specifies the raw string representation 
                returned by the database.
                Types: str

        RETURNS:
            List of element strings

        EXAMPLES:
            >>> DataFrameUtils._parse_array_representation('(1,2,3)')
            ['1', '2', '3']
            >>> DataFrameUtils._parse_array_representation("('a','b','c')")
            ['a', 'b', 'c']
            >>> DataFrameUtils._parse_array_representation("(12:34:56, 23:45:01)")
            ['12:34:56', '23:45:01']
        """
        
        # Normalize the raw string: trim whitespace and remove surrounding parentheses if present.
        s = raw.strip()
        if not s:
            # String is empty after trimming; nothing to parse.
            return []
        s = s[1:-1].strip() if s.startswith("(") and s.endswith(")") else s
        if not s:
            # Content was only parentheses or whitespace; return empty list.
            return []

        # Parse the string handling quoted fields with possible escaped quotes.
        tokens, buf, in_quote = [], [], False
        for i, ch in enumerate(s):
            if ch == "'":
                # Toggle quote state or handle escaped single quote inside quoted section.
                # Support doubled single quotes inside quoted strings ('' -> ').
                if in_quote and i + 1 < len(s) and s[i + 1] == "'":
                    buf.append("'")  # Escaped quote.
                    continue  # Skip next quote.
                in_quote = not in_quote
            elif ch == "," and not in_quote:
                # Comma outside quotes terminates current token.
                token = "".join(buf)
                tokens.append(token)
                buf.clear()
                continue
            # Accumulate character into current buffer.
            buf.append(ch)
        if buf:
            # Flush remaining buffer as final token.
            tokens.append("".join(buf))

        # Strip surrounding single quotes from each token when both first and last char are quotes.
        return [t[1:-1] if len(t) >= 2 and t[0] == "'" and t[-1] == "'" else t for t in tokens]

    @staticmethod
    def _build_row_with_converted_types(columns, dtypes, row_dict):
        """
        DESCRIPTION:
            Build a Row object converting each field value according 
            to its corresponding data type.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the ordered list of column names.
                Types: list[str]

            dtypes:
                Required Argument.
                Specifies the ordered list of data types matching columns.
                Types: list[DataType]

            row_dict:
                Required Argument.
                Specifies a dictionary mapping column names to raw values.
                Types: dict

        RETURNS:
            Row instance with converted values.

        EXAMPLES:
            >>> DataFrameUtils._build_row_with_converted_types(columns, dtypes, row_dict)
        """
        converted = {}
        for col, data_type in zip(columns, dtypes):
            # Get the raw value from the row_dict
            raw_val = row_dict.get(col)

            # For array types, if any value is None, pyspark skips the column entry in the row object.
            # So we handle None arrays by skipping the column.
            if isinstance(data_type, ArrayType):
                if raw_val is None:
                    converted[col] = None
                    continue
            # Convert the raw value according to its data_type in the below format.
            # converted[column name] = <converted value>
            # Example:
            # For ArrayIntegerType: converted[column_name] = [1, 2, 3]
            # For ArrayStringType: converted[column_name] = ['a', 'b', 'c']
            converted[col] = DataFrameUtils._convert_array_value(data_type, raw_val)

        # Return a Row object constructed from the converted dictionary.
        return Row(**converted)
    
    def _handle_exploded_dataframe(df, colname, col, colMap={}):
        """
        DESCRIPTION:
            Internal function to handle exploded DataFrame for withColumn and withColumns method.
        
        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame to apply explode on.
                Types: teradataml DataFrame

            colname:
                Required Argument.
                Specifies the column name for exploded column.
                Types: str

            col:
                Required Argument.
                Specifies the Column with explode expression.
                Types: teradatamlspk Column

            colMap:
                Optional Argument.
                Specifies the column map dictionary (Only for withColumns method).
                Default Value: {}
                Types: dict

        RETURNS:
            teradataml DataFrame with exploded column.
        """
        # Track if column exists in DataFrame and its position for maintaining order
        cols_list = df.columns
        col_exists = colname in cols_list
        if col_exists:
            df = df.drop(columns=[colname])
        df, colMap, _ = DataFrameUtils._handle_explode_expr_column(col.alias(colname), df, colMap)
        # Select columns in original order
        df = df.select(cols_list) if col_exists else df
        return df
