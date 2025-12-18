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
import re
from sqlalchemy import func, literal_column, literal
from teradataml import configure, execute_sql
from teradatamlspk.sql.column import Column
from teradataml.dataframe.sql import _SQLColumnExpression
from teradatasqlalchemy.types import INTEGER, SMALLINT, BYTEINT, DATE, FLOAT, NUMBER, INTERVAL_DAY_TO_SECOND, INTERVAL_YEAR_TO_MONTH, VARCHAR, TIMESTAMP, BIGINT, CHAR
from teradatamlspk.sql.types import StringType
from teradatamlspk.sql.dataframe_utils import DataFrameUtils as df_utils
from teradataml.dataframe.functions import call_udf as tdml_call_udf, make_interval as tdml_make_interval, sequence as tdml_sequence
from teradataml.dataframe.array import Array

# Suppressing the Validation in teradataml.
# Suppress the validation. PySpark accepts the columns in the form of a
# standalone Columns, i.e.,
# >>> from PySpark.sql.functions import col, sum
# >>> column_1 = col('x')
# >>> column_2 = col('y')
# >>> df.withColumn('new_column', sum(column1+column2).over(WindowSpec)
# Note that the above expression accepts Columns which are not bounded to
# any table. Since compilation is at run time in PySpark, if columns does not exist,
# the expression fails - BUT AT RUN TIME. On the other side, teradataml
# validates every thing before running it. To enable this behaviour,
# we are suppressing the validation.
from teradataml.common.utils import _Validators
from teradataml.dataframe.sql_functions import to_numeric, case as case_when
_Validators.skip_all = True
from sqlalchemy import literal_column, func, case, literal

_get_sqlalchemy_expr = lambda col: literal_column(col) if isinstance(col, str) else literal(col)
_get_tdml_col = lambda col: _SQLColumnExpression(_get_sqlalchemy_expr(col)) if isinstance(col, (str, int, float)) else col._tdml_column

col = lambda col: Column(tdml_column=_SQLColumnExpression(col))

column = lambda col: Column(tdml_column=_SQLColumnExpression(col))
lit = lambda col: Column(tdml_column=_SQLColumnExpression(literal(col)))
broadcast = lambda df: df
def coalesce(*cols):

    # cols can be a name of column or ColumnExpression. Prepare tdml column first.
    cols = [_SQLColumnExpression(col).expression if isinstance(col, str) else col._tdml_column.expression for col in cols]
    return Column(tdml_column=_SQLColumnExpression(func.coalesce(*cols)))

def input_file_name():
    raise NotImplementedError

isnan = lambda col: Column(tdml_column=(_SQLColumnExpression(col) if isinstance(col, str) else col._tdml_column).isna())
isnull = lambda col: Column(tdml_column=(_SQLColumnExpression(col) if isinstance(col, str) else col._tdml_column).isna())
monotonically_increasing_id = lambda : Column(tdml_column=_SQLColumnExpression('sum(1) over( rows unbounded preceding )'))
def named_struct(*cols):
    raise NotImplementedError
nanvl = lambda col1, col2: Column(tdml_column=_SQLColumnExpression(func.nvl(_get_tdml_col(col1).expression, _get_tdml_col(col2).expression)))
rand = lambda seed=0: Column(tdml_column=_SQLColumnExpression("cast(random(0,999999999) as float)/1000000000 (format '9.999999999')"))
randn = lambda seed=0: Column(tdml_column=_SQLColumnExpression("cast(random(0,999999999) as float)/1000000000 (format '9.999999999')"))
spark_partition_id = lambda: Column(tdml_column=_SQLColumnExpression("0"))
when = lambda condition, value: Column(tdml_column=_SQLColumnExpression(case((_get_tdml_col(condition).expression, value._tdml_column.expression if isinstance(value, Column) else value))))
bitwise_not = lambda col: Column(tdml_column=col._tdml_column.bitwise_not() if isinstance(col, Column) else _SQLColumnExpression(col).bitwise_not())
bitwiseNOT = lambda col: Column(tdml_column=col._tdml_column.bitwise_not() if isinstance(col, Column) else _SQLColumnExpression(col).bitwise_not())
expr = lambda str: Column(tdml_column=_SQLColumnExpression(str))
greatest = lambda *cols: Column(tdml_column=_get_tdml_col(cols[0]).greatest(*[_get_tdml_col(col) for col in cols[1:]]))
least = lambda *cols: Column(tdml_column=_get_tdml_col(cols[0]).least(*[_get_tdml_col(col) for col in cols[1:]]))
sqrt = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)<0, None)], else_=_get_tdml_col(col).sqrt()))
abs = lambda col: Column(tdml_column=_get_tdml_col(col).abs())
acos = lambda col: Column(tdml_column=case_when([((_get_tdml_col(col)<-1) | (_get_tdml_col(col)>1), None)], else_=_get_tdml_col(col).acos()))
asin = lambda col: Column(tdml_column=case_when([((_get_tdml_col(col)<-1) | (_get_tdml_col(col)>1), None)], else_=_get_tdml_col(col).asin()))
asinh = lambda col: Column(tdml_column=_get_tdml_col(col).asinh())
atan = lambda col: Column(tdml_column=_get_tdml_col(col).atan())
atanh = lambda col: Column(tdml_column=case_when([((_get_tdml_col(col)<=-1) | (_get_tdml_col(col)>=1), None)], else_=_get_tdml_col(col).atanh()))
atan2 = lambda col1, col2: Column(tdml_column=_get_tdml_col(col2).atan2(_get_tdml_col(col1)))
# For negative values, Compute the 2's complement with 64 bits, as PySpark returns all negative values in binary as 64-bit numbers.
bin= lambda col: Column(tdml_column=_SQLColumnExpression(case((_get_tdml_col(col).expression == 0, literal('0')),
                                                              (_get_tdml_col(col).expression > 0, _get_tdml_col(col).cast(BIGINT).cast(NUMBER).to_byte().from_byte('base2').expression),
                                                              else_=(_get_tdml_col(col).cast(BIGINT) + 2**64).cast(NUMBER).to_byte().from_byte('base2').expression)))
cbrt = lambda col: Column(tdml_column = case_when([((_get_tdml_col(col)==0), 0.0)], else_=_get_tdml_col(col).sign() * _get_tdml_col(col).abs().cbrt()))
ceil = lambda col: Column(tdml_column=_get_tdml_col(col).ceil())
ceiling = lambda col: Column(tdml_column=_get_tdml_col(col).ceiling())
conv = lambda col, fromBase, toBase : Column(tdml_column=_get_tdml_col(col).to_byte('base'+str(fromBase)).from_byte('base'+str(toBase)))
cos = lambda col: Column(tdml_column=_get_tdml_col(col).cos())
cosh = lambda col: Column(tdml_column=_get_tdml_col(col).cosh())
cot = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)==0, None)], else_=(1/_get_tdml_col(col).tan())))
csc = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)==0, None)], else_=(1/_get_tdml_col(col).sin())))
e = lambda: Column(tdml_column=_SQLColumnExpression(literal(2.718281828459045)))
exp = lambda col: Column(tdml_column=_get_tdml_col(col).exp())
expm1 = lambda col: Column(tdml_column=_get_tdml_col(col).exp()-1)
def factorial(col):
    raise NotImplementedError
floor = lambda col: Column(tdml_column=_get_tdml_col(col).floor())
hex = lambda col: Column(tdml_column=_get_tdml_col(col).floor().cast(INTEGER()).hex())
unhex = lambda col: Column(tdml_column=_get_tdml_col(col).unhex())
hypot = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).hypot(_get_tdml_col(col2)))
ln = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)<=0, None)], else_=_get_tdml_col(col).ln()))
log = lambda arg1, arg2: Column(tdml_column=case_when([((_get_tdml_col(arg1)<=0) | (_get_tdml_col(arg2)<=0), None)], else_=_get_tdml_col(arg2).log(_get_tdml_col(arg1))))
log10 = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)<=0, None)], else_=_get_tdml_col(col).log10()))
log1p = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col+1)<=0, None)], else_=_get_tdml_col(col+1).ln()))
log2 = lambda col: Column(tdml_column=case_when([(_get_tdml_col(col)<=0, None)], else_=_get_tdml_col(col).log(2.0)))
negate = lambda col: Column(tdml_column=_get_tdml_col(col)*-1)
negative = lambda col: Column(tdml_column=_get_tdml_col(col)*-1)
pi = lambda: Column(tdml_column=_SQLColumnExpression(literal(3.141592653589793)))
pmod = lambda dividend, divisor: Column(tdml_column=(_get_tdml_col(dividend)) % (_get_tdml_col(divisor)))
positive = lambda col: Column(tdml_column=_get_tdml_col(col)*1)
pow = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).pow(_get_tdml_col(col2)))
power = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).pow(_get_tdml_col(col2)))
rint = lambda col: Column(tdml_column=_get_tdml_col(col).round(0))
round = lambda col, scale=0: Column(tdml_column=_get_tdml_col(col).round(scale) if scale >= 0 else _get_tdml_col(col).trunc())
bround = lambda col, scale=0: Column(tdml_column=_get_tdml_col(col).round(scale) if scale >= 0 else _get_tdml_col(col).trunc())

