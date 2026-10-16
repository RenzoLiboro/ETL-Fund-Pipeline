from datetime import date
from calendar import monthrange


MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def get_month_end_date(year: int, month_name: str) -> date:
    # Handles cases like "July REVISED" by taking the first word
    month_key = month_name.strip().split()[0].lower()

    month_number = MONTH_MAP[month_key]

    last_day = monthrange(year, month_number)[1]

    return date(year, month_number, last_day)