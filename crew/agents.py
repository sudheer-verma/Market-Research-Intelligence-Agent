"""Specialized CrewAI agents."""

from crewai import Agent, LLM

from .tools.financial_parser import FinancialParserTool
from .tools.web_scraper import WebScraperTool


def build_agents(manager_llm: LLM) -> tuple[Agent, Agent, Agent]:
    lead_researcher = Agent(
        role="Market Research Specialist",
        goal="Find accurate, sourced market and financial information for: {query}",
        backstory=(
            "You are a rigorous market researcher. Search reliable sources, scrape accessible "
            "pages, preserve URLs and retrieval dates, and never fabricate facts."
        ),
        tools=[WebScraperTool()],
        llm=manager_llm,
        allow_delegation=False,
        verbose=True,
    )
    data_analyst = Agent(
        role="Financial Data Analyst",
        goal="Clean and statistically analyze supplied financial data without inventing values",
        backstory=(
            "You are an exacting financial analyst. Validate data, preserve source references, "
            "calculate requested statistics, and state clearly when data is insufficient."
        ),
        tools=[FinancialParserTool()],
        llm=manager_llm,
        allow_delegation=False,
        verbose=True,
    )
    content_writer = Agent(
        role="Technical Reports Writer",
        goal="Turn verified findings into a structured professional Markdown market report",
        backstory=(
            "You are a technical market-report writer. Summarize evidence, explain metrics, "
            "compare findings, and clearly discuss risks and limitations."
        ),
        llm=manager_llm,
        allow_delegation=False,
        verbose=True,
    )
    return lead_researcher, data_analyst, content_writer
