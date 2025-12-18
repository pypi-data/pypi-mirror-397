# Copyright 2018 by Teradata Corporation. All rights reserved.

from sqlalchemy import util
from sqlalchemy import types
from sqlalchemy.sql import sqltypes, operators

import datetime, decimal
import warnings, sys
import re
#import teradata.datatypes as td_dtypes


class _TDComparable:
    """Teradata Comparable Data Type."""

    class Comparator(types.TypeEngine.Comparator):
        """Comparator for expression adaptation.

        Use the TeradataExpressionAdapter to process the resulting types
        for binary operations over Teradata types.
        """

        def _adapt_expression(self, op, other_comparator):
            expr_type = TeradataExpressionAdapter().process(
                self.type, op=op, other=other_comparator.type)
            return op, expr_type()

    comparator_factory = Comparator


class _TDConcatenable:
    """Teradata Concatenable Data Type.

    This family of types currently encompasses the binary types
    (BYTE, VARBYTE, BLOB) and the character types (CHAR, VARCHAR, CLOB).
    """

    class Comparator(_TDComparable.Comparator):
        """Comparator for expression adaptation.

        Overloads the addition (+) operator over concatenable Teradata types
        to use concat_op. Note that this overloading only occurs between types
        within the same type_affinity.
        """

        def _adapt_expression(self, op, other_comparator):
            return super(_TDConcatenable.Comparator, self)._adapt_expression(
                operators.concat_op if op is operators.add and
                    isinstance(other_comparator.type, self.type._type_affinity)
                else op, other_comparator)

    comparator_factory = Comparator


class _TDLiteralCoercer:
    """Mixin for literal type processing against Teradata data types."""

    def coerce_compared_value(self, op, value):
        type_ = type(value)

        if type_ == int:
            return INTEGER()
        elif type_ == float:
            return FLOAT()
        elif type_ == bytes:
            return BYTE()
        elif type_ == str:
            return VARCHAR()
        elif type_ == decimal.Decimal:
            return DECIMAL()
        elif type_ == datetime.date:
            return DATE()
        elif type_ == datetime.datetime:
            return TIMESTAMP()
        elif type_ == datetime.time:
            return TIME()
       # elif type_ == td_dtypes.Interval:
       #     return getattr(sys.modules[__name__],
       #         'INTERVAL_' + value.type.replace(' ', '_'),
       #         sqltypes.NullType)()
        # TODO PERIOD

        return sqltypes.NullType()


class _TDType(_TDLiteralCoercer, _TDComparable):

    """ Teradata Data Type

    Identifies a Teradata data type. Currently used to override __str__
    behavior such that the type will get printed without being compiled by the
    GenericTypeCompiler (which would otherwise result in an exception).
    """

    def _parse_name(self, name):
        return name.replace('_', ' ')

    def __str__(self):
        return self._parse_name(self.__class__.__name__)
    
    @property
    def udt_name(self):
        """
        Returns the UDT name for types that use UDTs (like arrays).
        For standard types, returns None.
        
        Returns:
            None for non-UDT types
        """
        return None

