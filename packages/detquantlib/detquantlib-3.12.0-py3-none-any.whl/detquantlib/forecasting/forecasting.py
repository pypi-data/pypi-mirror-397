# Python built-in packages
from datetime import datetime

# Third-party packages
import numpy as np
import pandas as pd


def forecast_knife_strategy(
    dates: list[datetime] | list[pd.Timestamp] | pd.DatetimeIndex, values: list | np.ndarray
) -> np.ndarray:
    """
    Generates a forecast using the knife strategy (i.e. random walk).

    The knife strategy works as follows:
    - Set the forecasted value at time t equal to the observed value on the most recent
        previous date that has the same time (hour, minute, and second) and same day type
        (Mon-Fri, Sat, or Sun).
    - If there is no previous date with matching time and day type (i.e. very first observation
        for a given time and day type), the strategy sets the forecasted value at time t equal
        to the observed value at time t.

    Args:
        dates: Delivery dates
        values: Observed values

    Returns:
        Forecasted values
    """
    # Make sure input dates are stored as pd.DatetimeIndex and values as np.array
    dates = pd.DatetimeIndex(dates)
    values = np.array(values)

    # Get times
    hours = dates.hour
    minutes = dates.minute
    seconds = dates.second

    # Get weekday types (1 = Mon-Fri, 2 = Sat, 3 = Sun)
    weekdays = dates.weekday
    day_types = np.zeros_like(weekdays)
    day_types[weekdays < 5] = 1
    day_types[weekdays == 5] = 2
    day_types[weekdays == 6] = 3

    # Get forecasted values
    # Note: The logic below has been designed to optimize code speed, and works as follows:
    # - 1. Get all the unique pairs of time and day type in the input dataset.
    # - 2. For each pair:
    #   - 2.1. Get all the corresponding observed data.
    #   - 2.2. Set the forecast as: data[0], data[0], data[1], data[2], ..., data[N-1]
    fc_values = np.zeros_like(values)
    pairs = np.column_stack([hours, minutes, seconds, day_types])
    for hh, mm, ss, dt in np.unique(pairs, axis=0):
        idx = (hours == hh) & (minutes == mm) & (seconds == ss) & (day_types == dt)
        i_values = values[idx]
        fc_values[idx] = np.insert(i_values[:-1], 0, i_values[0])

    return fc_values