def shiftrightunsigned(col, numBits):
    raise NotImplementedError
sign = lambda col: Column(tdml_column=_get_tdml_col(col).sign())
signum = lambda col: Column(tdml_column=_get_tdml_col(col).sign())
sin = lambda col: Column(tdml_column=_get_tdml_col(col).sin())
sinh = lambda col: Column(tdml_column=_get_tdml_col(col).sinh())
tan = lambda col: Column(tdml_column=_get_tdml_col(col).tan())
tanh = lambda col: Column(tdml_column=_get_tdml_col(col).tanh())
toDegrees = lambda col: Column(tdml_column=_get_tdml_col(col).degrees())

# TODO: Ideal way is to write user defined function for all try-<arthimatic function> type functions.
try_add = lambda left, right: Column(tdml_column=_get_tdml_col(left) + _get_tdml_col(right))
try_avg = lambda col: Column(tdml_column=_get_tdml_col(col).avg())
try_divide = lambda left, right: Column(tdml_column=_get_tdml_col(left) / _get_tdml_col(right))
try_multiply = lambda left, right: Column(tdml_column=_get_tdml_col(left) * _get_tdml_col(right))
try_subtract = lambda left, right: Column(tdml_column=_get_tdml_col(left) - _get_tdml_col(right))
try_sum = lambda left: Column(tdml_column=_get_tdml_col(left).sum())

try_to_number = lambda col, format=None: Column(tdml_column=to_numeric(_get_tdml_col(col), format_ = format))
degrees = toDegrees
toRadians = lambda col: Column(tdml_column=_get_tdml_col(col).radians())
radians = toRadians
width_bucket = lambda v, min, max, numBucket: Column(tdml_column=_SQLColumnExpression(func.width_bucket(
    _get_tdml_col(v).expression, _get_tdml_col(min).expression, _get_tdml_col(max).expression, _get_tdml_col(numBucket).expression)))
add_months = lambda start, months: Column(tdml_column=_get_tdml_col(start).add_months(_get_tdml_col(months)))
def not_implemented(*args, **kwargs):
    raise NotImplementedError
def unknown(*args, **kwargs):
    raise NotImplementedError
convert_timezone = lambda sourceTz, targetTz, sourceTs:\
    Column(tdml_column=_get_tdml_col(sourceTs).
           concat("", _get_tdml_col(sourceTs).
                  cast(TIMESTAMP).
                  cast(TIMESTAMP(timezone=True), timezone=_get_tdml_col(sourceTz)).
                  to_char('TZH:TZM')).
           cast(TIMESTAMP).
           cast(TIMESTAMP(timezone=True), timezone = _get_tdml_col(targetTz)).
           to_char('YYYY-MM-DD HH24:MI:SS.FF6').
           cast(TIMESTAMP)) if sourceTz else Column(tdml_column=_get_tdml_col(sourceTs).cast(TIMESTAMP)\
                                                    .cast(TIMESTAMP(timezone=True), timezone=_get_tdml_col(targetTz)).\
                                                    to_char('YYYY-MM-DD HH24:MI:SS.FF6').cast(TIMESTAMP))
curdate = lambda : Column(tdml_column=_SQLColumnExpression(func.CURRENT_DATE()))
current_date = lambda : Column(tdml_column=_SQLColumnExpression(func.CURRENT_DATE()))
current_timestamp = lambda : Column(tdml_column=_SQLColumnExpression(func.CURRENT_TIMESTAMP()))
current_timezone = lambda : Column(tdml_column=_SQLColumnExpression(func.to_char(func.CURRENT_TIMESTAMP(), 'TZH:TZM'), type=VARCHAR))
date_add = lambda start, days: Column(tdml_column=_SQLColumnExpression(literal_column("({}) + (nvl({}, 0)  * interval '1' DAY)".format(_get_tdml_col(start).compile(), _get_tdml_col(days).compile()))))
date_diff = lambda end, start: Column(tdml_column=_get_tdml_col(end) - _get_tdml_col(start))
date_format = lambda date, format: Column(tdml_column=_get_tdml_col(date).to_char( _format_date_string(format)))
date_from_unix_date = lambda days:  Column(tdml_column=(_get_tdml_col(days)*24*60*60).cast(BIGINT).to_timestamp(timezone='GMT').to_char('YYYY-MM-DD').cast(DATE))
_trunc_map = {'MINUTE': 'MI', 'HOUR': 'HH', 'DAY': 'DDD', 'WEEK': 'IW', 'QUARTER': 'Q'}
date_trunc = lambda format, timestamp: Column(tdml_column=_get_tdml_col(timestamp).trunc(formatter=_trunc_map.get(format.upper(), format.upper())))
dateadd = date_add
datediff = date_diff
day = lambda col: Column(tdml_column=_get_tdml_col(col).day_of_month())
_extractDict = {"YEAR": "YEAR", "MONTH":"MONTH", "D": "DAY", "M": "MINUTE", "S": "SECOND", "HOUR":"HOUR", "TIMEZONE_HOUR":"TIMEZONE_HOUR", "TIMEZONE_MINUTE": "TIMEZONE_MINUTE"}
extract = lambda field, source: Column(tdml_column=_get_tdml_col(source).extract(_extractDict.get(field.upper())))
date_part = extract
datepart = extract
dayofmonth = lambda col: Column(tdml_column=_get_tdml_col(col).day_of_month())
dayofweek = lambda col: Column(tdml_column=_get_tdml_col(col).day_of_week())
dayofyear = lambda col: Column(tdml_column=_get_tdml_col(col).day_of_year())
second = lambda col: Column(tdml_column=_get_tdml_col(col).second())
weekofyear = lambda col: Column(tdml_column=_get_tdml_col(col).week_of_year()+1)
year = lambda col: Column(tdml_column=_get_tdml_col(col).year())
quarter = lambda col: Column(tdml_column=_get_tdml_col(col).quarter_of_year())
month = lambda col: Column(tdml_column=_get_tdml_col(col).month_of_year())
last_day = lambda col: Column(tdml_column=_get_tdml_col(col).month_end())
localtimestamp = lambda: Column(tdml_column=_SQLColumnExpression(literal_column('CURRENT_TIMESTAMP AT LOCAL')))
_none_if = lambda x, y: _get_tdml_col(x).to_interval(y, INTERVAL_DAY_TO_SECOND(4, 6)) if x else _SQLColumnExpression(literal(0)).to_interval(y, INTERVAL_DAY_TO_SECOND(4, 6))
make_dt_interval = lambda days=None, hours=None, mins=None, secs=None: \
    Column(tdml_column=(_none_if(days, 'DAY') +
                        _none_if(hours, 'HOUR') +
                        _none_if(mins, 'MINUTE') +
                        _none_if(secs, 'SECOND')).cast(INTERVAL_DAY_TO_SECOND(4, 6)))

make_interval = lambda years=None, months=None, weeks=None, days=None, \
                  hours=None, mins=None, secs=None: Column(tdml_column=tdml_make_interval(
                  years=_get_tdml_col(years) if years is not None else None,
                  months=_get_tdml_col(months) if months is not None else None,
                  weeks=_get_tdml_col(weeks) if weeks is not None else None,
                  days=_get_tdml_col(days) if days is not None else None,
                  hours=_get_tdml_col(hours) if hours is not None else None,
                  minutes=_get_tdml_col(mins) if mins is not None else None,
                  seconds=_get_tdml_col(secs) if secs is not None else None))

def make_timestamp(years, months, days, hours, mins, secs, timezone=None):
    if timezone:
        _str_col = (_get_tdml_col(years).to_char('0999').ltrim()+'-'+
                                    _get_tdml_col(months).to_char('09').ltrim()+'-'+
                                    _get_tdml_col(days).to_char('09').ltrim()+' '+
                                    _get_tdml_col(hours).to_char('09').ltrim()+':'+
                                    _get_tdml_col(mins).to_char('09').ltrim()+':'+
                                    _get_tdml_col(secs).to_char('09.999999').ltrim())
        return Column(tdml_column = _str_col.
                      concat("", _str_col.cast(TIMESTAMP).
                             cast(TIMESTAMP(timezone=True), timezone=_get_tdml_col(timezone)).
                             to_char('TZH:TZM')).
                      cast(TIMESTAMP))
    return make_timestamp_ntz(years, months, days, hours, mins, secs)

make_timestamp_ltz = make_timestamp
make_timestamp_ntz = lambda years, months, days, hours, mins, secs: \
    Column(tdml_column = (_get_tdml_col(years).to_char('0999').ltrim()+'-'+
                          _get_tdml_col(months).to_char('09').ltrim()+'-'+
                          _get_tdml_col(days).to_char()+' '+
                          _get_tdml_col(hours).to_char()+':'+
                          _get_tdml_col(mins).to_char()+':'+
                          _get_tdml_col(secs).to_char('99999.999999').ltrim()).to_timestamp(format='YYYY-MM-DD HH24:MI:SS.FF6'))
