# 📊 Autoprofiler

Autoprofiler is a lightweight, heuristic-based data profiling tool for pandas DataFrames.
It generates an HTML report with summaries, correlations, outlier detection, visualizations, and actionable suggestions — designed to scale to large datasets via sampling.

## ✨ Features
### 📌 Dataset Overview

Rows and columns

Numeric vs categorical features

Missing data indicators

High-cardinality detection

ML suitability hints

### 📈 Statistical Summaries

Numeric summaries (count, mean, std, quantiles, missing %)

Categorical summaries (unique values, top category, frequency)

### 🔗 Correlations

Numeric ↔ Numeric: Pearson & Spearman

Categorical ↔ Categorical: Cramér’s V (with safety heuristics)

Categorical ↔ Numeric: Correlation Ratio (η²)

Automatic skipping of unstable or misleading correlations

Warnings when sampling or heuristics are applied

### 🚨 Outlier Detection

IQR-based detection

Reports row indices per column

Skips constant or invalid columns

### 🧠 Heuristic Suggestions

Prioritized recommendations:

🚨 High priority

⚠️ Medium priority

ℹ️ Low priority

Examples:

High skew → consider log/Box-Cox transform

High missingness → consider imputation

Constant columns → consider dropping

### 📊 Visualizations

Histograms and distributions

Embedded directly into the HTML report (no temp files)

Filename-safe handling for special characters

### ⚡ Scales to Large Datasets

Automatic sampling for large DataFrames

Sampling warnings included in report

Designed to avoid O(n²) pitfalls where possible

### 🖥 Example Output

Autoprofiler generates a single self-contained HTML report that includes:

Dataset overview

Tables (summaries & correlations)

Suggestions with priority levels

Embedded plots

Example:

report.html

### 🚀 Installation

Clone the repository and install dependencies:

``cmd
git clone https://github.com/yourusername/autoprofiler.git
cd autoprofiler
pip install -r requirements.txt
```

### 🧪 Usage
```python
import pandas as pd
from autoprofiler import profiler

df = pd.read_csv("data.csv")

report = profiler.profile(df)
report.to_html("report.html")
```

Open report.html in your browser.

### 📦 Large Dataset Testing

Autoprofiler supports large datasets via sampling.

Example synthetic dataset:

import pandas as pd
import numpy as np

n = 1_000_000
df_large = pd.DataFrame({
    f"num_{i}": np.random.randn(n) for i in range(10)
})
for j in range(5):
    df_large[f"cat_{j}"] = np.random.choice(["A", "B", "C", "D"], size=n)

df_large.to_csv("synthetic_large.csv", index=False)

df = pd.read_csv("synthetic_large.csv")
report = profiler.profile(df)
report.to_html("large_report.html")

### 🧠 Design Philosophy

Transparency over magic

Heuristics over black boxes

Actionable insights over raw statistics

Graceful degradation on large data

This is not meant to replace full EDA — it’s meant to accelerate it.

### ⚠️ Known Limitations

Correlation measures are heuristic-based

ML readiness scoring is qualitative

Sampling may hide rare patterns

Not intended for real-time profiling

### 🛠 Roadmap

Execution timing per report section

ML readiness scoring (0–100)

Optional target leakage detection

Stability checks (sample vs full dataset)

Performance optimizations for >10M rows

### 📄 License

MIT License

### 🙌 Acknowledgments

Built with:

pandas

numpy

scipy

matplotlib

### 🧠 Why This Exists

This project was built to:

Understand how data profiling tools work internally

Explore scalability tradeoffs

Practice building interpretable, user-focused data tooling