class _TDArray(_TDType, types.UserDefinedType):

    """ Teradata Array Type

    This is a base class for Teradata array types. It provides common functionality
    for all array types including scope validation, dimension calculation, and
    UDT name generation. Individual array types (like ARRAY_INTEGER, ARRAY_DATE, etc.)
    inherit from this class.
    """


    def __init__(self, scope, **kwargs):
        """ Construct an Array object

        :param scope: The scope of the array in format '[n]' for 1D, '[n:m][p:q]' 
        or '[n][p]' for 2D, etc.
        """
        self.dimension, self.scope = self._process_scope_and_get_dimension(scope)
        self._udt_name = kwargs.get("udt_name", None)

        # Drop udt_name from kwargs.
        kwargs.pop("udt_name", None)
        super().__init__(**kwargs)

    def _process_scope_and_get_dimension(self, scope):
        """
        DESCRIPTION:
            Validates the scope format and returns the dimension and normalized scope string.
            
            Valid formats:
            - '[n]' for 1D array
            - '[n:m][p:q]' or '[n][p]' for 2D array 
            - '[n:m][p:q][r:s]' or '[n][p][r]' for 3D array
            - '[n:m][p:q][r:s][t:u]' or '[n][p][r][t]' for 4D array 
            - '[n:m][p:q][r:s][t:u][v:w]' or '[n][p][r][t][v]' for 5D array
        
        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str
            
        RETURNS:
            The dimension of the array (1-5) and normalized scope string.
            
        Raises:
            ValueError

        EXAMPLES:
            >>> _TDArray('[1:10]')._process_scope_and_get_dimension('[1:10]')
            (1, '[1:10]')
            >>> _TDArray('[ 1 : 10 ]')._process_scope_and_get_dimension('[ 1 : 10 ]')
            (1, '[1:10]')
            >>> _TDArray('[2  ][  5  ]')._process_scope_and_get_dimension('[2  ][  5  ]')
            (2, '[2][5]')
            >>> _TDArray('[1:10][2:5][3:4]')._process_scope_and_get_dimension('[1:10][2:5][3:4]')
            (3, '[1:10][2:5][3:4]')
            >>> _TDArray('[1:10][2][4][5:6]')._process_scope_and_get_dimension('[1:10][2][4][5:6]')
            (4, '[1:10][2][4][5:6]')
            >>> _TDArray('[10][2  :5][3:4][6][8]')._process_scope_and_get_dimension('[10][2  :5][3:4][6][8]')
            (5, '[10][2:5][3:4][6][8]')
            >>> _TDArray('[-2: 1]')._process_scope_and_get_dimension('[-2: 1]')
            (1, '[-2:1]')
            >>> _TDArray('[-2 :1][-5:  -3]')._process_scope_and_get_dimension('[-2 :1][-5:  -3]')
            (2, '[-2:1][-5:-3]')
        """
        # Validate and determine the array dimension from the scope
        if not scope:
            raise ValueError("Array scope cannot be empty.")
        
        if not isinstance(scope, str):
            raise ValueError("Scope must be a string")
        
        # Remove all spaces to simplify regex pattern and processing
        normalized_scope = scope.replace(' ', '')
        
        # Regex pattern to match array scope format
        # Matches patterns like [n], [n:m], etc.
        pattern = r'^\[(-?\d+(?::-?\d+)?)\](\[(-?\d+(?::-?\d+)?)\])*$'

        if not re.match(pattern, normalized_scope):
            raise ValueError(f"Invalid scope format: '{scope}'. Expected format is '[n]', '[n:m]' or '[n:m][p:q]' etc.")
        
        # Extract all bracket pairs to determine dimension
        bracket_pairs = re.findall(r'\[([^\]]+)\]', normalized_scope)
        dimension = len(bracket_pairs)

        if dimension > 5:
            raise ValueError(f"Array dimension {dimension} is not supported. Teradata supports only 5 dimensions.")
        
        return dimension, normalized_scope
    
    def _generate_array_size_string(self):
        """
        DESCRIPTION:
            Generate the array size string from the scope by calculating actual sizes.
        
        PARAMETERS:
            None

        RETURNS:
            Array size string for UDT name generation.

        EXAMPLE:
            >>> _TDArray('[1:10]')._generate_array_size_string()
            '10'
            >>> _TDArray('[1:10][2:5]')._generate_array_size_string()
            '10_4'
            >>> _TDArray('[1][2][3]')._generate_array_size_string()
            '1_2_3'
            >>> _TDArray('[-2:1][-5:-3]')._generate_array_size_string()
            '4'
            >>> _TDArray('[-3]')._generate_array_size_string()
            '-3'
        """
        # Extract all bracket contents.
        bracket_contents = re.findall(r'\[\s*([^\]]+)\s*\]', self.scope)
        
        size_parts = []
        for content in bracket_contents:
            content = content.strip()
            if ':' in content:
                # Range format.
                start, end = content.split(':')
                size_parts.append(str(int(end) - int(start) + 1))
            else:
                # Single index.
                size_parts.append(content)
        
        return '_'.join(size_parts)
    
    @property
    def udt_name(self):
        """
        DESCRIPTION:
            Returns the UDT name for the array type instance.
            
        RETURNS:
            str: The UDT name.
        """
        # If UDT name was explicitly provided, use it. Else compute dynamically
        # based on the current array properties.
        if self._udt_name is not None:
            return self._udt_name
        return self._generate_udt_name()

    _get_udt_base = lambda self: (self.__class__.__name__.replace('ARRAY_', '').lower(), 
                                  self._generate_array_size_string(), "dn" if self.default_null else "dnn")

    _generate_udt_name = lambda self: "tdml_array_{}_{}_{}".format(*self._get_udt_base())

    def _generate_udt_name_interval(self):
        """
        Generate the UDT name for interval array types.
        
        This is a specialized implementation for interval arrays that includes
        the interval type in the UDT name.
        
        Returns:
            str: Generated UDT name
        """
        # Get the base UDT name parts
        interval_type, array_size, dn_dnn = self._get_udt_base()

        # Build UDT name parts
        udt_parts = [f"tdml_array_{interval_type}"]
        
        # Add precision
        if hasattr(self, 'precision'):
            udt_parts.append(str(self.precision))
        
        # Add fractional precision if exists
        if hasattr(self, 'frac_precision'):
            udt_parts.append(str(self.frac_precision))
        
        # Add size and default null suffix
        udt_parts.extend([array_size, dn_dnn])
        
        return '_'.join(udt_parts)
    
    def _generate_udt_create_sql(self):
        """
        DESCRIPTION:
            Generate the CREATE TYPE SQL string for this array type instance.

        PARAMETERS:
            None

        RETURNS:
            str: The SQL string to create the UDT for this array type.

        EXAMPLE:

            # Example 1: Single-dimensional array
            >>> arr = ARRAY_INTEGER('[10]')
            >>> arr._generate_udt_create_sql()
            'CREATE TYPE tdml_array_integer_10_dnn AS INTEGER ARRAY[10];'

            # Example 2: Multi-dimensional array
            >>> arr = ARRAY_INTEGER('[1:10][2:5]')
            >>> arr._generate_udt_create_sql()
            'CREATE TYPE tdml_array_integer_10_4_dnn AS INTEGER ARRAY[1:10][2:5];'

            # Example 3: Interval array
            >>> arr = ARRAY_INTERVAL_DAY_TO_HOUR('[1:3]', precision=2)
            >>> arr._generate_udt_create_sql()
            'CREATE TYPE tdml_array_interval_day_to_hour_2_3_dnn AS INTERVAL DAY(2) TO HOUR ARRAY[3];'

            # Example 4: Interval array with default null
            >>> arr = ARRAY_INTERVAL_DAY_TO_MINUTE('[3]', precision=2, default_null=True)
            >>> arr._generate_udt_create_sql()
            'CREATE TYPE tdml_array_interval_day_to_minute_2_3_dn AS INTERVAL DAY(2) TO MINUTE ARRAY[3] DEFAULT NULL;'

        """
        # Use the correct UDT name generator for intervals
        if self.__class__.__name__.startswith("ARRAY_INTERVAL_"):
            udt_name = self._generate_udt_name_interval()
        else:
            udt_name = self._generate_udt_name()

        default_null_sql = " DEFAULT NULL" if getattr(self, "default_null", False) else ""

        # For 1D arrays, use [size] instead of scope.
        if self.dimension == 1:
            size = self._generate_array_size_string()
            array_part = f'[{size}]'
        else:
            array_part = self.scope
        return f"CREATE TYPE {udt_name} AS {self._element_type_sql} ARRAY{array_part}{default_null_sql};"
    
    def bind_processor(self, dialect):
        """
        Processes the array value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the array value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process
    
    def get_col_spec(self):
        return self.udt_name
    
class INTEGER(_TDType, sqltypes.INTEGER):
    """ Teradata INTEGER type

    Represents a signed, binary integer value from -2,147,483,648 to
    2,147,483,647.

    """

    def __init__(self, **kwargs):

        """ Construct a INTEGER Object """
        super(INTEGER, self).__init__(**kwargs)


class SMALLINT(_TDType, sqltypes.SMALLINT):

    """ Teradata SMALLINT type

    Represents a signed binary integer value in the range -32768 to 32767.

    """

    def __init__(self, **kwargs):

        """ Construct a SMALLINT Object """
        super(SMALLINT, self).__init__(**kwargs)


class BIGINT(_TDType, sqltypes.BIGINT):

    """ Teradata BIGINT type

    Represents a signed, binary integer value from -9,223,372,036,854,775,808
    to 9,223,372,036,854,775,807.

    """

    def __init__(self, **kwargs):

        """ Construct a BIGINT Object """
        super(BIGINT, self).__init__(**kwargs)


class DECIMAL(_TDType, sqltypes.DECIMAL):

    """ Teradata DECIMAL type

    Represents a decimal number of n digits, with m of those n digits to the
    right of the decimal point.

    """

    def __init__(self, precision = 38, scale = 19, **kwargs):

        """ Construct a DECIMAL Object """
        super(DECIMAL, self).__init__(precision = precision, scale = scale, **kwargs)

    def literal_processor(self, dialect):

        def process(value):
            return str(value) + ('' if value.as_tuple()[2] < 0 else '.')
        return process


class BYTEINT(_TDType, sqltypes.Integer):

    """ Teradata BYTEINT type

    This type represents a one byte signed integer.

    """

    __visit_name__ = 'BYTEINT'

    def __init__(self, **kwargs):

        """ Construct a BYTEINT Object """
        super(BYTEINT, self).__init__(**kwargs)


class _TDBinary(_TDConcatenable, _TDType, sqltypes._Binary):

    """ Teradata Binary Types

    This type represents a Teradata binary string. Warns users when
    data may get truncated upon insertion.

    """

    class TruncationWarning(UserWarning):
        pass

    def _length(self):
        """Compute the length allocated to this binary column."""

        multiplier_map = {
            'K': 1024,
            'M': 1048576,
            'G': 1073741824
        }
        if hasattr(self, 'multiplier') and self.multiplier in multiplier_map:
            return self.length * multiplier_map[self.multiplier]

        return self.length

    def bind_processor(self, dialect):
        if dialect.dbapi is None:
            return None

        def process(value):
            bin_length = self._length()
            if value is not None and bin_length is not None:
                if len(value) > bin_length:
                    warnings.warn(
                        'Attempting to insert an item that is larger than the '
                        'space allocated for this column. Data may get truncated.',
                        self.TruncationWarning)
                return value
            else:
                return None
        return process


class BYTE(_TDBinary, sqltypes.BINARY):

    """ Teradata BYTE type

    This type represents a fixed-length binary string and is equivalent to
    the BINARY SQL standard type.

    """

    __visit_name__ = 'BYTE'

    def __init__(self, length=None, **kwargs):

        """ Construct a BYTE object

        :param length: Optional 1 to n. Specifies the number of bytes in the
        fixed-length binary string. The maximum value for n is 64000.

        """
        super(BYTE, self).__init__(length=length, **kwargs)

    def literal_processor(self, dialect):

        def process(value):

            try:

              # Python 3.5+
              return "'%s'XB" % value.hex()

            except AttributeError:

              # try it with codecs
              import codecs
              return "'%s'XB" % codecs.encode(value, 'hex').decode('utf-8')

        return process


class VARBYTE(_TDBinary, sqltypes.VARBINARY):

    """ Teradata VARBYTE type

    This type represents a variable-length binary string and is equivalent to
    the VARBINARY SQL standard type.

    """

    __visit_name__ = 'VARBYTE'

    def __init__(self, length=None, **kwargs):

        """ Construct a VARBYTE object

        :param length: Optional 1 to n. Specifies the number of bytes in the
        fixed-length binary string. The maximum value for n is 64000.

        """
        super(VARBYTE, self).__init__(length=length, **kwargs)


class BLOB(_TDBinary, sqltypes.BLOB):

    """ Teradata BLOB type

    This type represents a large binary string of raw bytes. A binary large
    object (BLOB) column can store binary objects, such as graphics, video
    clips, files, and documents.

    """

    def __init__(self, length=None, multiplier=None, **kwargs):

        """ Construct a BLOB object

        :param length: Optional 1 to n. Specifies the number of bytes allocated
        for the BLOB column. The maximum number of bytes is 2097088000, which
        is the default if n is not specified.

        :param multiplier: Optional value in ('K', 'M', 'G'). Indicates that the
        length parameter n is specified in kilobytes (KB), megabytes (Mb),
        or gigabytes (GB) respectively. Note the following constraints on n
        hold for each of the allowable multiplier:

            'K' is specified, n cannot exceed 2047937.
            'M' is specified, n cannot exceed 1999.
            'G' is specified, n must be 1.

        If multiplier is None, the length is interepreted as bytes (B).

        Note: If you specify a multiplier without specifying the length, the
              multiplier argument will simply get ignored. On the other hand,
              specifying a length without a multiplier will implicitly indicate
              that the length value should be interpreted as bytes (B).

        """
        super(BLOB, self).__init__(length=length, **kwargs)
        self.multiplier = multiplier


class FLOAT(_TDType, sqltypes.FLOAT):

    """ Teradata FLOAT type

    This type represent values in sign/magnitude form ranging from
    2.226 x 10^-308 to 1.797 x 10^308.

    """

    def __init__(self, **kwargs):

        """ Construct a FLOAT object """
        super(FLOAT, self).__init__(**kwargs)

    def literal_processor(self, dialect):

        def process(value):
            return 'CAST(%s as FLOAT)' % value
        return process


class NUMBER(_TDType, sqltypes.NUMERIC):

    """ Teradata NUMBER type

    This type represents a numeric value with optional precision and scale
    limitations.

    """

    __visit_name__ = 'NUMBER'

    def __init__(self, precision=None, scale=None, **kwargs):

        """ Construct a NUMBER object

        :param precision: max number of digits that can be stored. Valid values
        range from 1 to 38.

        :param scale: number of fractional digits of :param precision: to the
        right of the decimal point. Valid values range from 0 to
        :param precision:.

        Note: Both parameters are optional. When both are left unspecified,
              defaults to NUMBER with the system limits for precision and scale.

        """
        prec = None if precision is not None and precision < 0 else precision
        scale = None if scale is not None and scale < 0 else scale
        super(NUMBER, self).__init__(precision=prec, scale=scale, **kwargs)


class DATE(_TDType, sqltypes.DATE):

    """ Teradata DATE type

    Identifies a field as a DATE value and simplifies handling and formatting
    of date variables.

    """

    def __init__(self, **kwargs):

        """ Construct a DATE Object """
        super(DATE, self).__init__(**kwargs)

    def literal_processor(self, dialect):

        def process(value):
            return "DATE '%s'" % value
        return process


class TIME(_TDType, sqltypes.TIME):

    """ Teradata TIME type

    This type identifies a field as a TIME value.

    """

    def __init__(self, precision=6, timezone=False, **kwargs):

        """ Construct a TIME stored as UTC in Teradata

        :param precision: optional fractional seconds precision. A single digit
        representing the number of significant digits in the fractional
        portion of the SECOND field. Valid values range from 0 to 6 inclusive.
        The default precision is 6.

        :param timezone: If set to True creates a Time WITH TIME ZONE type

        """
        super(TIME, self).__init__(timezone=timezone, **kwargs)
        self.precision = precision

    def literal_processor(self, dialect):

        def process(value):
            return "TIME '%s'" % value
        return process


class TIMESTAMP(_TDType, sqltypes.TIMESTAMP):

    """ Teradata TIMESTAMP type

    This type identifies a field as a TIMESTAMP value.

    """

    def __init__(self, precision=6, timezone=False, **kwargs):
        """ Construct a TIMESTAMP stored as UTC in Teradata

        :param precision: optional fractional seconds precision. A single digit
        representing the number of significant digits in the fractional
        portion of the SECOND field. Valid values range from 0 to 6 inclusive.
        The default precision is 6.

        :param timezone: If set to True creates a TIMESTAMP WITH TIME ZONE type

        """
        super(TIMESTAMP, self).__init__(timezone=timezone, **kwargs)
        self.precision = precision

    def literal_processor(self, dialect):

        def process(value):
            return "TIMESTAMP '%s'" % value
        return process

    def get_dbapi_type(self, dbapi):
      return dbapi.DATETIME


class _TDInterval(_TDType, types.UserDefinedType):

    """ Base class for the Teradata INTERVAL sqltypes """

    def __init__(self, precision=None, frac_precision=None, **kwargs):
        self.precision      = precision
        self.frac_precision = frac_precision

    def bind_processor(self, dialect):

        """
        Processes the Interval value from SQLAlchemy to DB
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):

        """
        Processes the Interval value from DB to SQLAlchemy
        """
        def process(value):
            return value
        return process

    def literal_processor(self, dialect):

        def process(value):
            return "INTERVAL '%s' %s" % (value, value.type)
        return process