make_ym_interval = lambda years=None, months=None: \
    Column(tdml_column = ((_get_tdml_col(years).to_interval('YEAR', INTERVAL_YEAR_TO_MONTH) if years else _SQLColumnExpression(literal(0)).to_interval('YEAR', INTERVAL_YEAR_TO_MONTH)) +
                         (_get_tdml_col(months).to_interval('MONTH', INTERVAL_YEAR_TO_MONTH) if months else _SQLColumnExpression(literal(0)).to_interval('MONTH', INTERVAL_YEAR_TO_MONTH))).cast(INTERVAL_YEAR_TO_MONTH(4)))
minute = lambda col: Column(tdml_column=_get_tdml_col(col).minute())
months_between = lambda date1, date2, roundOff=True : Column(tdml_column=_get_tdml_col(date1).months_between(_get_tdml_col(date2))) \
    if not roundOff else Column(tdml_column=_get_tdml_col(date1).months_between(_get_tdml_col(date2)).round(8))
_day_names = {"Mon": "MONDAY", "Tue": "TUESDAY", "Wed": "WEDNESDAY", "Thu": "THURSDAY", "Fri": "FRIDAY", "Sat": "SATURDAY", "Sun": "SUNDAY"}
next_day = lambda date, dayOfWeek: Column(tdml_column=_get_tdml_col(date).next_day(_day_names[dayOfWeek]))
hour = lambda col: Column(tdml_column=_get_tdml_col(col).hour())
make_date = lambda year, month, day: Column(tdml_column =(_get_tdml_col(year).to_char('0999').ltrim() + '-' +
                                                         _get_tdml_col(month).to_char('09').ltrim()+ '-' +
                                                         _get_tdml_col(day).to_char()).to_date())
now = localtimestamp
from_unixtime = lambda timestamp, format=None: Column(tdml_column=_get_tdml_col(timestamp).to_timestamp().to_char(formatter=_format_date_string(format) if format else format))
unix_timestamp = lambda timestamp, format=None: time_difference(
    Column(tdml_column = _get_tdml_col(timestamp).
           cast(TIMESTAMP, format=_format_date_string(format)).
           cast(TIMESTAMP(timezone=True), timezone='GMT').
           to_char('YYYY-MM-DD HH24:MI:SS.FF6').
           cast(TIMESTAMP)),
    Column(tdml_column = _SQLColumnExpression(literal_column('CAST(\'1970-01-01 00:00:00\' as TIMESTAMP)'))))
to_unix_timestamp = unix_timestamp

to_timestamp = lambda col, format=None: Column(tdml_column=_get_tdml_col(col).cast(TIMESTAMP, format= _format_date_string_cast(format) if format else None))
to_timestamp_ltz = lambda col, format=None: Column(tdml_column=_get_tdml_col(col).to_timestamp(format=(_get_tdml_col(format) if format else 'YYYY-MM-DD HH24:MI:SS.FF6')))
to_timestamp_ntz = lambda col, format=None:  Column(tdml_column=_get_tdml_col(col).to_timestamp(format=(_get_tdml_col(format) if format else 'YYYY-MM-DD HH24:MI:SS.FF6')))
to_date = lambda col, format=None: Column(tdml_column=_get_tdml_col(col).to_date(format)) if format else Column(tdml_column=_get_tdml_col(col).cast(DATE))
trunc = lambda date, format: Column(tdml_column=_get_tdml_col(date).trunc(formatter=_trunc_map.get(format.upper(), format.upper())))

from_utc_timestamp = lambda timestamp, tz: Column(tdml_column=_get_tdml_col(timestamp).
           concat("", _get_tdml_col(timestamp).
                  cast(TIMESTAMP).
                  cast(TIMESTAMP(timezone=True), timezone='GMT').
                  to_char('TZH:TZM')).
           cast(TIMESTAMP).
           cast(TIMESTAMP(timezone=True), timezone=tz if isinstance(tz, str) else _get_tdml_col(tz)).
           to_char('YYYY-MM-DD HH24:MI:SS.FF6').
           cast(TIMESTAMP))
to_utc_timestamp = lambda timestamp, tz: Column(tdml_column=_get_tdml_col(timestamp).
           concat("", _get_tdml_col(timestamp).
                  cast(TIMESTAMP).
                  cast(TIMESTAMP(timezone=True), timezone=tz if isinstance(tz, str) else _get_tdml_col(tz)).
                  to_char('TZH:TZM')).
           cast(TIMESTAMP).
           cast(TIMESTAMP(timezone=True), timezone = 'GMT').
           to_char('YYYY-MM-DD HH24:MI:SS.FF6').
           cast(TIMESTAMP))
weekday = lambda col: Column(tdml_column=_get_tdml_col(col).day_of_week()-2)
window = unknown
session_window = unknown
timestamp_micros = lambda col: Column(tdml_column = (_get_tdml_col(col)*10**-6).cast(BIGINT).to_timestamp())
timestamp_millis = lambda col: Column(tdml_column = (_get_tdml_col(col)*10**-3).cast(BIGINT).to_timestamp())
timestamp_seconds = lambda col: Column(tdml_column = _get_tdml_col(col).cast(BIGINT).to_timestamp())
try_to_timestamp = to_timestamp
unix_date = lambda col: Column(tdml_column=_SQLColumnExpression(_get_tdml_col(col).expression-func.to_date("1970-01-01", 'YYYY-MM-DD')))
unix_micros = lambda col: time_difference(Column(tdml_column = col._tdml_column.cast(TIMESTAMP(timezone=True), timezone='GMT').to_char('YYYY-MM-DD HH24:MI:SS.FF6').cast(TIMESTAMP)),
                           Column(tdml_column = _SQLColumnExpression(literal_column('CAST(\'1970-01-01 00:00:00\' as TIMESTAMP)'))),
                           10**6)
unix_millis = lambda col: time_difference(Column(tdml_column = col._tdml_column.cast(TIMESTAMP(timezone=True), timezone='GMT').to_char('YYYY-MM-DD HH24:MI:SS.FF6').cast(TIMESTAMP)),
                           Column(tdml_column = _SQLColumnExpression(literal_column('CAST(\'1970-01-01 00:00:00\' as TIMESTAMP)'))),
                           10**3)
unix_seconds = lambda col: time_difference(Column(tdml_column = col._tdml_column.cast(TIMESTAMP(timezone=True), timezone='GMT').to_char('YYYY-MM-DD HH24:MI:SS.FF6').cast(TIMESTAMP)),
                           Column(tdml_column = _SQLColumnExpression(literal_column('CAST(\'1970-01-01 00:00:00\' as TIMESTAMP)'))))

window_time = unknown

def _generate_array_func_col_name(fn_name, *raw_args):
    """
    DESCRIPTION:
        Helper function to generate the default alias name for array functions Column.

    PARAMETERS:
        fn_name:
            Required Argument.
            The function name.
            Type: str

        raw_args:
            Required Argument.
            The function arguments.
            Type: Column, string, or literal value

    RETURNS:
        str

    EXAMPLE:
    >>> _generate_array_func_col_name('array', 'col1', 'col2', 5)
    'array_col1_col2_5'
    """
    rendered = []

    # Support PySpark-style single-list form, e.g. array(['a', 'b'])
    args = raw_args[0] if len(raw_args) == 1 and isinstance(raw_args[0], (list)) else raw_args

    for arg in args:
        # Check if argument is a Column
        if isinstance(arg, Column):
            tdml_col = getattr(arg, "_tdml_column", None)

            # Prefer column name
            if getattr(tdml_col, "name", None):
                rendered.append(tdml_col.name)
                continue

            # Otherwise check expression
            expr = getattr(tdml_col, "expression", None)
            if expr is not None and hasattr(expr, "value"):
                rendered.append(str(expr.value))
                continue

        # Default case
        rendered.append(str(arg))

    return f"{fn_name}_{'_'.join(rendered)}"

def array(*cols):
    """
    DESCRIPTION:
        Creates an array column from the specified columns.

    PARAMETERS:
        cols: 
            Required Argument.
            The columns to include in the array.
            Type: Column, string, or literal value

    RETURNS:
        Column
    """
    # Mark the column as an array column for handling in DataFrame.select() method
    # We don't create the actual Array object here, as we don't have dataframe context
    # Instead, we'll pass the elements and let the DataFrame.select() method handle them.
    elements = []
    for col in cols:
        elements.append(col)
    
    return Column(expression=None, array_col=tuple(elements),
                  alias_name=_generate_array_func_col_name('array', *cols))

