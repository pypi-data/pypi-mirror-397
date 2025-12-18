import pandas as pd

def compute_outliers(df: pd.DataFrame, method='iqr', threshold=1.5) -> dict:
    """
    Detect outliers for numeric columns using IQR.

    Returns:
        dict: keys = column names, values = list of row indices of outliers.
    """
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    if numeric_df.empty:
        return {}

    outliers_dict = {}

    if method != 'iqr':
        raise NotImplementedError(f"Method '{method}' not implemented")

    # Compute Q1 and Q3 safely (works with constant columns)
    Q1 = numeric_df.quantile(0.25)
    Q3 = numeric_df.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - threshold * IQR
    upper = Q3 + threshold * IQR

    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if series.empty or IQR[col] == 0:
            continue  # skip constant columns
        mask = (series < lower[col]) | (series > upper[col])
        indices = series.index[mask].tolist()
        if indices:
            outliers_dict[col] = indices

    return outliers_dict
