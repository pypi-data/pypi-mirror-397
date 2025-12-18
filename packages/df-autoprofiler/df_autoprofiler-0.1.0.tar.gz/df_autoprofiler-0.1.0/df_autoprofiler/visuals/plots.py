from __future__ import annotations
from typing import Dict
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_plots(df: pd.DataFrame, max_kde_points: int = 100_000) -> Dict[str, plt.Figure]:
    """
    Generate exploratory plots for numeric columns in a DataFrame.
    
    Optimizations:
    - Skip constant columns
    - Skip KDE if column has more than max_kde_points
    - Use sensible figure size
    - Avoid unnecessary loops if possible
    
    Returns
    -------
    dict[str, matplotlib.figure.Figure]
        Dictionary of figures keyed by plot name.
    """
    plots: Dict[str, plt.Figure] = {}

    numeric_cols = df.select_dtypes(include="number").columns
    numeric_cols = [c for c in numeric_cols if df[c].nunique(dropna=True) > 1]

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        fig, ax = plt.subplots(figsize=(6, 4))
        kde_flag = len(series) <= max_kde_points
        sns.histplot(series, kde=kde_flag, ax=ax)
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")

        plots[f"hist_{col}"] = fig
        plt.close(fig)

    return plots
