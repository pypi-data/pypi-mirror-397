# Python built-in packages
from datetime import datetime

# Third-party packages
import numpy as np


def add_log(message: str):
    """
    Short helper function to print log messages, including time stamps.

    Args:
        message: Message to be printed
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def divide_with_nan(
    numerator: np.array, denominator: np.array, nan=np.nan, posinf=np.nan, neginf=np.nan
) -> np.array:
    """
    A short utility function to perform an element-wise division of two arrays and replace
    potential NaN, inf, and -inf results with user-defined values.

    Args:
        numerator: Numerator array
        denominator: Denominator array
        nan: Value to use to replace NaN results
        posinf: Value to use to replace positive inf results
        neginf: Value to use to replace negative inf results

    Returns:
        Quotient array
    """
    quotient = np.nan_to_num(
        x=np.divide(numerator, denominator), nan=nan, posinf=posinf, neginf=neginf
    )
    return quotient
