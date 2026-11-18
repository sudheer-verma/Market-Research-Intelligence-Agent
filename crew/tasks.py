"""Tasks for the hierarchical market research crew."""

from crewai import Task


def build_tasks(lead_researcher, data_analyst, content_writer) -> tuple[Task, Task, Task]:
    research_task = Task(
        description=(
            "Research this query: {query}. Use the web_market_research tool to find current, "
            "relevant market and financial information. Return findings with source URLs, "
            "retrieval timestamps, and clear statements for inaccessible sources."
        ),
        expected_output=(
            "A sourced research brief containing companies, financial metrics, market trends, "
            "source URLs, retrieval dates, and data gaps."
        ),
        agent=lead_researcher,
    )
    analysis_task = Task(
        description=(
            "Review the researcher findings for numeric market or financial datasets. "
            "Where CSV text is available, use the financial_data_parser tool. Produce "
            "summary statistics and a Markdown table. Never fabricate missing values."
        ),
        expected_output=(
            "A financial analysis with mean, median, minimum, maximum, and standard deviation "
            "for valid numeric columns, plus missing-data and source notes."
        ),
        agent=data_analyst,
        context=[research_task],
    )
    report_task = Task(
        description=(
            "Create a complete professional Markdown report for {query}. Include executive "
            "summary, market research findings, financial analysis, market trends, risks and "
            "limitations, conclusion, and source references. Base every claim on available "
            "research and explicitly label insufficient evidence."
        ),
        expected_output=(
            "A structured Markdown report beginning with '# Market Research Report' and "
            "containing all required sections."
        ),
        agent=content_writer,
        context=[research_task, analysis_task],
    )
    return research_task, analysis_task, report_task
