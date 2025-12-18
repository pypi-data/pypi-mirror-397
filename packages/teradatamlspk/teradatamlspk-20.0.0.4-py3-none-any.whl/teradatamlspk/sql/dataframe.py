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
from collections import OrderedDict
from teradataml.dataframe.dataframe import DataFrame as tdml_DataFrame
from teradataml.dataframe.sql import _SQLColumnExpression
from teradataml.dataframe.setop import td_minus, td_intersect
from teradataml.dataframe.sql_functions import case
from teradataml.common.utils import UtilFuncs
from teradataml.dbutils.dbutils import db_drop_view
from teradataml.dataframe.setop import concat
from teradataml import TeradataConstants, execute_sql
from prettytable import PrettyTable

import sqlalchemy
from sqlalchemy.sql import literal_column, literal
from sqlalchemy.sql.elements import BooleanClauseList, BinaryExpression
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy import func
import teradatasqlalchemy
from teradatamlspk.sql.constants import SPARK_TYPE_CLASS_TO_SQL_NAME, TD_TO_SPARK_TYPES
from teradatamlspk.sql.utils import AnalysisException
from teradatamlspk.sql.column import Column
from teradatamlspk.sql.dataframe_utils import DataFrameUtils as df_utils
from teradatamlspk.storagelevel import StorageLevel
from teradatamlspk.common.constants import _SPARK_TO_TDML_FN_MAPPER as FN_MAPPER, _DataFrameReturnDF
from teradatamlspk.sql.readwriter import DataFrameWriter
from teradatamlspk.sql.types import Row, StructField, StructType
from teradatamlspk.sql.utils import _get_spark_type
from teradataml.table_operators.table_operator_util import _TableOperatorUtils
import math, re
from functools import reduce
from teradatasqlalchemy.types import *
from teradatamlspk.sql.constants import TD_ARRAY_TO_ELEM

