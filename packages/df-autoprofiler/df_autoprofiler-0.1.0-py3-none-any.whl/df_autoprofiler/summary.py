import pandas as pd
import numpy as np

def compute_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized numeric summary with safe outlier detection.
    """
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    if numeric_df.empty:
        return pd.DataFrame()

    # Basic stats
    stats = numeric_df.describe().transpose()  # rows=columns, easier to access
    stats = stats.reindex(columns=['count','mean','std','min','25%','50%','75%','max'], fill_value=0)

    # Missing
    stats['missing_count'] = numeric_df.isna().sum()
    stats['missing_percent'] = numeric_df.isna().mean() * 100

    # Outliers using IQR
    Q1 = stats['25%']
    Q3 = stats['75%']
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    def count_outliers(col):
        series = numeric_df[col].dropna()
        if IQR[col] == 0 or series.empty:
            return 0
        return ((series < lower[col]) | (series > upper[col])).sum()

    stats['outlier_count'] = [count_outliers(c) for c in numeric_df.columns]
    stats['dtype'] = numeric_df.dtypes

    return stats


def compute_categorical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized categorical summary.
    """
    cat_df = df.select_dtypes(include=['object', 'category'])
    if cat_df.empty:
        return pd.DataFrame()

    count = cat_df.count()
    nunique = cat_df.nunique()
    missing_count = cat_df.isna().sum()
    missing_percent = cat_df.isna().mean() * 100

    # Mode and frequency
    mode = pd.Series(index=cat_df.columns, dtype=object)
    freq = pd.Series(index=cat_df.columns, dtype=int)
    for col in cat_df.columns:
        if not cat_df[col].empty:
            mode[col] = cat_df[col].mode().iloc[0] if not cat_df[col].mode().empty else None
            freq[col] = cat_df[col].value_counts().iloc[0] if not cat_df[col].value_counts().empty else 0
        else:
            mode[col] = None
            freq[col] = 0

    summary = pd.DataFrame({
        'count': count,
        'unique': nunique,
        'mode': mode,
        'freq': freq,
        'missing_count': missing_count,
        'missing_percent': missing_percent,
        'dtype': cat_df.dtypes
    })

    return summary
