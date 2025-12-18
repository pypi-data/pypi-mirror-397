## Teradata Python package for running Spark workloads on Vantage.

teradatamlspk is a Python module to run PySpark workloads on Vantage with minimal changes to the Python script.  

For community support, please visit the [Teradata Community](https://support.teradata.com/community?id=community_forum&sys_id=14fe131e1bf7f304682ca8233a4bcb1d).

For Teradata customer support, please visit [Teradata Support](https://support.teradata.com/csm).

Copyright 2024, Teradata. All Rights Reserved.

### Table of Contents
* [Release Notes](#release-notes)
* [Installation and Requirements](#installation-and-requirements)
* [Using the Teradata Python Package](#using-the-teradata-Python-package)
* [Documentation](#documentation)
* [License](#license)

## Release Notes:

#### teradatamlspk 20.00.00.04
* ##### New Features/Functionality
  * ###### Array Functionality - teradatamlspk now supports arrays.
    * ###### teradatamlspk global functions
      * `array()` - Creates an array column from one or more columns.
      * `array_contains()` - Returns True if the array contains the specified value.
      * `array_append()` - Appends an element to the end of an array column.
      * `array_prepend()` - Prepends an element to the beginning of an array column.
      * `array_size()` - Returns the size of the array column.
      * `size()` - Returns the size of the array column.
      * `cardinality()` - Returns the size of the array column.
      * `get()` - Returns the element at the specified position in the array (0-based index).
      * `element_at()` - Returns the element at the specified position in the array (1-based index).
      * `array_min()` - Returns the minimum value in the array column.
      * `array_max()` - Returns the maximum value in the array column.
      * `try_element_at()` - Returns the element at the specified position in the array (1-based index).
      * `array_agg()` - Aggregate the rows of a column into an array.
      * `explode()` - Explodes the array column into multiple rows.
      * `explode_outer()` - Explodes the array column into multiple rows.
      * `posexplode()` - Explodes the array column into multiple rows with position.
      * `posexplode_outer()` - Explodes the array column into multiple rows with position.
      * `array_sort()` - Sorts the elements of an array in ascending order.
      * `sort_array()` - Sorts the elements of an array in ascending or descending order.
      * `array_join()` - Joins the elements of an array into a single string with a specified delimiter.
      * `arrays_overlap()` - Checks if two arrays have any elements in common.
      * `array_insert()` - Inserts an element at a specific index in an array.
      * `array_remove()` - Removes all occurrences of a specified element from an array.
      * `array_distinct()` - Removes duplicate elements from an array.
      * `array_intersect()` - Returns the intersection of two arrays.
      * `array_union()` - Returns the union of two arrays with distinct elements.
      * `array_except()` - Returns the elements of the first array that are not in the second array.
      * `array_compact()` - Removes null elements from an array.
      * `array_repeat()` - Creates an array by repeating a value for a specified number of times.
      * `array_position()` - Gets the position of an element in the array.
      * `slice()` - Gets a subset of an array based on specified start index and length.
      * `shuffle()` - Randomly shuffles the elements of an array.
      * `sequence()` - Generates an array of values in a specified range with a given step.

    * ###### teradatamlspk types
      * `ArrayType()` - Array data type is now supported.

  * ###### teradatamlspk global functions
      * `make_interval()` - Makes interval from years and months or weeks, days, hours, mins and secs.

* ##### Updates
  * `concat()` now supports array columns as input.
  * `reverse()` now supports array column as input.

#### teradatamlspk 20.00.00.03
* ##### New Features/Functionality
  * ###### pyspark2teradataml
    * This release has enhanced the utility `pyspark2teradataml` to convert PySpark scripts or notebooks to teradatamlspk scripts or notebooks.
      * The utility now generates the HTML report with a split screen interface with two panes:
        * The left pane:
          * Displays both the original PySpark script and the converted teradatamlspk script. One can switch between the two using a dropdown menu.
          * Color-coded bell icons are placed next to lines in the original PySpark script that require attention. Every colored bell icon signifies a different alert. Clicking a bell icon displays the details for the corresponding line's API in the right pane.
        * The right pane:
          * Displays important notes and instructions for the user.
          * Displays the conversion summary by file, conversion summary by function/module.
      * If a directory is provided as input to the utility, a single HTML file is generated with the name `<your directory name>_index.html` in the same directory with the two panes:
        * The left pane displays a list of all scripts and notebooks in the provided directory, showing their full paths. Clicking on the filename will redirect to the corresponding file report.
        * The right pane displays important notes and instructions for the user, and the summarized statistics from the directory.
    * Added optional argument `interactive_mode` to ask questions during the conversion.
    * Added optional argument `csv_report` to generate a csv file containing summary of alerts for Python script/notebook.
    * Utility now processes notebooks also inside a directory.
  * ###### teradatamlspk MLlib Functions
    * `Tokenizer()` - Converts the input string to lowercase and splits it by  whitespaces
    * `Summarizer` - Contains methods to compute statistical summaries for a column in the DataFrame.
    * `SummaryBuilder()` - Provides a builder object to provide summary statistics about a given column.
  * ###### teradatamlspk TeradataSession
    * `_jsparkSession` - A new property is added to return the TeradataSession.
    * `newSession()` - Returns the existing TeradataSession.
    * `range()` - Creates a DataFrame with a range of numbers.
  * ###### teradatamlspk SQLContext
    * `newSession()` - Returns the SQLContext as existing session.
    * `range()` - Creates a DataFrame with a range of numbers.
  * ###### teradatamlspk TeradataContext
    * `range()` - Creates a DataFrame with a range of numbers.
  * ###### teradatamlspk global functions
    * `substring_index` - Returns the substring from the string provided in the argument `str` before count occurrences of the delimiter specified in the argument `delim`.
    * `rlike` - Returns True if the string matches the regular expression, False otherwise.
  * ###### teradatamlspk DataFrameColumn a.k.a. ColumnExpression
    * `DataFrameColumn.rlike()` - Returns True if the string matches the regular expression, False otherwise.
  * ###### teradatamlspk DataFrameWriter
    * `mode()` - Specifies the behavior when data or table already exists.
  * ###### teradatamlspk DataFrame
    * `approxQuantile()` - Computes the approximate quantiles of numerical columns of the DataFrame.

* ##### Updates
    * `createDataFrame()` now supports `pandas.DataFrame`, `numpy.ndarray`, `list`, and `Row` objects as input data.
    * `register()` can also be accessed from `sqlContext.udf`.
    * `convert_timezone()` now accepts `sourceTz` as an optional argument.
    * `cast()` now accepts the format specifiers to convert to `TimestampType` and `TimestampNTZType`.
    * `bin()` now accepts float values.
    * `cbrt()`, `sqrt()`, `log()`, `log2()`, `log10()`, `acos()`, `asin()`, `atanh()`, `cot()`, `csc()`, `ln()`, `log1p()`, `sign()`, `signum()` returns None, when value in column is outside of the permitted values.
    * `shiftright()` and `shiftleft()` now casts float values to integers before processing the function.
    * `udf()` and `call_udf()` now raise an exception if the Column used by UDF is not present in the corresponding DataFrame.
    * `DataFrame.fillna()` , `DataFrame.na.fill()` and `DataFrame.replace()` now ignore replacements if the provided value in the argument `value` is not compatible with the column types specified in the argument `subset`.
    * `DataFrame.join()` and `DataFrame.crossJoin()` now raise a warning if the resultant DataFrame contains duplicate column names.
    * `substr()` now accepts Column for arguments `pos` and `len`.
    * `to_char()` and `to_varchar()` now accepts Column for argument `format`.
    * `to_number()` now accepts Column for argument `format`.
    * `to_timestamp_ltz()` and `to_timestamp_ntz()` now accepts Column for argument `format`.
    * `like()`and `ilike()` now supports `escapeChar` argument to escape special characters in the pattern and `pattern` argument accepts Column as input.
    * `from_utc_timestamp()` and  `to_utc_timestamp()` now accepts string value for argument `tz`.
    * `DataFrame.cube()` and `DataFrame.rollup()` now include aggregation on the grouping column(s).
    * `parse_url()` now supports `key` argument to extract a specific query parameter when `partToExtract` is set to "QUERY".
    * `udf()` and `udf.register()` now supports lambda functions.
    * `DataFrame.persist()` will now persist the DataFrame in Vantage.
    * `count_distinct()` and `countDistinct()` accepts multiple Columns for argument `col`.
    * `DataFrame.dtypes` will now return the data types similar to PySpark types.
    
* ##### Bug Fixes
    * `bin()` now works similar to pyspark if negative values are passed as input.
    * `params` function under ML class now returns all attributes of type `Param`.
    * Fixed a bug in `getOrCreate()` under SparkSession and SparkContext class to enable creating or updating a SparkSession.
    * Fixed the error messages for the unimplemented methods and attributes under ML class.
    * Fixed a bug in `DataFrame.describe()` to return the Summary statistics of the Dataframe.
    * Fixed a bug in `DataFrame.summary()` to return the DataFrame with the specified statistics.
    * Fixed a bug in `concat_ws()` to return the concatenated string if argument `cols` is a list of strings.

#### teradatamlspk 20.00.00.02
* ##### New Features/Functionality
  * ###### teradatamlspk DataFrameReader
    * `table()` - Returns the specified table as a DataFrame.
  * ###### teradatamlspk DataFrameWriterV2
    * `partitionedBy` - Partition the output table created by create, createOrReplace, or replace using the given columns or transforms.
    * `option` - Add an output option while writing a DataFrame to a data source.
    * `options` - Adds output options while writing a DataFrame to a data source.
  * ###### teradatamlspk global functions
    * `years` - Partition transform function: A transform for timestamps and dates to partition data into years.
    * `days` - Partition transform function: A transform for timestamps and dates to partition data into days.
    * `months` - Partition transform function: A transform for timestamps and dates to partition data into months.
    * `hours` - Partition transform function: A transform for timestamps and dates to partition data into hours.
    * `udf` - Creates a user defined function (UDF).
    * `conv` - Convert a number in a string column from one base to another.
    * `log` - Returns the first argument-based logarithm of the second argument.
    * `log2` - Returns the base-2 logarithm of the argument.
    * `date_from_unix_date` - Create date from the number of days since 1970-01-01.
    * `extract` - Extracts a part of the date/timestamp or interval source.
    * `datepart` - Extracts a part of the date/timestamp or interval source.
    * `date_part` - Extracts a part of the date/timestamp or interval source.
    * `make_dt_interval` - Make DayTimeIntervalType duration from days, hours, mins and secs.
    * `make_timestamp` - Create timestamp from years, months, days, hours, mins, secs and timezone fields.
    * `make_timestamp_ltz` - Create the current timestamp with local time zone from years, months, days, hours, mins, secs and timezone fields.
    * `make_timestamp_ntz` - Create local date-time from years, months, days, hours, mins, secs fields
    * `make_ym_interval` - Make year-month interval from years, months.
    * `make_date` - Returns a column with a date built from the year, month and day columns.
    * `from_unixtime` - Converts the number of seconds from unix epoch (1970-01-01 00:00:00 UTC) to a string representing the timestamp.
    * `unix_timestamp` - Convert time string with given pattern to unix epoch.
    * `to_unix_timestamp` - Convert time string with given pattern to unix epoch.
    * `to_timestamp` - Converts a string column to timestamp.
    * `to_timestamp_ltz` - Converts a string column to timestamp.
    * `to_timestamp_ntz` - Converts a string column to timestamp.
    * `from_utc_timestamp` - Converts column to utc timestamp from different timezone columns.
    * `to_utc_timestamp` - Converts column to given timestamp from utc timezone columns.
    * `timestamp_micros` - Creates timestamp from the number of microseconds since UTC epoch.
    * `timestamp_millis` - Creates timestamp from the number of milliseconds since UTC epoch.
    * `timestamp_seconds` - Converts the number of seconds from the Unix epoch to a timestamp
    * `unix_micros` - Returns the number of microseconds since 1970-01-01 00:00:00 UTC.
    * `unix_millis` - Returns the number of milliseconds since 1970-01-01 00:00:00 UTC. 
    * `unix_seconds` - Returns the number of seconds since 1970-01-01 00:00:00 UTC. 
    * `base64` - Computes the BASE64 encoding of a binary column and returns it as a string column.
    * `current_timezone` - Returns the current session local timezone.
    * `format_string` - Formats the arguments in printf-style and returns the result as a string column.
    * `elt` - Returns the n-th input, e.g., returns input2 when n is 2. The function returns NULL if the index exceeds the
              length of the array.
    * `to_varchar` - Convert col to a string based on the format.
    * `current_catalog` - Returns the current catalog. 
    * `equal_null` - Returns same result as the EQUAL(=) operator for non-null operands, but returns True
                    if both are null, False if one of the them is null.
    * `version` - Returns the teradatamlspk version.
    * `parse_url` - Extracts a part from a URL.
    * `reverse` - Returns a reversed string with reverse order of elements.
    * `convert_timezone` - Converts the timestamp without time zone sourceTs from the sourceTz time zone to targetTz.
    * `call_udf` - Register a user defined function (UDF).
  * ###### teradatamlspk UDFRegistration
    * `register()` - Call a registered user defined function (UDF).
  * ###### teradatamlspk DataFrameColumn a.k.a. ColumnExpression
    * `eqNullSafe()` - Equality test that is safe for null values.
  * ###### teradatamlspk MLlib Functions
    * `RegexTokenizer()` - Extracts tokens based on the pattern.
  * ###### pyspark2teradataml
    * `pyspark2teradataml` utility accepts directory containing Pyspark scripts as input.
    * `pyspark2teradataml` utility accepts Pyspark notebook as input.
* ##### Updates
  * `spark.conf.set` - Supports set time zone to session.
  * `spark.conf.unset` - Supports unset time zone to previous time zone set by user.
  *  `DataFrame.select()`, `DataFrame.withColumn()`, `DataFrame.withColumns()` function now accept functions `like`, `ilike`, `isNull`,`isNotNull`, `contains`, `startswith`, `endswith`, `booleanexpressions`, `binaryexpressions` without `when` clause.
  * `DataFrameColumn.cast()` and `DataFrameColumn.astype()` function supports `TimestampNTZType`, `DayTimeIntervalType`, `YearMonthIntervalType`.
  * `DataFrame.createTempView()` and `DataFrame.createOrReplaceTempView()` now drops view at the end of session.
  * `DataFrame.agg()` and `GroupedData.agg()` function supports aggregate functions generated using arthimetic operators.
* ##### Bug Fixes
  * `DataFrame.withColumnRenamed()` and `DataFrame.withColumnsRenamed()` will work if columns are renamed with same name of a column that is already present irrespective of case.
  * `DataFrame.join()` now works smiliar to pyspark if column name or list of column names are passed to `on` clause.
  
#### teradatamlspk 20.00.00.01
* ##### New Features/Functionality
  * ###### teradatamlspk DataFrame
    * `write()` - Supports writing the DataFrame to local file system or to Vantage or to cloud storage.
    * `writeTo()` - Supports writing the DataFrame to a Vantage table.
    * `rdd` - Returns the same DataFrame.
  * ###### teradatamlspk DataFrameColumn a.k.a. ColumnExpression
    * `desc_nulls_first()` - Returns a sort expression based on the descending order of the given column name, and null values appear before non-null values.
    * `desc_nulls_last()` - Returns a sort expression based on the descending order of the given column name, and null values appear after non-null values.
    * `asc_nulls_first()` - Returns a sort expression based on the ascending order of the given column name, and null values appear before non-null values.
    * `asc_nulls_last()` - Returns a sort expression based on the ascending order of the given column name, and null values appear after non-null values.
* ##### Updates
  * `DataFrame.fillna()` and `DataFrame.na.fill()` now supports input arguments of the same data type or their types must be compatible. 
  * `DataFrame.agg()` and `GroupedData.agg()` function supports Column as input and '*' for 'count'.
  * `DataFrameColumn.cast()` and `DataFrameColumn.astype()` now accepts string literal which are case insensitive.
  * Optimised performance for `DataFrame.show()`  
  * Classification Summary, TrainingSummary object and MulticlassClassificationEvaluator now supports `weightedTruePositiveRate` and `weightedFalsePositiveRate` metric.
  * Arithmetic operations can be performed on window aggregates.
* ##### Bug Fixes
  * `DataFrame.head()` returns a list when n is 1.
  * `DataFrame.union()` and `DataFrame.unionAll()` now performs union of rows based on columns position.
  * `DataFrame.groupBy()` and `DataFrame.groupby()` now accepts columns as positional arguments as well, for example `df.groupBy("col1", "col2")`.
  * MLlib Functions attribute `numClasses` and `intercept` now return value.
  * Appropriate error is raised if invalid file is passed to `pyspark2teradataml`.
  * `when` function accepts Column also along with literal for `value` argument. 

#### teradatamlspk 20.0.0.0
* `teradatamlspk 20.0.0.0` is the initial release version. Please refer to the teradatamlspk User Guide for the available API's and their functionality.

## Installation and Requirements

### Package Requirements:
* Python 3.9 or later

Note: 32-bit Python is not supported.

### Minimum System Requirements:
* Windows 7 (64Bit) or later
* macOS 10.9 (64Bit) or later
* Red Hat 7 or later versions
* Ubuntu 16.04 or later versions
* CentOS 7 or later versions
* SLES 12 or later versions
* Teradata Vantage Advanced SQL Engine:
    * Advanced SQL Engine 16.20 Feature Update 1 or later

### Installation

Use pip to install the teradatamlspk for running PySpark workloads.

Platform       | Command
-------------- | ---
macOS/Linux    | `pip install teradatamlspk`
Windows        | `py -3 -m pip install teradatamlspk`

When upgrading to a new version, you may need to use pip install's `--no-cache-dir` option to force the download of the new version.

Platform       | Command
-------------- | ---
macOS/Linux    | `pip install --no-cache-dir -U teradatamlspk`
Windows        | `py -3 -m pip install --no-cache-dir -U teradatamlspk`

## Usage the `teradatamlspk` Package

`teradatamlspk` has a utility `pyspark2teradataml` which accepts either PySpark script or PySpark notebook or a directory which has PySpark scripts or notebooks, analyzes and generates 2 files as below:
  1. HTML file - Created in the same directory where users PySpark script or notebook resides with name as `<your pyspark script name>_tdmlspk.html`. This file contains the script conversion report. Based on the report user can take the action on the generated scripts or notebooks.
      - If a directory is provided as input to the utility, a single HTML file is generated with the name `<your directory name>_index.html` in the same directory that displays a list of all scripts and notebooks in the provided directory, showing their full paths. Clicking on the filename will redirect to the corresponding file report.
  2. Python script/notebook - Created in the same directory where users PySpark script/notebook resides with name as `<your pyspark script name>_tdmlspk.py` for PySpark script or `<your pyspark script name>_tdmlspk.ipynb` for notebook, that can be run on Vantage.
      - Refer to the HTML report to understand the changes done and required to be done in the script/notebook.
    
### Example to demostrate the usage of utility `pyspark2teradataml`

```
>>> from teradatamlspk import pyspark2teradataml
>>> pyspark2teradataml('/tmp/pyspark_script.py')
Python script '/tmp/pyspark_script.py' converted to '/tmp/pyspark_script_tdmlspk.py' successfully.
Script conversion report '/tmp/pyspark_script_tdmlspk.html' published successfully. 

```

### Example to demostrate the `teradatamlspk` DataFrame creation.
```
>>> from teradatamlspk.sql import TeradataSession.
>>> spark = TeradataSession.builder.getOrCreate(host=host, user = user, password=password)
>>> df = spark.createDataFrame("test_classification")
>>> df.show()
+----------------------+---------------------+---------------------+----------------------+-------+
|         col1         |         col2        |         col3        |         col4         | label |
+----------------------+---------------------+---------------------+----------------------+-------+
| -1.1305820619922704  | -0.0202959251414216 | -0.7102336334648424 | -1.4409910829920618  |   0   |
| -0.28692000017174224 | -0.7169529842687833 | -0.9865850877151031 |  -0.848214734984639  |   0   |
| -2.5604297516143286  |  0.4022323367243113 | -1.1007419820939435 | -2.9595882598466674  |   0   |
|  0.4223414406917685  | -2.0391144030275625 |  -2.053215806414584 | -0.8491230457662061  |   0   |
|  0.7216694959200303  | -1.1215566442946217 | -0.8318398647044646 | 0.15074209659533433  |   0   |
| -0.9861325665504175  |  1.7105310292848412 |  1.3382818041204743 | -0.08534109029742933 |   1   |
| -0.5097927128625588  |  0.4926589443964751 |  0.2482067293662461 | -0.3095907315896897  |   1   |
| 0.18332468205821462  |  -0.774610353732039 |  -0.766054694735782 | -0.29366863291253276 |   0   |
| -0.4032571038523639  |  2.0061840569850093 |  2.0275124771199318 |  0.8508919440196763  |   1   |
| -0.07156025619387396 |  0.2295539000122874 | 0.21654344712218576 | 0.06527397921673575  |   1   |
+----------------------+---------------------+---------------------+----------------------+-------+
```

## Documentation

General product information, including installation instructions, is available in the [Teradata Documentation website](#)

## License

Use of the Teradata Spark Package is governed by the *License Agreement for teradatamlspk and pyspark2teradataml*. 
After installation, the `LICENSE` and `LICENSE-3RD-PARTY` files are located in the `teradatamlspk` directory of the Python installation directory.
