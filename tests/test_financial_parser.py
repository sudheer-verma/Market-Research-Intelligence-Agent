"""Tests for the financial parser."""

import pytest

from crew.tools.financial_parser import parse_financial_csv


def test_valid_csv_statistics():
    result = parse_financial_csv("Revenue,Costs\n100,80\n200,120\n300,160\n")
    assert result["status"] == "ok"
    revenue = result["summary"]["Revenue"]
    assert revenue["mean"] == 200
    assert revenue["median"] == 200
    assert revenue["min"] == 100
    assert revenue["max"] == 300
    assert revenue["std"] == pytest.approx(100)


def test_missing_values():
    result = parse_financial_csv("Revenue\n100\nNaN\n300\n")
    assert result["status"] == "ok"
    revenue = result["summary"]["Revenue"]
    assert revenue["missing"] == 1
    assert revenue["count"] == 2
    assert revenue["mean"] == 200


def test_invalid_csv_input():
    result = parse_financial_csv("")
    assert result["status"] == "error"
    assert "empty" in result["error"].lower()


def test_empty_dataset():
    result = parse_financial_csv("Revenue\n")
    assert result["status"] in {"error", "ok"}


def test_invalid_values_are_not_silently_converted():
    result = parse_financial_csv("Revenue\nN/A\nunknown\n")
    assert result["status"] == "ok"
    assert result["summary"]["Revenue"]["valid"] is False


def test_markdown_table_is_generated():
    result = parse_financial_csv("Revenue\n100\n200\n")
    assert "|" in result["markdown"]
