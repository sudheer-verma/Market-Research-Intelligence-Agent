"""Clearly labelled sample data for offline mock execution."""

from __future__ import annotations

from datetime import datetime, timezone


MOCK_CSV = """Quarter,Revenue_USD_Billions,Cloud_Growth_Percent,AI_Revenue_USD_Billions
2025-Q1,101.4,18.2,14.8
2025-Q2,105.8,19.6,16.2
2025-Q3,109.5,21.1,18.4
2025-Q4,113.2,22.4,20.1
"""


def get_mock_research(query: str) -> dict:
    return {
        "status": "ok",
        "mode": "MOCK",
        "provider": "local_mock_fixture",
        "query": query,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "notice": (
            "All findings below are illustrative sample data for offline testing. "
            "They are not live market research and must not be interpreted as facts."
        ),
        "results": [
            {
                "title": "MOCK: Technology demand remained resilient",
                "url": "mock://sample/technology-demand",
                "snippet": (
                    "Illustrative finding: enterprise AI, cloud infrastructure, and "
                    "cybersecurity products showed positive demand."
                ),
                "content": (
                    "Illustrative scenario: recurring software revenue and AI-related "
                    "spending increased across the sample quarter, while investment "
                    "capacity and valuation sensitivity remained variable."
                ),
                "retrieval_error": None,
                "mock": True,
            },
            {
                "title": "MOCK: Competitive and margin pressure",
                "url": "mock://sample/competitive-pressure",
                "snippet": (
                    "Illustrative finding: competition and infrastructure costs may "
                    "limit near-term margin expansion."
                ),
                "content": (
                    "Illustrative scenario: infrastructure investment, talent cost, "
                    "and customer concentration could affect profitability and execution."
                ),
                "retrieval_error": None,
                "mock": True,
            },
        ],
    }