class DataFrame:
    
    """ The teraspark DataFrame enables data manipulation, exploration, and analysis
        on tables, views, and queries on Teradata Vantage.
    """
    def __init__(self, data=None):
        self._data = data
        self.__get_tdml_column = lambda col: col._tdml_column

        self.corr = lambda col1, col2: next(
            self._data.assign(
                n=self._data[col1].corr(self._data[col2]), drop_columns=True).itertuples(name=None))[0]
        self.cov = lambda col1, col2: next(
            self._data.assign(
                n=self._data[col1].covar_samp(self._data[col2]), drop_columns=True).itertuples(name=None))[0]

        # where and filter are aliases.
        self.where = self.filter

        self.take = lambda num: self.head(num)
        self.first = lambda: self.head()

        # sort, sortWithinPartitions and orderBy are aliases.
        self.orderBy = self.sort
        self.sortWithinPartitions = self.sort

        # unpivot and melt are aliases.
        self.melt = self.unpivot

        #unionAll and union are aliases
        self.unionAll = self.union

        # createTempView, createOrReplaceTempView, createGlobalTempView, createOrReplaceGlobalTempView and registerTempTable will be alias.
        # we don't support multiple sessions in teraspark
        self.createTempView = lambda name: self._data.create_temp_view(name)
        self.createGlobalTempView = self.createTempView
        self.createOrReplaceGlobalTempView = self.createOrReplaceTempView
        self.registerTempTable = self.createOrReplaceTempView
        self._ml_params = {}

    cache = lambda self: self
    checkpoint = lambda self, eager=True: self
    localCheckpoint = lambda self, eager=True: self
    unpersist = lambda self, blocking=True: self
    collect = lambda self: list(self.toLocalIterator())
    toDF = lambda self, *cols: self.withColumnsRenamed(dict(zip(self.columns, cols)))
    isEmpty = lambda self: self.shape[0] == 0
    colRegex = lambda self, colName: [getattr(self, column) for column in self._tdml_filter(regex=colName).columns]
    hint = lambda self, name, *parameters: self
    coalesce = lambda self, numPartitions: self
    repartition = lambda self, numPartitions, *cols: self
    repartitionByRange = lambda self, numPartitions, *cols: self
    sameSemantics = lambda self, other: False
    semanticHash = lambda self: 0
    inputFiles = lambda self: []
    isLocal = lambda self: False    
    foreachPartition = lambda self, f: f(self.toLocalIterator())
    transform = lambda self, func, *args, **kwargs: func(self, *args, **kwargs)
    alias = lambda self, alias: DataFrame(self._data.alias(alias))

    def head(self, n = None):
        """ Returns the first n rows."""
        num = 1 if n is None else n
        df = self._data.head(num)
        # If it has array types, then we need to convert the types.
        if self._has_array_types():
            # Gather schema data types for conversion.
            field_types = [f.dataType for f in self.schema.fields]
            recs = []
            for rec in df.itertuples(name=None):
                row_dict = dict(zip(self.columns, rec))
                recs.append(df_utils._build_row_with_converted_types(self.columns, field_types, row_dict))
        else:
            recs = [Row(**rec._asdict()) for rec in df.itertuples()]

        # Return single row or list based on n and length
        if not recs:
            return None
        return recs[0] if n is None else recs

    def show(self, n = 20, truncate = True, vertical = False):
        """ Function to show the DataFrame. """
        tdml_df = self._data
        # If it has ml params, then it should be show in different way.
        if self._ml_params:
            from sqlalchemy import func
            first_col, other_cols = self._ml_params["inputCols"][0], self._ml_params["inputCols"][1:]
            inp_cols = [literal_column(first_col)]
            for other_col in other_cols:
                inp_cols = inp_cols + [',', literal_column(other_col)]
            tdml_df = tdml_df.assign(**{self._ml_params["outputCol"]: func.concat('[', *inp_cols, ']')})

        # If truncate set to True then truncate strings longer than 20 chars.
        # If set to a number greater than zero then truncate strings to length truncate.
        if isinstance(truncate, bool):
            trunc = 20 if truncate else None
        else:
            trunc= truncate if truncate>0 else None
        data = []

        # Instead of retrieving "n" records, retrieve "n+1" records.
        # If variable data has "n+1" records, then the DataFrame has more
        # than "n" records. So, print a message at end of table.
        for rec in tdml_df.itertuples(name=None, num_rows=n+1):
            data.append(Row(**{k: str(val)[:trunc] for k,val in zip(tdml_df.columns, rec)}))

        # Print dataframe vertically or in tabular format.
        if vertical:
            max_len = max(len(col) for col in self.columns)
            #Print rows vertically as one line per column value.
            for i,row in enumerate(data):
                # index starts from 0.
                if i ==n:
                    break
                print(f"-RECORD {i}"+"-" * (max_len + 5))
                for col in self.columns:
                    # left aligned the columns wrt col having max length .
                    print(f"{str(col).ljust(max_len)} | {row[col]}")
        else:
            _table = PrettyTable(align='r', padding_width=0)
            for _index, rec in enumerate(data):
                # index starts from 0.
                if _index == n:
                    break
                _table.add_row(rec)
            _table.field_names = tdml_df.columns
            print(_table)

        if(len(data) > n):
            print(f"only showing top {n} rows")

    def __repr__(self):
        """ String representation of teraspark DataFrame. """
        _iter = map(lambda c: "{}: {}".format(c[0], c[1].lower()), self._data._column_names_and_types)
        return "{}[{}]".format(self.__class__.__name__, ", ".join(_iter))

    def __str__(self):
        """ String representation of teraspark DataFrame. """
        return self.__repr__()

    @property
    def dtypes(self):
        """Returns a list of (column name, Spark SQL type name in lowercase) tuples."""
        dtype_result = []
        for col in self._metaexpr.c:
            # If the column is a NullType, then its data type is void.
            if isinstance(col.type, sqlalchemy.sql.sqltypes.NullType):
                sql_name = "void"
            # If the column is a BYTEINT type, then its data type is boolean.
            elif isinstance(col.type, teradatasqlalchemy.types.BYTEINT):
                sql_name = "boolean"
            # If the column is a DECIMAL type, then its data type is decimal with precision and scale.
            elif isinstance(col.type, teradatasqlalchemy.types.DECIMAL):
                sql_name = f"decimal({col.type.precision},{col.type.scale})"
            # If the column is of TIMESTAMP type, then check if it has timezone or not
            # and assign the corresponding data type.
            elif isinstance(col.type, teradatasqlalchemy.types.TIMESTAMP):
                sql_name = "timestamp" if col.type.timezone else "timestamp_ntz"
            # If the column is of ARRAY type, then its data type is array with element type.
            elif type(col.type) in TD_ARRAY_TO_ELEM:
                sql_name = type(col.type).__name__.lower()
            # Get the Spark type from TD_TO_SPARK_TYPES mapping and its corresponding data type from
            # SPARK_TYPE_CLASS_TO_SQL_NAME mapping.
            else:
                spk_type = TD_TO_SPARK_TYPES.get(type(col.type))
                sql_name = SPARK_TYPE_CLASS_TO_SQL_NAME.get(spk_type, str(col.type)).lower()
   
            dtype_result.append((str(col.name), sql_name))

        return dtype_result

    def __getattr__(self, item):
        """ Returns an attribute of the DataFrame. """
        # If a direct one on one API available, use it.
        if item in FN_MAPPER:
            return lambda *args, **kwargs: self.__process_function(*args, **kwargs, _f_n_internal=item)

        try:
            obj = getattr(self._data, item)
        except AttributeError:
            raise AttributeError("'DataFrame' object has no attribute '{}'".format(item))

        # If it is a Column, then return Spark DataFrame Column.
        if isinstance(obj, _SQLColumnExpression):
            return Column(tdml_column=obj)

        # For tdml Functions like head() etc.
        def _run_tdml_df_api(*c, **kwargs):

            vals = obj(*c, **kwargs)
            if isinstance(vals, tdml_DataFrame):
                return DataFrame(data=vals)

            return vals

        if callable(obj):
            return _run_tdml_df_api

        return obj

    @staticmethod
    def __process_tdml_functions(*args, **kwargs):
        """ Internal function to process teraspark DataFrame. """
        func_ = kwargs.pop("func_")
        tdml_df = func_(*args, **kwargs)
        return DataFrame(tdml_df)

    def _repr_html_(self):
        """ Internal function to process teraspark DataFrame. """
        return self.__repr__()

    def _build_assign_arguments(self, mapper_values, args, kwargs):
        """ Internal function to process `assign` opertation. """
        _spark_tdml_argument_map = mapper_values.get("func_params")
        _spark_args = list(_spark_tdml_argument_map.keys())
        spark_arg_values = {}
        for index, arg in enumerate(args):
            spark_arg_values[_spark_args[index]] = arg

        spark_arg_values.update(kwargs)

        tdml_arg_values = mapper_values.get("default_tdml_values", {})

        _column_expressions = mapper_values.get("column_expressions", [])
        for idx, exp in enumerate(_column_expressions):
            # _SQLColumnExpression for left and right columns.
            left_column = getattr(self._data, spark_arg_values[exp["left"]])
            right_column = getattr(self._data, spark_arg_values[exp["right"]])
            op = exp["operation"]
            tdml_arg_values[f"{op}_{exp['left']}_{exp['right']}"] = getattr(left_column, op)(right_column)

        return tdml_arg_values

    def __process_function(self, *args, **kwargs):
        """ Internal function to process teraspark API's. """
        # Get the function name.
        function_name = kwargs.pop("_f_n_internal")

        mapper_values = FN_MAPPER.get(function_name)
        # Get the available mapper for the function.
        _spark_tdml_argument_map = mapper_values.get("func_params")
        _return_func = mapper_values.get("return_func", None)
        _tdml_func_name = mapper_values["tdml_func"]

        if _tdml_func_name == "assign":
            tdml_arguments_values = self._build_assign_arguments(mapper_values, args, kwargs)
        else:
            # Get the arguments.
            _spark_args = list(_spark_tdml_argument_map.keys())

            # Convert positional arguments also to keyword arguments.
            spark_arguments_values = {}
            for index, arg in enumerate(args):
                spark_arguments_values[_spark_args[index]] = arg

            # Combine both keyword arguments and positional arguments.
            spark_arguments_values.update(kwargs)

            # Mapper which maps values of arguments. 'outer' in pySpark's join is same as 'full' in tdml's join.
            # Such argument values are mapped in "argument_value_map" in _SPARK_TO_TDML_FN_MAPPER.
            spark_tdml_argument_value_map = mapper_values.get("argument_value_map", {})

            # Convert all the arguments to teradataml arguments.
            # While converting, make sure to pass teradataml DataFrame
            # Column for teraspark DataFrame Column.
            tdml_arguments_values = mapper_values.get("default_tdml_values", {})
            for k, v in spark_arguments_values.items():
                tdml_argument_name = _spark_tdml_argument_map[k]

                if spark_tdml_argument_value_map and spark_tdml_argument_value_map.get(tdml_argument_name, None)\
                        and spark_tdml_argument_value_map.get(tdml_argument_name).get(v, None):
                    # Get the mapped argument value in tdml corresponding to spark's argument value.
                    v = spark_tdml_argument_value_map.get(tdml_argument_name).get(v)

                if isinstance(v, list):
                    for idx, val in enumerate(v):
                        if isinstance(val, Column):
                            v[idx] = val.expression if not val.name else val.name
                        elif isinstance(val, DataFrame):
                            v[idx] = val._data
                        else:
                            v[idx] = val
                elif isinstance(v, Column):
                    v = v.expression if not v.name else v.name
                elif isinstance(v, DataFrame):
                    v = v._data

                if _tdml_func_name == "select":
                    # Select all columns if "*" is present in the list of columns as per PySpark.
                    if v == "*" or "*" in v:
                        v = self._data.columns

                tdml_arguments_values[tdml_argument_name] = v

        # Call the corresponding function.
        call_value = getattr(self._data, _tdml_func_name)  # This will hold value for tdml DataFrame properties.
        if callable(call_value):
            call_value = call_value(**tdml_arguments_values)
        # Return result.
        if _return_func:
            return _return_func(call_value)

        return call_value

    def __getitem__(self, item):
        """ Return a column from the DataFrame or filter the DataFrame using an expression. """
        if item in self.columns and isinstance(item, str):
            return Column(tdml_column=self._data[item])

        if isinstance(item, Column):
            item = item._tdml_column

        return DataFrame(self._data.__getitem__(item))


    def withColumn(self, colName, col):
        """ Creates new column with name as `colName` and corresponding value as `col`. """
        # Use helper to prepare tdml column and flags. Explode needs special handling.
        df = self._data
        if col._explode_col:
            return DataFrame(df_utils._handle_exploded_dataframe(df, colName, col))
        # Use helper to prepare tdml column and flags.
        tdml_column, col_with_null_type, _ = df_utils._prepare_tdml_column(df, col)
        res_df = DataFrame(df.assign(**{colName: tdml_column}))
        if col_with_null_type:  # If column with NullType, use database query to get actual types.
            res_df = df_utils._fix_null_type_col(res_df)
        return res_df


    def withColumns(self, colMap):
        """ Creates new columns with ColMap. Key represents alias name and value represents ColumnExpression. """
        col_with_null_type = False
        df = self._data
        for colname, col in colMap.items():
            if col._explode_col:
                df = df_utils._handle_exploded_dataframe(df, colname, col, colMap)
                continue
            # Use helper to prepare tdml column and flags.
            tdml_column, col_with_null_type, _ = df_utils._prepare_tdml_column(df, col)
            colMap[colname] = tdml_column

        res_df = DataFrame(data=df.assign(**colMap))
        if col_with_null_type:  # If columns with NullType, use database query to get actual types.
            res_df = df_utils._fix_null_type_col(res_df)
        return res_df

    def crossJoin(self, other):
        """ Function to perform cartesian product with other DataFrame. """
        join_params_ = {"other": other._data, "how": "cross"}

        # Check if dataframe has common column names.
        # If yes, use "lsuffix" and "rsuffix" arguments in teradataml DataFrame.join
        if self.__is_dataframes_has_common_names(other):
            # If there are duplicate columns in the joined dataframe, then raise warning.
            df_utils.raise_duplicate_cols_warnings()
            join_params_.update({"lprefix": "l", "rprefix": "r"})

        return DataFrame(self._data.join(**join_params_))

    def dropna(self, how='any', thresh=None, subset=None):
        """ Drops the null value rows. """

        # Pyspark allows "subset" to be in tuple also. But, teradataml do not allow tuple
        # hence converting it.
        if isinstance(subset, str):
            subset = [subset]
        elif isinstance(subset, tuple) or isinstance(subset, Column):
            subset = list(subset)
        return DataFrame(self._data.dropna(how=how, thresh=thresh, subset=subset))

    def exceptAll(self, other):
        """
        Returns the resulting rows that appear in first DataFrame and not in other
        DataFrame by preserving the duplicates.
        """
        return DataFrame(td_minus([self._data, other._data]))

    def subtract(self, other):
        """
        Returns the resulting rows that appear in first DataFrame and not in other
        DataFrame.
        """
        return DataFrame(td_minus([self._data, other._data], allow_duplicates=False))

    def intersect(self, other):
        """
        Returns the resulting rows that are common in first DataFrame and in other
        DataFrame without preserving duplicates.
        """
        return DataFrame(td_intersect([self._data, other._data], allow_duplicates=False))

    def intersectAll(self, other):
        """
        Returns the resulting rows that are common in first DataFrame and in other
        DataFrame by preserving duplicates.
        """
        return DataFrame(td_intersect([self._data, other._data], allow_duplicates=True))

    def filter(self, condition):
        """
        Returns the resulting rows that are common in first DataFrame and in other
        DataFrame by preserving duplicates.
        """
        # condition can be spark ColumnExpression or string or can be instance of 'col', 'Column'.
        if isinstance(condition, str):
            expr_ = literal_column(condition)
        elif isinstance(condition, Column):
            expr_ = condition._tdml_column
        else:
            # User has passed either 'col' or 'Column' function object.
            expr_ = literal_column(condition.expr)
        result_df = DataFrame(self._data[expr_])
        
        # Fix NullType columns if any exist after filtering
        return df_utils._fix_null_type_col(result_df)

    def randomSplit(self, weights, seed=None):
        """ Randomly splits dataframe into multiple fractions based on weights. """
        tdml_df_ = self._data.sample(frac=weights)
        dfs = [_DataFrameReturnDF.limit_func(tdml_df_[tdml_df_.sampleid==i]) for i in range(1, len(weights)+1)]
        [setattr(df, "_ml_params",self._ml_params) for df in dfs]
        return dfs

    def sample(self, withReplacement=False, fraction=None, seed=None):
        """ Randomly samples dataframe into multiple fractions based on weights. """

        # Fraction will be a floating number between 0 and 1.
        tdml_df_ = self._data.sample(frac=fraction, replace=withReplacement)
        return _DataFrameReturnDF.limit_func(tdml_df_)

    def withColumnRenamed(self, existing, new):
        """ Rename a Column. """
        return self.withColumnsRenamed({existing: new})

    def withColumnsRenamed(self, colsMap):
        """ Rename multiple Columns. """
        _drop_columns = []
        _df_columns = {col.lower():col for col in self.columns}
        for col, new_col in colsMap.items():
            if col.lower() != new_col.lower() and new_col.lower() in _df_columns:
                _drop_columns.append(_df_columns[new_col.lower()])
        _new_data = self._data.drop(columns=_drop_columns) if _drop_columns else self._data
        new_columns = [colsMap.get(col, col) for col in self.columns if col not in _drop_columns]
        return DataFrame(_new_data.assign(**{new: _new_data[old] for old, new in colsMap.items()}).select(new_columns))

    def _has_array_types(self):
        """Check if the DataFrame schema contains any array types."""
        # Try to check using the database column types directly
        # TD_ARRAY_TO_ELEM mapping contains all array type classes.
        for col in self._data._metaexpr.c:
            if type(col.type) in TD_ARRAY_TO_ELEM:
                return True
        return False
    
    def toLocalIterator(self):
        """Return iterator over Rows with native Python types."""
        if self._has_array_types():
            # For DataFrames with array columns, convert types appropriately.
            field_types = [f.dataType for f in self.schema.fields]
            for rec in self._data.itertuples(name=None):
                row_dict = dict(zip(self.columns, rec))
                yield df_utils._build_row_with_converted_types(self.columns, field_types, row_dict)
        else:
            # For DataFrames without array columns, use existing approach.
            recs = self._data.itertuples(name=None)
            for rec in recs:
                yield Row(**{k: val for k, val in zip(self.columns, rec)})

    def select(self, *cols):
        """ Creates a new DataFrame based on expressions from "cols" argument."""
        # cols can be str, list or Column or *.
        if len(cols) == 1 and isinstance(cols[0], str) and cols[0] == "*":
            return self

        # cols be a string or Column Object or list of strings or Column Objects.
        # If none of the element is a Column object and all strings are column names, use
        # teradataml DataFrame.select() API.
        # If element is a Column object, then use assign API to create a new Column.
        _is_column_expression_noticed = False
        _assign_expr = OrderedDict()
        alias_dict = {}
        drop_cols = True
        col_with_null_type = False

        if isinstance(cols[0], list):
            cols = cols[0]

        df = self._data
        explode_col_count = 1
        for column in cols:
            if isinstance(column, str):
                _assign_expr[column] = self[column]._tdml_column
                continue
            elif column._explode_col is not None:
                df, _assign_expr, explode_col_count =  df_utils._handle_explode_expr_column(
                                                                column, df, _assign_expr, explode_col_count)
                _is_column_expression_noticed = True
            else:
                tdml_column, col_with_null_type, drop_cols = df_utils._prepare_tdml_column(
                                                                             df, column, 
                                                                             col_with_null_type=col_with_null_type,
                                                                             drop_cols=drop_cols)

                # If expression is a UDF and alias name is None then create a default column name
                # using udf name and func args that is supported by assign call, else if alias name
                # is passed with expression use it as column name.
                if (column._udf or column._udf_name) and not column.alias_name:
                    func_name = column._udf.__name__ if column._udf else column._udf_name
                    column_name = func_name + ''.join([str(col) for col in column._udf_args])

                    # Create a dictionary of default column name genertated to column name same as pyspark notation. 
                    funcargs = ', '.join([str(col) for col in column._udf_args])
                    alias_dict[column_name]  = f'{func_name}({funcargs})'
                else:
                    column_name = column.alias_name if column.alias_name else column._tdml_column.compile().replace('"', "")
                _assign_expr[column_name] = tdml_column
                _is_column_expression_noticed = True
                
        if _is_column_expression_noticed:
            df = DataFrame(df.assign(drop_columns = drop_cols, **_assign_expr))
            if bool(alias_dict):
                df = df.withColumnsRenamed(alias_dict)
                for old, new in alias_dict.items():
                    _assign_expr[new] = _assign_expr.pop(old)
            res_df = DataFrame(df._data.select(list(_assign_expr.keys())))
            # If we have columns with NullType, use database query to get actual types
            if col_with_null_type:
                res_df = df_utils._fix_null_type_col(res_df)
            return res_df
                    
        return DataFrame(df.select(list(cols)))

    def fillna(self, value, subset=None):
        """ Replace the null values. """
        df = self
        if isinstance(value, dict):
            for col, val in value.items():
                # Check the compatibility of value and column type, if not compatible skip the fillna operation.
                if not df_utils.check_value_subset_arg_compatiblity(self, val, col):
                    continue
                df = df.withColumn(col, Column(tdml_column=_SQLColumnExpression(func.nvl(literal_column(col), literal(val)))))
        else:
            if subset is None:
                subset = self.columns
            subset = list(subset) if isinstance(subset, tuple) else UtilFuncs._as_list(subset)
            for column in subset:
                # Check the compatibility of value and column type, if not compatible skip the fillna operation.
                if not df_utils.check_value_subset_arg_compatiblity(self, value, column):
                    continue
                df = df.withColumn(column, Column(tdml_column=_SQLColumnExpression(func.nvl(literal_column(column), literal(value)))))
        return df

    def sort(self, *cols, **kwargs):
        """ Sort the data according to cols. """
        # Extract the column names from cols.
        cols = cols[0] if isinstance(cols, list) else cols
        columns = []

        # PySpark prefers ColumnExpression over argument "ascending". However,
        # teradataml ignores the corresponding element in "ascending" if element in
        # "columns" is a ColumnExpression.
        # Look at below example:
        # >>> teraspark_df._data
        #               Feb    Jan    Mar    Apr    datetime
        # accounts
        # Red Inc     200.0  150.0  140.0    NaN  04/01/2017
        # Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
        # Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
        # >>>
        # >>> pyspark_df.show()
        # +----------+-----+----+----+----+----------+
        # |  accounts|  Feb| Jan| Mar| Apr|  datetime|
        # +----------+-----+----+----+----+----------+
        # |   Red Inc|200.0| 150| 140|null|2017-01-04|
        # |  Alpha Co|210.0| 200| 215| 250|2017-01-04|
        # |Yellow Inc| 90.0|null|null|null|2017-01-04|
        # +----------+-----+----+----+----+----------+
        # >>> tdml_df.sort([tdml_df.Feb,'Jan',tdml_df.accounts], ascending=[False, True, True])
        #               Feb    Jan    Mar    Apr    datetime
        # accounts
        # Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
        # Red Inc     200.0  150.0  140.0    NaN  04/01/2017
        # Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
        # >>> pyspark_df.sort(pyspark_df.Feb,'Jan', pyspark_df.accounts,ascending=[False, True, True]).show()
        # +----------+-----+----+----+----+----------+
        # |  accounts|  Feb| Jan| Mar| Apr|  datetime|
        # +----------+-----+----+----+----+----------+
        # |  Alpha Co|210.0| 200| 215| 250|2017-01-04|
        # |   Red Inc|200.0| 150| 140|null|2017-01-04|
        # |Yellow Inc| 90.0|null|null|null|2017-01-04|
        # +----------+-----+----+----+----+----------+
        #
        # >>>
        # Hence,
        #  If argument is a string,
	    #     convert it to ColumnExpression.
        #  if ascending is True:
        #     send ColumnExpression as it is.
        #  else
        #     send ColumnExpression.desc().
        asc = []
        if "ascending" in kwargs:
            asc = kwargs["ascending"]
            asc = asc if isinstance(asc, list) else [asc]

        for index, col in enumerate(cols):
            column = col._tdml_column if not isinstance(col, str) else self._data[col]
            column = column.desc() if self.__get_list_element(asc, index, True) is False else column
            columns.append(column)

        return DataFrame(data=self._data.sort(columns))

    def __get_list_element(self, l, index, default_value):
        """Internal function to get a value from a list. If specified index does not exist, returns a default value. """
        try:
            return l[index]
        except IndexError:
            return default_value

    def union(self, other):
        """ Union the data considering column by position."""
        colsMap = dict(zip(other.columns, self.columns))
        new_columns = [colsMap.get(col, col) for col in other.columns]
        df = other._data.assign(**{new: other._data[old] for old, new in colsMap.items()}).select(new_columns)
        return self.concat(df)

    def unionByName(self, other, allowMissingColumns=False):
        """ Union the data considering column names."""
        if not allowMissingColumns and not set(self.columns).issubset(set(other.columns)):
            unique_column = next((col2 for col1, col2 in zip(other.columns, self.columns) if col1 != col2), None)
            raise AnalysisException("Cannot resolve column name \"{0}\" among ({1}).".format(str(unique_column),
                                                                                             ", ".join(other.columns)),1)
        return self._tdml_concat(other)

    def join(self, other, on=None, how=None):
        """Joins two teraspark DataFrames. """

        if how == "cross":
            return self.crossJoin(other)

        # Prepare "how" for teradataml.
        pyspark_tdml_join_types = {"outer":"full",
                                   "fullouter": "full",
                                   "full_outer": "full",
                                   "leftouter": "left",
                                   "left_outer": "left",
                                   "semi": "inner",
                                   "leftsemi": "inner",
                                   "left_semi": "inner",
                                   "anti": "inner",
                                   "leftanti": "inner",
                                   "left_anti": "inner",
                                   "rightouter": "right",
                                   "right_outer": "right"
                                   }
        tdml_how_ = "inner" if how is None else pyspark_tdml_join_types.get(how, how)

        on = [on] if not isinstance(on, list) else on
        on = [col._tdml_column if not isinstance(col, str) else col for col in on]

        # For "semi", "left_semi", "leftsemi", "anti", "leftanti", "left_anti" type of joins,
        # only the left DataFrame columns are required. Hence no need to validate for duplicate
        # columns.
        if how in ("semi", "left_semi", "leftsemi"):
            tdml_df_ = self._data.join(other._data, on=on, how=tdml_how_, rprefix="r")
            return DataFrame(data=tdml_df_.select(self.columns))

        if how in ("anti", "leftanti", "left_anti"):
            tdml_df_ = self._data.join(other._data, on=on, how=tdml_how_, rprefix="r").select(self.columns)
            return self.exceptAll(DataFrame(data=tdml_df_))

        # If list of column names or column name is passed, do not maintain columns twice in joined DataFrame.
        if isinstance(on[0], str):

            # Check if columns passed for "on" clause alone are existed in both DataFrames or other
            # columns also existed in Both DataFrames.
            # Look at below example PySpark -
            # >>> pyspark_emp.show()
            # +------+--------+---------------+-----------+-------+------+------+
            # |emp_id|    name|superior_emp_id|year_joined|dept_id|gender|salary|
            # +------+--------+---------------+-----------+-------+------+------+
            # |     1|   Smith|             -1|       2018|     10|     M|  3000|
            # |     2|    Rose|              1|       2010|     20|     M|  4000|
            # |     3|Williams|              1|       2010|     10|     M|  1000|
            # |     4|   Jones|              2|       2005|     10|     F|  2000|
            # |     5|   Brown|              2|       2010|     40|      |    -1|
            # |     6|   Brown|              2|       2010|     50|      |    -1|
            # +------+--------+---------------+-----------+-------+------+------+
            #
            # >>> pyspark_dep.show()
            # +---------+-------+
            # |dept_name|dept_id|
            # +---------+-------+
            # |  Finance|     10|
            # |Marketing|     20|
            # |    Sales|     30|
            # |       IT|     40|
            # +---------+-------+
            #
            # when NO columns other than on clause columns are same, then only one set of on clause
            # columns show up in joined DataFrame. Note the order of the columns as well. on clause
            # columns come first, then remaining columns of 1st dataframe and then remaining columns
            # of 2nd dataframe.
            # >>> pyspark_emp.join(pyspark_dep, 'dept_id').show()
            # +-------+------+--------+---------------+-----------+------+------+---------+
            # |dept_id|emp_id|    name|superior_emp_id|year_joined|gender|salary|dept_name|
            # +-------+------+--------+---------------+-----------+------+------+---------+
            # |     10|     1|   Smith|             -1|       2018|     M|  3000|  Finance|
            # |     10|     3|Williams|              1|       2010|     M|  1000|  Finance|
            # |     10|     4|   Jones|              2|       2005|     F|  2000|  Finance|
            # |     20|     2|    Rose|              1|       2010|     M|  4000|Marketing|
            # |     40|     5|   Brown|              2|       2010|      |    -1|       IT|
            # +-------+------+--------+---------------+-----------+------+------+---------+
            #
            # When columns other than join clause columns are same, they show up in joined DataFrame.
            # Here, "dept_name" is same in both dataframes and we see both "dept_name" columns in
            # joined DataFrame.
            #
            # >>> pyspark_dep.join(pyspark_dep, 'dept_id').show()
            # +-------+---------+---------+
            # |dept_id|dept_name|dept_name|
            # +-------+---------+---------+
            # |     10|  Finance|  Finance|
            # |     20|Marketing|Marketing|
            # |     30|    Sales|    Sales|
            # |     40|       IT|       IT|
            # +-------+---------+---------+
            #
            # >>>
            is_dup_col = False
            _dup_cols = set(col for col in self.columns).intersection(
                col for col in other.columns)
            tdml_df_ = self._data.join(other._data, on=on, how=tdml_how_, rprefix="r")
            columns_to_select = [col for col in self.columns if col not in on]
            for col in other.columns:
                if col not in _dup_cols:
                    columns_to_select.append(col)
                elif col not in on:
                    columns_to_select.append("r_{}".format(col))
                    is_dup_col = True
            df = DataFrame(data=tdml_df_)
            # If how is "left", "right" or "full", then fill the missing columns values with
            # values from other dataframe, for the columns in "on" clause.
            if tdml_how_ in ("left", "right", "full"):
                col_expr = {}
                for col in on:
                    col_expr[col] = Column(tdml_column=_SQLColumnExpression(func.nvl(df[col].expression,\
                                                                                      df['r_{}'.format(col)].expression)))
                df = df.withColumns(col_expr)
            if is_dup_col:
                # If there are duplicate columns in the joined dataframe, then raise warning.
                df_utils.raise_duplicate_cols_warnings(only_r_prefix=True)
            return df.select(on+columns_to_select)

        # No such differences in columns of joined dataframe when columns are passed as
        # Column objects, unlike when columns are passed as strings. So, using prefixes if
        # same column names exists irrespective of whether they are in on clause or not.
        # Otherwise, returning without prefixes.
        # Convert tdml expression for "on".
        _tdml_kwargs = {"on": on, "how": tdml_how_}
        # Check if duplicates exist or not.
        if self.__is_dataframes_has_common_names(other):
            # If there are duplicate columns in the joined dataframe, then raise warning.
            df_utils.raise_duplicate_cols_warnings()
            _tdml_kwargs.update({"lprefix": "l", "rprefix": "r"})

        tdml_df_ = self._data.join(other._data, **_tdml_kwargs)

        return DataFrame(data=tdml_df_)

    def summary(self, *statistics):
        """ Computes specified statistics """
        if not statistics:
            summary_df = DataFrame(data=self._summary(statistics=["count", "mean", "std", "min", "percentile", "max"], pivot=True))
        else:
            percentile = []
            statistic = []

            statistics = df_utils._tuple_to_list(statistics, "statistics")

            for stats in statistics:
                if stats == "stddev":
                    statistic.append("std")
                elif "%" in stats:
                    # If '%' value specified then pass it to percentile argument of tdml summary,
                    # and append percentile to the list of statistics, also remove the '%' value
                    # from statistics because it is not allowed value for summary in tdml.
                    percentile.append(float(stats.strip('%'))/100)
                    if "percentile" not in statistic: statistic.append("percentile")
                else:
                    statistic.append(stats)
            summary_df = DataFrame(data=self._summary(percentile=percentile, statistics=statistic, pivot=True))

        # Rename 'std' to 'stddev'
        summary_df = summary_df.assign(func=case([(summary_df.func.expression == "std", "stddev"),
                                                  (summary_df.func.expression != "std", literal_column('func'))]))

        # Rename the column 'func' to 'summary'
        return summary_df.withColumnRenamed("func", "summary")

    def describe(self, *cols):
        """ Computes the basic statistics for specified columns"""
        if not cols:
            cols = self.columns
        else:
            cols = df_utils._tuple_to_list(cols, "cols")

        describe_df = DataFrame(data=self._summary(statistics=["count", "mean", "std", "min", "max"],
                                columns=cols, pivot=True))
        # Rename 'std' to 'stddev'
        describe_df = describe_df.assign(func=case([(describe_df.func.expression == "std", "stddev"),
                                            (describe_df.func.expression != "std", literal_column('func'))]))
        return describe_df.withColumnRenamed("func", "summary")
    
    def unpivot(self, ids, values, variableColumnName, valueColumnName):
        """ Unpivot the dataframe """
        # Convert ids column to ColumnExpression.
        ids = [ids] if not isinstance(ids, (list,tuple)) else ids
        ids = [getattr(self, id) if isinstance(id, str) else id for id in ids]

        # Convert values column to ColumnExpression.
        # For values equals None, fetch all non-id columns to be unpivoted.
        if values is None:
            values = [getattr(self, col) for col in self.columns if col not in [id.name for id in ids]]
        else:
            values = [values] if not isinstance(values, (list,tuple)) else values
            values = [getattr(self, value) if isinstance(value, str) else value for value in values]

        # Fetch the data based on ids and values for unpivoting.
        df = self.select(ids+values)

        # Create a dictonary of values column (as ColumnExpression) of the data.
        cols = df.columns[len(ids): ]
        dict_col = {tuple([getattr(df._data,col) for col in cols]): None}

        return DataFrame(df._data.unpivot(columns=dict_col,
                                          transpose_column= variableColumnName,
                                          measure_columns= valueColumnName,
                                          exclude_nulls=False))

    def drop(self, *cols):
        """ Returns DataFrame without specified columns."""
        columns = df_utils._get_columns_from_tuple_args(cols, self.columns)
        if len(columns) == 0:
            return self

        return DataFrame(data=self._data.drop(columns=columns, axis=1))

    def selectExpr(self, *expr):
        """Projects a set of SQL expressions and returns a new DataFrame."""
        _assign_expr = OrderedDict()
        for colExpr in expr:
            _assign_expr[colExpr] = literal_column(colExpr)
        tdml_df = self._data.assign(drop_columns=True, **_assign_expr)
        return DataFrame(tdml_df.select(list(_assign_expr.keys())))

    def replace(self, to_replace, value=None, subset=None):
        """ Replace a value with another value. """

        # If value is a scalar and to_replace is a sequence, then value is used as
        # a replacement for each item in to_replace.
        if (not isinstance(to_replace, (dict))) and isinstance(to_replace, list) and (not isinstance(value, list)):
            to_replace = dict(zip(to_replace, [value]*len(to_replace)))
        # If value is a list, to_replace must be a list and both lengths should be same.
        elif isinstance(value, list):
            to_replace = dict(zip(to_replace, value))
            value = None

        # If the value is scalar, then convert it to list to check the compatibility with the subset.
        values = [value] if isinstance(value, (int, float, bool, str)) else list(to_replace.values())
        # If subset is None, then consider all columns.
        if subset is None:
            subset = self.columns

        # Check the type compatibility of the value with the subset.
        columns_to_remove = []
        for val in values:
            for column in subset:
                if not df_utils.check_value_subset_arg_compatiblity(self, val, column):
                    columns_to_remove.append(column)
        # Remove the incompatible columns after iteration
        subset = [col for col in subset if col not in columns_to_remove]

        return DataFrame(self._data.replace(to_replace, value, subset))

    def createOrReplaceTempView(self, name):
        """ Create or replace temporary view. """
        try:
            db_drop_view(name)
        except:
            pass
        self._data.create_temp_view(name)

    def printSchema(self, level=None):
        """ Prints schema in tree format. """
        print("root")
        for column in self.columns:
            type_ = getattr(self, column)._tdml_column.type
            # Check if the type is an array type.
            if type(type_) in TD_ARRAY_TO_ELEM:
                type_name = type(type_).__name__.lower()
            else:
                type_name = _get_spark_type(type_).typeName()
            print(f" |-- {column}: {type_name} (nullable = true)")

    def crosstab(self, col1, col2):
        """ Returns frequency matrix of two columns. """
        # tdml pivot gives exception if column contain null values.
        # It converts column name to lower case and special chars i.e ".","\" to "_"
        col = self._data[col2]
        df = self.select(col1, col2)
        freq_df = df.pivot(columns=col, aggfuncs=col.count())
        dict = {col: col.replace(f"count_{col2.lower()}_","") for col in freq_df.columns}
        dict[col1] = col1+ "_"+ col2
        return freq_df.withColumnsRenamed(dict)

    def foreach(self, f):
        """ Applies the f function to all rows of the data. """
        for row in self.collect():
            f(row)
            
    def __is_dataframes_has_common_names(self, other):
        return bool(set(self.columns).intersection(other.columns))

    def __get_tdml_column(self, col):
        return col._tdml_column
    
    @property
    def isStreaming(self):
        """ Returns whether DataFrame is streaming or not."""
        return False

    @property
    def schema(self):
        """ Returns the schema for DataFrame. """
        struct_type = StructType()
        for column in self.columns:
            type_ = getattr(self, column)._tdml_column.type
            field = StructField(name=column, dataType=_get_spark_type(type_), nullable=True)
            struct_type.add(field)
        return struct_type

    def sampleBy(self, col, fractions, seed=None):
        """ Returns a stratified sample based on each stratum. """
        if isinstance(col, Column):
            col = col._tdml_column.name

        tdf_s_ = []
        tdml_df = self._data

        # Generate Unique ID.
        tdml_df = tdml_df.assign(row_num__=func.sum(1).over(rows=(None, 0)))

        # Iterate through every fraction. Filter it, then sample it. After sampling,
        # remove additional columns.
        for val, frac in fractions.items():
            tdml_df_ = tdml_df[tdml_df[col]==val].sample(
                frac=frac, stratify_column=col, seed=1 if seed is None else seed, id_column='row_num__')
            tdf_s_.append(tdml_df_[tdml_df_.sampleid == 1].drop(columns=['row_num__', 'sampleid']))

        # If user provides only one value to sample, return it as it is. Else,
        # concatenate it and return it.
        if len(tdf_s_) == 1:
            return DataFrame(tdf_s_[0])
        return DataFrame(concat(tdf_s_))
    
    def cube(self, *cols):
        """Create multi-dimensional cube for the DataFrame."""
        columns = df_utils._get_columns_from_tuple_args(cols, self.columns)
        if len(columns) == 0:
            return self
        return DataFrame(self._data.cube(columns, include_grouping_columns = True))
    
    def rollup(self, *cols):
        """Create multi-dimensional rollup for the DataFrame."""
        columns = df_utils._get_columns_from_tuple_args(cols, self.columns)
        if len(columns) == 0:
            return self
        return DataFrame(self._data.rollup(columns, include_grouping_columns = True))

    @property
    def na(self):
        """ Work with missing data in DataFrame. """
        return DataFrameNaFunctions(_spark_df=self)

    @property
    def stat(self):
        """ Statistic functions for DataFrames. """
        return DataFrameStatFunctions(_spark_df=self)

    def groupBy(self, *expr):
        if not expr:
            # If no grouping columns are passed, return GroupedData with entire DataFrame as single group.
            return _DataFrameReturnDF.dataframe_grouped_func(self._data, self._data)
        is_list = isinstance(expr[0], list)
        if is_list:
            return _DataFrameReturnDF.dataframe_grouped_func(self._data.groupby(expr[0]), self._data)
        return _DataFrameReturnDF.dataframe_grouped_func(self._data.groupby(list(expr)), self._data)

    def groupby(self, *expr):
        return self.groupBy(*expr)

    def agg(self, *expr):
        """Perform aggregates using one or more operations."""
        column_expression = isinstance(expr[0], Column)        
        if column_expression:
            func_expr = []
            for func in expr:
                # Determine alias preference order: explicit alias > compiled expression
                alias = func.alias_name or func._tdml_column.compile()
                func_expr.append(func._tdml_column.alias(alias))
            return DataFrame(self._data.agg(func_expr))

        # Creating a new column with any value only when user passes {'*': 'count'}
        # We can use that column for count in agg function.
        _new_data = self._data
        if expr[0].get('*', None):
            _new_data = self._data.assign(all_rows_ = 1)
            expr[0].pop('*')
            expr[0]['all_rows_'] = 'count'
        return DataFrame(_new_data.agg(*expr))

    def toTeradataml(self):
        """Converts teradatamlspk DataFrame to teradataml DataFrame. """
        return self._data

    def writeTo(self, table, schema_name=None):
        """Function to write DataFrame to table. """
        from teradatamlspk.sql.readwriter import DataFrameWriterV2
        return DataFrameWriterV2(self, table, schema_name)

    def persist(self, StorageLevel=StorageLevel.MEMORY_AND_DISK_DESER):
        """ Function to persist the DataFrame. """
        # Create a temporary table to persist the DataFrame.
        table_name = UtilFuncs._generate_temp_table_name(prefix="tdspk_tmp_",
                                                        table_type=TeradataConstants.TERADATA_TABLE,
                                                        gc_on_quit=True)
        self.writeTo(table_name).create()
        return DataFrame(tdml_DataFrame(table_name))

    def approxQuantile(self, col, probabilities, relativeError):
        """ Calculates the approximate quantiles of numerical columns of a DataFrame. """

        df = self._data.materialize()
        is_col_str = isinstance(col, str)
        # If col is a string or tuple, convert it to a list.
        if isinstance(col, (str, tuple)):
            col = list(col) if isinstance(col, tuple) else [col]

        # If the probabilities contains only 0.0 and 1.0 then get the min and max values of the columns.
        # Get the count of non-null values in the column to calculate the position of the percentiles.
        # Create a SQL query to get the min, max and count of the columns.
        select_exprs = []
        for c in col:
            if 0.0 in probabilities:
                select_exprs.append(f"min({c}) as {c}_min") # Get the minimum value of the column.
            if 1.0 in probabilities:
                select_exprs.append(f"max({c}) as {c}_max") # Get the maximum value of the column.
            # Count the number of non-null values in the column.
            select_exprs.append(f"sum(CASE WHEN {c} IS NOT NULL THEN 1 ELSE 0 END) AS {c}_count")

        # SQL query to get the min, max and count of the column.
        select_clause = ", ".join(select_exprs)
        select_clausequery = f'SELECT {select_clause} FROM {df._table_name}'

        # Get the aggregate results for the columns as a dictionary eg.{col name: <value>}.
        agg_df = execute_sql(select_clausequery)
        agg_res = {}
        for rec in agg_df:
            agg_res = dict(zip([row[0] for row in agg_df.description], rec))

        # Get the SQL query to rank the values of the columns and filter the columns based on percentiles.
        rank_exprs = []
        where_exprs = []
        for c in col:
            # SQL expression to rank the values of the column.
            rank_exprs.append(f"{c} as {c}, ROW_NUMBER() OVER (ORDER BY {c} ASC NULLS LAST) AS tdspk_rank_{c}")
            percentile_pos = []
            for p in probabilities:
                # If probability is 0 or 1, skip the calculation of position.
                if p == 0.0 or p == 1.0:
                    continue
                # Calculate the position of the percentile in the ranked DataFrame.
                pos = (agg_res[f"{c}_count"]) * p
                percentile_pos.append(int(math.ceil(pos)))
            # SQL expression to filter the ranked values based on percentiles.
            where_exprs.append(f"(tdspk_rank_{c} IN ({', '.join(map(str, percentile_pos))}))")

        # SQL query to rank the values of the columns and filter the columns based on percentiles.
        rank_clause = ", ".join(rank_exprs)
        where_clause = " OR ".join(where_exprs)
        rank_clausequery = f'SELECT {rank_clause} FROM {df._table_name} QUALIFY {where_clause}'

        # Get the ranked values of the columns based on percentiles as a dictionary.
        # eg.{col name: {percentile position: value}}.
        percentile_df = execute_sql(rank_clausequery)
        percentile_df_cols = [row[0] for row in percentile_df.description]
        recs = []
        for rec in percentile_df:
            recs.append(dict(zip(percentile_df_cols, rec)))
        recs = {c: {rec[f'tdspk_rank_{c}']: rec[c] for rec in recs if f'tdspk_rank_{c}' in rec} for c in col}

        # Create a list to store the resultant values for each column based on the percentiles.
        res  = []
        for c in col:
            values = []
            # If count of non-null values in the column is 0, return None for all probabilities.
            if agg_res[f"{c}_count"] == 0:
                res.append([None] * len(probabilities))
                continue
            for p in probabilities:
                if p == 0.0:
                    value = agg_res[f"{c}_min"] # If probability is 0, return min value of the column.
                elif p == 1.0:
                    value = agg_res[f"{c}_max"] # If probability is 1, return max value of the column.
                else:
                    # Get the value at the specified percentile position from the column ranked dictionary.
                    percentile_pos = int(math.ceil((agg_res[f"{c}_count"]) * p))
                    value = recs[c].get(percentile_pos)
                values.append(float(value) if value is not None else None)
            res.append(values)

        # If column is a string, return the first element of the resultant list else return the list.
        return res[0] if is_col_str else res

    @property
    def write(self):
        return DataFrameWriter(data=self._data)
    
    @property
    def rdd(self):
        """Returns the same DataFrame."""
        return self