def element_at(col, index):
    """
    DESCRIPTION:
        Returns the element at the specified position in the array.

    PARAMETERS:
        col: 
            Required Argument.
            The array column to extract the element from.
            Type: Column

        index: 
            Required Argument.
            The position of the element to retrieve (1-based index).
            Type: int

    RETURNS:
        Column
    """
    # Create a case expression to check if the effective index is within bounds.
    # Compute effective_index: for negative index, treat as from end (1-based).
    # effective_index = array_size + index + 1 
    array_size_expr = _get_tdml_col(col).array_size()
    effective_index = case_when([(_get_tdml_col(index) <= 0, array_size_expr + _get_tdml_col(index) + 1)], \
                                else_=_get_tdml_col(index))
    result = case_when([
        # If negative index exceeds array size or is zero, return NULL
        (effective_index <= 0, None),
        (effective_index > array_size_expr, None)
    ], else_=_get_tdml_col(col).get(effective_index))
    return Column(tdml_column=result, 
                  alias_name=_generate_array_func_col_name('element_at', col, index))

def get(col, index):
    """
    DESCRIPTION:
        Returns the element at the specified position in the array.
        Behavior:
        - If index is an int literal, use element_at(col, index+1).
        - If index is a Column (expression), build tdml index expression, cast numeric
            index types to INTEGER and use _get_tdml_col(col).get(idx_ce).
        - Otherwise fallback to element_at for non-Column expressions.

    PARAMETERS:
        col:
            Required Argument.
            The array column to extract the element from.
            Type: Column
        
        index:
            Required Argument.
            The position of the element to retrieve (0-based index).
            Type: int or Column

    RETURNS:
        Column
    """
    # If index is a Column that wraps a literal integer (e.g. lit(2)), treat it
    # as an integer literal and use element_at. This handles cases where users
    # pass a literal via Column(...) rather than a bare int.
    if isinstance(index, Column):
        inner_expr = getattr(index._tdml_column, 'expression', None)
        literal_val = getattr(inner_expr, 'value', None)
        if isinstance(literal_val, int):
            return Column(tdml_column=element_at(col, literal_val + 1)._tdml_column,
                            alias_name=_generate_array_func_col_name('get', col, index))

    # Literal integer index -> use 1-based element_at
    if isinstance(index, int):
        return Column(tdml_column=element_at(col, index + 1)._tdml_column,
                      alias_name=_generate_array_func_col_name('get', col, index))

    # Build tdml expression for index+1 (covers Column and expression cases)
    idx_ce = _get_tdml_col(index + 1)
    idx_ce = idx_ce.cast(INTEGER()) # Directly cast to INTEGER types. 
    return Column(tdml_column=_get_tdml_col(col).get(idx_ce),
                  alias_name=_generate_array_func_col_name('get', col, index))

size = lambda col: Column(tdml_column=_get_tdml_col(col).array_size(),
                          alias_name=_generate_array_func_col_name('size', col))

cardinality = lambda col: Column(tdml_column=_get_tdml_col(col).array_size(),
                                 alias_name=_generate_array_func_col_name('cardinality', col))

array_contains = lambda col, value: Column(tdml_column=_get_tdml_col(col).array_contains(_get_tdml_col(value) \
                                            if isinstance(value, Column) else value),
                                           alias_name=_generate_array_func_col_name('array_contains', col, value))

array_size = lambda col: Column(tdml_column=_get_tdml_col(col).array_size(),
                                alias_name=_generate_array_func_col_name('array_size', col))

array_max = lambda col: Column(tdml_column=_get_tdml_col(col).array_max(),
                               alias_name=_generate_array_func_col_name('array_max', col))

array_min = lambda col: Column(tdml_column=_get_tdml_col(col).array_min(),
                               alias_name=_generate_array_func_col_name('array_min', col))

array_agg = lambda col: Column(tdml_column=_get_tdml_col(col).array_agg(),
                                alias_name=_generate_array_func_col_name('collect_list', col), is_array_col=True)

try_element_at = lambda col, index: Column(tdml_column=element_at(col, index)._tdml_column,
                                           alias_name=_generate_array_func_col_name('try_element_at', col, index))

create_map = not_implemented
explode = lambda col:Column(explode_expr = (col, False))
explode_outer = explode
posexplode = lambda col:Column(explode_expr = (col, True))
posexplode_outer = posexplode

def concat(*cols):
    """
    DESCRIPTION:
        Concatenates multiple columns into a single column.
        When used with array columns, performs array concatenation.
        Otherwise, performs string concatenation.

    PARAMETERS:
        cols: 
            Required Argument.
            A variable number of column expressions or column names to concatenate.
            Type: Column or str

    RETURNS:
        Column: A column representing the concatenation result.
    """
    if len(cols) == 1:
        return cols[0]
    
    # Create a column with a special marker for concat operation
    # The actual concatenation will be determined in the DataFrame methods
    # based on the column types
    tdml_columns = [_get_tdml_col(col) for col in cols]
    
    # Create a column with concat_columns attribute to hold the original columns
    # and use it to determine the correct concat operation later
    return Column(tdml_column=tdml_columns[0],
                  concat_columns=tdml_columns[1:],
                  alias_name=_generate_array_func_col_name('concat', *cols))

array_position = not_implemented
array_append = lambda arr, element: Column(tdml_column=_get_tdml_col(arr).array_append(_get_tdml_col(element) \
                                            if element is not None else _SQLColumnExpression(literal(None))), 
                                           alias_name=_generate_array_func_col_name('array_append', arr, element))

array_prepend = lambda arr, element: Column(tdml_column=_get_tdml_col(arr).array_prepend(_get_tdml_col(element) \
                                            if element is not None else _SQLColumnExpression(literal(None))), 
                                            alias_name=_generate_array_func_col_name('array_prepend', arr, element))

array_sort = lambda col, comparator=None: Column(tdml_column=_get_tdml_col(col).array_sort(),
                                alias_name=_generate_array_func_col_name('array_sort', col))

array_insert = lambda arr, pos, value: Column(tdml_column=_get_tdml_col(arr).array_insert(pos if isinstance(pos, int) else _get_tdml_col(pos),
                                                                                          _get_tdml_col(value)if isinstance(value, Column) else value),
                                              alias_name=_generate_array_func_col_name('array_insert', arr, pos, value))

array_remove = lambda col, element: Column(tdml_column=_get_tdml_col(col).array_remove(_get_tdml_col(element) if isinstance(element, Column) else element),
                                           alias_name=_generate_array_func_col_name('array_remove', col, element))

array_distinct = lambda col: Column(tdml_column=_get_tdml_col(col).array_distinct(),
                                   alias_name=_generate_array_func_col_name('array_distinct', col))

array_intersect = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).array_intersect(_get_tdml_col(col2)),
                                            alias_name=_generate_array_func_col_name('array_intersect', col1, col2))

array_union = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).array_union(_get_tdml_col(col2)),
                                        alias_name=_generate_array_func_col_name('array_union', col1, col2))

array_except = lambda col1, col2: Column(tdml_column=_get_tdml_col(col1).array_except(_get_tdml_col(col2)),
                                        alias_name=_generate_array_func_col_name('array_except', col1, col2))

array_compact = lambda col: Column(tdml_column=_get_tdml_col(col).array_compact(),
                                  alias_name=_generate_array_func_col_name('array_compact', col))

arrays_overlap = lambda a1, a2: Column(tdml_column=_get_tdml_col(a1).array_overlap(_get_tdml_col(a2)),
                                           alias_name=_generate_array_func_col_name('arrays_overlap', a1, a2))

array_position = lambda col, value: Column(tdml_column=_get_tdml_col(col).array_position(_get_tdml_col(value) if isinstance(value, Column) else value),
                                          alias_name=_generate_array_func_col_name('array_position', col, value))

array_join = lambda col, delimiter, null_replacement=None: Column(tdml_column=_get_tdml_col(col).array_join(delimiter, null_replacement),
                                                                  alias_name=_generate_array_func_col_name('array_join', col, delimiter, null_replacement))

slice = lambda x, start, length=None: Column(tdml_column=_get_tdml_col(x).slice(start if isinstance(start, int) else _get_tdml_col(start),
                                                                                      length if isinstance(length, int) else _get_tdml_col(length)),
                                            alias_name=_generate_array_func_col_name('slice', x, start, length))

shuffle = lambda col: Column(tdml_column=_get_tdml_col(col).shuffle(),
                                       alias_name=_generate_array_func_col_name('shuffle', col))

reverse = lambda col: Column(tdml_column=_get_tdml_col(col), reverse_column=_get_tdml_col(col),
                              alias_name=_generate_array_func_col_name('reverse', col))

sort_array = lambda col, asc=True: Column(tdml_column=_get_tdml_col(col).array_sort(elements_order='ASC' if asc else 'DESC',
                                                                                    nulls_order='FIRST' if asc else 'LAST'),
                                          alias_name=_generate_array_func_col_name('sort_array', col, asc))

sequence = lambda start, stop, step=1: Column(tdml_column = tdml_sequence(_get_tdml_col(start), _get_tdml_col(stop),
                                                                          step if isinstance(step, int) else _get_tdml_col(step)),
                                             alias_name=_generate_array_func_col_name('sequence', start, stop, step))

