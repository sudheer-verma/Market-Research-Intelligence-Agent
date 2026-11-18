"""Web and API-backed market research tool."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class WebScraperTool(BaseTool):
    name: str = "web_market_research"
    description: str = (
        "Search the web for a query and retrieve readable page text. "
        "Input must be a concise market research query."
    )

    def _run(self, query: str) -> dict:
        return search_and_scrape(query)


def _valid_http_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def search_and_scrape(query: str, max_results: int = 5) -> dict:
    if not isinstance(query, str) or not query.strip():
        return {"status": "error", "error": "Search query is empty.", "results": [], "retrieved_at": datetime.now(timezone.utc).isoformat()}

    if os.getenv("MOCK_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}:
        from .mock_data import get_mock_research
        return get_mock_research(query)

    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    serper_key = os.getenv("SERPER_API_KEY", "").strip()
    results = []
    provider = None

    if tavily_key:
        try:
            from tavily import TavilyClient
            response = TavilyClient(api_key=tavily_key).search(
                query=query, max_results=max_results, include_answer=False
            )
            provider = "tavily"
            for item in response.get("results", []):
                if _valid_http_url(item.get("url", "")):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item["url"],
                        "snippet": item.get("content", ""),
                    })
        except Exception as exc:
            provider = "tavily-error"
            results.append({"title": "Tavily error", "url": "", "snippet": str(exc)})

    elif serper_key:
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                json={"q": query},
                timeout=20,
            )
            response.raise_for_status()
            provider = "serper"
            for item in response.json().get("organic", [])[:max_results]:
                if _valid_http_url(item.get("link", "")):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item["link"],
                        "snippet": item.get("snippet", ""),
                    })
        except requests.RequestException as exc:
            provider = "serper-error"
            results.append({"title": "Serper error", "url": "", "snippet": str(exc)})
    else:
        return {
            "status": "error",
            "error": "Missing search credential: configure TAVILY_API_KEY or SERPER_API_KEY.",
            "results": [],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    for item in results:
        url = item.get("url")
        if not url:
            item["content"] = ""
            item["retrieval_error"] = "No accessible source URL."
            continue
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "MarketResearchAgent/1.0"},
                timeout=12,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = " ".join(soup.get_text(" ", strip=True).split())
            item["content"] = text[:12000]
            item["retrieval_error"] = None
        except requests.RequestException as exc:
            item["content"] = ""
            item["retrieval_error"] = f"Unable to retrieve page: {exc}"
        time.sleep(0.1)

    return {
        "status": "ok" if results else "error",
        "provider": provider,
        "query": query,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
