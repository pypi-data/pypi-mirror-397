from __future__ import annotations
import pandas as pd
from .report import Report


def profile(df: pd.DataFrame) -> Report:
    """
    Generate a profiling report for a pandas DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset to profile.

    Returns
    -------
    Report
        A Report object containing summary statistics, visualizations,
        and an HTML export of the profiling results.
    """
    return Report(df).run()
