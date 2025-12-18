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
from collections import OrderedDict
from teradataml import execute_sql
from teradatamlspk.sql.constants import *
from teradataml.dbutils.dbutils import db_drop_table, db_list_tables, db_drop_view
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml.dataframe.dataframe import DataFrame as tdml_DataFrame
import datetime, pytz
import importlib.util
from teradatasqlalchemy.types import *
from teradataml.dataframe.copy_to import _extract_column_info, _detect_array_udt_types
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.common.constants import ArrayDefaults

class AnalysisException(Exception):
    def __init__(self, msg, code):
        super(AnalysisException, self).__init__(msg)
        self.code = code

def _check_lib(lib_name, functionality):
    """
    Function to raise exception if library is not present
    """

    if not importlib.util.find_spec(lib_name):
        raise Exception(f"Please install library '{lib_name}', {lib_name} is required for {functionality} support.")

def _get_spark_type(td_type):
    """
    Function to get the corresponding Spark Type from Teradata Type.
    """

    # td_type is a class.
    if isinstance(td_type, type):
        return _get_spark_type(td_type())

    # td_type is an instance of some Data Type.
    if isinstance(td_type, (CHAR, VARCHAR)):
        return TD_TO_SPARK_TYPES.get(td_type.__class__)(length=td_type.length)

    if isinstance(td_type, DECIMAL):
        return TD_TO_SPARK_TYPES.get(td_type.__class__)(precision=td_type.precision, scale=td_type.scale)

    if isinstance(td_type, TIMESTAMP):
        return TimestampType() if td_type.timezone else TimestampNTZType()

    if td_type.__class__ in TD_ARRAY_TO_ELEM:
        elem_spk_cls = TD_ARRAY_TO_ELEM[td_type.__class__]
        # Timestamp arrays
        if elem_spk_cls in (TimestampType, TimestampNTZType):
            return ArrayType(TimestampType()) if td_type.timezone else ArrayType(TimestampNTZType())

        # Decimal arrays
        if elem_spk_cls == DecimalType:
            return ArrayType(DecimalType(precision=td_type.precision, scale=td_type.scale))
        
        # Char/Varchar arrays
        if elem_spk_cls in (CharType, VarcharType):
            return ArrayType(elem_spk_cls(length=td_type.length))

        # Generic fallback
        return ArrayType(elem_spk_cls())

    return TD_TO_SPARK_TYPES.get(td_type.__class__)()


def _get_tdml_type(spark_type):
    # if spark_type is a class.
    if isinstance(spark_type, type):
        return _get_tdml_type(spark_type())

    # td_type is an instance of some Data Type.
    if isinstance(spark_type, (VarcharType)):
        return SPARK_TO_TD_TYPES.get(spark_type.__class__)(spark_type.length)

    if isinstance(spark_type, DayTimeIntervalType):
        return DAY_TIME_INTERVAL_TYPE.get(f"{spark_type.startField}{spark_type.endField}")

    if isinstance(spark_type, YearMonthIntervalType):
        return YEAR_MONTH_INTERVAL_TYPE.get(f"{spark_type.startField}{spark_type.endField}")

    if isinstance(spark_type, DecimalType):
        return SPARK_TO_TD_TYPES.get(spark_type.__class__)(spark_type.precision, spark_type.scale)
    
    if isinstance(spark_type, ArrayType):
        default_array_size = _InternalBuffer.get("default_array_size") or \
                             ArrayDefaults.DEFAULT_ARRAY_SIZE.value
        scope = f'[{default_array_size}]'

        spk_type = spark_type.elementType
        
        # Timestamp arrays
        if isinstance(spk_type, (TimestampType, TimestampNTZType)):
            tz = True if isinstance(spk_type, TimestampType) else False
            return ARRAY_TIMESTAMP(scope, timezone=tz)

        # Decimal arrays
        if isinstance(spk_type, DecimalType):
            return ARRAY_DECIMAL(scope, precision=spk_type.precision, scale=spk_type.scale)
        
        # Varchar arrays
        if isinstance(spk_type, VarcharType):
            return ARRAY_VARCHAR(scope, length=spk_type.length)
        
        # Generic fallback (for arrays like ARRAY_DATE, ARRAY_INTEGER, etc.)
        return SPARK_ELEM_TO_TD_ARRAY.get(spk_type.__class__)(scope)
    
    return SPARK_TO_TD_TYPES.get(spark_type.__class__)()

