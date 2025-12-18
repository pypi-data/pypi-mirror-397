import pandas as pd
from df_autoprofiler.summary import compute_numeric_summary, compute_categorical_summary

def test_numeric_summary():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [10, 20, 30, 40, 50]
    })
    summary = compute_numeric_summary(df)
    assert "a" in summary.index
    assert "b" in summary.index
    assert summary.loc["a", "count"] == 5
    assert summary.loc["b", "mean"] == 30

def test_categorical_summary():
    df = pd.DataFrame({
        "c": ["x", "y", "x", "y", "x"]
    })
    summary = compute_categorical_summary(df)
    assert "c" in summary.index
    assert summary.loc["c", "unique"] == 2
    assert summary.loc["c", "freq"] == 3
