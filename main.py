"""Command-line entry point for the market research agent."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from benchmarks.benchmark import Benchmark
from crew.crew import create_market_research_crew
from crew.tools.financial_parser import parse_financial_csv
from crew.tools.mock_data import MOCK_CSV, get_mock_research
from pdf_generator.report_builder import build_report_pdf


ROOT = Path(__file__).resolve().parent
BENCHMARK_PATH = ROOT / "benchmarks" / "benchmarks.json"
OUTPUT_PATH = ROOT / "output" / "market_report.pdf"
MARKDOWN_OUTPUT_PATH = ROOT / "output" / "market_report.md"


def validate_environment() -> list[str]:
    missing = []
    if not os.getenv("OPENAI_API_KEY", "").strip():
        missing.append("OPENAI_API_KEY")
    if not os.getenv("TAVILY_API_KEY", "").strip() and not os.getenv("SERPER_API_KEY", "").strip():
        missing.append("TAVILY_API_KEY or SERPER_API_KEY")
    return missing


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Generate a professional market research PDF using a CrewAI hierarchical agent team.",
    )
    parser.add_argument("--query", required=True, help='Market research query, e.g. "Tech Sector Q3 Analysis"')
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip live CrewAI execution and generate a clearly labeled offline report.",
    )
    return parser.parse_args(argv)


def validate_query(query: str) -> str:
    cleaned = " ".join(query.strip().split())
    if len(cleaned) < 3:
        raise ValueError("Query must contain at least 3 characters.")
    if len(cleaned) > 500:
        raise ValueError("Query must contain no more than 500 characters.")
    return cleaned


def fallback_markdown(query: str) -> str:
    return (
        "# Market Research Report\n\n"
        "## Executive Summary\n"
        "Live market research was not executed because required API credentials were not configured.\n\n"
        "## Market Research Findings\n"
        f"No verified findings are available for: {query}.\n\n"
        "## Financial Analysis\n"
        "Insufficient data: no valid source dataset was supplied.\n\n"
        "## Market Trends\n"
        "No market trends can be stated without sourced, live evidence.\n\n"
        "## Risks and Limitations\n"
        "This offline report does not contain live market or financial claims.\n\n"
        "## Conclusion\n"
        "Configure the required API keys and rerun the live hierarchical CrewAI workflow.\n\n"
        "## Source References\n"
        "No external sources were retrieved.\n"
    )


def mock_markdown(query: str) -> tuple[str, str, dict[str, float]]:
    research_start = time.perf_counter()
    research = get_mock_research(query)
    research_duration = time.perf_counter() - research_start

    analyst_start = time.perf_counter()
    parser = parse_financial_csv(MOCK_CSV)
    financial_markdown = parser["markdown"]
    analyst_duration = time.perf_counter() - analyst_start

    findings = "\n".join(
        f"- **{item['title'].replace('MOCK: ', '')}:** {item['snippet']}"
        for item in research["results"]
    )
    writer_start = time.perf_counter()
    report = (
        "# Market Research Report\n\n"
        "> **MOCK MODE:** This report uses clearly labelled illustrative sample data. "
        "It is not live market research and must not be treated as factual market evidence.\n\n"
        "## Executive Summary\n"
        f"This mock report provides an offline demonstration for: **{query}**. "
        "It illustrates resilient technology demand, AI and cloud growth, and "
        "competitive execution risks using synthetic fixture data.\n\n"
        "## Market Research Findings\n"
        f"{findings}\n\n"
        "## Financial Analysis\n"
        "The following real statistics were calculated with Pandas from the local mock CSV.\n\n"
        f"{financial_markdown}\n\n"
        "## Market Trends\n"
        "- Illustrative AI spending and cloud infrastructure demand remain growth themes.\n"
        "- Illustrative recurring software revenue shows a positive quarterly trend.\n"
        "- These trends come from mock fixture values, not current external observations.\n\n"
        "## Risks and Limitations\n"
        "- The data is synthetic and may not represent actual company or sector performance.\n"
        "- No live websites, search providers, or financial filings were accessed.\n"
        "- The report is suitable for UI, workflow, and PDF testing only.\n"
        "- Real decisions require independently verified sources and current financial data.\n\n"
        "## Conclusion\n"
        "MOCK MODE successfully demonstrates the research, analyst, writer, PDF, and benchmark workflow "
        "without API credentials. Activate live integrations only after configuring the required keys.\n\n"
        "## Source References\n"
        "- `mock://sample/technology-demand` - Illustrative technology-demand fixture.\n"
        "- `mock://sample/competitive-pressure` - Illustrative competitive-pressure fixture.\n"
        "- `local://data/mock_financial_data.csv` - Synthetic values from the local mock CSV fixture.\n"
    )
    writer_duration = time.perf_counter() - writer_start
    durations = {
        "mock_researcher": research_duration,
        "mock_financial_analyst": analyst_duration,
        "mock_content_writer": writer_duration,
    }
    return report, financial_markdown, durations


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    args = parse_arguments(argv)
    try:
        query = validate_query(args.query)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    benchmark = Benchmark(BENCHMARK_PATH)
    report_markdown = ""
    financial_markdown = ""
    mock_mode = (
        args.offline
        or os.getenv("MOCK_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}
    )
    if mock_mode:
        print("MOCK MODE: running without OpenAI, Tavily, or Serper API calls.")
        print("MOCK MODE: using clearly labelled illustrative research and financial data.")
        report_markdown, financial_markdown, mock_durations = mock_markdown(query)
        benchmark.record_task("mock_researcher", "completed", round(mock_durations["mock_researcher"], 6))
        benchmark.record_delegation("manager_mock_orchestrator", "mock_researcher", "illustrative market research")
        benchmark.record_task("mock_financial_analyst", "completed", round(mock_durations["mock_financial_analyst"], 6))
        benchmark.record_delegation("manager_mock_orchestrator", "mock_financial_analyst", "Pandas mock CSV analysis")
        benchmark.record_task("mock_content_writer", "completed", round(mock_durations["mock_content_writer"], 6))
        benchmark.record_delegation("manager_mock_orchestrator", "mock_content_writer", "Markdown report generation")
    else:
        missing = validate_environment()
        if missing:
            print(
                "Error: missing required environment variables: " + ", ".join(missing),
                file=sys.stderr,
            )
            print(
                "Configure .env from .env.example before live execution.",
                file=sys.stderr,
            )
            benchmark.record_error("Missing required API credentials: " + ", ".join(missing))
            benchmark.finish()
            return 3

        crew, report_task = create_market_research_crew(query)
        start = time.perf_counter()
        try:
            print(f"Starting hierarchical CrewAI research for: {query}")
            result = crew.kickoff(inputs={"query": query})
            report_markdown = str(result)
            benchmark.record_delegation("manager_llm", "hierarchical_crew", "market research and report generation")
            benchmark.record_task("hierarchical_crew", "completed", time.perf_counter() - start)
        except Exception as exc:
            elapsed = time.perf_counter() - start
            benchmark.record_task("hierarchical_crew", "failed", elapsed, str(exc))
            benchmark.record_error(exc)
            benchmark.finish()
            print(f"Error: CrewAI execution failed: {exc}", file=sys.stderr)
            return 1

    pdf_start = time.perf_counter()
    try:
        MARKDOWN_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        MARKDOWN_OUTPUT_PATH.write_text(report_markdown, encoding="utf-8")
        pdf_path = build_report_pdf(OUTPUT_PATH, query, report_markdown, financial_markdown)
        benchmark.pdf_duration_seconds = round(time.perf_counter() - pdf_start, 6)
        benchmark.record_task("pdf_generation", "completed", benchmark.pdf_duration_seconds)
        benchmark.finish()
    except Exception as exc:
        benchmark.pdf_duration_seconds = round(time.perf_counter() - pdf_start, 6)
        benchmark.record_task("pdf_generation", "failed", benchmark.pdf_duration_seconds, str(exc))
        benchmark.record_error(exc)
        benchmark.finish()
        print(f"Error: PDF generation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Report generated: {pdf_path}")
    print(f"Markdown report generated: {MARKDOWN_OUTPUT_PATH}")
    print(f"Benchmark written: {BENCHMARK_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
