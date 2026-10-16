import glob, os
import pandas
from openpyxl.utils import column_index_from_string
from .cleaner_helper import _clean_value, to_float, to_int
from decimal import Decimal, InvalidOperation
from datetime import date
from .date_helper import get_month_end_date


class PandasMeta(type):
    """Metaclass that forwards missing attribute access to the pandas module."""

    def __getattr__(cls, name):
        return getattr(pandas, name)


class pd(metaclass=PandasMeta):
    """Lightweight pandas shim that delegates all operations to the pandas module."""

    @staticmethod
    def DataFrame(*args, **kwargs):
        return pandas.DataFrame(*args, **kwargs)

    @staticmethod
    def read_excel(*args, **kwargs):
        return pandas.read_excel(*args, **kwargs)

    @staticmethod
    def concat(*args, **kwargs):
        return pandas.concat(*args, **kwargs)

    @staticmethod
    def to_datetime(*args, **kwargs):
        return pandas.to_datetime(*args, **kwargs)

    @staticmethod
    def isna(*args, **kwargs):
        return pandas.isna(*args, **kwargs)

    @staticmethod
    def isnull(*args, **kwargs):
        return pandas.isnull(*args, **kwargs)


def collect_excel_files() -> list[str]:
    """Checks whether the landing directory exists, then finds and lists the Excel files inside it.
    """
    
    landing_path: str = "../landing"
    excel_files: list[str] = []

    if not os.path.isdir(landing_path):
        raise FileNotFoundError("Landing directory does not exist.")

    else: #compiles a sorted list of the file paths (as strings) that are of the form ../landing/*.xls or ../landing/*.xlsx, where * is a placeholder.
        excel_files: list[str] = sorted(
            file_path
            for pattern in ["*.xls", "*.xlsx"]
            for file_path in glob.glob(os.path.join(landing_path, pattern))
            if not os.path.basename(file_path).startswith("~$") #list does not include temporary files (i.e. files starting w/ ~$)
        )

        if not excel_files:
            raise FileNotFoundError(f"No Excel files found in {landing_path} directory.")

        else:
            print(f"Found {len(excel_files)} Excel file(s).\n")

            for index, file_path in enumerate(excel_files, start = 1):
                print(f"[{index}] {os.path.basename(file_path)}")
            
    return excel_files

def getCellValue(sheet: pandas.DataFrame, col: str, row: int):
        
    """ Function Summary
    Returns the cleaned cell value at the given Excel-style column letter and 1-based row index.
    The _clean_value(value) returns None if the value is empty, whitespace, or a null-like string.
    """

    """ In-depth Function Explanation
    The getCellValue function retrieves a value from a pandas DataFrame using
    Excel-style coordinates.

    Parameters:
        - dataframe: A pandas DataFrame representing a worksheet from an Excel file.
        - col: The Excel column reference as a letter (e.g., 'A', 'B', 'AA').
        - row: The Excel row number using one-based indexing.

    How it works:
        1. The column_index_from_string function from openpyxl.utils converts
        the Excel column letter into its corresponding one-based numeric index.
        For example:
            'A'  -> 1
            'B'  -> 2
            'AA' -> 27

        2. The DataFrame is accessed using pandas .iloc, which uses zero-based
        indexing. Therefore:
            - row - 1 converts the Excel row number to a zero-based index.
            - column_index - 1 converts the Excel column number to a zero-based index.

        3. The extracted value is passed to _clean_value(), which standardizes
        empty cells, whitespace, and null-like strings by converting them to None.

    Example:
        getCellValue(df, 'C', 5)

    This returns the cleaned value found in cell C5 of the Excel worksheet.
    """

    value = sheet.iloc[row - 1, column_index_from_string(col) - 1]

    return _clean_value(value)

