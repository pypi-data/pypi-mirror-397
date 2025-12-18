from sqlalchemy import literal_column
from teradatamlspk.sql import dataframe
from teradatamlspk.sql.column import Column
from teradataml.dataframe.sql import _SQLColumnExpression
from teradatamlspk.sql.dataframe_utils import DataFrameUtils as df_utils



class GroupedData:
    def __init__(self, data=None, non_grouped_data=None):
        self._data = data
        self.avg = self.mean
        self.__pivot_data = None
        self._non_grouped_data = non_grouped_data

    def count(self):
        if self.__pivot_data:
            return self.__new_pivot_df((), "count")

        return dataframe.DataFrame(self._data.assign(count = literal_column("count(*)")))

    def agg(self, *expr):
        column_expression = isinstance(expr[0], Column)
        if self.__pivot_data:
            if column_expression:
                # Storing the column in __pivot_columns extracting from Column
                for fun in expr:
                    self.__pivot_columns.update({fun.alias_name if fun.alias_name else fun.expr_.compile(): fun.expr_})
            else:
                # If dictionary is given directly storing the columns
                self.__pivot_columns.update({col: self._data[col] for col in expr[0]})

            df = self._non_grouped_data.assign(drop_columns=True, **self.__pivot_columns)
            cols=list()
            if column_expression:
                for fun in expr:
                    cols.append(getattr(df[fun.alias_name if fun.alias_name else fun.expr_.compile()],
                                        fun.agg_func_params['name'])())

            else:
                cols = [getattr(df[key], value)() for key, value in expr[0].items()]
            return dataframe.DataFrame(df.pivot(columns=self.__pivot_data, aggfuncs=cols))

        if column_expression:
            func_expr = []
            for func in expr:
                alias = func.alias_name if func.alias_name else func._tdml_column.compile()
                func_expr.append(func._tdml_column.alias(alias))
            return dataframe.DataFrame(self._data.agg(func_expr))
        
        # Creating a new column with any value only when user passes {'*': 'count'}
        # We can use that column for count in agg function.
        _new_data = self._data
        if expr[0].get('*', None):
            _new_data = self._data.assign(all_rows_ = 1)
            expr[0].pop('*')
            expr[0]['all_rows_'] = 'count'
        return dataframe.DataFrame(_new_data.agg(*expr))

    def max(self, *cols):
        if self.__pivot_data:
            return self.__new_pivot_df(cols, "max")

        if cols:
            df = self._data.select(list(set(self._data.groupby_column_list).union(set(cols))))
        else:
            df = self._data.select(list(self._data.columns))
        return dataframe.DataFrame(df.groupby(self._data.groupby_column_list).max())

    def min(self, *cols):
        if self.__pivot_data:
            return self.__new_pivot_df(cols, "min")

        if cols:
            df = self._data.select(list(set(self._data.groupby_column_list).union(set(cols))))
        else:
            df = self._data.select(list(self._data.columns))
        return dataframe.DataFrame(df.groupby(self._data.groupby_column_list).min())

    def mean(self, *cols):
        if self.__pivot_data:
            return self.__new_pivot_df(cols, "mean")

        if cols:
            df = self._data.select(list(set(self._data.groupby_column_list).union(set(cols))))
        else:
            df = self._data.select(list(self._data.columns))
        return dataframe.DataFrame(df.groupby(self._data.groupby_column_list).mean())

    def sum(self, *cols):
        if self.__pivot_data:
            return self.__new_pivot_df(cols, "sum")
        if cols:
            df = self._data.select(list(set(self._data.groupby_column_list).union(set(cols))))
        else:
            df = self._data.select(list(self._data.columns))
        return dataframe.DataFrame(df.groupby(self._data.groupby_column_list).sum())

    def pivot(self, pivot_col, values=None):
        # __pivot_data stores parameters which are passed to teradataml pivot function.
        self.__pivot_data = {getattr(self._non_grouped_data, pivot_col): values} \
            if values else getattr(self._non_grouped_data, pivot_col)
        # __pivot_columns stores the column names and corresponding ColumnExpression which is required
        # to generate new dataframe.
        self.__pivot_columns = dict({pivot_col: self._data[pivot_col]})
        # Updating __pivot_columns
        for column in self._data.groupby_column_list:
            if isinstance(column, _SQLColumnExpression):
                self.__pivot_columns.update({column.compile(): column})
            else:
                self.__pivot_columns.update({column: self._data[column]})
        # __col_values stores what columns user provided in teradatamlspk pivot function
        self.__col_values = pivot_col
        return self

    def __new_pivot_df(self, cols, agg_func):
        self.__pivot_columns.update({col: self._data[col] for col in cols})
        # Creating new dataframe based on columns in __pivot_columns which is stored in df
        df = self._non_grouped_data.assign(drop_columns=True, **self.__pivot_columns)
        # As "count" doesnot accepts any parameter providing column which is given in pivot parameter.
        if agg_func == "count":
            cols = df[self.__col_values].count()
        else:
            cols = [getattr(df[col], agg_func)() for col in cols]
        return dataframe.DataFrame(df.pivot(columns=self.__pivot_data, aggfuncs=cols))
