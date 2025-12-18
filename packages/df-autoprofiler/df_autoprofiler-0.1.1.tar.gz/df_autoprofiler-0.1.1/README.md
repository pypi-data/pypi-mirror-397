# df-autoprofiler

**df-autoprofiler** is a lightweight, heuristic-based data profiling tool for pandas DataFrames.  
It generates a **self-contained HTML report** with summaries, correlations, outlier detection, visualizations, and actionable suggestions — designed to scale to large datasets via sampling.

---

### 1. Dataset Overview
Provides a high-level summary of your dataset:
- Number of rows and columns
- Numeric vs categorical feature detection
- Missing data indicators
- High-cardinality detection
- Machine Learning suitability hints

Once you create a profile with `from df_autoprofiler.profiler import profile`, you can do:

```python
report = profile(df)
```

You can then access:

 - **report.numerics** — numeric feature summaries

 - **report.categoricals** — categorical feature summaries

 - **report.correlations** — correlation tables

 - **report.outliers** — outlier detection results

 - **report.missing** — missing data summaries

 - **report.suggestions** — actionable suggestions

### 2. Statistical Summaries

Numeric features: count, mean, std, quantiles, missing %

Categorical features: unique values, top category, frequency

All summaries are available via the report object:

```python
numeric_summary = report.numerics
categorical_summary = report.categoricals
```

### 3. Correlations

Numeric ↔ Numeric: Pearson & Spearman

Categorical ↔ Categorical: Cramér’s V (with safety heuristics)

Categorical ↔ Numeric: Correlation Ratio (η²)

Automatic skipping of unstable or misleading correlations

Warnings when sampling or heuristics are applied

Access correlations:

```python
report.correlations["numeric"]["pearson"]
report.correlations["numeric"]["spearman"]
report.correlations["mixed"]
```

### 4. Outlier Detection

IQR-based detection

Reports row indices per column

Skips constant or invalid columns

Access outliers:

```python
outliers = report.outliers
```

### 5. Missing Data Analysis

Detects missing values across columns

Generates summary tables with counts and percentages

Access missing data:

```python
missing_data = report.missing
```

### 6. Heuristic Suggestions

Prioritized recommendations with three levels:

 - 🚨 High priority

 - ⚠️ Medium priority

 - ℹ️ Low priority

Examples:

High skew → consider log/Box-Cox transform

High missingness → consider imputation

Constant columns → consider dropping

Access suggestions:

```python
suggestions = report.suggestions
```

### 7. Visualizations

Histograms, distributions, and correlation plots

Embedded directly into the HTML report

Handles special characters safely in filenames

Generate plots:

```python
report.plots['hist_{NAME_OF_COL}']
```

## Quickstart Example

```python
import pandas as pd
from df_autoprofiler.profiler import profile

df = pd.read_csv("data.csv")

# Create the profile
report = profile(df)

# Access summaries
print(report.numerics.head())
print(report.categoricals.head())
print(report.missing.head())

# Generate HTML report
report.to_html("report.html")
```

## Handling Large Datasets

 - Automatic sampling to maintain performance

 - Warnings included in report when sampling is applied

Example with a large synthetic dataset:

```python
import pandas as pd
import numpy as np
from df_autoprofiler.profiler import profile

n = 1_000_000
df_large = pd.DataFrame({
    f"num_{i}": np.random.randn(n) for i in range(10)
})
for j in range(5):
    df_large[f"cat_{j}"] = np.random.choice(["A","B","C","D"], size=n)

report = profile(df_large)
report.to_html("large_report.html")
```

## Installation

```bash
pip install df-autoprofiler
```
## Known Limitations

 - Correlation measures are heuristic-based

 - ML readiness scoring is qualitative

 - Sampling may hide rare patterns

 - Bugs

## 📄 License

MIT License

## 🙌 Acknowledgments

Built with:

 - pandas

 - numpy

 - scipy

 - matplotlib