array_repeat = lambda col, count: Column(tdml_column=_get_tdml_col(col).array_repeat(count if isinstance(count, int) else _get_tdml_col(count)),
                                         alias_name=_generate_array_func_col_name('array_repeat', col, count))

transform = not_implemented
exists = not_implemented
forall = not_implemented
filter = not_implemented
aggregate = not_implemented
zip_with = not_implemented
transform_keys = not_implemented
transform_values = not_implemented
map_filter = not_implemented
map_from_arrays = not_implemented
map_zip_with = not_implemented
inline = not_implemented
inline_outer = not_implemented
get_json_object = not_implemented
json_tuple = not_implemented
from_json = not_implemented
schema_of_json = not_implemented
to_json = not_implemented
json_array_length = not_implemented
json_object_keys = not_implemented
struct = not_implemented
flatten = not_implemented
map_contains_key = not_implemented
map_keys = not_implemented
map_values = not_implemented
map_entries = not_implemented
map_from_entries = not_implemented
arrays_zip = not_implemented
map_concat = not_implemented
from_csv = not_implemented
schema_of_csv = not_implemented
str_to_map = not_implemented
to_csv = not_implemented
years = lambda col: Column(tdml_column=_SQLColumnExpression(func.extract('YEAR', _get_tdml_col(col).expression)))
months = lambda col: Column(tdml_column=_SQLColumnExpression(func.extract('MONTH', _get_tdml_col(col).expression)))
days = lambda col: Column(tdml_column=_SQLColumnExpression(func.extract('DAY', _get_tdml_col(col).expression)))
hours = lambda col: Column(tdml_column=_SQLColumnExpression(func.extract('HOUR', _get_tdml_col(col).expression)))
bucket = not_implemented



def asc(col):

    # col can be a string or Column Object.
    if isinstance(col, str):
        return Column(tdml_column=_SQLColumnExpression(col).asc().nulls_first())
    return Column(tdml_column=col._tdml_column.asc().nulls_first())

asc_nulls_first = lambda col: asc(col)

def asc_nulls_last(col):
    # col can be a string or Column Object.
    if isinstance(col, str):
        return Column(tdml_column=_SQLColumnExpression(col).asc().nulls_last())
    return Column(tdml_column=col._tdml_column.asc().nulls_last())


def desc(col):

    # col can be a string or Column Object.
    if isinstance(col, str):
        return Column(tdml_column=_SQLColumnExpression(col).desc().nulls_last())
    return Column(tdml_column=col._tdml_column.desc().nulls_last())

def desc_nulls_first(col):

    # col can be a string or Column Object.
    if isinstance(col, str):
        return Column(tdml_column=_SQLColumnExpression(col).desc().nulls_first())
    return Column(tdml_column=col._tdml_column.desc().nulls_first())

desc_nulls_last = lambda col: desc(col)

def _get_agg_expr(col, func_name, **params):
    """Helper function to get aggregate function expression. """
    # Params can have teradatamlspk Column. Convert it to teradataml Column.
    params = {pname: pcol._tdml_column if isinstance(pcol, Column) else pcol for pname,pcol in params.items()}
    tdml_column = getattr(_SQLColumnExpression(col), func_name)(**params) if isinstance(col, str)\
        else getattr(col._tdml_column, func_name)(**params)
    expr_ = _SQLColumnExpression(col) if isinstance(col, str) else col._tdml_column
    agg_func_params = {"name": func_name, **params}
    return {"tdml_column": tdml_column, "expr_": expr_, "agg_func_params": agg_func_params}

avg = lambda col: Column(**_get_agg_expr(col, "mean", distinct=False))
any_value = lambda col, ignoreNulls=None: Column(**_get_agg_expr(col, "first_value"))
row_number = lambda: Column(**_get_agg_expr('col_', "row_number"))
count = lambda col: Column(**_get_agg_expr(col, "count", distinct=False))
rank = lambda: Column(**_get_agg_expr('col_', "rank"))
cume_dist = lambda: Column(**_get_agg_expr('col_', "cume_dist"))
dense_rank = lambda: Column(**_get_agg_expr('col_', "dense_rank"))
percent_rank = lambda: Column(**_get_agg_expr('col_', "percent_rank"))
max = lambda col: Column(**_get_agg_expr(col, "max", distinct=False))
mean = lambda col: Column(**_get_agg_expr(col, "mean", distinct=False))
min = lambda col: Column(**_get_agg_expr(col, "min", distinct=False))
sum = lambda col: Column(**_get_agg_expr(col, "sum", distinct=False))
std = lambda col: Column(**_get_agg_expr(col, "std", distinct=False, population=False))
stddev = std
stddev_samp = std
stddev_pop = lambda col: Column(**_get_agg_expr(col, "std", distinct=False, population=True))
var_pop = lambda col: Column(**_get_agg_expr(col, "var", distinct=False, population=True))
var_samp = lambda col: Column(**_get_agg_expr(col, "var", distinct=False, population=False))
variance = var_samp
lag = lambda col, offset=1, default=None: Column(**_get_agg_expr(col, "lag", offset_value=offset, default_expression=default))
lead = lambda col, offset=1, default=None: Column(**_get_agg_expr(col, "lead", offset_value=offset, default_expression=default))

def count_distinct(*cols):
    """
    DESCRIPTION:
        Returns the number of distinct values in the specified column(s).

    PARAMETERS:
        *cols:
            Required Argument.
            One or more columns to count distinct values.
            Type: List of strings or Column objects
    """
    if len(cols) == 1:
        return Column(**_get_agg_expr(cols[0], "count", distinct=True))
    else:
        # Convert each column to string to ensure consistent concatenation.
        concat_exprs = []
        for col in cols:
            concat_exprs.append(_SQLColumnExpression(func.to_char(_get_tdml_col(col).expression)))

        # SQL concat function for all columns.
        concat_col = _SQLColumnExpression(func.concat(*[expr.expression for expr in concat_exprs]))

        # Wrap the concatenated column in a Column object.
        wrapped_col = Column(tdml_column=concat_col)

        return Column(**_get_agg_expr(wrapped_col, "count", distinct=True))

countDistinct = count_distinct
corr = lambda col1, col2: Column(**_get_agg_expr(col1, "corr", expression=col2))
covar_pop = lambda col1, col2: Column(**_get_agg_expr(col1, "covar_pop", expression=col2))
covar_samp = lambda col1, col2: Column(**_get_agg_expr(col1, "covar_samp", expression=col2))
first = lambda col, ignorenulls=False: Column(**_get_agg_expr(col, "first_value"))
first_value = lambda col, ignorenulls=False: Column(**_get_agg_expr(col, "first_value"))
last = lambda col, ignorenulls=False: Column(**_get_agg_expr(col, "last_value"))
last_value = lambda col, ignorenulls=False: Column(**_get_agg_expr(col, "last_value"))
regr_avgx = lambda y, x: Column(**_get_agg_expr(y, "regr_avgx", expression=x))
regr_avgy = lambda y, x: Column(**_get_agg_expr(y, "regr_avgy", expression=x))
regr_count = lambda y, x: Column(**_get_agg_expr(y, "regr_count", expression=x))
regr_intercept = lambda y, x: Column(**_get_agg_expr(y, "regr_intercept", expression=x))
regr_r2 = lambda y, x: Column(**_get_agg_expr(y, "regr_r2", expression=x))
regr_slope = lambda y, x: Column(**_get_agg_expr(y, "regr_slope", expression=x))
regr_sxx = lambda y, x: Column(**_get_agg_expr(y, "regr_sxx", expression=x))
regr_sxy = lambda y, x: Column(**_get_agg_expr(y, "regr_sxy", expression=x))
regr_syy = lambda y, x: Column(**_get_agg_expr(y, "regr_syy", expression=x))
sum_distinct = lambda col: Column(**_get_agg_expr(col, "sum", distinct=True))
sumDistinct = sum_distinct

ascii = lambda col: Column(tdml_column=_get_tdml_col(col).substr(1,1).ascii())
base64 = lambda col: Column(tdml_column=_get_tdml_col(col).to_byte('ASCII').from_byte('BASE64M'))
btrim = lambda str, trim=lit(" "): Column(tdml_column=_get_tdml_col(str).trim(_get_tdml_col(trim)))
char = lambda col: Column(tdml_column=_get_tdml_col(col).char())
character_length = lambda str: Column(tdml_column=_get_tdml_col(str).character_length())
char_length = character_length
concat_ws = lambda sep, *cols: Column(tdml_column=_get_tdml_col(cols[0]).concat(sep, *(_get_tdml_col(col) for col in cols[1:])))
contains = lambda left, right: Column(tdml_column=_get_tdml_col(left).str.contains(_get_tdml_col(right)))
decode = not_implemented
def elt(*inputs):
    """
    DESCRIPTION:
        Returns the n-th input, e.g., returns input2 when n is 2. The function returns NULL if the index exceeds the
        length of the array.

    PARAMETERS:
        *inputs:
            Required Argument.
            Input columns or strings.
            Type: List of strings
    """
    # Converting inputs to Column Expression accepted by teradataml
    inputs = [_get_tdml_col(col) for col in inputs]
    # generate case here based on input
    # If input length is 2
    # Generate case example case([(inputs[0]==1, inputs[1])])
    # If inputs length is 3
    #Generate case example case([(inputs[0]==1, inputs[1]), (inputs[0]==2, inputs[2])])
    _expression = case_when([(inputs[0]==i, inputs[i]) for i in range(1, len(inputs))])
    return Column(tdml_column=_expression)
