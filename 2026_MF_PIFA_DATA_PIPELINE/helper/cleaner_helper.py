import pandas as pd
from decimal import Decimal, InvalidOperation

def _clean_value(value, default = None):

    """Returns None if value is null-like, otherwise returns cleaned value."""

    """ In-depth Function Explanation
    The _clean_value function standardizes a single value by converting empty,
    missing, and null-like values to None.

    Parameters:
        - value: Any Python object, typically a value extracted from a pandas
        DataFrame.

    How it works:
        1. The function first checks whether the value is considered missing
        using pandas.isna().

        2. pandas.isna() returns True for values such as:
            - None
            - numpy.nan
            - pandas.NA
            - NaT

        3. If the value is missing, the function immediately returns None.

        4. If the value is a string, leading and trailing whitespace is removed
        using the .strip() method.
        For example:
            '  hello  ' -> 'hello'
            '   '       -> ''

        5. The cleaned string is converted to lowercase and compared against
        the NULL_STRINGS set, which contains text representations of missing
        values.
        Common examples include:
            - ''
            - 'n/a'
            - 'na'
            - 'none'
            - 'null'

        6. If the cleaned string matches one of the entries in NULL_STRINGS,
        the function returns None.

        7. Otherwise, the cleaned string is returned.

        8. If the value is neither missing nor a string (e.g., an integer,
        float, or datetime object), the original value is returned unchanged.

    Example:
        _clean_value('  N/A  ')   -> None
        _clean_value('  Hello ')  -> 'Hello'
        _clean_value(123)         -> 123
        _clean_value(float('nan')) -> None

    This function ensures that all null-like values are represented
    consistently as None throughout the project.
    """
    
    NULL_STRINGS = {'nan', 'none', 'n/a', 'null', '', '-'}

    if pd.isna(value):
        return default
    if isinstance(value, str):
        stripped = " ".join(value.strip().split())
        return default if stripped.lower() in NULL_STRINGS else stripped
    return value

def _clean_dtype(value, dtype, default = None):
    """
    Strips and replaces commas "," with "".

    Once successfully cleaned, the value is put into a speific dtype.
    
    Instead of crashing the program, ValueError and TypeError are tirggered and will lead to default

    """
    if pd.isna(value):
        return default
    
    try:
        if isinstance(value, str):
            value = value.strip().replace(",", "")

            if value == "":
                return default

        return dtype(value)
    
    except (ValueError, TypeError):
        return default

def to_float(value):
    """
    Convert Excel-style numeric values to Decimal.
    Handles commas, blanks, dashes, and parentheses for negatives.
    Example: '(27,906,986)' becomes Decimal('-27906986')
    """
    if pd.isna(value):
        return None

    if isinstance(value, float):
        return value

    text = str(value).strip()

    if text in ("", "-", "–", ):
        return None

    if text.startswith("#"):
        return None

    is_negative = text.startswith("(") and text.endswith(")")

    text = text.replace(",", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.strip()

    try:
        number = float(text)
    except InvalidOperation:
        return None

    if is_negative:
        number = -number

    return number
    
def to_int(value):
    """
    Call on to_float first then converts results into integer

    """

    number = to_float(value)

    if number is None:
        return None

    return int(number)

def _cast_all(matrix, dtype, default = None):
    """Casts all values in a matrix to `dtype`. None-safe."""
    return [[
        _clean_dtype(cell, dtype, default)
        for cell in row
    ]
        for row in matrix
    ]