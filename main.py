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
from pdf_generator.report_builder import build_report_pdf


ROOT = Path(__file__).resolve().parent
BENCHMARK_PATH = ROOT / "benchmarks" / "benchmarks.json"
OUTPUT_PATH = ROOT / "output" / "market_report.pdf"


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
    if args.offline:
        print("Running in offline mode; live research and LLM calls will be skipped.")
        report_markdown = fallback_markdown(query)
        benchmark.record_task("offline_report", "completed", 0.0)
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
    print(f"Benchmark written: {BENCHMARK_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