encode = unknown
endswith = lambda str, suffix: Column(tdml_column=_SQLColumnExpression(case((_get_tdml_col(str).endswith(_get_tdml_col(suffix)).expression, 1), else_=0)))
find_in_set = unknown
# Now it supports length of float upto 40
format_number = lambda col, d: Column(tdml_column=_get_tdml_col(col).format("z(40)" if d ==0 else f"z(40).z({d})"))

def _string_spacing(val, col_expr):
    """
    DESCRIPTION:
        Returns  +, -, integervalue, 0 present in string or not.

    PARAMETERS:
        val:
            Required Argument.
            Species a string in format starts with '%'.
            Type: str
        col_expr:
            Required Argument.
            Species a column expression.
            Type: _SQLColumnExpression
    """
    # Initilaize all variables with False and spacing with 0
    plus, minus, zero, spacing = False, False, False, 0
    # if '+' and '-' are present in 'val' set variables to True
    if '+' in val:
        plus = True
    if '-' in val:
        minus = True

    # Let suppose string is like this '%+010.2f' then to find 0 present in 'val' or not
    # If we first encounter digit and it is 0 then we will set 'zero' to True.
    for x in val:
        if x.isdigit() and x!='0':
            break
        if '0' == x:
            zero=True
    # Find spacing if it is present or not in this example '%+010.2f' spacing is 10.
    spacing = re.findall(r"(\d+)", val) if re.search(r"(\d+)", val) else []
    if '.' in val and len(spacing) == 2:
        spacing = int(spacing[0])
    elif '.' not in val and len(spacing) == 1:
        spacing = int(spacing[0])
    else:
        spacing = 0
    # When minus and spacing is present provide padding from last
    # Example: "%-10d" for 100 = "100       "
    if minus and spacing:
        return [col_expr.rpad(spacing, ' ').expression]
    # When plus, zero and spacing is present provide padding of 0 from start with sign
    # Example: "%+010d" for 100 = "+0000000100"
    elif plus and zero and spacing:
        return [(_SQLColumnExpression(literal('+'))+ col_expr.lpad(spacing-1, '0')).expression]
    # When plus, spacing is present provide padding from start with sign
    # Example: "%+10d" for 100 = "       +100"
    elif plus and spacing:
        return [(_SQLColumnExpression(literal('+'))+col_expr).lpad(spacing-1, ' ').expression]
    # When zero, spacing is present provide padding of 0 from start
    # Example: "%010d" for 100 = "0000000100"
    elif zero and spacing:
        return [col_expr.lpad(spacing, '0').expression]
    # When spacing is present provide padding from start
    # Example: "%10d" for 100 = "       100"
    elif spacing:
        return [col_expr.lpad(spacing, ' ').expression]
    # When plus is present provide sign
    # Example: "%+d" for 100 = "+100"
    elif plus:
        return [(_SQLColumnExpression(literal('+'))+col_expr).expression]

def format_string(format, *cols):
    """
    DESCRIPTION:
        Formats the arguments in printf-style and returns the result as a string column.

    PARAMETERS:
        format:
            Required Argument.
            Specifies string that can contain embedded format tags and used as result column’s value.
            Type: str

        *cols:
            Required Argument.
            Specifies column names or Columns to be used in formatting.
            Type: Column or str

    """
    # Find a pattern in format which should start with % and ends with either [d,i,o,u,x,X,e,E,f,F,g,G,c,b,s,a,r]
    pattern = "(\%.*?[diouxXeEfFgGcbsar])"
    # Split the format bases on pattern
    # Example if format="hello %s, age=%.4f" then resultant string = ['hello ', '%s', ', age=', '%.4f', '']
    resultant_string = re.split(pattern, format)

    idx = 0
    for i, strs in enumerate(resultant_string):

        # Make operations only if 'strs' starts with % else use as it is in concat function.
        if strs.startswith('%'):

            # If 'strs' ends with 'X' Change to hexadecimal expression Example: 10='A'
            if strs.endswith('X'):
                resultant_string[i] = _get_tdml_col(cols[idx]).to_byte('base10').from_byte('base16')
                if '#' in strs:
                    resultant_string[i] = _SQLColumnExpression(literal('0X')) + resultant_string[i]
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with 'x' Change to hexadecimal expression with lower case Example: 10: 'a'
            elif strs.endswith('x'):
                resultant_string[i] = _get_tdml_col(cols[idx]).to_byte('base10').from_byte('base16').lower()
                if '#' in strs:
                    resultant_string[i] = _SQLColumnExpression(literal('0x')) + resultant_string[i]
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with 'o' Change to octal values
            elif strs.endswith('o'):
                resultant_string[i] = _get_tdml_col(cols[idx]).to_byte('base10').from_byte('base8')
                if '#' in strs:
                    resultant_string[i] = _SQLColumnExpression(literal('0o')) + resultant_string[i]
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with either d, i, u consider it as integer value
            elif strs.endswith('d') or strs.endswith('i') or strs.endswith('u'):
                resultant_string[i] = _get_tdml_col(cols[idx]).cast(BIGINT).to_char().ltrim(' ')
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with either e convert to exponential format in with 'e' in lower case.
            elif strs.endswith('e'):
                round_off_value = int(re.findall('\.(\d+)', strs)[0]) if re.search('\.(\d+)', strs) else 6
                resultant_string[i] = _get_tdml_col(cols[idx]).to_char('9.{}EEEE'.format('9' * round_off_value)).lower().ltrim(
                    ' ') \
                    if round_off_value != 0 else _get_tdml_col(cols[idx]).to_char('9EEEE').lower().ltrim(' ')
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with either E convert to exponential format with 'e' in upper case.
            elif strs.endswith('E'):
                round_off_value = int(re.findall('\.(\d+)', strs)[0]) if re.search('\.(\d+)', strs) else 6
                resultant_string[i] = _get_tdml_col(cols[idx]).to_char('9.{}EEEE'.format('9'*round_off_value)).ltrim(' ') \
                    if round_off_value != 0 else _get_tdml_col(cols[idx]).to_char('9EEEE').ltrim(' ')
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # If 'strs' ends with either f, F, g, G convert float to string.
            elif strs.endswith('f') or strs.endswith('F') or strs.endswith('g') or strs.endswith('G'):
                round_off_value=int(re.findall('\.(\d+)', strs)[0]) if re.search('\.(\d+)', strs) else 6
                character_format = '9({}).9({})'.format(40, round_off_value) if round_off_value != 0 else "9({})".format(40)
                resultant_string[i] = _get_tdml_col(cols[idx]).round(round_off_value).format(character_format).ltrim('0')
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # Single character to ASCII value
            elif strs.endswith("c"):
                resultant_string[i] = _get_tdml_col(cols[idx]).char()
                if isinstance(_get_tdml_col(cols[idx])._type, (CHAR, VARCHAR)):
                    resultant_string[i] = _get_tdml_col(cols[idx])
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression

            # Append string column
            elif strs.endswith("s") or strs.endswith("r") or strs.endswith("a") or strs.endswith("b"):
                resultant_string[i] = _get_tdml_col(cols[idx])
                _new_expr = _string_spacing(strs, resultant_string[i])
                if _new_expr:
                    resultant_string[i] = _new_expr[0]
                else:
                    resultant_string[i] = resultant_string[i].expression
            idx+=1
    return Column(tdml_column=_SQLColumnExpression(func.concat(*resultant_string)))
