import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from collections import defaultdict

# -----------------------------
# Helpers
# -----------------------------

def is_constant(series: pd.Series) -> bool:
    return series.std(skipna=True) == 0

def high_cardinality(series: pd.Series, threshold=0.5) -> bool:
    return series.nunique(dropna=True) / len(series) > threshold

def min_category_count(series: pd.Series) -> int:
    return series.value_counts(dropna=True).min()

# -----------------------------
# Numeric correlations
# -----------------------------

def numeric_correlations(df: pd.DataFrame, sample_size: int | None = None):
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    numeric_cols = [c for c in numeric_cols if not is_constant(df[c])]
    
    df_to_use = df[numeric_cols]
    if sample_size and len(df) > sample_size:
        df_to_use = df_to_use.sample(n=sample_size, random_state=42)
    
    return {
        "pearson": df_to_use.corr(method="pearson"),
        "spearman": df_to_use.corr(method="spearman")
    }

# -----------------------------
# Categorical correlations (Cramér's V)
# -----------------------------

def cramers_v(x: pd.Series, y: pd.Series) -> float:
    confusion = pd.crosstab(x, y)
    if confusion.size == 0:
        return np.nan
    chi2 = chi2_contingency(confusion)[0]
    n = confusion.sum().sum()
    r, k = confusion.shape
    if min(r, k) <= 1:
        return np.nan
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))

def categorical_correlations(df: pd.DataFrame, warnings: list[str]):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_cols = [c for c in cat_cols if not high_cardinality(df[c]) and min_category_count(df[c]) >= 2]

    if len(cat_cols) < 2:
        warnings.append("Categorical correlations skipped due to high cardinality or low sample size")
        return None

    matrix = pd.DataFrame(index=cat_cols, columns=cat_cols, dtype=float)

    # Precompute value_counts for efficiency
    value_counts = {col: df[col].value_counts(dropna=True) for col in cat_cols}

    for i, c1 in enumerate(cat_cols):
        for j, c2 in enumerate(cat_cols[i:], start=i):
            if c1 == c2:
                matrix.loc[c1, c2] = 1.0
            else:
                matrix.loc[c1, c2] = cramers_v(df[c1], df[c2])
                matrix.loc[c2, c1] = matrix.loc[c1, c2]  # mirror to lower triangle

    return matrix

# -----------------------------
# Mixed correlations (Correlation Ratio η²)
# -----------------------------

def correlation_ratio(categories: pd.Series, values: pd.Series) -> float:
    valid = ~(categories.isna() | values.isna())
    categories = pd.Categorical(categories[valid])
    values = values[valid]
    if len(values) < 2:
        return np.nan

    means = []
    counts = []

    for cat in categories.categories:
        vals = values[categories == cat]
        if len(vals) < 2:
            continue
        means.append(vals.mean())
        counts.append(len(vals))

    if not counts:
        return np.nan

    grand_mean = values.mean()
    numerator = sum(c * (m - grand_mean) ** 2 for m, c in zip(means, counts))
    denominator = ((values - grand_mean) ** 2).sum()
    return numerator / denominator if denominator != 0 else np.nan

def mixed_correlations(df: pd.DataFrame, warnings: list[str]):
    numeric_cols = [c for c in df.select_dtypes(include=["int64", "float64"]).columns if not is_constant(df[c])]
    cat_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns]

    rows = []

    for cat in cat_cols:
        if high_cardinality(df[cat]) or min_category_count(df[cat]) < 3:
            continue
        for num in numeric_cols:
            val = correlation_ratio(df[cat], df[num])
            if not np.isnan(val):
                rows.append({"categorical": cat, "numeric": num, "correlation_ratio": val})

    if not rows:
        warnings.append("Mixed correlations skipped due to insufficient category sizes or constant numeric columns")
        return None

    return pd.DataFrame(rows).sort_values("correlation_ratio", ascending=False)

# -----------------------------
# Public API
# -----------------------------

def compute_correlations(df: pd.DataFrame, sample_size: int | None = None):
    warnings: list[str] = []
    correlations = {
        "numeric": numeric_correlations(df, sample_size=sample_size),
        "categorical": categorical_correlations(df, warnings),
        "mixed": mixed_correlations(df, warnings)
    }
    return correlations, warnings
