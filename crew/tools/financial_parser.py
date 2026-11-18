"""Pandas-backed financial data parser."""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
from crewai.tools import BaseTool
from pydantic import Field


class FinancialParserTool(BaseTool):
    name: str = "financial_data_parser"
    description: str = (
        "Parse CSV text, validate numeric columns, and return summary statistics "
        "and a Markdown table. Input must be CSV text."
    )
    csv_input: Optional[str] = Field(default=None, exclude=True)

    def _run(self, csv_input: str) -> dict:
        return parse_financial_csv(csv_input)


def parse_financial_csv(csv_input: str) -> dict:
    if not isinstance(csv_input, str) or not csv_input.strip():
        return {"status": "error", "error": "CSV input is empty.", "summary": {}, "markdown": ""}

    try:
        frame = pd.read_csv(io.StringIO(csv_input))
    except Exception as exc:
        return {"status": "error", "error": f"Invalid CSV input: {exc}", "summary": {}, "markdown": ""}

    if frame.empty:
        return {"status": "error", "error": "The CSV dataset contains no rows.", "summary": {}, "markdown": ""}

    if len(frame.columns) == 0:
        return {"status": "error", "error": "The CSV dataset has no columns.", "summary": {}, "markdown": ""}

    numeric = frame.apply(pd.to_numeric, errors="coerce")
    invalid_counts = frame.apply(
        lambda column: column.notna().sum() - pd.to_numeric(column, errors="coerce").notna().sum()
    )

    result = {}
    details = []
    for column in numeric.columns:
        series = numeric[column].dropna()
        if series.empty:
            result[column] = {"count": 0, "valid": False, "reason": "No valid numeric values."}
            continue
        result[column] = {
            "count": int(series.count()),
            "valid": True,
            "mean": round(float(series.mean()), 6),
            "median": round(float(series.median()), 6),
            "min": round(float(series.min()), 6),
            "max": round(float(series.max()), 6),
            "std": round(float(series.std()), 6),
            "missing": int(frame[column].isna().sum()),
            "invalid": int(invalid_counts[column]),
        }
        details.append({
            "Column": column,
            "Count": int(series.count()),
            "Mean": result[column]["mean"],
            "Median": result[column]["median"],
            "Minimum": result[column]["min"],
            "Maximum": result[column]["max"],
            "Std Dev": result[column]["std"],
        })

    if details:
        markdown = pd.DataFrame(details).to_markdown(index=False)
    else:
        markdown = "_No numeric columns with valid data._"

    return {"status": "ok", "summary": result, "markdown": markdown}