ilike = lambda str, pattern, escapeChar=None: Column(tdml_column=_SQLColumnExpression(_get_tdml_col(str).ilike(_get_tdml_col(pattern), escapeChar._tdml_column.expression.value if escapeChar else None).expression))
initcap = lambda col: Column(tdml_column=_get_tdml_col(col).initcap())
instr = lambda str, substr: Column(tdml_column=_get_tdml_col(str).instr(substr, 1, 1))
lcase = lambda str: Column(tdml_column=_get_tdml_col(str).lower())
length = lambda col: Column(tdml_column=_get_tdml_col(col).length())
like = lambda str, pattern, escapeChar=None: Column(tdml_column=_SQLColumnExpression(_get_tdml_col(str).like(_get_tdml_col(pattern), escapeChar._tdml_column.expression.value if escapeChar else None).expression))
lower = lcase
left = lambda str, len: Column(tdml_column=_get_tdml_col(str).left(_get_tdml_col(len)))
levenshtein = lambda left, right, threshold=None: Column(tdml_column=_get_tdml_col(left).edit_distance(_get_tdml_col(right)))
locate = lambda substr, str, pos = 1: Column(tdml_column=_get_tdml_col(str).instr(substr, pos))
lpad = lambda col, len, pad: Column(tdml_column=_get_tdml_col(col).lpad(len, pad))
ltrim = lambda col: Column(tdml_column=_get_tdml_col(col).ltrim())
mask = unknown
octet_length = unknown
parse_url = lambda url, pathToExtract, key=None: Column(tdml_column=_get_tdml_col(url).parse_url(_get_tdml_col(pathToExtract), _get_tdml_col(key) if isinstance(key, Column) else key if key else None))
position = lambda substr, str, start = 1: Column(tdml_column=_get_tdml_col(str).instr(_get_tdml_col(substr), _get_tdml_col(start)))
printf = unknown
rlike = lambda str, pattern: Column(tdml_column=_SQLColumnExpression(case((_get_tdml_col(str).rlike(_get_tdml_col(pattern) if isinstance(pattern, Column) else pattern).expression, 1), else_=0)))
regexp = unknown
regexp_like = unknown
regexp_count = unknown
regexp_extract = unknown
regexp_extract_all = unknown
regexp_replace = lambda string, pattern, replacement: Column(tdml_column=_get_tdml_col(string).regexp_replace(pattern, replacement))
regexp_substr = lambda str, regexp: Column(tdml_column=_get_tdml_col(str).regexp_substr(regexp))
regexp_instr = lambda str, regexp, idx = 1: Column(tdml_column=_get_tdml_col(str).regexp_instr(regexp, idx))
replace = lambda src, search, replace='': Column(tdml_column=_get_tdml_col(src).oreplace(_get_tdml_col(search), _get_tdml_col(replace)))
right = lambda str, len: Column(tdml_column=_get_tdml_col(str).right(_get_tdml_col(len)))
ucase = lambda str: Column(tdml_column=_get_tdml_col(str).upper())
unbase64 = unknown
rpad = lambda col, len, pad: Column(tdml_column=_get_tdml_col(col).rpad(len, pad))
repeat = lambda col, n: Column(tdml_column=_get_tdml_col(col).concat("", *[_get_tdml_col(col) for i in range(n-1)]))
rtrim = lambda col: Column(tdml_column=_get_tdml_col(col).rtrim())
soundex = lambda col: Column(tdml_column=_get_tdml_col(col).soundex())
split = not_implemented
split_part = not_implemented
startswith = lambda str, prefix: Column(tdml_column=_SQLColumnExpression(case((_get_tdml_col(str).startswith(_get_tdml_col(prefix)).expression, 1), else_=0)))
substr = lambda str, pos, len=1:Column(tdml_column=_get_tdml_col(str).substr(_get_tdml_col(pos),  _get_tdml_col(len)))
substring = substr
substring_index = lambda str, delim, count:Column(tdml_column=_get_tdml_col(str).substring_index(delim, count))
overlay = unknown
sentences = not_implemented
to_binary = unknown
to_char = lambda col, format: Column(tdml_column=_get_tdml_col(col).to_char(_get_tdml_col(format)))
to_number = lambda col, format: Column(tdml_column=_get_tdml_col(col).to_number(_get_tdml_col(format)))
to_varchar = lambda col, format: Column(tdml_column=_get_tdml_col(col).to_char(_get_tdml_col(format)))
translate = lambda srcCol, matching, replace: Column(tdml_column=_get_tdml_col(srcCol).translate(matching, replace))
trim = lambda col: Column(tdml_column=_get_tdml_col(col).trim())
upper = lambda col: Column(tdml_column=_get_tdml_col(col).upper())
url_decode = unknown
url_encode = unknown
bit_count = unknown
bit_get = unknown
getbit = unknown
call_function = unknown
pandas_udf = unknown
udtf = unknown
unwrap_udt = unknown
aes_decrypt = unknown
aes_encrypt = unknown
bitmap_bit_position = unknown
bitmap_bucket_number = unknown
bitmap_construct_agg = unknown
bitmap_count = unknown
bitmap_or_agg = unknown
current_catalog = lambda : Column(tdml_column=_SQLColumnExpression(literal("teradata_catalog")))
current_database = lambda : Column(tdml_column=_SQLColumnExpression(literal_column("USER")))
current_schema = lambda : Column(tdml_column=_SQLColumnExpression(literal_column("DATABASE")))
current_user = lambda : Column(tdml_column=_SQLColumnExpression(literal_column("USER")))
input_file_block_length = not_implemented
input_file_block_start = not_implemented
md5 = unknown
sha = unknown
sha1 = unknown
sha2 = unknown
crc32 = unknown
hash = unknown
xxhash64 = unknown
assert_true = unknown
raise_error = unknown
reflect = unknown
hll_sketch_estimate = unknown
hll_union = unknown
java_method = unknown
stack = unknown
try_aes_decrypt = unknown
typeof = unknown
user = lambda : Column(tdml_column=_SQLColumnExpression(literal_column("USER")))
version = lambda : Column(tdml_column=_SQLColumnExpression(literal(configure.database_version)))
equal_null = lambda col1, col2: Column(tdml_column=case_when([((_get_tdml_col(col1).isnull()==True) & (_get_tdml_col(col2).isnull()==True), 1), (_get_tdml_col(col1) == _get_tdml_col(col2), 1)], else_=0))
ifnull = lambda col1, col2: nanvl(col1, col2)
isnotnull = lambda col: Column(tdml_column=_get_tdml_col(col).notnull())
nullif = lambda col1, col2: Column(tdml_column=case((_get_tdml_col(col1).expression == _get_tdml_col(col2).expression, None), else_=_get_tdml_col(col1).expression))
nvl = lambda col1, col2: Column(tdml_column=_SQLColumnExpression(func.nvl(_get_tdml_col(col1).expression, _get_tdml_col(col2).expression)))
nvl2 = lambda col1, col2, col3: Column(tdml_column=_SQLColumnExpression(
    func.nvl2(_get_tdml_col(col1).expression, _get_tdml_col(col2).expression, _get_tdml_col(col3).expression)))
xpath = not_implemented
xpath_boolean = not_implemented
xpath_double = not_implemented
xpath_float = not_implemented
xpath_int = not_implemented
xpath_long = not_implemented
xpath_number = not_implemented
xpath_short = not_implemented
xpath_string = not_implemented

def time_difference(col1, col2, seconds = 1):
    """Returns the difference between two timestamps in seconds. """
    col1 = col1 if isinstance(col1, str) else col1._tdml_column.compile()
    col2 = col2 if isinstance(col2, str) else col2._tdml_column.compile()
    s = """
    (CAST((CAST({0} AS DATE)-CAST({1} AS DATE)) AS FLOAT) * 86400 * {2}) +
    ((EXTRACT(HOUR FROM {0}) - EXTRACT(HOUR FROM {1})) * 3600 * {2}) +
    ((EXTRACT(MINUTE FROM {0}) - EXTRACT(MINUTE FROM {1})) * 60 * {2}) +
    ((EXTRACT(SECOND FROM {0}) - EXTRACT(SECOND FROM {1})) * {2})
    """.format(col1, col2, seconds)
    return Column(tdml_column=_SQLColumnExpression(literal_column(s, type_=FLOAT())))

def udf(f=None, returnType=StringType(), **kwargs):
    """ Creates a user defined function (UDF)."""
    # Notation: @udf(returnType=IntegerType())
    delimiter = kwargs.pop('delimiter', ',')
    quotechar = kwargs.pop('quotechar', None)
    envName = kwargs.pop('env_name', None)
    if f is None:
        def wrapper(f):
            def func_(*args):
                return Column(udf=f, udf_type=returnType, udf_args=args, env_name=envName, delimiter=delimiter, quotechar=quotechar)
            return func_
        return wrapper
    # Notation: @udf
    else:
        def func_(*args):
            return Column(udf=f, udf_type=returnType, udf_args=args, env_name=envName, delimiter=delimiter, quotechar=quotechar)
    return func_

def call_udf(name, *cols, **kwargs):
    """ Call a registered user defined function (UDF)."""
    from teradatamlspk.sql.utils import _get_spark_type
    delimiter = kwargs.pop('delimiter', ',')
    quotechar = kwargs.pop('quotechar', None)
    # Call teradataml call_udf function to get Column object.
    tdml_col = tdml_call_udf(name, cols, delimiter = delimiter, quotechar = quotechar)
    return Column(expression=None, udf_args = tdml_col._udf_args , udf_script = tdml_col._udf_script,\
                  udf_type =_get_spark_type(tdml_col.type), delimiter = delimiter,\
                  quotechar = quotechar, udf_name = name)

