import pandas as pd

def compute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame summarizing missing values per column.
    """
    missing_count = df.isna().sum()
    missing_percent = df.isna().mean() * 100

    return pd.DataFrame({
        'missing_count': missing_count,
        'missing_percent': missing_percent
    })
