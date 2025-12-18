from __future__ import annotations
import base64
import io
import re
from typing import Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
from .summary import compute_numeric_summary, compute_categorical_summary
from .outliers import compute_outliers
from .missing import compute_missing
from .correlations import compute_correlations
from .suggestions import generate_suggestions
from .visuals.plots import generate_plots
from .utils import maybe_sample
from .dataset_summary import dataset_summary


class Report:
    """
    Generate an automated profiling report for a pandas DataFrame.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

        # Populated after run()
        self.df_sample: pd.DataFrame | None = None
        self.sampled: bool = False
        self.numerics: pd.DataFrame | None = None
        self.categoricals: pd.DataFrame | None = None
        self.outliers: Any = None
        self.missing: Any = None
        self.correlations: Dict[str, Any] | None = None
        self.correlation_warnings: list[str] = []
        self.suggestions: Dict[str, list[str]] | None = None
        self.plots: Dict[str, plt.Figure] | None = None
        self.dataset_summary: list[str] | None = None

    def run(self) -> "Report":
        """
        Compute all statistics, correlations, plots, and suggestions.
        """
        self.df_sample, self.sampled = maybe_sample(self.df)

        self.numerics = compute_numeric_summary(self.df)
        self.categoricals = compute_categorical_summary(self.df)
        self.outliers = compute_outliers(self.df)
        self.missing = compute_missing(self.df)

        self.correlations, self.correlation_warnings = compute_correlations(
            self.df_sample
        )

        self.suggestions = generate_suggestions(self.df)
        self.plots = generate_plots(self.df_sample)
        self.dataset_summary = dataset_summary(self.df)

        if self.sampled:
            msg = f"⚠️ Analysis performed on a sample of {len(self.df_sample):,} rows for performance"
            self.dataset_summary.append(msg)
            self.correlation_warnings.append(msg)

        return self
    
    @staticmethod
    def _correlation_color(val: float) -> str:
        """Return CSS style based on correlation strength."""
        if pd.isna(val):
            return ""

        v = abs(val)

        if v >= 0.9:
            color = "#005B0E"   # very strong
        elif v >= 0.7:
            color = "#177340"   # strong
        elif v >= 0.5:
            color = "#44AA5E"   # moderate
        elif v >= 0.3:
            color = "#5add5a"   # weak
        else:
            color = "#99d8a3"   # very weak

        return f"background-color: {color};"


    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Replace illegal filename characters with underscores."""
        return re.sub(r"[^0-9a-zA-Z]+", "_", name)

    def to_html(self, filename: str = "report.html") -> str:
        """
        Write the profiling report to an HTML file.

        Returns
        -------
        str
            Path to the generated HTML file.
        """
        if self.numerics is None:
            raise RuntimeError("Report has not been run. Call report.run() first.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                """<html>
<head>
<meta charset="UTF-8">
<title>Autoprofiler Report</title>
</head>
<body>"""
            )

            f.write("<h1>Dataset Overview</h1><ul>")
            for item in self.dataset_summary:
                f.write(f"<li>{item}</li>")
            f.write("</ul>")

            f.write("<h1>Numeric Summary</h1>")
            f.write(self.numerics.to_html())

            f.write("<h1>Categorical Summary</h1>")
            f.write(self.categoricals.to_html())

            f.write("<h1>Correlations</h1>")

            # Numeric correlations
            if "numeric" in self.correlations:
                for method, df_corr in self.correlations["numeric"].items():
                    f.write(f"<h2>{method.title()} Correlation</h2>")
                    styled = df_corr.style.applymap(Report._correlation_color)
                    f.write(styled.to_html())

            # Categorical correlations
            if self.correlations.get("categorical") is not None:
                f.write("<h2>Categorical Correlations</h2>")
                styled = self.correlations["categorical"].style.applymap(Report._correlation_color)
                f.write(styled.to_html())

            # Mixed correlations (numeric ↔ categorical)
            if self.correlations.get("mixed") is not None and not self.correlations["mixed"].empty:
                f.write("<h2>Mixed Correlations</h2>")
                df_mixed = self.correlations["mixed"].reset_index(drop=True)

                # Apply coloring only to the correlation_ratio column
                def mixed_color(val):
                    if isinstance(val, (int, float)):
                        return Report._correlation_color(val)
                    return ""

                styled = df_mixed.style.applymap(mixed_color, subset=["correlation_ratio"])
                f.write(styled.to_html(index=False))


            f.write("<h2>Correlation Warnings</h2>")
            if self.correlation_warnings:
                f.write("<ul>")
                for w in self.correlation_warnings:
                    f.write(f"<li>{w}</li>")
                f.write("</ul>")
            else:
                f.write("<p>No correlation warnings.</p>")

            f.write("<h1>Suggestions</h1>")

            for level, title in [
                ("high", "🚨 High Priority"),
                ("medium", "⚠️ Medium Priority"),
                ("low", "ℹ️ Low Priority"),
            ]:
                items = self.suggestions.get(level, [])
                if items:
                    f.write(f"<h2>{title}</h2><ul>")
                    for s in items:
                        f.write(f"<li>{s}</li>")
                    f.write("</ul>")

            if self.plots:
                f.write("<h1>Plots</h1>")
                for name, fig in self.plots.items():
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight")
                    plt.close(fig)
                    buf.seek(0)
                    img = base64.b64encode(buf.read()).decode("utf-8")
                    safe = self.sanitize_filename(name)
                    f.write(f"<h2>{safe}</h2>")
                    f.write(f'<img src="data:image/png;base64,{img}" width="600"><br><br>')

            f.write("</body></html>")

        return filename
