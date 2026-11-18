"""Offline mock-mode tests."""

from crew.tools.mock_data import MOCK_CSV
from crew.tools.web_scraper import search_and_scrape
from crew.tools.financial_parser import parse_financial_csv
from main import mock_markdown


def test_mock_search_requires_no_api(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "true")
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    result = search_and_scrape("Tech Sector Q3 Analysis")
    assert result["status"] == "ok"
    assert result["mode"] == "MOCK"
    assert result["provider"] == "local_mock_fixture"


def test_mock_csv_produces_real_statistics():
    result = parse_financial_csv(MOCK_CSV)
    assert result["status"] == "ok"
    revenue = result["summary"]["Revenue_USD_Billions"]
    assert revenue["mean"] == 107.475
    assert revenue["median"] == 107.65
    assert revenue["min"] == 101.4
    assert revenue["max"] == 113.2
    assert "std" in revenue
    assert "|" in result["markdown"]


def test_mock_markdown_is_complete_and_labelled():
    report, financial_markdown, durations = mock_markdown("Tech Sector Q3 Analysis")
    assert "MOCK MODE" in report
    assert "not live market research" in report
    for section in (
        "Executive Summary",
        "Market Research Findings",
        "Financial Analysis",
        "Market Trends",
        "Risks and Limitations",
        "Conclusion",
        "Source References",
    ):
        assert section in report
    assert "|" in financial_markdown
    assert set(durations) == {
        "mock_researcher",
        "mock_financial_analyst",
        "mock_content_writer",
    }
