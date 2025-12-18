from teradataml import create_context, db_list_tables, DataFrame as tdml_DataFrame
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.sql.session import TeradataSession


class SQLContext:
    def __init__(self, *args, **kwargs):
        self.teradataSession = TeradataSession()

    @classmethod
    def getOrCreate(cls, **kwargs):
        create_context(**kwargs)
        return SQLContext()

    def getActiveSession(self):
        return self

    def active(self):
        return self

    def newSession(self):
        """ Returns the existing SQLContext object. """
        return self

    def setConf(self, key, value):
        pass

    def getConf(self, key: str):
        return

    @property
    def udf(self):
        return self.teradataSession.udf

    @staticmethod
    def udtf():
        raise NotImplemented("Not supported in Teradata Vantage.")

    def range(self, start, end=None, step=1, numPartitions = None):
        """ Creates a DataFrame with a range of numbers. """
        from teradataml import td_range
        return DataFrame(td_range(start, end, step))

    def registerFunction(self, name, f, returnType = None):
        raise NotImplemented("Not yet supported in Teradata Vantage.")

    def registerJavaFunction(self, name, javaClassName, returnType = None):
        raise NotImplemented("Not yet supported in Teradata Vantage.")

    def createDataFrame(self, data, schema=None):
        """
        :param data: Vantage Table name.
        :return: teradatamlspk DataFrame.
        """
        return  self.teradataSession.createDataFrame(data, schema=schema)

    def registerDataFrameAsTable(self, df, tableName):
        df._data.to_sql(table_name=tableName)

    def dropTempTable(self, tableName):
        self.teradataSession.catalog.dropTempView(tableName)

    def sql(self, sqlQuery: str):
        return self.teradataSession.sql(sqlQuery)

    def table(self, tableName: str):
        return self.teradataSession.table(tableName)

    def tables(self, dbName=None):
        return db_list_tables(schema_name=dbName)

    def tableNames(self, dbName=None):
        return list(db_list_tables(schema_name=dbName)['TableName'].values)

    def cacheTable(self, tableName):
        return

    def uncacheTable(self, tableName):
        return

    def clearCache(self) -> None:
        return
    
    def setLogLevel(self, logLevel):
        print("Set `log` argument in TeradataSession.getOrCreate. Refer teradatasql logging for more details.")

    @property
    def read(self):
        from teradatamlspk.sql.readwriter import DataFrameReader
        return DataFrameReader()

    @property
    def readStream(self):
        raise NotImplemented("The API is not applicable for Teradata Vantage.")

    @property
    def streams(self):
        raise NotImplemented("The API is not applicable for Teradata Vantage.")