"""Crew construction and hierarchical orchestration."""

from __future__ import annotations

import os

from crewai import Crew, LLM, Process

from .agents import build_agents
from .tasks import build_tasks


def create_market_research_crew(
    query: str,
    task_callback=None,
) -> tuple[Crew, object]:
    model_name = os.getenv("MODEL_NAME", "openai/gpt-4o-mini").strip()
    if not model_name:
        model_name = "openai/gpt-4o-mini"

    manager_llm = LLM(model=model_name, temperature=0.2)
    lead_researcher, data_analyst, content_writer = build_agents(manager_llm)
    research_task, analysis_task, report_task = build_tasks(
        lead_researcher, data_analyst, content_writer
    )

    crew = Crew(
        agents=[lead_researcher, data_analyst, content_writer],
        tasks=[research_task, analysis_task, report_task],
        process=Process.hierarchical,
        manager_llm=manager_llm,
        task_callback=task_callback,
        verbose=True,
    )
    return crew, report_task