class INTERVAL_YEAR(_TDInterval):

    """ Teradata INTERVAL YEAR type

    This type identifies a field defining a period of time in years.

    """
    __visit_name__ = 'INTERVAL_YEAR'

    def __init__(self, precision=None, **kwargs):

       """ Construct an INTERVAL_YEAR object

       :param precision: permitted range of digits for year ranging from 1 to 4

       """
       super(INTERVAL_YEAR, self).__init__(precision=precision)

class INTERVAL_YEAR_TO_MONTH(_TDInterval):

    """ Teradata INTERVAL YEAR TO MONTH type

    This type identifies a field defining a period of time in years and months.

    """

    __visit_name__ = 'INTERVAL_YEAR_TO_MONTH'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_YEAR_TO_MONTH object

        :param precision: permitted range of digits for year ranging from 1 to 4

        """
        super(INTERVAL_YEAR_TO_MONTH, self).__init__(precision=precision)

class INTERVAL_MONTH(_TDInterval):

    """ Teradata INTERVAL MONTH type

    This type identifies a field defining a period of time in months.

    """

    __visit_name__ = 'INTERVAL_MONTH'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_MONTH object

        :param precision: permitted range of digits for month ranging from 1 to 4

        """
        super(INTERVAL_MONTH, self).__init__(precision=precision)

