"""Utility functions for parsing time periods and other helpers."""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from .exceptions import InvalidTimeFormatError


def parse_time_period(time_str: str) -> Tuple[str, str]:
    """
    Parse a time period string and return start and end dates.

    Supported formats:
    - "last N days/weeks/months/years"
    - "past N days/weeks/months/years"
    - "this month/year"
    - "last month/year"
    - "YYYY-MM-DD to YYYY-MM-DD" (explicit date range)

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    time_str = time_str.strip().lower()
    today = datetime.now()

    # Handle explicit date ranges
    date_range_pattern = r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})'
    match = re.match(date_range_pattern, time_str)
    if match:
        return match.group(1), match.group(2)

    # Handle "this month/year"
    if time_str == "this month":
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    if time_str == "last month":
        # Get first day of current month, then go back one day to get last day of previous month
        first_of_this_month = today.replace(day=1)
        last_of_last_month = first_of_this_month - timedelta(days=1)
        # Get first day of that month
        first_of_last_month = last_of_last_month.replace(day=1)
        return first_of_last_month.strftime("%Y-%m-%d"), last_of_last_month.strftime("%Y-%m-%d")

    if time_str == "this year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    if time_str == "last year":
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        end_date = today.replace(year=today.year - 1, month=12, day=31)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # Handle "last/past N period" patterns
    period_pattern = r'(?:last|past)\s+(\d+)\s+(day|week|month|year)s?'
    match = re.match(period_pattern, time_str)
    if match:
        number = int(match.group(1))
        unit = match.group(2)

        if unit == "day":
            start_date = today - timedelta(days=number)
        elif unit == "week":
            start_date = today - timedelta(weeks=number)
        elif unit == "month":
            # Approximate months as 30 days for simplicity
            start_date = today - timedelta(days=number * 30)
        elif unit == "year":
            start_date = today.replace(year=today.year - number)

        end_date = today
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # Handle single numbers (assume days)
    if time_str.isdigit():
        days = int(time_str)
        start_date = today - timedelta(days=days)
        end_date = today
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    raise InvalidTimeFormatError(f"Unable to parse time period: '{time_str}'")


def normalize_taxon_name(name: str) -> str:
    """Normalize a taxon name for API queries."""
    # Basic cleaning - remove extra whitespace, handle common formatting
    name = name.strip()

    # If it looks like a Latin name (two words), capitalize appropriately
    parts = name.split()
    if len(parts) == 2 and all(part.replace('-', '').isalpha() for part in parts):
        # Genus species format
        return f"{parts[0].capitalize()} {parts[1].lower()}"

    return name