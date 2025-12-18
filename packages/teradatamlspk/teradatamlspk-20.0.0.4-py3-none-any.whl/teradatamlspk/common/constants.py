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
from teradatamlspk.sql import dataframe
from teradatamlspk.sql import group
from teradatamlspk.sql.types import Row


class _DataFrameReturnDF:
    """
    Internal class which maintains the functions which takes teradataml DataFrame
    as input and returns the corresponding Spark analogous output.
    """
    value_func = lambda x: x.get_values()[0][0]
    dataframe_func = lambda x: dataframe.DataFrame(data=x)
    dataframe_grouped_func = lambda x, y: group.GroupedData(data=x, non_grouped_data=y)
    reset_pandas_df_index = lambda pdf: pdf.reset_index() if pdf.index.name is not None else pdf
    to_row_ = lambda recs: (Row(**rec._asdict()) for rec in recs)
    shape = lambda x: x[0]

    @staticmethod
    def tail_func(df):
        return [rec for rec in df.itertuples()]

    @staticmethod
    def limit_func(df):
        return _DataFrameReturnDF.dataframe_func(df.drop(["sampleid"], axis=1))

# Mapper which stores the mapping between teradataml and teradatamlspk.
# Parameters:
#   Key - function name in teradatamlspk.
#   Value - dictionary with below properties:
#               tdml_func: Represents the name of the function in teradataml.
#               func_params: Again a dictionary. Key represents the argument name
#                            in PySpark and value represents the argument name in
#                            teradataml.
#                            Notes:
#                               * If teradataml do not have corresponding argument, then ignore that argument i.e.,
#                                 argument should not have an entry in 'func_params'.
#                               * Value None represents the argument is not significant in teradataml.
#               return_func: A callable object which should take teradataml API response as input. This is
#                            significant when the output of teradataml API is not matching with output of
#                            Spark. Example - count API in teradataml returns DataFrame but in Spark it
#                            returns the number of rows. So, the output of teradataml needs to be
#                            processed again to get the number of rows. Hence, 'count' has function
#                            which uses shape and returns number of rows.
_SPARK_TO_TDML_FN_MAPPER = {
    "count": {"tdml_func": "shape",
              "func_params": {},
              "return_func": _DataFrameReturnDF.shape
              },
    "distinct": {"tdml_func": "drop_duplicate",
              "func_params": {},
               "return_func": _DataFrameReturnDF.dataframe_func
              },
    "select": {"tdml_func": "select",
               "func_params": {"cols": "select_expression"},
               "return_func": _DataFrameReturnDF.dataframe_func
               },
    "limit": {"tdml_func": "sample",
              "func_params": {"num": "n"},
              "return_func": _DataFrameReturnDF.limit_func
              },
    "dropDuplicates": {"tdml_func": "drop_duplicate",
                       "func_params": {"subset": "column_names"},
                       "return_func": _DataFrameReturnDF.dataframe_func
                       },
    "drop_duplicates": {"tdml_func": "drop_duplicate",
                        "func_params": {"subset": "column_names"},
                        "return_func": _DataFrameReturnDF.dataframe_func
                        },
    "orderBy": {"tdml_func": "sort",
                "func_params": {"cols": "columns", "ascending": "ascending"},
                "return_func": _DataFrameReturnDF.dataframe_func
                # TODO: cols accepts Column object also along with str. tdml do not accept Column object.
                #   Will be addressed with ELE-5976.
                },
    "where": {"tdml_func": "__getitem__",
              "func_params": {"condition": "key"},
              "return_func": _DataFrameReturnDF.dataframe_func
              },
    "tail": {"tdml_func": "tail",
             "func_params": {"num": "n"},
             "return_func": _DataFrameReturnDF.tail_func
             },
    "toPandas": {"tdml_func": "to_pandas",
                 "func_params": {"all_rows": True},
                 "return_func": _DataFrameReturnDF.reset_pandas_df_index
                 },
    "_tdml_concat": {"tdml_func": "concat",
                     "func_params": {"other": "other", "allow_duplicates": False},
                     "return_func": _DataFrameReturnDF.dataframe_func
                     },
    "cov": {"tdml_func": "assign",
            # No mapping to tdml assign exists. Uses these columns to build _SQLColumnExpression.
            "func_params": {"col1": None, "col2": None},
            "default_tdml_values": {"drop_columns": True},
            "column_expressions": [{"left": "col1", "right": "col2", "operation": "covar_samp"}],
            "return_func": _DataFrameReturnDF.value_func
            },
    "corr": {"tdml_func": "assign",
             # No mapping to tdml assign exists. Uses these columns to build _SQLColumnExpression.
             "func_params": {"col1": None, "col2": None, "method": None},
             "default_tdml_values": {"drop_columns": True},
             "column_expressions": [{"left": "col1", "right": "col2", "operation": "corr"}],
             "return_func": _DataFrameReturnDF.value_func
             },
    "toLocalIterator": {"tdml_func": "itertuples",
             "func_params": {},
             "return_func": _DataFrameReturnDF.to_row_
             },
    "_summary": {"tdml_func": "describe",
                 "func_params": {"percentile": "percentiles", "statistics": "statistics", "columns": "columns", "pivot": "pivot"}
             },
    "_tdml_filter": {"tdml_func": "filter",
                     "func_params": {"regex":"regex"},
                     "return_func": _DataFrameReturnDF.dataframe_func}
}
