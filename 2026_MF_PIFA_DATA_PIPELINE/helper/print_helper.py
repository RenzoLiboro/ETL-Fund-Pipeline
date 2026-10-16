from pprint import pformat
import pandas as pd

def printData(data, label=None):
    """
    Prints any data type in a readable format for debugging.
    Supports DataFrame, Series, dict, list, and primitives.
    Use `label` to identify output when printing multiple variables.
    """
    if label:
        print(f"\n=== {label} ===")

    if isinstance(data, pd.DataFrame):
        print(data.to_string())
    elif isinstance(data, pd.Series):
        print(data.to_string())
    elif isinstance(data, dict):
        print(pformat(data, indent=2))
    elif isinstance(data, list):
        if all(isinstance(row, (list, tuple)) for row in data):
            for row in data:
                print("\t".join(str(cell) for cell in row))
        else:
            print(pformat(data, indent=2))
    elif isinstance(data, (int, float, bool, str, type(None))):
        print(data)
    else:
        print(pformat(data, indent=2))