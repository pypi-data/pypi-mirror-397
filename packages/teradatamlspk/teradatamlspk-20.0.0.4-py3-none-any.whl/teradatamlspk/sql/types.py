#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
import decimal
import time
import math
import datetime
import calendar
import json
import re
import base64
from array import array
import ctypes
from collections.abc import Iterable
from functools import reduce
from typing import (
    cast,
    overload,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
    Tuple,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

T = TypeVar("T")
U = TypeVar("U")

class DataType:
    """Base class for data types."""

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @classmethod
    def typeName(cls) -> str:
        return cls.__name__[:-4].lower()

    def simpleString(self) -> str:
        return self.typeName()

    def jsonValue(self) -> Union[str, Dict[str, Any]]:
        return self.typeName()

    def json(self) -> str:
        return json.dumps(self.jsonValue(), separators=(",", ":"), sort_keys=True)

    def needConversion(self) -> bool:
        """
        Does this type needs conversion between Python object and internal SQL object.

        This is used to avoid the unnecessary conversion for ArrayType/MapType/StructType.
        """
        return False

    def toInternal(self, obj: Any) -> Any:
        """
        Converts a Python object into an internal SQL object.
        """
        return obj

    def fromInternal(self, obj: Any) -> Any:
        """
        Converts an internal SQL object into a native Python object.
        """
        return obj


# This singleton pattern does not work with pickle, you will get
# another object after pickle and unpickle
class DataTypeSingleton(type):
    """Metaclass for DataType"""

    _instances: ClassVar[Dict[Type["DataTypeSingleton"], "DataTypeSingleton"]] = {}

    def __call__(cls: Type[T]) -> T:
        if cls not in cls._instances:  # type: ignore[attr-defined]
            cls._instances[cls] = super(  # type: ignore[misc, attr-defined]
                DataTypeSingleton, cls
            ).__call__()
        return cls._instances[cls]  # type: ignore[attr-defined]


class NullType(DataType, metaclass=DataTypeSingleton):
    """Null type.

    The data type representing None, used for the types that cannot be inferred.
    """

    @classmethod
    def typeName(cls) -> str:
        return "void"


class AtomicType(DataType):
    """An internal type used to represent everything that is not
    null, UDTs, arrays, structs, and maps."""


class NumericType(AtomicType):
    """Numeric data types."""


class IntegralType(NumericType, metaclass=DataTypeSingleton):
    """Integral data types."""

    pass


class FractionalType(NumericType):
    """Fractional data types."""


class StringType(AtomicType, metaclass=DataTypeSingleton):
    """String data type."""

    pass


class CharType(AtomicType):
    """Char data type

    Parameters
    ----------
    length : int
        the length limitation.
    """

    def __init__(self, length: int):
        self.length = length

    def simpleString(self) -> str:
        return "char(%d)" % (self.length)

    def jsonValue(self) -> str:
        return "char(%d)" % (self.length)

    def __repr__(self) -> str:
        return "CharType(%d)" % (self.length)


class VarcharType(AtomicType):
    """Varchar data type

    Parameters
    ----------
    length : int
        the length limitation.
    """

    def __init__(self, length: int):
        self.length = length

    def simpleString(self) -> str:
        return "varchar(%d)" % (self.length)

    def jsonValue(self) -> str:
        return "varchar(%d)" % (self.length)

    def __repr__(self) -> str:
        return "VarcharType(%d)" % (self.length)


class BinaryType(AtomicType, metaclass=DataTypeSingleton):
    """Binary (byte array) data type."""

    pass


class BooleanType(AtomicType, metaclass=DataTypeSingleton):
    """Boolean data type."""

    pass


class DateType(AtomicType, metaclass=DataTypeSingleton):
    """Date (datetime.date) data type."""

    EPOCH_ORDINAL = datetime.datetime(1970, 1, 1).toordinal()

    def needConversion(self) -> bool:
        return True

    def toInternal(self, d: datetime.date) -> int:
        if d is not None:
            return d.toordinal() - self.EPOCH_ORDINAL

    def fromInternal(self, v: int) -> datetime.date:
        if v is not None:
            return datetime.date.fromordinal(v + self.EPOCH_ORDINAL)


class TimestampType(AtomicType, metaclass=DataTypeSingleton):
    """Timestamp (datetime.datetime) data type."""

    def needConversion(self) -> bool:
        return True

    def toInternal(self, dt: datetime.datetime) -> int:
        if dt is not None:
            seconds = (
                calendar.timegm(dt.utctimetuple()) if dt.tzinfo else time.mktime(dt.timetuple())
            )
            return int(seconds) * 1000000 + dt.microsecond

    def fromInternal(self, ts: int) -> datetime.datetime:
        if ts is not None:
            # using int to avoid precision loss in float
            return datetime.datetime.fromtimestamp(ts // 1000000).replace(microsecond=ts % 1000000)


class TimestampNTZType(AtomicType, metaclass=DataTypeSingleton):
    """Timestamp (datetime.datetime) data type without timezone information."""

    def needConversion(self) -> bool:
        return True

    @classmethod
    def typeName(cls) -> str:
        return "timestamp_ntz"

    def toInternal(self, dt: datetime.datetime) -> int:
        if dt is not None:
            seconds = calendar.timegm(dt.timetuple())
            return int(seconds) * 1000000 + dt.microsecond

    def fromInternal(self, ts: int) -> datetime.datetime:
        if ts is not None:
            # using int to avoid precision loss in float
            return datetime.datetime.utcfromtimestamp(ts // 1000000).replace(
                microsecond=ts % 1000000
            )


class DecimalType(FractionalType):
    """Decimal (decimal.Decimal) data type.

    The DecimalType must have fixed precision (the maximum total number of digits)
    and scale (the number of digits on the right of dot). For example, (5, 2) can
    support the value from [-999.99 to 999.99].

    The precision can be up to 38, the scale must be less or equal to precision.

    When creating a DecimalType, the default precision and scale is (10, 0). When inferring
    schema from decimal.Decimal objects, it will be DecimalType(38, 18).

    Parameters
    ----------
    precision : int, optional
        the maximum (i.e. total) number of digits (default: 10)
    scale : int, optional
        the number of digits on right side of dot. (default: 0)
    """

    def __init__(self, precision: int = 10, scale: int = 0):
        self.precision = precision
        self.scale = scale
        self.hasPrecisionInfo = True  # this is a public API

    def simpleString(self) -> str:
        return "decimal(%d,%d)" % (self.precision, self.scale)

    def jsonValue(self) -> str:
        return "decimal(%d,%d)" % (self.precision, self.scale)

    def __repr__(self) -> str:
        return "DecimalType(%d,%d)" % (self.precision, self.scale)


class DoubleType(FractionalType, metaclass=DataTypeSingleton):
    """Double data type, representing double precision floats."""

    pass


class FloatType(FractionalType, metaclass=DataTypeSingleton):
    """Float data type, representing single precision floats."""

    pass


class ByteType(IntegralType):
    """Byte data type, i.e. a signed integer in a single byte."""

    def simpleString(self) -> str:
        return "tinyint"


class IntegerType(IntegralType):
    """Int data type, i.e. a signed 32-bit integer."""

    def simpleString(self) -> str:
        return "int"


class LongType(IntegralType):
    """Long data type, i.e. a signed 64-bit integer.

    If the values are beyond the range of [-9223372036854775808, 9223372036854775807],
    please use :class:`DecimalType`.
    """

    def simpleString(self) -> str:
        return "bigint"


class ShortType(IntegralType):
    """Short data type, i.e. a signed 16-bit integer."""

    def simpleString(self) -> str:
        return "smallint"


# Newly added types for teradatamlspk.
class BlobType(DataType):
    pass


class TimeType(DataType):
    pass


class IntervalYearType(DataType):
    pass


class IntervalYearToMonthType(DataType):
    pass


class IntervalMonthType(DataType):
    pass


class IntervalDayType(DataType):
    pass


class IntervalDayToHourType(DataType):
    pass


class IntervalDayToMinuteType(DataType):
    pass


class IntervalDayToSecondType(DataType):
    pass


class IntervalHourType(DataType):
    pass


class IntervalHourToMinuteType(DataType):
    pass


class IntervalHourToSecondType(DataType):
    pass


class IntervalMinuteType(DataType):
    pass


class IntervalMinuteToSecondType(DataType):
    pass


class IntervalSecondType(DataType):
    pass


class PeriodDateType(DataType):
    pass


class PeriodTimeType(DataType):
    pass


class PeriodTimestampType(DataType):
    pass


class ClobType(DataType):
    pass


class XmlType(DataType):
    pass


class JsonType(DataType):
    pass


class GeometryType(DataType):
    pass


class MbrType(DataType):
    pass


class MbbType(DataType):
    pass


class AnsiIntervalType(AtomicType):
    """The interval type which conforms to the ANSI SQL standard."""

    pass


class DayTimeIntervalType(AnsiIntervalType):
    """DayTimeIntervalType (datetime.timedelta)."""

    DAY = 0
    HOUR = 1
    MINUTE = 2
    SECOND = 3

    _fields = {
        DAY: "day",
        HOUR: "hour",
        MINUTE: "minute",
        SECOND: "second",
    }

    _inverted_fields = dict(zip(_fields.values(), _fields.keys()))

    def __init__(self, startField: Optional[int] = None, endField: Optional[int] = None):
        if startField is None and endField is None:
            # Default matched to scala side.
            startField = DayTimeIntervalType.DAY
            endField = DayTimeIntervalType.SECOND
        elif startField is not None and endField is None:
            endField = startField

        fields = DayTimeIntervalType._fields
        if startField not in fields.keys() or endField not in fields.keys():
            raise RuntimeError("interval %s to %s is invalid" % (startField, endField))
        self.startField = cast(int, startField)
        self.endField = cast(int, endField)

    def _str_repr(self) -> str:
        fields = DayTimeIntervalType._fields
        start_field_name = fields[self.startField]
        end_field_name = fields[self.endField]
        if start_field_name == end_field_name:
            return "interval %s" % start_field_name
        else:
            return "interval %s to %s" % (start_field_name, end_field_name)

    simpleString = _str_repr

    jsonValue = _str_repr

    def __repr__(self) -> str:
        return "%s(%d, %d)" % (type(self).__name__, self.startField, self.endField)

    def needConversion(self) -> bool:
        return True

    def toInternal(self, dt: datetime.timedelta) -> Optional[int]:
        if dt is not None:
            return (((dt.days * 86400) + dt.seconds) * 1_000_000) + dt.microseconds

    def fromInternal(self, micros: int) -> Optional[datetime.timedelta]:
        if micros is not None:
            return datetime.timedelta(microseconds=micros)
        
class ArrayType(DataType):
    """Array data type, consisting of elements of a specified type.

    Parameters
    ----------
    elementType : :class:`DataType`
        The data type of elements.
    containsNull : bool, optional
        Whether the array can contain null (None) values (default: True)
    """

    def __init__(self, elementType: DataType, containsNull: bool = True):
        assert isinstance(elementType, DataType), "elementType %s should be an instance of %s" % (
            elementType,
            DataType,
        )
        self.elementType = elementType
        self.containsNull = containsNull

    def simpleString(self) -> str:
        return "array<%s>" % self.elementType.simpleString()

    def jsonValue(self) -> dict:
        return {
            "type": "array",
            "elementType": self.elementType.jsonValue(),
            "containsNull": self.containsNull,
        }

    def __repr__(self) -> str:
        return "ArrayType(%r, %r)" % (self.elementType, self.containsNull)
    
    @classmethod
    def fromJson(cls, json: dict) -> "ArrayType":
        return ArrayType(
            _parse_datatype_json_value(json["elementType"]),
            json.get("containsNull", True),
        )

    def needConversion(self) -> bool:
        return self.elementType.needConversion()

    def toInternal(self, obj: List[Optional[T]]) -> List[Optional[T]]:
        if not self.needConversion():
            return obj
        return obj and [self.elementType.toInternal(v) for v in obj]

    def fromInternal(self, obj: List[Optional[T]]) -> List[Optional[T]]:
        if not self.needConversion():
            return obj
        return obj and [self.elementType.fromInternal(v) for v in obj]


class YearMonthIntervalType(AnsiIntervalType):
    """YearMonthIntervalType, represents year-month intervals of the SQL standard"""

    YEAR = 0
    MONTH = 1

    _fields = {
        YEAR: "year",
        MONTH: "month",
    }

    _inverted_fields = dict(zip(_fields.values(), _fields.keys()))

    def __init__(self, startField: Optional[int] = None, endField: Optional[int] = None):
        if startField is None and endField is None:
            # Default matched to scala side.
            startField = YearMonthIntervalType.YEAR
            endField = YearMonthIntervalType.MONTH
        elif startField is not None and endField is None:
            endField = startField

        fields = YearMonthIntervalType._fields
        if startField not in fields.keys() or endField not in fields.keys():
            raise RuntimeError("interval %s to %s is invalid" % (startField, endField))
        self.startField = cast(int, startField)
        self.endField = cast(int, endField)

    def _str_repr(self) -> str:
        fields = YearMonthIntervalType._fields
        start_field_name = fields[self.startField]
        end_field_name = fields[self.endField]
        if start_field_name == end_field_name:
            return "interval %s" % start_field_name
        else:
            return "interval %s to %s" % (start_field_name, end_field_name)

    simpleString = _str_repr

    jsonValue = _str_repr

    def __repr__(self) -> str:
        return "%s(%d, %d)" % (type(self).__name__, self.startField, self.endField)


class StructField(DataType):
    """A field in :class:`StructType`.

    Parameters
    ----------
    name : str
        name of the field.
    dataType : :class:`DataType`
        :class:`DataType` of the field.
    nullable : bool, optional
        whether the field can be null (None) or not.
    metadata : dict, optional
        a dict from string to simple type that can be toInternald to JSON automatically

    Examples
    --------
    >>> from pyspark.sql.types import StringType, StructField
    >>> (StructField("f1", StringType(), True)
    ...      == StructField("f1", StringType(), True))
    True
    >>> (StructField("f1", StringType(), True)
    ...      == StructField("f2", StringType(), True))
    False
    """

    def __init__(
        self,
        name: str,
        dataType: DataType,
        nullable: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        assert isinstance(name, str), "field name %s should be a string" % (name)
        self.name = name
        self.dataType = dataType
        self.nullable = nullable
        self.metadata = metadata or {}

    def simpleString(self) -> str:
        return "%s:%s" % (self.name, self.dataType.simpleString())

    def __repr__(self) -> str:
        return "StructField('%s', %s, %s)" % (self.name, self.dataType, str(self.nullable))

    def jsonValue(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.dataType.jsonValue(),
            "nullable": self.nullable,
            "metadata": self.metadata,
        }

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> "StructField":
        return StructField(
            json["name"],
            _parse_datatype_json_value(json["type"]),
            json["nullable"],
            json["metadata"],
        )

    def needConversion(self) -> bool:
        return self.dataType.needConversion()

    def toInternal(self, obj: T) -> T:
        return self.dataType.toInternal(obj)

    def fromInternal(self, obj: T) -> T:
        return self.dataType.fromInternal(obj)

    def typeName(self) -> str:  # type: ignore[override]
        raise Exception("Invalid call to typeName()")


class StructType(DataType):
    """Struct type, consisting of a list of :class:`StructField`.

    This is the data type representing a :class:`Row`.

    Iterating a :class:`StructType` will iterate over its :class:`StructField`\\s.
    A contained :class:`StructField` can be accessed by its name or position.

    Examples
    --------
    >>> from pyspark.sql.types import *
    >>> struct1 = StructType([StructField("f1", StringType(), True)])
    >>> struct1["f1"]
    StructField('f1', StringType(), True)
    >>> struct1[0]
    StructField('f1', StringType(), True)

    >>> struct1 = StructType([StructField("f1", StringType(), True)])
    >>> struct2 = StructType([StructField("f1", StringType(), True)])
    >>> struct1 == struct2
    True
    >>> struct1 = StructType([StructField("f1", CharType(10), True)])
    >>> struct2 = StructType([StructField("f1", CharType(10), True)])
    >>> struct1 == struct2
    True
    >>> struct1 = StructType([StructField("f1", VarcharType(10), True)])
    >>> struct2 = StructType([StructField("f1", VarcharType(10), True)])
    >>> struct1 == struct2
    True
    >>> struct1 = StructType([StructField("f1", StringType(), True)])
    >>> struct2 = StructType([StructField("f1", StringType(), True),
    ...     StructField("f2", IntegerType(), False)])
    >>> struct1 == struct2
    False

    The below example demonstrates how to create a DataFrame based on a struct created
    using class:`StructType` and class:`StructField`:

    >>> data = [("Alice", ["Java", "Scala"]), ("Bob", ["Python", "Scala"])]
    >>> schema = StructType([
    ...     StructField("name", StringType()),
    ...     StructField("languagesSkills", ArrayType(StringType())),
    ... ])
    >>> df = spark.createDataFrame(data=data, schema=schema)
    >>> df.printSchema()
    root
     |-- name: string (nullable = true)
     |-- languagesSkills: array (nullable = true)
     |    |-- element: string (containsNull = true)
    >>> df.show()
    +-----+---------------+
    | name|languagesSkills|
    +-----+---------------+
    |Alice|  [Java, Scala]|
    |  Bob|[Python, Scala]|
    +-----+---------------+
    """

    def __init__(self, fields: Optional[List[StructField]] = None):
        if not fields:
            self.fields = []
            self.names = []
        else:
            self.fields = fields
            self.names = [f.name for f in fields]
            assert all(
                isinstance(f, StructField) for f in fields
            ), "fields should be a list of StructField"
        # Precalculated list of fields that need conversion with fromInternal/toInternal functions
        self._needConversion = [f.needConversion() for f in self]
        self._needSerializeAnyField = any(self._needConversion)

    @overload
    def add(
        self,
        field: str,
        data_type: Union[str, DataType],
        nullable: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "StructType":
        ...

    @overload
    def add(self, field: StructField) -> "StructType":
        ...

    def add(
        self,
        field: Union[str, StructField],
        data_type: Optional[Union[str, DataType]] = None,
        nullable: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "StructType":
        """
        Construct a :class:`StructType` by adding new elements to it, to define the schema.
        The method accepts either:

            a) A single parameter which is a :class:`StructField` object.
            b) Between 2 and 4 parameters as (name, data_type, nullable (optional),
               metadata(optional). The data_type parameter may be either a String or a
               :class:`DataType` object.

        Parameters
        ----------
        field : str or :class:`StructField`
            Either the name of the field or a :class:`StructField` object
        data_type : :class:`DataType`, optional
            If present, the DataType of the :class:`StructField` to create
        nullable : bool, optional
            Whether the field to add should be nullable (default True)
        metadata : dict, optional
            Any additional metadata (default None)

        Returns
        -------
        :class:`StructType`

        Examples
        --------
        >>> from pyspark.sql.types import IntegerType, StringType, StructField, StructType
        >>> struct1 = StructType().add("f1", StringType(), True).add("f2", StringType(), True, None)
        >>> struct2 = StructType([StructField("f1", StringType(), True),
        ...     StructField("f2", StringType(), True, None)])
        >>> struct1 == struct2
        True
        >>> struct1 = StructType().add(StructField("f1", StringType(), True))
        >>> struct2 = StructType([StructField("f1", StringType(), True)])
        >>> struct1 == struct2
        True
        >>> struct1 = StructType().add("f1", "string", True)
        >>> struct2 = StructType([StructField("f1", StringType(), True)])
        >>> struct1 == struct2
        True
        """
        if isinstance(field, StructField):
            self.fields.append(field)
            self.names.append(field.name)
        else:
            if isinstance(field, str) and data_type is None:
                raise ValueError("Argument `data_type` is required when passing name of struct_field to create.")

            if isinstance(data_type, str):
                data_type_f = _parse_datatype_json_value(data_type)
            else:
                data_type_f = data_type
            self.fields.append(StructField(field, data_type_f, nullable, metadata))
            self.names.append(field)
        # Precalculated list of fields that need conversion with fromInternal/toInternal functions
        self._needConversion = [f.needConversion() for f in self]
        self._needSerializeAnyField = any(self._needConversion)
        return self

    def __iter__(self) -> Iterator[StructField]:
        """Iterate the fields"""
        return iter(self.fields)

    def __len__(self) -> int:
        """Return the number of fields."""
        return len(self.fields)

    def __getitem__(self, key: Union[str, int]) -> StructField:
        """Access fields by name or slice."""
        if isinstance(key, str):
            for field in self:
                if field.name == key:
                    return field
            raise KeyError("No StructField named {0}".format(key))
        elif isinstance(key, int):
            try:
                return self.fields[key]
            except IndexError:
                raise IndexError("StructType index out of range")
        elif isinstance(key, slice):
            return StructType(self.fields[key])
        else:
            raise NotImplementedError()

    def simpleString(self) -> str:
        return "struct<%s>" % (",".join(f.simpleString() for f in self))

    def __repr__(self) -> str:
        return "StructType([%s])" % ", ".join(str(field) for field in self)

    def jsonValue(self) -> Dict[str, Any]:
        return {"type": self.typeName(), "fields": [f.jsonValue() for f in self]}

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> "StructType":
        """
        Constructs :class:`StructType` from a schema defined in JSON format.

        Below is a JSON schema it must adhere to::

            {
              "title":"StructType",
              "description":"Schema of StructType in json format",
              "type":"object",
              "properties":{
                 "fields":{
                    "description":"Array of struct fields",
                    "type":"array",
                    "items":{
                        "type":"object",
                        "properties":{
                           "name":{
                              "description":"Name of the field",
                              "type":"string"
                           },
                           "type":{
                              "description": "Type of the field. Can either be
                                              another nested StructType or primitive type",
                              "type":"object/string"
                           },
                           "nullable":{
                              "description":"If nulls are allowed",
                              "type":"boolean"
                           },
                           "metadata":{
                              "description":"Additional metadata to supply",
                              "type":"object"
                           },
                           "required":[
                              "name",
                              "type",
                              "nullable",
                              "metadata"
                           ]
                        }
                   }
                }
             }
           }

        Parameters
        ----------
        json : dict or a dict-like object e.g. JSON object
            This "dict" must have "fields" key that returns an array of fields
            each of which must have specific keys (name, type, nullable, metadata).

        Returns
        -------
        :class:`StructType`

        Examples
        --------
        >>> json_str = '''
        ...  {
        ...      "fields": [
        ...          {
        ...              "metadata": {},
        ...              "name": "Person",
        ...              "nullable": true,
        ...              "type": {
        ...                  "fields": [
        ...                      {
        ...                          "metadata": {},
        ...                          "name": "name",
        ...                          "nullable": false,
        ...                          "type": "string"
        ...                      },
        ...                      {
        ...                          "metadata": {},
        ...                          "name": "surname",
        ...                          "nullable": false,
        ...                          "type": "string"
        ...                      }
        ...                  ],
        ...                  "type": "struct"
        ...              }
        ...          }
        ...      ],
        ...      "type": "struct"
        ...  }
        ...  '''
        >>> import json
        >>> scheme = StructType.fromJson(json.loads(json_str))
        >>> scheme.simpleString()
        'struct<Person:struct<name:string,surname:string>>'
        """
        return StructType([StructField.fromJson(f) for f in json["fields"]])

    def fieldNames(self) -> List[str]:
        """
        Returns all field names in a list.

        Examples
        --------
        >>> from pyspark.sql.types import StringType, StructField, StructType
        >>> struct = StructType([StructField("f1", StringType(), True)])
        >>> struct.fieldNames()
        ['f1']
        """
        return list(self.names)

    def needConversion(self) -> bool:
        # We need convert Row()/namedtuple into tuple()
        return True

    def toInternal(self, obj: Tuple) -> Tuple:
        if obj is None:
            return

        if self._needSerializeAnyField:
            # Only calling toInternal function for fields that need conversion
            if isinstance(obj, dict):
                return tuple(
                    f.toInternal(obj.get(n)) if c else obj.get(n)
                    for n, f, c in zip(self.names, self.fields, self._needConversion)
                )
            elif isinstance(obj, (tuple, list)):
                return tuple(
                    f.toInternal(v) if c else v
                    for f, v, c in zip(self.fields, obj, self._needConversion)
                )
            elif hasattr(obj, "__dict__"):
                d = obj.__dict__
                return tuple(
                    f.toInternal(d.get(n)) if c else d.get(n)
                    for n, f, c in zip(self.names, self.fields, self._needConversion)
                )
            else:
                raise PySparkValueError(
                    error_class="UNEXPECTED_TUPLE_WITH_STRUCT",
                    message_parameters={"tuple": str(obj)},
                )
        else:
            if isinstance(obj, dict):
                return tuple(obj.get(n) for n in self.names)
            elif isinstance(obj, (list, tuple)):
                return tuple(obj)
            elif hasattr(obj, "__dict__"):
                d = obj.__dict__
                return tuple(d.get(n) for n in self.names)
            else:
                raise PySparkValueError(
                    error_class="UNEXPECTED_TUPLE_WITH_STRUCT",
                    message_parameters={"tuple": str(obj)},
                )

    def fromInternal(self, obj: Tuple) -> "Row":
        if obj is None:
            return
        if isinstance(obj, Row):
            # it's already converted by pickler
            return obj

        values: Union[Tuple, List]
        if self._needSerializeAnyField:
            # Only calling fromInternal function for fields that need conversion
            values = [
                f.fromInternal(v) if c else v
                for f, v, c in zip(self.fields, obj, self._needConversion)
            ]
        else:
            values = obj
        return _create_row(self.names, values)


class UserDefinedType(DataType):
    """User-defined type (UDT).

    .. note:: WARN: Spark Internal Use Only
    """

    @classmethod
    def typeName(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def sqlType(cls) -> DataType:
        """
        Underlying SQL storage type for this UDT.
        """
        raise NotImplementedError()

    @classmethod
    def module(cls) -> str:
        """
        The Python module of the UDT.
        """
        raise NotImplementedError()

    @classmethod
    def scalaUDT(cls) -> str:
        """
        The class name of the paired Scala UDT (could be '', if there
        is no corresponding one).
        """
        return ""

    def needConversion(self) -> bool:
        return True

    @classmethod
    def _cachedSqlType(cls) -> DataType:
        """
        Cache the sqlType() into class, because it's heavily used in `toInternal`.
        """
        if not hasattr(cls, "_cached_sql_type"):
            cls._cached_sql_type = cls.sqlType()  # type: ignore[attr-defined]
        return cls._cached_sql_type  # type: ignore[attr-defined]

    def toInternal(self, obj: Any) -> Any:
        if obj is not None:
            return self._cachedSqlType().toInternal(self.serialize(obj))

    def fromInternal(self, obj: Any) -> Any:
        v = self._cachedSqlType().fromInternal(obj)
        if v is not None:
            return self.deserialize(v)

    def serialize(self, obj: Any) -> Any:
        """
        Converts a user-type object into a SQL datum.
        """
        raise NotImplementedError()

    def deserialize(self, datum: Any) -> Any:
        """
        Converts a SQL datum into a user-type object.
        """
        raise NotImplementedError()

    def simpleString(self) -> str:
        return "udt"

    def json(self) -> str:
        return json.dumps(self.jsonValue(), separators=(",", ":"), sort_keys=True)

    def jsonValue(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> "UserDefinedType":
        raise NotImplementedError()

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other)


class Row(tuple):

    """
    A row in :class:`DataFrame`.
    The fields in it can be accessed:

    * like attributes (``row.key``)
    * like dictionary values (``row[key]``)

    ``key in row`` will search through row keys.

    Row can be used to create a row object by using named arguments.
    It is not allowed to omit a named argument to represent that the value is
    None or missing. This should be explicitly set to None in this case.

    Examples
    --------
    >>> row = Row(name="Alice", age=11)
    >>> row
    Row(name='Alice', age=11)
    >>> row['name'], row['age']
    ('Alice', 11)
    >>> row.name, row.age
    ('Alice', 11)
    >>> 'name' in row
    True
    >>> 'wrong_key' in row
    False

    Row also can be used to create another Row like class, then it
    could be used to create Row objects, such as

    >>> Person = Row("name", "age")
    >>> Person
    <Row('name', 'age')>
    >>> 'name' in Person
    True
    >>> 'wrong_key' in Person
    False
    >>> Person("Alice", 11)
    Row(name='Alice', age=11)

    This form can also be used to create rows as tuple values, i.e. with unnamed
    fields.

    >>> row1 = Row("Alice", 11)
    >>> row2 = Row(name="Alice", age=11)
    >>> row1 == row2
    True
    """
    
    def __call__(self, *args: Any) -> "Row":
        """Create a new Row object with the given values."""
        if len(args) > len(self):
            raise ValueError(f"[TOO_MANY_VALUES] Expected {len(self)} values for `fields`, got {len(args)}.")
        # Create a new Row instance with the same fields and new values.
        row = Row(*args)
        row.__fields__ = list(self)
        return row
    
    def __new__(cls, *args, **kwargs):
        if args and kwargs:
            raise ValueError("Can not use both args "
                             "and kwargs to create Row")
        if kwargs:
            # create row objects
            row = tuple.__new__(cls, list(kwargs.values()))
            row.__fields__ = list(kwargs.keys())
            return row
        else:
            # create row class or objects
            return tuple.__new__(cls, args)

    def asDict(self, recursive=False):
        """
        Return as a dict

        Parameters
        ----------
        recursive : bool, optional
            turns the nested Rows to dict (default: False).

        Examples
        --------
        >>> Row(name="Alice", age=11).asDict() == {'name': 'Alice', 'age': 11}
        True
        >>> row = Row(key=1, value=Row(name='a', age=2))
        >>> row.asDict() == {'key': 1, 'value': Row(name='a', age=2)}
        True
        >>> row.asDict(True) == {'key': 1, 'value': {'name': 'a', 'age': 2}}
        True
        """
        if not hasattr(self, "__fields__"):
            raise TypeError("Cannot convert a Row class into dict")

        if recursive:
            def conv(obj):
                if isinstance(obj, Row):
                    return obj.asDict(True)
                elif isinstance(obj, list):
                    return [conv(o) for o in obj]
                elif isinstance(obj, dict):
                    return dict((k, conv(v)) for k, v in obj.items())
                else:
                    return obj
            return dict(zip(self.__fields__, (conv(o) for o in self)))
        else:
            return dict(zip(self.__fields__, self))

    def __contains__(self, item):
        if hasattr(self, "__fields__"):
            return item in self.__fields__
        else:
            return super(Row, self).__contains__(item)

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return super(Row, self).__getitem__(item)
        try:
            # it will be slow when it has many fields,
            # but this will not be used in normal cases
            idx = self.__fields__.index(item)
            return super(Row, self).__getitem__(idx)
        except IndexError:
            raise KeyError(item)
        except ValueError:
            raise ValueError(item)

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        try:
            # it will be slow when it has many fields,
            # but this will not be used in normal cases
            idx = self.__fields__.index(item)
            return self[idx]
        except IndexError:
            raise AttributeError(item)
        except ValueError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key != '__fields__':
            raise RuntimeError("Row is read-only")
        self.__dict__[key] = value

    def __repr__(self):
        """Printable representation of Row used in Python REPL."""
        if hasattr(self, "__fields__"):
            return "Row(%s)" % ", ".join("%s=%r" % (k, v)
                                         for k, v in zip(self.__fields__, tuple(self)))
        else:
            return "<Row(%s)>" % ", ".join("%r" % field for field in self)
