"""Programmatic professional PDF report generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_pages)
        for page in self._saved_pages:
            self.__dict__.update(page)
            self._draw_header_footer(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_header_footer(self, page_count: int):
        width, height = A4
        self.setFillColor(colors.HexColor("#17324D"))
        self.rect(0, height - 0.62 * inch, width, 0.62 * inch, fill=1, stroke=0)
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 9)
        self.drawString(0.55 * inch, height - 0.38 * inch, "MARKET RESEARCH REPORT")
        self.setStrokeColor(colors.HexColor("#D5A62A"))
        self.setLineWidth(2)
        self.line(0.55 * inch, height - 0.54 * inch, width - 0.55 * inch, height - 0.54 * inch)
        self.setFillColor(colors.HexColor("#596778"))
        self.setFont("Helvetica", 8)
        self.drawString(0.55 * inch, 0.42 * inch, f"Generated {datetime.now().strftime('%Y-%m-%d')}")
        self.drawRightString(width - 0.55 * inch, 0.42 * inch, f"Page {self._pageNumber} of {page_count}")


def _clean_paragraph(text: object) -> str:
    value = str(text or "").replace("\n", " ").strip()
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return value or "Not available."


def build_report_pdf(
    output_path: str | Path,
    query: str,
    report_markdown: str,
    financial_markdown: str = "",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.82 * inch,
        bottomMargin=0.62 * inch,
        title=f"Market Research Report: {query}",
        author="Multi-Agent Market Research Agent",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#17324D"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    h1 = ParagraphStyle(
        "Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#263746"),
        spaceAfter=7,
    )

    story = [
        Spacer(1, 0.12 * inch),
        Paragraph(_clean_paragraph(query), title),
        Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %H:%M')}",
            ParagraphStyle("Date", parent=body, alignment=TA_CENTER),
        ),
        Spacer(1, 0.18 * inch),
    ]

    sections = _split_markdown_sections(report_markdown)
    if not sections:
        sections = {"Executive Summary": ["No live report content was produced."]}

    wanted = [
        "Executive Summary",
        "Market Research Findings",
        "Financial Analysis",
        "Market Trends",
        "Risks and Limitations",
        "Conclusion",
        "Source References",
    ]
    for section_name in wanted:
        content = sections.get(section_name)
        if content:
            story.append(Paragraph(section_name, h1))
            for line in content:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("|"):
                    continue
                if line.startswith("- ") or line.startswith("* "):
                    story.append(Paragraph(_clean_paragraph(line[2:].strip()), body))
                else:
                    story.append(Paragraph(_clean_paragraph(line.lstrip("#").strip()), body))

    if financial_markdown.strip():
        story.append(Paragraph("Pandas Statistical Summary", h1))
        table = _markdown_table(financial_markdown)
        if table:
            story.append(table)
            story.append(Spacer(1, 0.12 * inch))

    story.append(Spacer(1, 0.14 * inch))
    doc.build(story, canvasmaker=NumberedCanvas)
    return output


def _split_markdown_sections(markdown: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            name = stripped[3:].strip()
            current = name
            sections[current] = []
        elif stripped.startswith("# ") and "Market Research Report" in stripped:
            continue
        elif current is not None:
            sections[current].append(raw_line)
    return sections


def _markdown_table(markdown: str) -> Table | None:
    rows = []
    for raw in markdown.splitlines():
        if raw.startswith("|") and "|" in raw[1:-1]:
            cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
            if set("".join(cells).replace("-", "").replace(":", "").strip()) == set():
                continue
            rows.append(cells)
    if len(rows) < 2:
        return None
    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    table = Table(normalized, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#AAB7C4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table