class INTERVAL_DAY(_TDInterval):

    """ Teradata INTERVAL DAY type

    This type identifies a field defining a period of time in days.

    """

    __visit_name__ = 'INTERVAL_DAY'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_DAY object

        :param precision: permitted range of digits for day ranging from 1 to 4

        """
        super(INTERVAL_DAY, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL DAY
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                value = td_dtypes.Interval(days=value.days)
#            return value
#        return process

class INTERVAL_DAY_TO_HOUR(_TDInterval):

    """ Teradata INTERVAL DAY TO HOUR type

    This type identifies a field defining a period of time in days and hours.

    """

    __visit_name__ = 'INTERVAL_DAY_TO_HOUR'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_DAY_TO_HOUR object

        :param precision: permitted range of digits for day ranging from 1 to 4

        """
        super(INTERVAL_DAY_TO_HOUR, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL DAY
#        TO HOUR
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                hours = int(value.seconds / 3600)
#                value = td_dtypes.Interval(days=value.days, hours=hours)
#            return value
#        return process

class INTERVAL_DAY_TO_MINUTE(_TDInterval):

    """ Teradata INTERVAL DAY TO MINUTE type

    This type identifies a field defining a period of time in days, hours,
    and minutes.

    """

    __visit_name__ = 'INTERVAL_DAY_TO_MINUTE'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_DAY_TO_MINUTE object

        :param precision: permitted range of digits for day ranging from 1 to 4

        """
        super(INTERVAL_DAY_TO_MINUTE, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL DAY
#        TO MINUTE
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                minutes = int(value.seconds / 60)
#                value   = td_dtypes.Interval(days=value.days, minutes=minutes)
#            return value
#        return process

class INTERVAL_DAY_TO_SECOND(_TDInterval):

    """ Teradata INTERVAL DAY TO SECOND type

    This type identifies a field during a period of time in days, hours, minutes,
    and seconds.

    """

    __visit_name__ = 'INTERVAL_DAY_TO_SECOND'

    def __init__(self, precision=None, frac_precision=None, **kwargs):

        """ Construct an INTERVAL_DAY_TO_SECOND object

        :param precision: permitted range of digits for day ranging from 1 to 4

        :param frac_precision: fracional_seconds_precision ranging from 0 to 6

        """
        super(INTERVAL_DAY_TO_SECOND, self).__init__(precision=precision,
                                                     frac_precision=frac_precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL DAY
#        TO SECOND
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                seconds = value.seconds + value.microseconds / 1000000
#                value   = td_dtypes.Interval(days=value.days, seconds=seconds)
#            return value
#        return process

class INTERVAL_HOUR(_TDInterval):

    """ Teradata INTERVAL HOUR type

    This type identifies a field defining a period of time in hours.

    """

    __visit_name__ = 'INTERVAL_HOUR'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_HOUR object

        :param precision: permitted range of digits for hour ranging from 1 to 4

        """
        super(INTERVAL_HOUR, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL HOUR
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                hours = int(value.total_seconds() / 3600)
#                value = td_dtypes.Interval(hours=hours)
#            return value
#        return process

class INTERVAL_HOUR_TO_MINUTE(_TDInterval):

    """ Teradata INTERVAL HOUR TO MINUTE type

    This type identifies a field defining a period of time in hours and minutes.

    """

    __visit_name__ = 'INTERVAL_HOUR_TO_MINUTE'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_HOUR_TO_MINUTE object

        :param precision: permitted range of digits for hour ranging from 1 to 4

        """
        super(INTERVAL_HOUR_TO_MINUTE, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL HOUR
#        TO MINUTE
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                hours, seconds = divmod(value.total_seconds(), 3600)
#                hours   = int(hours)
#                minutes = int(seconds / 60)
#                value   = td_dtypes.Interval(hours=hours, minutes=minutes)
#            return value
#        return process

class INTERVAL_HOUR_TO_SECOND(_TDInterval):

    """ Teradata INTERVAL HOUR TO SECOND type

    This type identifies a field defining a period of time in hours, minutes,
    and seconds.

    """

    __visit_name__ = 'INTERVAL_HOUR_TO_SECOND'

    def __init__(self, precision=None, frac_precision=None, **kwargs):

        """ Construct an INTERVAL_HOUR_TO_SECOND object

        :param precision: permitted range of digits for hour ranging from 1 to 4

        :param frac_precision: fracional_seconds_precision ranging from 0 to 6

        """
        super(INTERVAL_HOUR_TO_SECOND, self).__init__(precision=precision,
                                                      frac_precision=frac_precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL HOUR
#        TO SECOND
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                hours, seconds = divmod(value.total_seconds(), 3600)
#                hours   = int(hours)
#                seconds = int(seconds) + value.microseconds / 1000000
#                value   = td_dtypes.Interval(hours=hours, seconds=seconds)
#            return value
#        return process

class INTERVAL_MINUTE(_TDInterval):

    """ Teradata INTERVAL MINUTE type

    This type identifies a field defining a period of time in minutes.

    """

    __visit_name__ = 'INTERVAL_MINUTE'

    def __init__(self, precision=None, **kwargs):

        """ Construct an INTERVAL_MINUTE object

        :param precision: permitted range of digits for minute ranging from 1 to 4

        """
        super(INTERVAL_MINUTE, self).__init__(precision=precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL MINUTE
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                minutes = int(value.total_seconds() / 60)
#                value = td_dtypes.Interval(minutes=minutes)
#            return value
#        return process

class INTERVAL_MINUTE_TO_SECOND(_TDInterval):

    """ Teradata INTERVAL MINUTE TO SECOND type

    This type identifies a field defining a period of time in minutes and seconds.

    """

    __visit_name__ = 'INTERVAL_MINUTE_TO_SECOND'

    def __init__(self, precision=None, frac_precision=None, **kwargs):

        """ Construct an INTERVAL_MINUTE_TO_SECOND object

        :param precision: permitted range of digits for minute ranging from 1 to 4

        :param frac_precision: fracional_seconds_precision ranging from 0 to 6

        """
        super(INTERVAL_MINUTE_TO_SECOND, self).__init__(precision=precision,
                                                        frac_precision=frac_precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL MINUTE
#        TO SECOND
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                minutes, seconds = divmod(value.total_seconds(), 60)
#                minutes = int(minutes)
#                seconds = int(seconds) + value.microseconds / 1000000
#                value   = td_dtypes.Interval(minutes=minutes, seconds=seconds)
#            return value
#        return process

class INTERVAL_SECOND(_TDInterval):

    """ Teradata INTERVAL SECOND type

    This type identifies a field defining a period of time in seconds.

    """

    __visit_name__ = 'INTERVAL_SECOND'

    def __init__(self, precision=None, frac_precision=None, **kwargs):

        """ Construct an INTERVAL_SECOND object

        :param precision: permitted range of digits for second ranging from 1 to 4

        :param frac_precision: fractional_seconds_precision ranging from 0 to 6

        """
        super(INTERVAL_SECOND, self).__init__(precision=precision,
                                              frac_precision=frac_precision)

#    def bind_processor(self, dialect):
#
#        """
#        Handles the conversion from a datetime.timedelta object to an Interval
#        object appropriate for inserting into a column with type INTERVAL SECOND
#
#        """
#        def process(value):
#            if isinstance(value, datetime.timedelta):
#                seconds = value.total_seconds()
#                value = td_dtypes.Interval(seconds=seconds)
#            return value
#        return process


class _TDPeriod(_TDType, types.UserDefinedType):

    """ Base class for the Teradata Period sqltypes """

    def __init__(self, format=None, **kwargs):
        self.format = format

    def bind_processor(self, dialect):

        """
        Processes the Period value from SQLAlchemy to DB
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):

        """
        Processes the Period value from DB to SQLAlchemy
        """
        def process(value):
            return value
        return process

class PERIOD_DATE(_TDPeriod):

    """ Teradata PERIOD DATE type

    This type identifies a field defining a duration with a beginning and end date.

    """

    __visit_name__ = 'PERIOD_DATE'

    def __init__(self, format=None, **kwargs):

        """ Construct a PERIOD_DATE object

        :param format: format of the date, e.g. 'yyyy-mm-dd'

        """
        super(PERIOD_DATE, self).__init__(format=format, **kwargs)

class PERIOD_TIME(_TDPeriod):

    """ Teradata PERIOD TIME type

    This type identifies a field defining a duration with a beginning and end time.

    """

    __visit_name__ = 'PERIOD_TIME'

    def __init__(self, format=None, frac_precision=None, timezone=False, **kwargs):

        """ Construct a PERIOD_TIME object

        :param format: format of the time, e.g. 'HH:MI:SS.S(6)' and
        'HH:MI:SS.S(6)Z' (with timezone)

        :param frac_precision: fractional_seconds_precision ranging from 0 to 6

        :param timezone: true if WITH TIME ZONE, false otherwise

        """
        super(PERIOD_TIME, self).__init__(format=format, **kwargs)
        self.frac_precision = frac_precision
        self.timezone       = timezone

class PERIOD_TIMESTAMP(_TDPeriod):

    """ Teradata PERIOD TIMESTAMP type

    This type identifies a field defining a duration with a beginning and end timestamp.

    """

    __visit_name__ = 'PERIOD_TIMESTAMP'

    def __init__(self, format=None, frac_precision=None, timezone=False, **kwargs):

        """ Construct a PERIOD_TIMESTAMP object

        :param format: format of the timestamp, e.g. 'YYYY-MM-DDBHH:MI:SS.S(6)'
        and 'YYYY-MM-DDBHH:MI:SS.S(6)Z' (with timezone)

        :param frac_precision: fractional_seconds_precision ranging from 0 to 6

        :param timezone: true if WITH TIME ZONE, false otherwise

        """
        super(PERIOD_TIMESTAMP, self).__init__(format=format, **kwargs)
        self.frac_precision = frac_precision
        self.timezone       = timezone


class CHAR(_TDConcatenable, _TDType, sqltypes.CHAR):

    """ Teradata CHAR type

    This type represents a fixed-length character string for Teradata Database
    internal character storage.

    """

    def __init__(self, length=1, charset=None, **kwargs):

        """ Construct a CHAR object

        :param length: number of characters or bytes allocated. Maximum value
        for n depends on the character set. For LATIN - 64000 characters,
        For UNICODE - 32000 characters, For KANJISJIS - 32000 bytes. If a value
        for n is not specified, the default is 1.

        :param charset: Server character set for the character column.
        Supported values:
            'LATIN': fixed 8-bit characters from the ASCII ISO 8859 Latin1
            or ISO 8859 Latin9.
            'UNICODE': fixed 16-bit characters from the UNICODE 6.0 standard.
            'GRAPHIC': fixed 16-bit UNICODE characters defined by IBM for DB2.
            'KANJISJIS': mixed single byte/multibyte characters intended for
            Japanese applications that rely on KanjiShiftJIS characteristics.
        Note: GRAPHIC(n) is equivalent to CHAR(n) CHARACTER SET GRAPHIC

        """
        super(CHAR, self).__init__(length=length, **kwargs)
        self.charset = charset


class VARCHAR(_TDConcatenable, _TDType, sqltypes.VARCHAR):

    """ Teradata VARCHAR type

    This type represents a variable length character string of length 0 to n
    for Teradata Database internal character storage. LONG VARCHAR specifies
    the longest permissible variable length character string for Teradata
    Database internal character storage.

    """

    def __init__(self, length=None, charset=None, **kwargs):

        """ Construct a VARCHAR object

        :param length: Optional 0 to n. If None, LONG is used
        (the longest permissible variable length character string)

        :param charset: optional character set for varchar.

        Note: VARGRAPHIC(n) is equivalent to VARCHAR(n) CHARACTER SET GRAPHIC

        """
        super(VARCHAR, self).__init__(length=length, **kwargs)
        self.charset = charset


class CLOB(_TDConcatenable, _TDType, sqltypes.CLOB):

    """ Teradata CLOB type

    This type represents a large character string. A character large object
    (CLOB) column can store character data, such as simple text or HTML.

    """

    def __init__(self, length=None, charset=None, multiplier=None, **kwargs):

        """ Construct a CLOB object

        :param length: Optional length for clob. For Latin server character set,
        length cannot exceed 2097088000. For Unicode server character set,
        length cannot exceed 1048544000.
        If no length is specified then the maximum is used.

        :param multiplier: Either 'K', 'M', or 'G'.
        K specifies number of characters to allocate as nK, where K=1024
        (For Latin char sets, n < 2047937 and For Unicode char sets, n < 1023968)
        M specifies nM, where M=1024K
        (For Latin char sets, n < 1999 and For Unicode char sets, n < 999)
        G specifies nG, where G=1024M
        (For Latin char sets, n must be 1 and char set must be LATIN)

        :param charset: LATIN (fixed 8-bit characters ASCII ISO 8859 Latin1 or ISO 8859 Latin9)
        or UNICODE (fixed 16-bit characters from the UNICODE 6.0 standard)

        """
        super(CLOB, self).__init__(length=length, **kwargs)
        self.charset    = charset
        self.multiplier = multiplier

class XML(_TDType, types.UserDefinedType):

    """Class for the Teradata datatype XML """

    #maximum_length = 2097088000, inline_length = 4046

    __visit_name__ = "XML"

    def __init__(self, maximum_length=2097088000, inline_length=4046,
                 **kwargs):
        self.maximum_length = maximum_length
        self.inline_length = inline_length

    def bind_processor(self, dialect):

        """
        Processes the XML value from SQLAlchemy to DB
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):

        """
        Processes the XML value from DB to SQLAlchemy
        """
        def process(value):
            return value
        return process


class JSON(_TDType, types.UserDefinedType):

    """ Class for the Teradata JSON type """

    __visit_name__ = "JSON"

    def __init__(self, max_length=16776192, inline_length=64000, charset=None,
                 storage_format=None, **kwargs):
        """
        Constructor for JSON Data Type.

        PARAMETERS:
            max_length:
                Optional Argument.
                Specifies the maximum length of JSON type.
                Default Value: 16776192
                Type: int

            inline_length:
                Optional Argument.
                Specifies the inline storage size of JSON type.
                Default Value: 64000
                Type: int

            charset:
                Optional Argument.
                Specifies the character set for JSON type.
                Note:
                    This argument cannot be specified with storage_format. Teradata
                    databases throws error in that case.
                Default Value: None
                Type: str

            storage_format:
                Optional Argument.
                Specifies storage format for the JSON type.
                Note:
                    This argument cannot be specified with storage_format, Teradata
                    databases throws error in that case.
                Default Value: None
                Type: str

        RETURNS:
            Object of JSON() type.

        RAISES:
            None.
        """
        self.max_length = max_length
        self.inline_length = inline_length
        self.charset = charset
        self.storage_format = storage_format
        
    def bind_processor(self, dialect):
        """
        Processes the value from SQLAlchemy to database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the XML value from database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class TDUDT(_TDType, types.UserDefinedType):
    """Class for the Teradata User Defined types """

    __visit_name__ = "TDUDT"

    def __init__(self, type_name=None,  **kwargs):
        """
        Constructor for User Defined Types

        PARAMETERS:
            type_name:
                Optional Argument.
                Specifies the name of User Defined Type.
                Type: str

        RETURNS:
            Object of TDUDT().

        RAISES:
            None.
        """
        self.type_name = type_name

    def bind_processor(self, dialect):
        """
        Processes the  value from SQLAlchemy to DB
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the XML value from DB to SQLAlchemy
        """
        def process(value):
            return value
        return process

class GEOMETRY(_TDType, types.UserDefinedType):

    """ Class for the Teradata datatype ST_GEOMETRY """

    __visit_name__ = "GEOMETRY"

    def __init__(self, max_length=16776192, inline_length=9920,
                 **kwargs):
        """
        Constructor for GEOMETRY Data Type.

        PARAMETERS:
           maximum_length:
               Optional Argument.
               Specifies the maximum length of GEOMETRY type.
               Default Value: 16776192
               Type: int

           inline_length:
               Optional Argument.
               Specifies the inline storage size of GEOMETRY type.
               Default Value: 9920
               Type: int

        RETURNS:
           Object of GEOMETRY() type.

        RAISES:
           None.
        """
        self.max_length = max_length
        self.inline_length = inline_length

    def bind_processor(self, dialect):
        """
        Processes the GEOMETRY value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the GEOMETRY value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class MBR(_TDType, types.UserDefinedType):

    """ Class for the Teradata datatype MBR """

    __visit_name__ = "MBR"

    def bind_processor(self, dialect):
        """
        Processes the MBR value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the MBR value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class MBB(_TDType, types.UserDefinedType):

    """ Class for the Teradata datatype MBB """

    __visit_name__ = "MBB"

    def bind_processor(self, dialect):
        """
        Processes the MBB value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the MBB value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class VECTOR(_TDType, types.UserDefinedType):

    """ Class for the Teradata datatype VECTOR """

    __visit_name__ = "VECTOR"

    def bind_processor(self, dialect):
        """
        Processes the VECTOR value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the VECTOR value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class VECTOR32(_TDType, types.UserDefinedType):
    """
    Class for the Teradata datatype Vector32 (SYSUDTLIB.Vector32)

    This UDT supports Float32 embeddings up to 8192 dimensions.
    Accepts input as comma-separated float values in VARCHAR (max 64000),
    VARBYTE (max 64000), CLOB, or VECTOR formats.
    """
    __visit_name__ = "VECTOR32"
    def bind_processor(self, dialect):
        """
        Processes the VECTOR32 value from SQLAlchemy to Database.
        """
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        """
        Processes the VECTOR32 value from Database to SQLAlchemy.
        """
        def process(value):
            return value
        return process

class ARRAY_INTEGER(_TDArray):
    """Class for the Teradata ARRAY_INTEGER type"""

    __visit_name__ = "ARRAY_INTEGER"

    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_INTEGER Data Type.

        PARAMETERS:
           scope:
               Required Argument.
               Specifies the scope of the array.
               Type: str
            
           default_null:
               Optional Argument.
               Specifies whether the array type prepopulates the missing values
               with NULL or not. When set to True, missing values will be
               populated with NULL values. Else missing values will be undefined.
               Default Value: False
               Type: bool
           
           kwargs:
               Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "INTEGER"


class ARRAY_SMALLINT(_TDArray):
    """Class for the Teradata ARRAY_SMALLINT type"""

    __visit_name__ = "ARRAY_SMALLINT"
    
    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_SMALLINT Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "SMALLINT"

class ARRAY_BYTEINT(_TDArray):
    """Class for the Teradata ARRAY_BYTEINT type"""

    __visit_name__ = "ARRAY_BYTEINT"

    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_BYTEINT Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "BYTEINT"
    
class ARRAY_BIGINT(_TDArray):
    """Class for the Teradata ARRAY_BIGINT type"""

    __visit_name__ = "ARRAY_BIGINT"

    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_BIGINT Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "BIGINT"

class ARRAY_DATE(_TDArray):
    """Class for the Teradata ARRAY_DATE type"""

    __visit_name__ = "ARRAY_DATE"

    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_DATE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "DATE"
    
class ARRAY_TIME(_TDArray):
    """Class for the Teradata ARRAY_TIME type"""

    __visit_name__ = "ARRAY_TIME"

    def __init__(self, scope, default_null=False, precision=6, timezone=False, **kwargs):
        """
        Constructor for ARRAY_TIME Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the fractional seconds precision for TIME.
                Default Value: 6
                Type: int

            timezone:
                Optional Argument.
                If set to True, creates a TIME WITH TIME ZONE type.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.timezone = timezone
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_TIME"""
        array_size = self._generate_array_size_string()
        dn_dnn = "dn" if self.default_null else "dnn"
        tz_suffix = "tz" if self.timezone else "ntz"
        return f"tdml_array_time_{tz_suffix}_{self.precision}_{array_size}_{dn_dnn}"

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.timezone:
            return f"TIME({self.precision}) WITH TIME ZONE"
        else:
            return f"TIME({self.precision})"

class ARRAY_TIMESTAMP(_TDArray):
    """Class for the Teradata ARRAY_TIMESTAMP type"""

    __visit_name__ = "ARRAY_TIMESTAMP"

    def __init__(self, scope, default_null=False, precision=6, timezone=False, **kwargs):
        """
        Constructor for ARRAY_TIMESTAMP Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the fractional seconds precision for TIMESTAMP.
                Default Value: 6
                Type: int
                
            timezone:
                Optional Argument.
                If set to True, creates a TIMESTAMP WITH TIME ZONE type.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.timezone = timezone
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_TIMESTAMP"""
        array_size = self._generate_array_size_string()
        dn_dnn = "dn" if self.default_null else "dnn"
        tz_suffix = "tz" if self.timezone else "ntz"
        return f"tdml_array_timestamp_{tz_suffix}_{self.precision}_{array_size}_{dn_dnn}"

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.timezone:
            return f"TIMESTAMP({self.precision}) WITH TIME ZONE"
        else:
            return f"TIMESTAMP({self.precision})"

class ARRAY_INTERVAL_YEAR(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_YEAR type"""

    __visit_name__ = "ARRAY_INTERVAL_YEAR"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_YEAR Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
                
            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_YEAR"""
        return super()._generate_udt_name_interval()

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL YEAR({self.precision})"
        else:
            return "INTERVAL YEAR"

class ARRAY_INTERVAL_YEAR_TO_MONTH(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_YEAR_TO_MONTH type"""

    __visit_name__ = "ARRAY_INTERVAL_YEAR_TO_MONTH"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_YEAR_TO_MONTH Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
            
            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_YEAR_TO_MONTH"""
        return super()._generate_udt_name_interval()

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL YEAR({self.precision}) TO MONTH"
        else:
            return "INTERVAL YEAR TO MONTH"

class ARRAY_INTERVAL_MONTH(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_MONTH type"""

    __visit_name__ = "ARRAY_INTERVAL_MONTH"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_MONTH Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_MONTH"""
        return super()._generate_udt_name_interval()

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL MONTH({self.precision})"
        else:
            return "INTERVAL MONTH"

class ARRAY_INTERVAL_DAY(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_DAY type"""

    __visit_name__ = "ARRAY_INTERVAL_DAY"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_DAY Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str
                
            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int
                
            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_DAY"""
        return super()._generate_udt_name_interval()

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL DAY({self.precision})"
        else:
            return "INTERVAL DAY"

class ARRAY_INTERVAL_DAY_TO_HOUR(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_DAY_TO_HOUR type"""

    __visit_name__ = "ARRAY_INTERVAL_DAY_TO_HOUR"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_DAY_TO_HOUR Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str
            
            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
            
            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL DAY({self.precision}) TO HOUR"
        else:
            return "INTERVAL DAY TO HOUR"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_DAY_TO_HOUR"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_DAY_TO_MINUTE(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_DAY_TO_MINUTE type"""

    __visit_name__ = "ARRAY_INTERVAL_DAY_TO_MINUTE"

    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_DAY_TO_MINUTE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
                
            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL DAY({self.precision}) TO MINUTE"
        else:
            return "INTERVAL DAY TO MINUTE"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_DAY_TO_MINUTE"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_DAY_TO_SECOND(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_DAY_TO_SECOND type"""

    __visit_name__ = "ARRAY_INTERVAL_DAY_TO_SECOND"

    def __init__(self, scope, default_null=False, precision=None, frac_precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_DAY_TO_SECOND Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the interval leading field precision.
                Type: int

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision.
                Type: int
            
            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.frac_precision = frac_precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        # Consider all combinations of precision and frac_precision
        prec = f"({self.precision})" if self.precision is not None else ""
        frac_prec = f"({self.frac_precision})" if self.frac_precision is not None else ""
        return f"INTERVAL DAY{prec} TO SECOND{frac_prec}"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_DAY_TO_SECOND"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_HOUR(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_HOUR type"""

    __visit_name__ = "ARRAY_INTERVAL_HOUR"
    
    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_HOUR Data Type.
        
        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL HOUR type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL HOUR({self.precision})"
        else:
            return "INTERVAL HOUR"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_HOUR"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_HOUR_TO_MINUTE(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_HOUR_TO_MINUTE type"""

    __visit_name__ = "ARRAY_INTERVAL_HOUR_TO_MINUTE"
    
    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_HOUR_TO_MINUTE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL HOUR TO MINUTE type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL HOUR({self.precision}) TO MINUTE"
        else:
            return "INTERVAL HOUR TO MINUTE"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_HOUR_TO_MINUTE"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_HOUR_TO_SECOND(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_HOUR_TO_SECOND type"""

    __visit_name__ = "ARRAY_INTERVAL_HOUR_TO_SECOND"
    
    def __init__(self, scope, default_null=False, precision=None, frac_precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_HOUR_TO_SECOND Data Type.
        
        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL HOUR TO SECOND type.
                Type: int

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision for INTERVAL HOUR TO SECOND.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.frac_precision = frac_precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        # Consider all combinations of precision and frac_precision
        prec = f"({self.precision})" if self.precision is not None else ""
        frac_prec = f"({self.frac_precision})" if self.frac_precision is not None else ""
        return f"INTERVAL HOUR{prec} TO SECOND{frac_prec}"
        
    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_HOUR_TO_SECOND"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_MINUTE(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_MINUTE type"""

    __visit_name__ = "ARRAY_INTERVAL_MINUTE"
    
    def __init__(self, scope, default_null=False, precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_MINUTE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL MINUTE type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None:
            return f"INTERVAL MINUTE({self.precision})"
        else:
            return "INTERVAL MINUTE"
    
    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_MINUTE"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_MINUTE_TO_SECOND(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_MINUTE_TO_SECOND type"""

    __visit_name__ = "ARRAY_INTERVAL_MINUTE_TO_SECOND"
    
    def __init__(self, scope, default_null=False, precision=None, frac_precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_MINUTE_TO_SECOND Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL MINUTE TO SECOND type.
                Type: int

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision for INTERVAL MINUTE TO SECOND.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.frac_precision = frac_precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        # Consider all combinations of precision and frac_precision
        prec = f"({self.precision})" if self.precision is not None else ""
        frac_prec = f"({self.frac_precision})" if self.frac_precision is not None else ""
        return f"INTERVAL MINUTE{prec} TO SECOND{frac_prec}"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_MINUTE_TO_SECOND"""
        return super()._generate_udt_name_interval()

class ARRAY_INTERVAL_SECOND(_TDArray):
    """Class for the Teradata ARRAY_INTERVAL_SECOND type"""

    __visit_name__ = "ARRAY_INTERVAL_SECOND"

    def __init__(self, scope, default_null=False, precision=None, frac_precision=None, **kwargs):
        """
        Constructor for ARRAY_INTERVAL_SECOND Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the INTERVAL SECOND type.
                Type: int

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision for INTERVAL SECOND.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.frac_precision = frac_precision
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        # Consider all combinations of precision and frac_precision
        if self.precision is not None and self.frac_precision is not None:
            return f"INTERVAL SECOND({self.precision}, {self.frac_precision})"
        elif self.precision is not None:
            return f"INTERVAL SECOND({self.precision})"
        else:
            return "INTERVAL SECOND"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_INTERVAL_SECOND"""
        return super()._generate_udt_name_interval()

class ARRAY_FLOAT(_TDArray):
    """Class for the Teradata ARRAY_FLOAT type"""

    __visit_name__ = "ARRAY_FLOAT"
    
    def __init__(self, scope, default_null=False, **kwargs):
        """
        Constructor for ARRAY_FLOAT Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return "FLOAT"

class ARRAY_DECIMAL(_TDArray):
    """Class for the Teradata ARRAY_DECIMAL type"""

    __visit_name__ = "ARRAY_DECIMAL"

    def __init__(self, scope, default_null=False, precision=38, scale=19, **kwargs):
        """
        Constructor for ARRAY_DECIMAL Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            precision:
                Optional Argument.
                Specifies the precision for the DECIMAL type.
                Default Value: 38
                Type: int

            scale:
                Optional Argument.
                Specifies the scale for the DECIMAL type.
                Default Value: 19
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.scale = scale
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        return f"DECIMAL({self.precision},{self.scale})"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_DECIMAL"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_decimal_{self.precision}_{self.scale}_{array_size}_{dn_dnn}"

class ARRAY_CHAR(_TDArray):
    """Class for the Teradata ARRAY_CHAR type"""

    __visit_name__ = "ARRAY_CHAR"

    def __init__(self, scope, default_null=False, length=1, charset=None, **kwargs):
        """
        Constructor for ARRAY_CHAR Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            length:
                Optional Argument.
                Specifies the length for the CHAR type.
                Default Value: 1
                Type: int

            charset:
                Optional Argument.
                Specifies the character set for the CHAR type.
                Type: str

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.length = length
        self.charset = charset
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.charset:
            return f"CHAR({self.length}) CHARACTER SET {self.charset}"
        else:
            return f"CHAR({self.length})"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_CHAR"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_char_{self.charset}_{self.length}_{array_size}_{dn_dnn}"

class ARRAY_BYTE(_TDArray):
    """Class for the Teradata ARRAY_BYTE type"""

    __visit_name__ = "ARRAY_BYTE"

    def __init__(self, scope, default_null=False, length=None, **kwargs):
        """
        Constructor for ARRAY_BYTE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
            
            length:
                Optional Argument.
                Specifies the length for the BYTE type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.length = length
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.length is not None:
            return f"BYTE({self.length})"
        else:
            return "BYTE"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_BYTE"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_byte_{self.length}_{array_size}_{dn_dnn}"

class ARRAY_VARCHAR(_TDArray):
    """Class for the Teradata ARRAY_VARCHAR type"""

    __visit_name__ = "ARRAY_VARCHAR"

    def __init__(self, scope, default_null=False, length=100, charset=None, **kwargs):
        """
        Constructor for ARRAY_VARCHAR Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            length:
                Optional Argument.
                Specifies the length for the VARCHAR type.
                Default Value: 100
                Type: int

            charset:
                Optional Argument.
                Specifies the character set for the VARCHAR type.
                Type: str

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.length = length
        self.charset = charset
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.charset:
            return f"VARCHAR({self.length}) CHARACTER SET {self.charset}"
        else:
            return f"VARCHAR({self.length})"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_VARCHAR"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_varchar_{self.charset}_{self.length}_{array_size}_{dn_dnn}"

class ARRAY_VARBYTE(_TDArray):
    """Class for the Teradata ARRAY_VARBYTE type"""

    __visit_name__ = "ARRAY_VARBYTE"

    def __init__(self, scope, default_null=False, length=None, **kwargs):
        """
        Constructor for ARRAY_VARBYTE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            length:
                Optional Argument.
                Specifies the length for the VARBYTE type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        
        self.default_null = default_null
        self.length = length
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.length is not None:
            return f"VARBYTE({self.length})"
        else:
            return "VARBYTE"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_VARBYTE"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_varbyte_{self.length}_{array_size}_{dn_dnn}"

class ARRAY_NUMBER(_TDArray):
    """Class for the Teradata ARRAY_NUMBER type"""

    __visit_name__ = "ARRAY_NUMBER"
    
    def __init__(self, scope, default_null=False, precision=None, scale=None, **kwargs):
        """
        Constructor for ARRAY_NUMBER Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
            
            precision:
                Optional Argument.
                Specifies the precision for the NUMBER type.
                Type: int
            
            scale:
                Optional Argument.
                Specifies the scale for the NUMBER type.
                Type: int

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.precision = precision
        self.scale = scale
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.precision is not None and self.scale is not None:
            return f"NUMBER({self.precision},{self.scale})"
        elif self.precision is not None:
            return f"NUMBER({self.precision})"
        else:
            return "NUMBER"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_NUMBER"""
        _, array_size, dn_dnn = self._get_udt_base()
        return f"tdml_array_number_{self.precision}_{self.scale}_{array_size}_{dn_dnn}"

class ARRAY_PERIOD_DATE(_TDArray):
    """Class for the Teradata ARRAY_PERIOD_DATE type"""

    __visit_name__ = "ARRAY_PERIOD_DATE"
    
    def __init__(self, scope, default_null=False, format=None, **kwargs):
        """
        Constructor for ARRAY_PERIOD_DATE Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool
            
            format:
                Optional Argument.
                Specifies the format for the DATE type.
                Type: str

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.format = format
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        if self.format:
            return f"PERIOD(DATE) FORMAT '{self.format}'"
        else:
            return "PERIOD(DATE)"

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_PERIOD_DATE"""
        _, array_size, dn_dnn = self._get_udt_base()
        # Replace special characters with underscores for UDT name
        format_str = self.format.replace('-', '_').replace(':', '_').replace(' ', '_') if self.format else ""
        return f"tdml_array_period_date_{format_str}_{array_size}_{dn_dnn}"

class ARRAY_PERIOD_TIME(_TDArray):
    """Class for the Teradata ARRAY_PERIOD_TIME type"""

    __visit_name__ = "ARRAY_PERIOD_TIME"

    def __init__(self, scope, default_null=False, format=None, frac_precision=None, timezone=False, **kwargs):
        """
        Constructor for ARRAY_PERIOD_TIME Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            format:
                Optional Argument.
                Specifies the format for the TIME type.
                Type: str

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision for TIME.
                Type: int

            timezone:
                Optional Argument.
                Specifies whether the TIME type includes a timezone.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """
        self.default_null = default_null
        self.format = format
        self.frac_precision = frac_precision
        self.timezone = timezone
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        base = f"PERIOD(TIME({self.frac_precision})" if self.frac_precision is not None else "PERIOD(TIME"
        base += " WITH TIME ZONE" if self.timezone else ""
        base += ")"
        base += f" FORMAT '{self.format}'" if self.format else ""
        return base

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_PERIOD_TIME"""
        _, array_size, dn_dnn = self._get_udt_base()
        # Replace special characters with underscores for UDT name
        format_str = self.format.replace('-', '_').replace(':', '_').replace(' ', '_') if self.format else ""
        # Combine format and frac_precision with _
        format_frac = f"{format_str}_{self.frac_precision}"
        return f"tdml_array_period_time_{format_frac}_{array_size}_{dn_dnn}"

class ARRAY_PERIOD_TIMESTAMP(_TDArray):
    """Class for the Teradata ARRAY_PERIOD_TIMESTAMP type"""

    __visit_name__ = "ARRAY_PERIOD_TIMESTAMP"
    
    def __init__(self, scope, default_null=False, format=None, frac_precision=None, timezone=False, **kwargs):
        """
        Constructor for ARRAY_PERIOD_TIMESTAMP Data Type.

        PARAMETERS:
            scope:
                Required Argument.
                Specifies the scope of the array.
                Type: str

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values
                with NULL or not. When set to True, missing values will be
                populated with NULL values. Else missing values will be undefined.
                Default Value: False
                Type: bool

            format:
                Optional Argument.
                Specifies the format for the TIMESTAMP type.
                Type: str

            frac_precision:
                Optional Argument.
                Specifies the fractional seconds precision for TIMESTAMP.
                Type: int

            timezone:
                Optional Argument.
                Specifies whether the TIMESTAMP type includes a timezone.
                Default Value: False
                Type: bool

            kwargs:
                Additional keyword arguments.
        """

        self.default_null = default_null
        self.format = format
        self.frac_precision = frac_precision
        self.timezone = timezone
        super().__init__(scope, **kwargs)

    @property
    def _element_type_sql(self):
        """Returns the SQL string for the element type of this ARRAY."""
        base = "PERIOD(TIMESTAMP"
        if self.frac_precision is not None:
            base += f"({self.frac_precision})"
        if self.timezone:
            base += " WITH TIME ZONE"
        base += ")"
        if self.format:
            base += f" FORMAT '{self.format}'"
        return base

    def _generate_udt_name(self):
        """Generate UDT name for ARRAY_PERIOD_TIMESTAMP"""
        _, array_size, dn_dnn = self._get_udt_base()
        # Replace special characters with underscores for UDT name
        format_str = self.format.replace('-', '_').replace(':', '_').replace(' ', '_') if self.format else ""
        # Combine format and frac_precision with _
        format_frac = f"{format_str}_{self.frac_precision}"
        return f"tdml_array_period_timestamp_{format_frac}_{array_size}_{dn_dnn}"

class TeradataExpressionAdapter:
    """Expression Adapter for Teradata Data Types.

    For inferring the resulting type of a BinaryExpression whose operation
    involves operands that are of Teradata types.
    """

    def process(self, type_, op=None, other=None, **kw):
        """Adapts the expression.

        Infer the type of the resultant BinaryExpression defined by the passed
        in operator and operands. This resulting type should be consistent with
        the Teradata database when the operation is defined.

        Args:
            type_: The type instance of the left operand.

            op:    The operator of the BinaryExpression.

            other: The type instance of the right operand.

        Returns:
            The type to adapt the BinaryExpression to.
        """

        if isinstance(type_, _TDInterval) or isinstance(other, _TDInterval):
            adapt_strategy = _IntervalRuleStrategy()
        else:
            adapt_strategy = _LookupStrategy()

        return adapt_strategy.adapt(type_, op, other, **kw)


class _AdaptStrategy:
    """Interface for expression adaptation strategies."""

    def adapt(self, type_, op, other, **kw):
        """Adapt the expression according to some strategy.

        Given the type of the left and right operand, and the operator, produce
        a resulting type class for the BinaryExpression.
        """

        raise NotImplementedError()

class _IntervalRuleStrategy(_AdaptStrategy):
    """Expression adaptation strategy which follows a set of rules for inferring
    Teradata Interval types.
    """

    ordering = ('YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND')

    def adapt(self, type_, op, other, **kw):
        """Adapt the expression by a set of predefined rules over the Teradata
        Interval types.
        """

        # If the (Interval) types are equal, simply return the class of
        # those types
        if type_.__class__ == other.__class__:
            return type_.__class__

        # If the (Interval) types are not equal, return the valid Interval type
        # with the greatest range.
        #
        # E.g. INTERVAL YEAR TO MONTH and INTERVAL DAY TO HOUR -->
        #      INTERVAL YEAR TO HOUR.
        #
        # Otherwise if the resulting Interval type is invalid, return NullType.
        #
        # E.g. INTERVAL YEAR TO MONTH and INTERVAL MINUTE TO SECOND -->
        #      INTERVAL YEAR TO SECOND (invalid) -->
        #      NullType
        elif isinstance(type_, _TDInterval) and isinstance(other, _TDInterval):
            tokens = self._tokenize_name(type_.__class__.__name__) + \
                     self._tokenize_name(other.__class__.__name__)
            tokens.sort(key=lambda tok: self.ordering.index(tok))

            return getattr(sys.modules[__name__],
                self._combine_tokens(tokens[0], tokens[-1]),
                sqltypes.NullType)()

        # Else the binary expression has an Interval and non-Interval operand.
        # If the non-Interval operand is a Date, Time, or Datetime, return that
        # type, otherwise return the Interval type.
        else:
            interval, non_interval = (type_, other) if \
                    isinstance(type_, _TDInterval) \
                else (other, type_)

            return non_interval.__class__ if \
                    isinstance(non_interval, (sqltypes.Date,
                                              sqltypes.Time,
                                              sqltypes.DateTime)) \
                else interval.__class__

    def _tokenize_name(self, interval_name):
        """Tokenize the name of Interval types.

        Returns a list of (str) tokens of the corresponding Interval type name.

        E.g. 'INTERVAL_DAY_TO_HOUR' --> ['DAY', 'HOUR'].
        """

        return list(filter(lambda tok: tok not in ('INTERVAL', 'TO'),
                           interval_name.split('_')))

    def _combine_tokens(self, tok_l, tok_r):
        """Combine the tokens of an Interval type to form its name.

        Returns a string for the name of the Interval type corresponding to the
        tokens passed in.

        E.g. tok_l='DAY' and tok_r='HOUR' --> 'INTERVAL_DAY_TO_HOUR'
        """

        return 'INTERVAL_%s_TO_%s' % (tok_l, tok_r)

class _LookupStrategy(_AdaptStrategy):
    """Expression adaptation strategy which employs a general lookup table."""

    def adapt(self, type_, op, other, **kw):
        """Adapt the expression by looking up a hardcoded table.

        The lookup table is defined as `visit_` methods below. Each method
        returns a nested dictionary which is keyed by the operator and the other
        operand's type.
        """

        return getattr(self, self._process_visit_name(type_.__visit_name__),
                   lambda *args, **kw: {})(type_, other, **kw) \
            .get(op, util.immutabledict()) \
            .get(other.__class__, type_.__class__)

    def _process_visit_name(self, visit_name):
        """Generate the corresponding visit function name from a type's
        __visit_name__ field.
        """

        prefix = 'visit_'
        return prefix + visit_name

    def _flatten_tuple_keyed_dict(self, tuple_dict):
        """Recursively flatten a dictionary with (many-to-one) tuple keys to a
        standard one.
        """

        flat_dict = {}
        for ks, v in tuple_dict.items():
            v = self._flatten_tuple_keyed_dict(v) if isinstance(v, dict) else v
            if isinstance(ks, tuple):
                for k in ks:
                    flat_dict[k] = v
            else:
                flat_dict[ks] = v
        return flat_dict

    def visit_INTEGER(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:  BIGINT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER,
                DATE:    DATE
            },
            (operators.sub, operators.mul, operators.truediv,
             operators.mod): {
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:  BIGINT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER
            }
        })

    def visit_SMALLINT(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (INTEGER, SMALLINT, BYTEINT): INTEGER,
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:  BIGINT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER,
                DATE:    DATE
            },
            (operators.sub, operators.mul, operators.truediv,
             operators.mod): {
                (INTEGER, SMALLINT, BYTEINT, DATE): INTEGER,
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:  BIGINT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER,
            }
        })

    def visit_BIGINT(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER,
                DATE:    DATE
            },
            (operators.sub, operators.mul, operators.truediv,
             operators.mod): {
                (CHAR, VARCHAR, BLOB): FLOAT,
                DECIMAL: DECIMAL,
                FLOAT:   FLOAT,
                NUMBER:  NUMBER
            }
        })

    def visit_DECIMAL(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                FLOAT:  FLOAT,
                NUMBER: NUMBER,
                DATE:   DATE
            },
            (operators.sub, operators.mul, operators.truediv,
             operators.mod): {
                (CHAR, VARCHAR, BLOB): FLOAT,
                FLOAT:  FLOAT,
                NUMBER: NUMBER
            }
        })

    def visit_DATE(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                DATE:  INTEGER,
                FLOAT: FLOAT
            },
            operators.sub: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                DATE:  INTEGER,
                FLOAT: FLOAT
            },
            (operators.mul, operators.truediv, operators.mod): {
                (DATE, INTEGER, SMALLINT, BYTEINT): INTEGER,
                (CHAR, VARCHAR, BLOB): FLOAT,
                (FLOAT, TIME): FLOAT,
                BIGINT:  BIGINT,
                DECIMAL: DECIMAL,
                NUMBER:  NUMBER,
            }
        })

    def visit_TIME(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            (operators.add, operators.mul, operators.truediv,
             operators.mod): {
                DATE: FLOAT
            }
        })

    def visit_CHAR(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.concat_op: {
                CHAR:    VARCHAR if hasattr(other, 'charset') and \
                            ((type_.charset == 'unicode') !=
                             (other.charset == 'unicode'))
                         else CHAR,
                VARCHAR: VARCHAR,
                CLOB:    CLOB
            },
            (operators.add, operators.sub, operators.mul,
             operators.truediv, operators.mod): {
                (INTEGER, SMALLINT, BIGINT, BYTEINT, NUMBER, FLOAT, DECIMAL,
                 DATE, CHAR, VARCHAR): FLOAT
            }
        })

    def visit_VARCHAR(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.concat_op: {
                CLOB: CLOB
            },
            (operators.add, operators.sub, operators.mul,
             operators.truediv, operators.mod): {
                (INTEGER, SMALLINT, BIGINT, BYTEINT, NUMBER, FLOAT, DECIMAL,
                 DATE, CHAR, VARCHAR): FLOAT
            }
        })

    def visit_BYTEINT(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            (operators.add, operators.sub): {
                (INTEGER, SMALLINT, BYTEINT): INTEGER,
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:   BIGINT,
                DECIMAL:  DECIMAL,
                FLOAT:    FLOAT,
                NUMBER:   NUMBER,
                DATE:     DATE
            },
            (operators.mul, operators.truediv, operators.mod): {
                (INTEGER, SMALLINT, BYTEINT, DATE): INTEGER,
                (CHAR, VARCHAR, BLOB): FLOAT,
                BIGINT:   BIGINT,
                DECIMAL:  DECIMAL,
                FLOAT:    FLOAT,
                NUMBER:   NUMBER
            }
        })

    def visit_BYTE(self, type_, other, **kw):
        return {
            operators.concat_op: {
                VARBYTE: VARBYTE,
                BLOB:    BLOB
            }
        }

    def visit_VARBYTE(self, type_, other, **kw):
        return {
            operators.concat_op: {
                BLOB: BLOB
            }
        }

    def visit_NUMBER(self, type_, other, **kw):
        return self._flatten_tuple_keyed_dict({
            operators.add: {
                (CHAR, VARCHAR, BLOB): FLOAT,
                FLOAT: FLOAT,
                DATE:  DATE
            },
            (operators.sub, operators.mul, operators.truediv,
             operators.mod): {
                (CHAR, VARCHAR, BLOB): FLOAT,
                FLOAT: FLOAT
            }
        })
