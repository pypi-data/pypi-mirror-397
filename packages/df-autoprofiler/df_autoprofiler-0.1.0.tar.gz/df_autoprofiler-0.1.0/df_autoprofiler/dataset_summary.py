import pandas as pd

def dataset_summary(df: pd.DataFrame) -> list[str]:
    """Generate a quick summary of the DataFrame."""
    summary: list[str] = []

    n_rows, n_cols = df.shape
    summary.append(f"Rows: {n_rows:,}, Columns: {n_cols}")

    # Precompute numeric and categorical subsets
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    cat_df = df.select_dtypes(include=["object", "category"])

    num_cols = numeric_df.shape[1]
    cat_cols = cat_df.shape[1]

    summary.append(f"Numeric features: {num_cols}")
    summary.append(f"Categorical features: {cat_cols}")

    # Missing columns
    missing_cols = df.isna().any(axis=0).sum()
    summary.append(f"Columns with missing values: {missing_cols}")

    # High-cardinality categorical columns
    if cat_cols > 0:
        high_card_mask = (cat_df.nunique() / n_rows) > 0.5
        high_card_cols = high_card_mask.sum()
    else:
        high_card_cols = 0

    if high_card_cols > 0:
        summary.append("High-cardinality categorical features detected")

    # Dataset type hint
    if num_cols > 0 and cat_cols > 0:
        summary.append("Suitable for tree-based ML models")
    elif num_cols > 0:
        summary.append("Primarily numeric dataset")

    # ML readiness score
    score = 100
    if missing_cols > 0:
        score -= min(30, missing_cols * 5)
    if high_card_cols > 0:
        score -= 15
    if n_rows < 500:
        score -= 20
    score = max(score, 0)

    summary.append(f"ML readiness score: {score}/100")

    return summary
