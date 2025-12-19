from datetime import date, datetime, timedelta
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd

AMS_TZ = ZoneInfo("Europe/Amsterdam")
UTC_TZ = ZoneInfo("UTC")


def safe_int(x: str) -> int | None:
    """Converts a string to int if possible, otherwise returns None."""
    try:
        return int(x)
    except ValueError:
        return None


def clean_dict(d: dict) -> dict:
    """Removes all None values from a dictionary."""
    return {k: v for k, v in d.items() if v is not None}


def is_dst_adj_day(date_obj: date) -> bool:
    """Checks if a given date is a day when Daylight Saving Time (DST) adjustment occurs.

    Assumes Amsterdam locality.
    """
    next_date_obj = date_obj + timedelta(days=1)

    day_start = datetime(date_obj.year, date_obj.month, date_obj.day, tzinfo=AMS_TZ)
    next_day_start = datetime(
        next_date_obj.year, next_date_obj.month, next_date_obj.day, tzinfo=AMS_TZ
    )

    duration_of_day = next_day_start - day_start
    return duration_of_day != timedelta(hours=24)


def safe_reset_index(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """Reset index safely by renaming index columns if they conflict with existing columns."""
    # Get current index names
    new_names = list(df.index.names)
    existing_cols = set(df.columns)

    for i, name in enumerate(new_names):
        # Handle unnamed indexes (None)
        if name is None:
            # Emulate pandas default naming: 'index' for single, 'level_x' for multi
            base_name = "index" if len(new_names) == 1 else f"level_{i}"
        else:
            base_name = name

        # Check for collision and rename if necessary
        candidate = base_name
        counter = 1

        # Keep appending suffix until the name is unique among columns
        # AND unique among other new index names we are generating
        while candidate in existing_cols:
            candidate = f"{base_name}_{counter}"
            counter += 1

        new_names[i] = candidate
        # Add to existing_cols so subsequent levels don't collide with this one
        existing_cols.add(candidate)

    # Apply new safe names and reset
    if inplace:
        df.index.names = new_names
        df.reset_index(inplace=True, drop=False)
        return df
    else:
        df = df.copy()
        df.index.names = new_names
        return df.reset_index(inplace=False, drop=False)


def standardize_to_utc(series: pd.Series) -> pd.Series:
    """Converts a Series (object or datetime) to UTC datetime.

    Logic:
    1. Converts object/string to datetime.
    2. Naive datetimes are localized to UTC (Assumed UTC).
    3. Aware datetimes are converted to UTC.
    """
    return pd.to_datetime(series, utc=True)


def time_range(
    start_dt: datetime, end_dt: datetime, step: Callable[[datetime], datetime]
):
    """Generates a sequence of datetimes from start_dt up to (but not including) end_dt."""
    current_dt = start_dt
    while current_dt < end_dt:
        yield current_dt
        next_dt = step(current_dt)
        assert (
            next_dt > current_dt
        ), f"Step function returned a time in the past: {next_dt}"
        current_dt = next_dt


def time_blocks(
    start_dt: datetime, end_dt: datetime, step: Callable[[datetime], datetime]
):
    """Generates contiguous time intervals (blocks) covering the duration from start_dt to end_dt."""
    gen = time_range(start_dt, end_dt, step)
    prev = next(gen)
    for dt in gen:
        yield prev, dt
        prev = dt
    yield prev, end_dt
