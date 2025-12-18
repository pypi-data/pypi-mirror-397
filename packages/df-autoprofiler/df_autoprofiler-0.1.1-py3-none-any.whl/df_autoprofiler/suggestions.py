import numpy as np
from scipy.stats import skew

def generate_suggestions(df):
    suggestions = {
        "high": [],
        "medium": [],
        "low": []
    }

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    missing_pct = df.isna().mean()

    # Handle missing values for all columns
    for col, pct in missing_pct.items():
        if pct > 0.3:
            suggestions["high"].append(f"{col}: {pct:.1%} missing → consider dropping")
        elif pct > 0.1:
            suggestions["medium"].append(f"{col}: {pct:.1%} missing → consider imputation")

    # Numeric suggestions
    for col in numeric_cols:
        s = df[col].dropna()
        if s.nunique() > 1:
            sk = skew(s.dropna())
            if abs(sk) > 2:
                suggestions["high"].append(
                    f"{col}: highly skewed (skew={sk:.2f}) → log/Box-Cox transform"
                )

        if s.nunique() <= 1:
            suggestions["low"].append(f"{col}: constant value → safe to drop")
            continue  # skip skew and negative checks

        if (s < 0).any():
            suggestions["medium"].append(f"{col}: contains negative values → validate data")

        sk = skew(s)
        if abs(sk) > 2:
            suggestions["high"].append(f"{col}: highly skewed (skew={sk:.2f}) → log/Box-Cox transform")

    return suggestions
