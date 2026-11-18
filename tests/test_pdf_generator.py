"""Tests for PDF report generation."""

from pathlib import Path
from pypdf import PdfReader

from pdf_generator.report_builder import build_report_pdf


def test_pdf_creation(tmp_path: Path):
    output = tmp_path / "report.pdf"
    markdown = (
        "# Market Research Report\n"
        "## Executive Summary\nTest summary\n"
        "## Market Research Findings\nTest finding\n"
        "## Financial Analysis\nTest analysis\n"
        "## Market Trends\nTest trend\n"
        "## Risks and Limitations\nTest risk\n"
        "## Conclusion\nTest conclusion\n"
        "## Source References\nTest source\n"
    )
    result = build_report_pdf(output, "Tech Sector Q3 Analysis", markdown)
    assert result.exists()
    assert result.stat().st_size > 500


def test_pdf_structure_and_page_number(tmp_path: Path):
    output = tmp_path / "report.pdf"
    long_markdown = "# Market Research Report\n## Executive Summary\n" + ("Test content. " * 500)
    build_report_pdf(output, "Test Query", long_markdown)
    reader = PdfReader(str(output))
    assert len(reader.pages) >= 1
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Page " in text
