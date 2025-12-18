"""Constants for the Bear Epoch Time package."""

from datetime import timedelta
from typing import Literal, LiteralString, overload
from zoneinfo import ZoneInfo


@overload
def neg(value: int) -> int: ...


@overload
def neg(value: float) -> float: ...


def neg(value: float) -> float | int:
    """Indicate that a value is negative.

    Args:
        value (float | int): The value to negate.

    Returns:
        float | int: The negated value.
    """
    return -abs(value)


# Time Zones #

UTC = ZoneInfo("UTC")
"""UTC timezone, a UTC timezone using a ZoneInfo timezone object"""

PT_TIME_ZONE = ZoneInfo("America/Los_Angeles")
"""A Pacific Time Zone using a ZoneInfo timezone object"""

ET_TIME_ZONE = ZoneInfo("America/New_York")
"""Eastern Time Zone using a ZoneInfo timezone object"""

# Date and Time Formats #

DATE_FORMAT = "%m-%d-%Y"
"""Date format"""

TIME_FORMAT = "%I:%M %p"
"""Time format with 12 hour format"""

TIME_FORMAT_WITH_SECONDS = "%I:%M:%S %p"
"""Time format with 12 hour format and seconds"""

DATE_TIME_FORMAT: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT}"
"""Datetime format with 12 hour format"""

DT_FORMAT_WITH_SECONDS: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT_WITH_SECONDS}"
"""Datetime format with 12 hour format and seconds"""

DT_FORMAT_WITH_TZ: LiteralString = f"{DATE_TIME_FORMAT} %Z"
"""Datetime format with 12 hour format and timezone"""

DT_FORMAT_WITH_TZ_AND_SECONDS: LiteralString = f"{DT_FORMAT_WITH_SECONDS} %Z"
"""Datetime format with 12 hour format, seconds, and timezone"""

# Time Related Constants #

MILLISECONDS_IN_SECOND: Literal[1000] = 1000
"""1000 milliseconds in a second"""

SECONDS_IN_MINUTE: Literal[60] = 60
"""60 seconds in a minute"""

MINUTES_IN_HOUR: Literal[60] = 60
"""60 minutes in an hour"""

HOURS_IN_DAY: Literal[24] = 24
"""24 hours in a day"""

DAYS_IN_MONTH: Literal[30] = 30
"""30 days in a month, approximation for a month"""

SECONDS_IN_HOUR: Literal[3600] = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
"""60 * 60 = 3600 seconds in an hour"""

SECONDS_IN_DAY: Literal[86400] = SECONDS_IN_HOUR * HOURS_IN_DAY
"""24 * 60 * 60 = 86400 seconds in a day"""

SECONDS_IN_MONTH: Literal[2592000] = SECONDS_IN_DAY * DAYS_IN_MONTH
"""30 * 24 * 60 * 60 = 2592000 seconds in a month"""

DAY_AGO_SECS: int = neg(SECONDS_IN_DAY)
"""Negative number of seconds in a day, useful for calculations"""

DAY_AGO = timedelta(seconds=DAY_AGO_SECS)
"""A timedelta representing 24 hours ago"""


def Minutes(minutes: int) -> int:
    """Create an integer representing the given number of minutes in seconds.

    Args:
        minutes (int): The number of minutes.

    Returns:
        int: The number of seconds in the given number of minutes.
    """
    return minutes * SECONDS_IN_MINUTE


def Seconds(seconds: int) -> int:
    """Create an integer representing the given number of seconds.

    Args:
        seconds (int): The number of seconds.

    Returns:
        int: The number of seconds.
    """
    return seconds


def Hours(hours: int) -> int:
    """Create an integer representing the given number of hours in seconds.

    Args:
        hours (int): The number of hours.

    Returns:
        int: The number of seconds in the given number of hours.
    """
    return hours * SECONDS_IN_HOUR


def Days(days: int) -> int:
    """Create an integer representing the given number of days in seconds.

    Args:
        days (int): The number of days.

    Returns:
        int: The number of seconds in the given number of days.
    """
    return days * SECONDS_IN_DAY


def Months(months: int) -> int:
    """Create an integer representing the given number of months in seconds.

    Args:
        months (int): The number of months.

    Returns:
        int: The number of seconds in the given number of months.
    """
    return months * SECONDS_IN_MONTH


def Interval(interval: str) -> float:
    """Convert a string interval to its equivalent in seconds.

    Args:
        interval (str): The interval string (e.g., '1m', '2h', '3d').

    Returns:
        float: The equivalent number of seconds.
    """
    from bear_epoch_time.time_converter import parse_to_seconds  # noqa: PLC0415

    return parse_to_seconds(interval)


DAYS_OF_THE_WEEK: set[str] = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}
"""Set of days of the week as strings."""

WEEK_STR_TO_NUM: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
"""Mapping of days of the week strings to their corresponding integer values."""

# ruff: noqa: N802

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DAYS_IN_MONTH",
    "DAY_AGO",
    "DAY_AGO_SECS",
    "DT_FORMAT_WITH_SECONDS",
    "DT_FORMAT_WITH_TZ",
    "DT_FORMAT_WITH_TZ_AND_SECONDS",
    "ET_TIME_ZONE",
    "HOURS_IN_DAY",
    "MILLISECONDS_IN_SECOND",
    "MINUTES_IN_HOUR",
    "PT_TIME_ZONE",
    "SECONDS_IN_DAY",
    "SECONDS_IN_HOUR",
    "SECONDS_IN_MINUTE",
    "SECONDS_IN_MONTH",
    "TIME_FORMAT",
    "TIME_FORMAT_WITH_SECONDS",
    "UTC",
    "Days",
    "Hours",
    "Interval",
    "Minutes",
    "Months",
    "Seconds",
]
