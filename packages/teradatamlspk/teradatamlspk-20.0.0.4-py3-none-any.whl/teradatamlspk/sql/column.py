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

from teradatamlspk.sql.utils import _get_tdml_type

_get_other = lambda other: other._tdml_column if isinstance(other, Column) else other
from teradataml.dataframe.sql import _SQLColumnExpression
from sqlalchemy import bindparam, func, literal_column, literal
from teradatamlspk.sql.constants import SQL_NAME_TO_SPARK_TYPES
from teradatamlspk.sql.types import TimestampNTZType, TimestampType
from teradataml.dataframe.sql_functions import case as case_when
import math
from teradatasqlalchemy import VARCHAR, CHAR


class Column:
    """ teradatamlspk DataFrame Column. """
    __or__ = lambda self, other: Column(tdml_column=self._tdml_column | _get_other(other))
    __and__ = lambda self, other: Column(tdml_column=self._tdml_column & _get_other(other))
    __ne__ = lambda self, other: Column(tdml_column=self._tdml_column != _get_other(other))
    __truediv__ = lambda self, other: Column(tdml_column=(self._tdml_column / _get_other(other)))
    __floordiv__ = lambda self, other: Column(tdml_column=(self._tdml_column // _get_other(other)))
    __mod__ = lambda self, other: Column(tdml_column=(self._tdml_column % _get_other(other)))
    desc = lambda self: Column(tdml_column=self._tdml_column.desc())
    asc = lambda self: Column(tdml_column=self._tdml_column.asc())
    nulls_first = lambda self: Column(tdml_column=self._tdml_column.nulls_first())
    nulls_last = lambda self: Column(tdml_column=self._tdml_column.nulls_last())
    desc_nulls_first = lambda self: Column(tdml_column=self._tdml_column.desc().nulls_first())
    desc_nulls_last = lambda self: Column(tdml_column=self._tdml_column.desc().nulls_last())
    asc_nulls_first = lambda self: Column(tdml_column=self._tdml_column.asc().nulls_first())
    asc_nulls_last = lambda self: Column(tdml_column=self._tdml_column.asc().nulls_last())
    contains = lambda self, other: Column(tdml_column=self._tdml_column.str.contains(
        other._tdml_column if isinstance(other, Column) else other)==True)
    like = lambda self, other: Column(tdml_column=self._tdml_column.like(other))
    ilike = lambda self, other: Column(tdml_column=self._tdml_column.ilike(other))
    rlike = lambda self, other: Column(tdml_column=self._tdml_column.rlike(other))
    substr = lambda self, startPos, length: Column(tdml_column=self._tdml_column.substr(_get_other(startPos), _get_other(length)))
    startswith = lambda self, other: Column(tdml_column=self._tdml_column.startswith(
        other._tdml_column if isinstance(other, Column) else other))
    endswith = lambda self, other: Column(tdml_column=self._tdml_column.endswith(
        other._tdml_column if isinstance(other, Column) else other))
    isNull = lambda self: Column(tdml_column=self._tdml_column.isna()==1)
    isNotNull = lambda self: Column(tdml_column=self._tdml_column.notna()==1)
    bitwiseAND = lambda self, other: Column(tdml_column= self._tdml_column.bitand(
        other._tdml_column if isinstance(other, Column) else other))
    bitwiseOR = lambda self, other: Column(tdml_column= self._tdml_column.bitor(
        other._tdml_column if isinstance(other, Column) else other))
    bitwiseXOR = lambda self, other: Column(tdml_column= self._tdml_column.bitxor(
        other._tdml_column if isinstance(other, Column) else other))
    isin = lambda self, *cols: Column(tdml_column=self._tdml_column.isin(cols[0] if len(cols) == 1 and isinstance(cols[0], list) else list(cols)))
    between = lambda self, lowerBound, upperBound: Column(tdml_column= (self._tdml_column >= _get_other(lowerBound)) & (self._tdml_column <= _get_other(upperBound)))
    when = lambda condition, value: Column(
        tdml_column=_SQLColumnExpression(case((_get_tdml_col(condition).expression, value))))

    def __init__(self, jc=None, **kwargs):
        self.__map = {}
        self._tdml_column = _SQLColumnExpression(jc) if jc else kwargs.get("tdml_column")
        self.astype = self.cast
        self.alias_name = kwargs.get("alias_name", None)

        # Store _SQLColumnExpression.
        self.expr_ = kwargs.get("expr_")
        self.agg_func_params = kwargs.get("agg_func_params")
        self._udf = kwargs.get("udf", None)
        self._udf_type = kwargs.get("udf_type", None)
        self._udf_args = kwargs.get("udf_args", None)
        self._env_name = kwargs.get("env_name", None)
        self._udf_name = kwargs.get("udf_name", None)
        self._udf_script = kwargs.get("udf_script", None)
        self._delimiter = kwargs.get("delimiter", None)
        self._quotechar = kwargs.get("quotechar", None)
        self._array_col = kwargs.get("array_col", None)
        self._concat_columns = kwargs.get("concat_columns", None)
        self._reverse_column = kwargs.get("reverse_column", None)
        self._explode_col = kwargs.get("explode_expr", None)

    def alias(self, *alias, **kwargs):
        self.alias_name = alias[0]
        return self

    @property
    def name(self):
        """ Property to return the name of the column. """
        return self._tdml_column.name

    @property
    def expression(self):
        """ Property to return the underlying expression. """
        return self._tdml_column.expression

    def __repr__(self):
        """ String representation of DataFrame Column. """
        if self._udf is not None:
            return "Column<'{}'>".format(self._udf.__name__)
        elif self._udf_name is not None:
            return "Column<'{}'>".format(self._udf_name)
        elif self._array_col is not None:
            return "Column<'{}'>".format(self._array_col)
        elif self._explode_col is not None:
            func_name = "posexplode" if self._explode_col[1] else "explode"
            return f"Column<'{func_name}({self._explode_col[0]})'>"
        elif self.alias_name is not None:
            return "Column<'{}'>".format(self.alias_name)
        return "Column<'{}'>".format(self._tdml_column.compile())

    def __getattr__(self, item):
        """ Returns an attribute of the DataFrame. """
        if item in self.__map:
            return lambda *args, **kwargs: self.__process_analytic_function(*args, **kwargs, _f_n_internal=item)

        return Column(tdml_column=getattr(self._tdml_column, item))

    def __process_analytic_function(self, *args, **kwargs):
        """ Internal function to process analytic function. """

        # Get the function name.
        function_name = kwargs.pop("_f_n_internal")

        # Get the available mapper for the function.
        _spark_tdml_argument_map = self.__map.get(function_name).get("func_params")

        # Get the arguments.
        _spark_args = list(_spark_tdml_argument_map.keys())

        # Convert positional arguments also to keyword arguments.
        spark_arguments_values = {}
        for index, arg in enumerate(args):
            spark_arguments_values[_spark_args[index]] = arg

        # Combine both keyword arguments and positional arguments.
        spark_arguments_values.update(kwargs)

        # Convert all the arguments to teradataml arguments.
        tdml_arguments_values = {_spark_tdml_argument_map[k]:v for k,v in spark_arguments_values.items()}
        tdml_func_name = self.__map[function_name]["tdml_func"]

        return Column(tdml_column=getattr(self._tdml_column, tdml_func_name)(**tdml_arguments_values))

    def __add__(self, other):
        """
        Compute the sum between two ColumnExpressions using +.
        This is also the concatenation operator for string-like columns.
        """
        return Column(tdml_column=self._tdml_column+_get_other(other))

    def __sub__(self, other):
        """
        Compute the difference between two ColumnExpressions using -.
        """
        return Column(tdml_column=self._tdml_column-_get_other(other))

    def __mul__(self, other):
        """ Compute the product between two ColumnExpressions using *. """
        return Column(tdml_column=self._tdml_column * _get_other(other))

    def __gt__(self, other):
        """ Compare the ColumnExpressions to check if one ColumnExpression has values
        greater than the other or not. """
        return Column(tdml_column=self._tdml_column > _get_other(other))

    def __ge__(self, other):
        """ Compare the ColumnExpressions to check if one ColumnExpression has values
        greater than or equal to the other or not. """
        return Column(tdml_column=self._tdml_column >= _get_other(other))

    def __lt__(self, other):
        """ Compare the ColumnExpressions to check if one ColumnExpression has values
        lesser than the other or not. """
        return Column(tdml_column=self._tdml_column < _get_other(other))

    def __le__(self, other):
        """ Compare the ColumnExpressions to check if one ColumnExpression has values
        lesser than or equal to the other or not. """
        return Column(tdml_column=self._tdml_column <= _get_other(other))

    def __eq__(self, other):
        """ Compare the ColumnExpressions to check if one ColumnExpression has values
        equal to the other or not. """
        return Column(tdml_column=self._tdml_column == _get_other(other))

    def when(self, condition, value):
        # Function is valid only on top of function when.
        self._tdml_column.expression.whens.append((condition._tdml_column.expression,
                                                  value._tdml_column.expression if isinstance(value, Column) else bindparam('value', value))
                                                  )
        return self

    def otherwise(self, value):
        # It will be triggered on top of case.
        self._tdml_column.expression.else_ = value._tdml_column.expression if isinstance(value, Column) else bindparam('value', value)
        return self

    def cast(self, dataType, format=None):
        """
        DECSRIPTION:
            Casts the column into type dataType.

        PARAMETERS:
            dataType (str or DataType):
                The target data type to cast the column to.
            format (str, optional):
                The format string to use for casting, if applicable.

        RETURNS:
            Column:
                A new Column object with the casted data type.

        NOTES:
            - If dataType is a string, it is mapped to the corresponding Spark SQL type.
            - If dataType is TimestampNTZType and format is provided, the column is casted to a timestamp using the format.
            - If dataType is TimestampType and format is provided, the column is casted to a timestamp using _format_date_string_cast.
            - Otherwise, the column is casted to the specified data type directly.
        """
        
        if isinstance(dataType, str):
            dataType = SQL_NAME_TO_SPARK_TYPES.get(dataType.upper())

        if isinstance(dataType, TimestampNTZType):
            if format:
                from teradatamlspk.sql.functions import _format_date_string
                return Column(tdml_column=self._tdml_column.to_timestamp(_format_date_string(format)))
            return Column(tdml_column=self._tdml_column.to_timestamp())
        
        if isinstance(dataType, TimestampType) and format:
            from teradatamlspk.sql.functions import _format_date_string_cast
            return Column(tdml_column=self._tdml_column.cast(_get_tdml_type(dataType), _format_date_string_cast(format)))
        
        return Column(tdml_column=self._tdml_column.cast(_get_tdml_type(dataType), format))

    def over(self, window):
        """ Function to get window aggregates. """

        # Extract window aggregate params.
        window_params = window.get_params()

        # Convert tdmlspk Column to tdml columns.
        if window_params["partition_columns"]:
            window_params["partition_columns"] = [col._tdml_column if isinstance(col, Column) else col
                                                  for col in window_params["partition_columns"]]

        if window_params["order_columns"]:
            window_params["order_columns"] = [col._tdml_column if isinstance(col, Column) else col
                                              for col in window_params["order_columns"]]

        # Prepare tdml Column with Window aggregate.
        tdml_window = self.expr_.window(**window_params)

        # Trigger regular window aggregate.
        agg_func_params = {**self.agg_func_params}
        func_name = agg_func_params.pop("name")
        tdml_col_expr = getattr(tdml_window, func_name)(**agg_func_params)

        return Column(tdml_column=tdml_col_expr)
    def eqNullSafe(self, other):
        """
        DESCRIPTION:
            Equality test that is safe for null values.
            Note: teradatamlspk considers NaN value as NULL.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Column, LiteralType, DecimalLiteral, DateTimeLiteral
                Type: Column, LiteralType, DecimalLiteral, DateTimeLiteral.
        EXAMPLES:
            # Load the data to run the example.
            >>> import pandas as pd
            >>> pandas_df = pd.DataFrame({"id": [0, 1, 2], "col1": [3, None, None], "col2": [2, None, 1]})
            >>> from teradataml import copy_to_sql
            >>> copy_to_sql(pandas_df, table_name='new_tab', if_exists='replace')
            >>> df1 = teraspark_session.createDataFrame('new_tab')
            >>> df1.show()
            +--+----+----+
            |id|col1|col2|
            +--+----+----+
            | 2|None| 1.0|
            | 1|None|None|
            | 0| 3.0| 2.0|
            +--+----+----+

            # Example 1: Equate Null value with 'col1'.
            >>> df1.select(df1['col1'].eqNullSafe(None).alias('r'), df1.col1, df1.col2).show()
            +-+----+----+
            |r|col1|col2|
            +-+----+----+
            |1|None| 1.0|
            |1|None|None|
            |0| 3.0| 2.0|
            +-+----+----+
        """
        if isinstance(other, Column):
            return Column(tdml_column=case_when(
                [((self._tdml_column.isnull() == True) & (other._tdml_column.isnull() == True), 1),
                 ((self._tdml_column == other._tdml_column), 1)], else_=0))
        if other is None or (isinstance(other, (int, float)) and math.isnan(other)):
            return Column(tdml_column=case_when(
                [((self._tdml_column.isnull() == True), 1)], else_=0))
        return Column(tdml_column=case_when([((self._tdml_column == other), 1)], else_=0))