def _format_date_string(pyspark_str):
    """
    DESCRIPTION:
        Internal function converts pyspark format date string to teradataml string.
        Example: 'yyyy-MM-dd HH-mm-ss' to 'YYYY-MM-DD HH24:MI:SS'

    PARAMETERS:
        pyspark_str:
            Required Argument.
            Specifies string in pyspark format date.
            Type: str
    """

    # Mapper for pyspark format values to teradataml format values.
    pyspk_to_tdspk_dateformat_map = [
        ('y', 'Y'),
        ('MMMM', 'MONTH') , ('MMM', 'MON'), ('MM', 'MM'), ('M', 'MM'),
        ('LLLL', 'MONTH'), ('LLL', 'MON'), ('LL', 'MM'), ('L', 'MM'),
        ('DDD', 'DDD'), ('DD', 'DDD'), ('D', 'DDD'),
        ('dd', 'DD'), ('d', 'DD'),
        ('EEEE', 'DAY'), ('EEE', 'DY'), ('EE', 'DY'), ('E', 'DY'),
        ('a', 'PM'),
        ('HH', 'HH24'), ('H', 'HH24'),
        ('hh', 'HH12'), ('h', 'HH12'),
        ('KK', 'HH12'), ('K', 'HH12'),
        ('kk', 'HH24'), ('k', 'HH24'),
        ('mm', 'MI'), ('m', 'MI'),
        ('SSSSSS', 'FF6'), ('SSSSS', 'FF5'), ('SSSS', 'FF4'), ('SSS', 'FF3'), ('SS', 'FF2'), ('S', 'FF1'),
        ('ss', 'SS'), ('s', 'SS'),
        ('xxxxx', 'TZH:TZM'), ('xxx', 'TZH:TZM'),
        ('XXXXX', 'TZH:TZM'), ('XXX', 'TZH:TZM'),
        ('ZZZZZ', 'TZH:TZM'),
        ('q', 'Q')
    ]

    # Create a new teraspark string using mapper.
    teraspark_str = pyspark_str
    # Edge cases for pyspark and teradataml values are same.
    # Convert those values to first '*'
    if 'H' in teraspark_str:
        teraspark_str = teraspark_str.replace('H', '*')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'HH24')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'HH24')

    if 'M' in teraspark_str:
        teraspark_str = teraspark_str.replace('M', '*')
        if '****' in teraspark_str:
            teraspark_str = teraspark_str.replace('****', 'MONTH')
        if '***' in teraspark_str:
            teraspark_str = teraspark_str.replace('***', 'MON')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'MM')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'MM')

    if 'D' in teraspark_str:
        teraspark_str = teraspark_str.replace('D', '*')
        if '***' in teraspark_str:
            teraspark_str = teraspark_str.replace('***', 'DDD')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'DDD')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'DDD')

    for pyspk_val, tdspk_val in pyspk_to_tdspk_dateformat_map:
        if pyspk_val in ['MMMM', 'MMM', 'MM', 'M', 'DDD', 'DD', 'D', 'HH', 'H']:
            continue
        teraspark_str = teraspark_str.replace(pyspk_val, tdspk_val)

    return teraspark_str

def _format_date_string_cast(pyspark_str):
    """
    DESCRIPTION:
        Internal function converts pyspark format date string to teradataml string for cast function.
        Example: 'yyyy-MM-dd HH-mm-ss' to 'YYYY-MM-DD HH24:MI:SS'

    PARAMETERS:
        pyspark_str:
            Required Argument.
            Specifies string in pyspark format date.
            Type: str
    """

    # Mapper for pyspark format values to teradataml format values.
    pyspk_to_tdspk_dateformat_map = [
        ('y', 'Y'),
        ('MMMM', 'MONTH') , ('MMM', 'MON'), ('MM', 'MM'), ('M', 'MM'),
        ('LLLL', 'MONTH'), ('LLL', 'MON'), ('LL', 'MM'), ('L', 'MM'),
        ('DDD', 'DDD'), ('DD', 'DDD'), ('D', 'DDD'),
        ('dd', 'DD'), ('d', 'DD'),
        ('EEEE', 'DAY'), ('EEE', 'DY'), ('EE', 'DY'), ('E', 'DY'),
        ('a', 'PM'),
        ('HH', 'HH'), ('H', 'HH'),
        ('hh', 'HH'), ('h', 'HH'),
        ('KK', 'HH'), ('K', 'HH'),
        ('kk', 'HH'), ('k', 'HH'),
        ('mm', 'MI'), ('m', 'MI'),
        ('SSSSSS', 'S(F)'), ('SSSSS', 'S(F)'), ('SSSS', 'S(F)'), ('SSS', 'S(F)'), ('SS', 'S(F)'), ('S', 'S(F)'),
        ('ss', 'SS'), ('s', 'SS'),
        ('xxxxx', 'Z'), ('xxx', 'Z'),
        ('XXXXX', 'Z'), ('XXX', 'Z'),
        ('ZZZZZ', 'Z'),
        ('q', 'Q')
    ]

    # Create a new teraspark string using mapper.
    teraspark_str = pyspark_str
    # Edge cases for pyspark and teradataml values are same.
    # Convert those values to first '*'

    if 'H' in teraspark_str:
        teraspark_str = teraspark_str.replace('H', '*')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'HH')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'HH')

    if 'M' in teraspark_str:
        teraspark_str = teraspark_str.replace('M', '*')
        if '****' in teraspark_str:
            teraspark_str = teraspark_str.replace('****', 'MONTH')
        if '***' in teraspark_str:
            teraspark_str = teraspark_str.replace('***', 'MON')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'MM')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'MM')

    if 'D' in teraspark_str:
        teraspark_str = teraspark_str.replace('D', '*')
        if '***' in teraspark_str:
            teraspark_str = teraspark_str.replace('***', 'DDD')
        if '**' in teraspark_str:
            teraspark_str = teraspark_str.replace('**', 'DDD')
        if '*' in teraspark_str:
            teraspark_str = teraspark_str.replace('*', 'DDD')

    if 'S' in teraspark_str:
        teraspark_str = teraspark_str.replace('S', '*')
        values = ['*' * i for i in range(6, 0, -1)]
        for value in values:
            if value in teraspark_str:
                teraspark_str = teraspark_str.replace(value, 'S(F)')

    for pyspk_val, tdspk_val in pyspk_to_tdspk_dateformat_map:
        if pyspk_val in ['MMMM', 'MMM', 'MM', 'M', 'DDD', 'DD', 'D', 'HH', 'H', 'SSSSSS', 'SSSSS', 'SSSS', 'SSS', 'SS', 'S']:
            continue
        elif pyspk_val in ['xxxxx', 'xxx', 'XXXXX', 'XXX', 'ZZZZZ']:
            teraspark_str = teraspark_str.replace(pyspk_val, 'Z')
        else:
            teraspark_str = teraspark_str.replace(pyspk_val, tdspk_val)
    teraspark_str = teraspark_str.replace(' ', 'B')

    return teraspark_str

def shiftleft(col, numBits):
    """
    DESCRIPTION:
        Function shifts the bits of the column values to the left by the specified number of bits.

    PARAMETERS:
        col:
            Required Argument.
            Specifies name of the column or ColumnExpression.
            Types: Column or str

        numBits:
            Required Argument.
            Specifies number of bits to shift.
            Types: int

    RETURNS:
        Column

    EXAMPLES:
        >>> df = spark.createDataFrame("table_name")
        >>> from teradatamlspk.sql.functions import shiftleft
        >>> df.withColumn("new_column", shiftleft(df.column, 50)).show()
    """
    # For INTEGER if numBits is greater than 32 we use modulo 32 to get bit in range 0-31.
    # For BIGINT if numBits is greater than 64 we use modulo 64 to get bit in range 0-63.
    col = _get_tdml_col(col)
    if isinstance(col._type, (BIGINT, INTEGER)):
        _value = 64 if col._type.__class__.__name__ == "BIGINT" else 32
        return Column(tdml_column=col.shiftleft(numBits%_value))
    # If Column is either float, decimal or NUMBER type pyspark converts column to Integer type.
    return Column(tdml_column=col.cast(INTEGER).shiftleft(numBits % 32))

def shiftright(col, numBits):
    """
    DESCRIPTION:
        Function shifts the bits of the column values to the right by the specified number of bits.

    PARAMETERS:
        col:
            Required Argument.
            Specifies name of the column or ColumnExpression.
            Types: Column or str

        numBits:
            Required Argument.
            Specifies number of bits to shift.
            Types: int

    RETURNS:
        Column

    EXAMPLES:
        >>> df = spark.createDataFrame("table_name")
        >>> from teradatamlspk.sql.functions import shiftright
        >>> df.withColumn("new_column", shiftright(df.column, 50)).show()
    """
    # For INTEGER if numBits is greater than 32 we use modulo 32 to get bit in range 0-31.
    # For BIGINT if numBits is greater than 64 we use modulo 64 to get bit in range 0-63.
    col = _get_tdml_col(col)
    if isinstance(col._type, (BIGINT, INTEGER)):
        _value = 64 if col._type.__class__.__name__ == "BIGINT" else 32
        return Column(tdml_column=col.cast(BIGINT).shiftright(numBits%_value))
    # If Column is either float, decimal or NUMBER type pyspark converts column to Integer type.
    return Column(tdml_column=col.cast(BIGINT).shiftright(numBits % 32))