def getMatrixData(dataframe: pandas.DataFrame, start_col: str, start_row: int, end_col: str, end_row: int):
    
    """ Function Summary
    Returns a matrix (list of lists) of cleaned values from the given Excel-style range.
    """
    
    """ In-depth Function Explanation
    The getMatrixData function retrieves a rectangular range of values from a
    pandas DataFrame using Excel-style coordinates and returns the result as a
    matrix (a list of lists).

    Parameters:
        - dataframe: A pandas DataFrame representing a worksheet from an Excel file.
        - start_col: The Excel column letter where the range begins.
        - start_row: The Excel row number where the range begins (one-based).
        - end_col: The Excel column letter where the range ends.
        - end_row: The Excel row number where the range ends (one-based).

    How it works:
        1. The column_index_from_string function from openpyxl.utils converts
        both the starting and ending Excel column letters into their
        corresponding one-based numeric indices.
        For example:
            'A'  -> 1
            'C'  -> 3
            'AA' -> 27

        2. Both column indices are reduced by one because pandas .iloc uses
        zero-based indexing.

        3. The DataFrame is sliced using pandas .iloc:
            dataframe.iloc[start_row - 1:end_row,
                        start_col_idx:end_col_idx + 1]

        4. The row and column indices are adjusted as follows:
            - start_row - 1 converts the starting Excel row number to a
            zero-based index.
            - end_row is used directly because the ending index in .iloc is
            exclusive, making the specified ending row inclusive.
            - end_col_idx + 1 is used because the ending column index in .iloc
            is also exclusive, ensuring that the specified ending column is
            included in the extracted range.

        5. Each extracted value is passed to _clean_value(), which standardizes
        empty cells, whitespace, and null-like strings by converting them to None.

        6. The cleaned DataFrame is converted into a standard Python list of
        lists using .values.tolist().

    Example:
        getMatrixData(df, 'B', 2, 'D', 4)

    This returns the cleaned values from cells B2 to D4 of the Excel worksheet
    as a matrix:
        [
            [B2, C2, D2],
            [B3, C3, D3],
            [B4, C4, D4]
        ]
    """
    
    start_col_idx = column_index_from_string(start_col) - 1
    end_col_idx = column_index_from_string(end_col) - 1

    matrix = dataframe.iloc[start_row - 1:end_row, start_col_idx:end_col_idx + 1]
    return matrix.map(_clean_value).values.tolist()

def extract_monthly_data(sheet: pandas.DataFrame) -> list[dict]:

    """Scans a monthly updated spreadsheet row by row. 
    Keeps track of:
    1. report data
    2. fund category
    3. investment focus

    Cleans fund names with parenthesis at the end.

    If a row is an individual fund, it will extract financial variables and store them as a dictionary
    """

    records: list[dict] = []

    report_date: date | None = None
    fund_category: str | None = None
    investment_focus: str | None = None

    for idx, row in sheet.iterrows():
        
        def _report(num: int):
            return to_float(row.iloc[num])

        col_a = _clean_value(row.iloc[0])
        col_b = _clean_value(row.iloc[1])
        fund_name = _clean_value(row.iloc[2])

        if fund_name and fund_name.endswith(")"):
            fund_name = _clean_value(fund_name.rsplit(" ", 1)[0])

        if col_a:
            col_a_lower = col_a.strip().lower()

            if col_a_lower.startswith("month of"):
                year: int = to_int(col_a.split()[-1])
                month: str = str(col_a.split()[-2])
                report_date = get_month_end_date(year, month)

            if col_a == "GRAND TOTAL" or idx == 314: #stop loop at grand total or idx == 314
                break

            if col_a_lower.endswith(("funds", "fund")) and not col_a_lower.startswith("sub total"):
                fund_category = col_a

            if col_a_lower.startswith("primarily invested"):
                investment_focus = col_a

            continue

        if (fund_name and col_b and to_int(col_b) > 0):

            assets = _report(3)

            if assets is None:
                continue

            record = {
                "report_date" : report_date,
                "fund_category" : fund_category,
                "investment_focus": investment_focus,
                "fund_name" : fund_name,

                "assets" : _report(3),
                "liabilities" : _report(4),

                "equity_investments" : _report(6),
                "number_of_accounts": to_int(row.iloc[7]),

                "monthly_sales" : _report(8),
                "monthly_redemption" : _report(9),

                "ytd_sales" : _report(11),
                "ytd_redemption" : _report(12)
            }

            records.append(record)

    return records

        