class DataFrameNaFunctions:
    """ Work with missing data in DataFrame. """
    def __init__(self, _spark_df):
        """ Constructor. """
        self._spark_df = _spark_df

    def fill(self, value, subset=None):
        """ Replace null values. """
        return self._spark_df.fillna(value, subset)

    def drop(self, how='any', thresh=None, subset=None):
        """ Omit rows with null values """
        return self._spark_df.dropna(how, thresh, subset)

    def replace(self, to_replace, value, subset=None):
        """ Replace a value with another value. """
        return  self._spark_df.replace(to_replace, value, subset)


class DataFrameStatFunctions:
    """ Statistic functions for DataFrames. """
    def __init__(self, _spark_df):
        self._spark_df = _spark_df

    def approxQuantile(self, col, probabilities, relativeError):
        """ Perform approximate quantiles for numeric columns. """
        return self._spark_df.approxQuantile(col, probabilities, relativeError)

    def corr(self, col1, col2):
        """ Perform correlation between two columns. """
        return self._spark_df.corr(col1, col2)

    def cov(self, col1, col2):
        """ Perform sample covariance between two columns. """
        return self._spark_df.cov(col1, col2)

    def crosstab(self, col1, col2):
        """ Computes the pair wise frequency for given columns. """
        return self._spark_df.crosstab(col1, col2)

    def freqItems(self, cols, support):
        """ Finding frequent items for columns. """
        return self._spark_df.freqItems(cols, support)

    def sampleBy(self, col, fractions, seed):
        """ Perform stratified sample without replacement based on the fraction given on each stratum. """
        return self._spark_df.sampleBy(col, fractions, seed)