def _pytz_to_teradataml_string_mapper(timezone_str):
    """
    Convert pyspark timezone string to timezone string accepted by vantage.
    Example:
        * 'America/Los_Angeles' -> '-07:00'
    Parameters
    timezone_str:
        Required Argument.
        Specifies pyspark timezone string
        Few examples:
            * America/Danmarkshavn
            * America/Miquelon
            * America/Noronha
        Types: str

    Returns:
    Time zone string accepted by vantage.
    """
    timezone = pytz.timezone(timezone_str)
    utc_offset = None
    # Here we are accepting timezone without dst so when user set session it will be consistent.
    for month in range(1, 13):
        if not timezone.localize(datetime.datetime(2000, month, 1)).dst():
            utc_offset = timezone.localize(datetime.datetime(2000, month, 1)).utcoffset().total_seconds()
    hours = str(int(utc_offset//3600))
    mins = str(int((utc_offset%3600)//60))
    return f"{hours}:{mins.zfill(2)}"

def _infer_dataframe_types(df):
    """
    DESCRIPTION:
        Identifies timestamp columns and converts them to timezone types.

    PARAMETERS:
        df:
            Required Argument.
            Specifies the pandas DataFrame whose types must be inferred.
            Types: pandas.DataFrame

    RAISES:
        None
    """
    arrays = _detect_array_udt_types(df)
    # Build mapping col -> SQLAlchemy ARRAY type (atype) expected by _extract_column_info
    udt_types = {c: arr.atype for c, arr in arrays.items()} if arrays else {}

    col_names, col_types = _extract_column_info(df, index=False, index_label=None, udt_types=udt_types)
    inferred_types = {c: t for c, t in zip(col_names, col_types)}

    # Promote TIMESTAMP types to timezone=True
    for col, t in list(inferred_types.items()):
        # Promote scalar TIMESTAMP.
        if (t == TIMESTAMP):
            inferred_types[col] = TIMESTAMP(timezone=True)
        # Promote ARRAY_TIMESTAMP (array of datetime) preserving scope.
        elif isinstance(t, ARRAY_TIMESTAMP):
            inferred_types[col] = ARRAY_TIMESTAMP(t.scope, t.default_null, timezone=True)

    return inferred_types

class SQLquery:
    """ This class identifies the SQL query based on the regex
        and performs the corresponding operation based on the query.
    """
    @staticmethod
    def _drop_table_if_exists_query(sqlQuery):
        """
        DESCRIPTION:
            Drops the table whether the table exists or not based on the "DROP TABLE IF EXISTS" query.
        PARAMETERS:
            sqlQuery:
                Required Argument.
                Specifies the sql query.
                Types: str
                Supported query syntax: "DROP TABLE IF EXISTS table_identifier"
                                "table_identifier" syntax: [ database_name. ] table_name
        RETURNS:
            None

        EXAMPLES:
        >>> _drop_table_if_exists_query("drop table if exists alice.admissions_train;")
        """
        # Regular expression pattern to search schema name(if given) and table name after "DROP TABLE IF EXISTS".
        match = re.search(r'''^\s*DROP\s+TABLE\s+IF\s+EXISTS\s+             # Match "DROP TABLE IF EXISTS" with any whitespace.
                        (?:["`']?(?P<schema>[a-zA-Z0-9_]+)["`\']?\.)?     # Allows for optional quotes and captures the schema name if it exists.
                        ["`']?(?P<table>[a-zA-Z0-9_]+)["`\']?           # Allows for optional quotes and captures the table name.
                        ''',sqlQuery, re.IGNORECASE | re.VERBOSE)
        
        # Fetching the schema name and table name from the captured groups.
        schema_name = match.group('schema')
        table_name = match.group('table')
        try:
            db_drop_table(table_name, schema_name)
        except:
            pass

    @staticmethod
    def _select_query(sqlQuery):
        """
        DESCRIPTION:
            Returns the teradatamlspk DataFrame based on the "SELECT" query.
        PARAMETERS:
            sqlQuery:
                Required Argument.
                Specifies the sql query.
                Types: str
                Supported query syntax: Only "SELECT" query are supported.
        RETURNS:
            teradatamlspk DataFrame

        EXAMPLES:
        >>> _select_query("SELECT * from admissions_train;")
        """
        from teradatamlspk.sql.dataframe import DataFrame
        return DataFrame(tdml_DataFrame.from_query(sqlQuery))

    @staticmethod
    def _show_table_query(sqlQuery):
        """
        DESCRIPTION:
            Returns the lists the Vantage objects(table/view) names based on the "SHOW TABLES" query.
        PARAMETERS:
            sqlQuery:
                Required Argument.
                Specifies the sql query.
                Types: str
                Supported query syntax: "SHOW TABLES [{FROM|IN} database_name] [LIKE 'regex_pattern']"
        RETURNS:
            Pandas DataFrame

        EXAMPLES:
        >>> _select_query("show tables in alice LIKE 'sales_%';")
        """
        from teradatamlspk.sql.dataframe import DataFrame
        match = re.search(r'''^\s*SHOW\s+TABLES
                        (?:\s+(?:FROM|IN)\s+(?P<schema>\w+))?
                        (?:\s+LIKE\s+'(?P<regex>[^']*)')?
                        ''',sqlQuery, re.IGNORECASE | re.VERBOSE)

        # Fetching the database name and regex_pattern from the captured groups.
        schema_name = match.group('schema')
        object_name = match.group('regex')
        return db_list_tables(schema_name, object_name)

    @staticmethod
    def _describe_table_query(sqlQuery):
        """
        DESCRIPTION:
            Returns the teradatamlspk DataFrame metadata containing column names and
            corresponding teradatasqlalchemy types. based on the "DESCRIBE TABLE" query.
        PARAMETERS:
            sqlQuery:
                Required Argument.
                Specifies the sql query.
                Types: str
                Supported query syntax: "{ DESC | DESCRIBE } [ TABLE ] [ format ] table_identifier [ partition_spec ] [ col_name ]"
                                        "table_identifier" syntax: [ database_name. ] table_name
                                Note: Parameters "format", "partition_spec", "col_name" can be passed to the query 
                                      but will be ignored in further operation.

        RETURNS:
            MetaData containing the column names and Teradata types

        EXAMPLES:
        >>> _describe_table_query("DESCRIBE TABLE sales;")
        """
        from teradatamlspk.sql.dataframe import DataFrame
        match = re.search(r'^\s*(?:DESC|DESCRIBE)\s+(?:TABLE\s+)?(?:\w+\s+)?(?:\w+\.)?(?P<table>\w+)',sqlQuery, re.IGNORECASE)
        table_name = match.group('table')
        return tdml_DataFrame(table_name).tdtypes

    @staticmethod
    def _create_or_replace_view_query(sqlQuery):
        """
        DESCRIPTION:
            Create or Replace a view based on the "CREATE VIEW" query.
        PARAMETERS:
            sqlQuery:
                Required Argument.
                Specifies the sql query.
                Types: str
                Supported query syntax: "CREATE [OR REPLACE] [[GLOBAL] TEMPORARY] VIEW [IF NOT EXISTS] [db_name.]view_name create_view_clauses AS query;"
                                        "query" format: SELECT statements
                                Note: Parameters "[GLOBAL] TEMPORARY", "IF NOT EXISTS", "create_view_clauses" can be passed to the query 
                                      but will be ignored in further operation.
        RETURNS:
            Cursor object.

        EXAMPLES:
        >>> _create_or_replace_view_query("CREATE VIEW alice.FebData AS select Feb from sales;")
        """
        # Check if 'or replace' exists or not in the query.
        or_replace_exists = 'OR REPLACE' in sqlQuery.upper()
        # Extract schema and view names
        match = re.search(r'^\s*CREATE\s+(?:OR REPLACE\s+)?(?:GLOBAL\s+TEMPORARY\s+|TEMPORARY\s+)?VIEW\s+(?:IF NOT EXISTS\s+)?(?:(?P<schema_name>\w+)\.)?(?P<view_name>\w+)',
                          sqlQuery, re.IGNORECASE)
        schema_name = match.group('schema_name')
        view_name =match.group('view_name')
        if or_replace_exists:
            try:
                db_drop_view(view_name, schema_name)
            except:
                pass

        # Transforms the query in format 
        # "CREATE [OR REPLACE] [[GLOBAL] TEMPORARY] VIEW [IF NOT EXISTS] [db_name.]view_name create_view_clauses AS query;"
        # to "CREATE VIEW [db_name.]view_name AS query;"
        query = re.sub(r'CREATE\s+(?:OR REPLACE\s+)?(?:GLOBAL\s+TEMPORARY\s+|TEMPORARY\s+)?VIEW\s+(?:IF NOT EXISTS\s+)?',
                        'CREATE VIEW ', sqlQuery, flags=re.IGNORECASE).strip()
        return execute_sql(query)

    @staticmethod
    def _execute_query(query):
        """ Function to map the SQL query to the corresponding function to execute the query if exists,
            else execute it using teradataml execute_sql()"""
        for pattern, func in query_mapper.items():
            if re.search(pattern, query, re.IGNORECASE):
                return func(query)
        return execute_sql(query)
    
query_mapper = OrderedDict([
    (r'^\s*DROP\s+TABLE\s+IF\s+EXISTS', SQLquery._drop_table_if_exists_query),
    (r'^\s*select', SQLquery._select_query),
    (r'^\s*SHOW\s+TABLES', SQLquery._show_table_query),
    (r'^\s*DESC|DESCRIBE', SQLquery._describe_table_query),
    (r'^\s*CREATE\s+(?:OR REPLACE\s+)?(?:GLOBAL\s+TEMPORARY\s+|TEMPORARY\s+)?VIEW', SQLquery._create_or_replace_view_query)
])
        

    

