#!/usr/bin/env python3
"""
Perform comprehensive data quality checks on a dataset.

Usage: python data_quality_check.py input.csv [output_report.txt]
"""

import sys
from pathlib import Path
from typing import Dict, Any

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Error: pandas and numpy not installed. Run: pip install pandas numpy")
    sys.exit(1)


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality and return comprehensive report.

    Args:
        df: DataFrame to analyze.

    Returns:
        Dictionary containing quality analysis results.
    """
    report = {
        "shape": df.shape,
        "columns": list(df.columns),
        "data_types": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
        "duplicates": df.duplicated().sum(),
        "unique_values": df.nunique().to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum(),
    }

    # Numeric columns analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        report["numeric_summary"] = df[numeric_cols].describe().to_dict()

        # Outlier detection using IQR method
        outliers = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers[col] = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        report["outliers"] = outliers

    # Categorical columns analysis
    categorical_cols = df.select_dtypes(include=["object"]).columns
    if len(categorical_cols) > 0:
        categorical_info = {}
        for col in categorical_cols:
            categorical_info[col] = {
                "unique_count": df[col].nunique(),
                "top_values": df[col].value_counts().head(5).to_dict(),
            }
        report["categorical_summary"] = categorical_info

    return report


def generate_report_text(report: Dict[str, Any]) -> str:
    """Generate human-readable report text."""
    lines = ["DATA QUALITY REPORT", "=" * 50, ""]

    # Basic info
    lines.extend(
        [
            f"Dataset Shape: {report['shape'][0]} rows × {report['shape'][1]} columns",
            f"Memory Usage: {report['memory_usage'] / 1024 / 1024:.2f} MB",
            f"Duplicate Rows: {report['duplicates']}",
            "",
        ]
    )

    # Missing values
    lines.append("MISSING VALUES:")
    lines.append("-" * 20)
    for col, missing in report["missing_values"].items():
        if missing > 0:
            pct = report["missing_percentage"][col]
            lines.append(f"{col}: {missing} ({pct:.1f}%)")
    if not any(report["missing_values"].values()):
        lines.append("No missing values found")
    lines.append("")

    # Data types
    lines.append("DATA TYPES:")
    lines.append("-" * 15)
    for col, dtype in report["data_types"].items():
        unique_count = report["unique_values"][col]
        lines.append(f"{col}: {dtype} ({unique_count} unique values)")
    lines.append("")

    # Outliers
    if "outliers" in report:
        lines.append("OUTLIERS (IQR Method):")
        lines.append("-" * 25)
        for col, count in report["outliers"].items():
            if count > 0:
                lines.append(f"{col}: {count} outliers")
        if not any(report["outliers"].values()):
            lines.append("No outliers detected")
        lines.append("")

    # Categorical summaries
    if "categorical_summary" in report:
        lines.append("CATEGORICAL COLUMNS:")
        lines.append("-" * 22)
        for col, info in report["categorical_summary"].items():
            lines.append(f"{col} ({info['unique_count']} unique values):")
            for value, count in info["top_values"].items():
                lines.append(f"  {value}: {count}")
            lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python data_quality_check.py input.csv [output_report.txt]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)

    try:
        # Load data
        print(f"Loading data from: {input_path}")
        if input_path.endswith(".csv"):
            df = pd.read_csv(input_path)
        elif input_path.endswith(".json"):
            df = pd.read_json(input_path)
        elif input_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(input_path)
        else:
            print("Unsupported file format. Trying CSV...")
            df = pd.read_csv(input_path)

        # Analyze data quality
        print("Analyzing data quality...")
        report = analyze_data_quality(df)
        report_text = generate_report_text(report)

        # Output results
        if output_path:
            with open(output_path, "w") as f:
                f.write(report_text)
            print(f"Report saved to: {output_path}")
        else:
            print("\n" + report_text)

    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
