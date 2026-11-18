# Multi-Agent Market Research & Report Generator with CrewAI

## Project overview

This project uses a CrewAI hierarchical crew to research a market topic, analyze financial data, write a sourced Markdown report, and generate a professional PDF. It contains exactly three specialized agents coordinated by a CrewAI manager LLM.

## Architecture

- **Lead Researcher:** searches Tavily or Serper and scrapes accessible web pages.
- **Data Analyst:** validates CSV data with Pandas and produces statistics.
- **Content Writer:** produces a structured Markdown report.
- **Manager LLM:** dynamically delegates work using `Crew`, `Process.hierarchical`, and `manager_llm`.

## Folder structure

```text
market-research-agent/
├── crew/
│   ├── agents.py
│   ├── tasks.py
│   ├── crew.py
│   └── tools/
├── pdf_generator/
├── tests/
├── config/
├── data/
├── output/
├── benchmarks/
├── main.py
└── README.md
```

## Python requirements

- Windows, macOS, or Linux
- Python 3.12 recommended
- Internet access for live CrewAI research

## Setup

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## API key configuration

Copy `.env.example` to `.env`, then configure:

```text
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
SERPER_API_KEY=
MODEL_NAME=openai/gpt-4o-mini
```

One search credential is required: `TAVILY_API_KEY` or `SERPER_API_KEY`. Live execution also requires `OPENAI_API_KEY`.

## Run live hierarchical research

```powershell
python main.py --query "Tech Sector Q3 Analysis"
```

## Run offline PDF generation

```powershell
python main.py --query "Tech Sector Q3 Analysis" --offline
```

The offline command intentionally produces a report that clearly states that no live research was performed.

## Output

- PDF: `output/market_report.pdf`
- Benchmark JSON: `benchmarks/benchmarks.json`
- Environment template: `.env.example`

## Benchmarking

`benchmarks.json` records wall-clock start/end times, measured duration, task statuses, errors, PDF generation duration, and manager delegation fields when available. Measurements are not simulated.

## Tests

```powershell
pytest
```

Tests use temporary directories and mocked/offline data. They do not require paid APIs or internet access.

## Troubleshooting

- **Missing API credentials:** copy `.env.example` to `.env` and set at least one search key plus `OPENAI_API_KEY`.
- **CrewAI model errors:** verify `MODEL_NAME` and provider credentials.
- **PDF page count:** run tests or open `output/market_report.pdf`.
- **Dependency issues:** recreate the Python 3.12 virtual environment before reinstalling.

## Sample output

The PDF includes an A4 title banner, executive summary, findings, financial analysis, trends, risks, conclusion, source references, and `Page X of Y` numbering.
