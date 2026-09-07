#!/usr/bin/env python3
"""Build the deterministic v0.63.26 bilingual learner-start PDF."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


rl_config.invariant = True

PAGE_WIDTH, PAGE_HEIGHT = A4
NAVY = colors.HexColor("#172033")
INDIGO = colors.HexColor("#5145CD")
TEAL = colors.HexColor("#0E7490")
PALE_INDIGO = colors.HexColor("#EEF2FF")
PALE_TEAL = colors.HexColor("#ECFEFF")
INK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#526074")
LINE = colors.HexColor("#D7DDEA")
WHITE = colors.white

ID_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/id/"
EN_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/en/"
REPO_URL = "https://github.com/KokunoYumeto/program-matematika-indonesia"
DOI_URL = "https://doi.org/10.5281/zenodo.22059707"


class DeterministicCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)
        self.setTitle("Program Matematika Indonesia - Panduan singkat / Quick start")
        self.setSubject("Bilingual learner-start guide for the public mathematics curriculum hub")
        self.setAuthor("Program Matematika Indonesia")
        self.setCreator("scripts/build-learner-start-pdf.py")


class Banner(Flowable):
    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.width = PAGE_WIDTH - 36 * mm
        self.height = 38 * mm

    def draw(self):
        self.canv.setFillColor(NAVY)
        self.canv.roundRect(0, 0, self.width, self.height, 5 * mm, fill=1, stroke=0)
        self.canv.setFillColor(colors.HexColor("#85E5F2"))
        self.canv.circle(self.width - 13 * mm, self.height - 12 * mm, 7 * mm, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 22)
        self.canv.drawString(8 * mm, self.height - 16 * mm, self.title)
        self.canv.setFont("Helvetica", 10.5)
        self.canv.drawString(8 * mm, self.height - 25 * mm, self.subtitle)
        self.canv.setFont("Helvetica-Bold", 8.5)
        self.canv.drawString(8 * mm, 6 * mm, "PUBLIC LEARNER GUIDE  |  VERSION 0.63.26")


class LinkCard(Flowable):
    def __init__(self, label: str, description: str, url: str, color: colors.Color):
        super().__init__()
        self.label = label
        self.description = description
        self.url = url
        self.color = color
        self.width = (PAGE_WIDTH - 44 * mm) / 2
        self.height = 34 * mm

    def draw(self):
        self.canv.setFillColor(colors.white)
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(1.2)
        self.canv.roundRect(0, 0, self.width, self.height, 4 * mm, fill=1, stroke=1)
        self.canv.setFillColor(self.color)
        self.canv.setFont("Helvetica-Bold", 15)
        self.canv.drawString(6 * mm, self.height - 10 * mm, self.label)
        self.canv.setFillColor(INK)
        self.canv.setFont("Helvetica", 8.7)
        self.canv.drawString(6 * mm, self.height - 18 * mm, self.description)
        shown = self.url.replace("https://", "")
        self.canv.setFillColor(self.color)
        self.canv.setFont("Helvetica-Bold", 7.4)
        if stringWidth(shown, "Helvetica-Bold", 7.4) > self.width - 12 * mm:
            while shown and stringWidth(shown + "...", "Helvetica-Bold", 7.4) > self.width - 12 * mm:
                shown = shown[:-1]
            shown += "..."
        self.canv.drawString(6 * mm, 6 * mm, shown)
        self.canv.linkURL(self.url, (0, 0, self.width, self.height), relative=0)


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "lead": ParagraphStyle(
            "Lead",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=INK,
            spaceAfter=4 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=NAVY,
            spaceBefore=2 * mm,
            spaceAfter=3 * mm,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=INK,
            spaceAfter=2 * mm,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=11.5,
            textColor=MUTED,
        ),
        "stat": ParagraphStyle(
            "Stat",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "statlabel": ParagraphStyle(
            "StatLabel",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=14,
            textColor=INK,
            leftIndent=2 * mm,
            rightIndent=2 * mm,
        ),
        "link": ParagraphStyle(
            "Link",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=13,
            textColor=INK,
            alignment=TA_LEFT,
        ),
    }


def page_chrome(canvas: Canvas, doc: BaseDocTemplate) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, PAGE_WIDTH - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 9 * mm, "Program Matematika Indonesia - bilingual public learning hub")
    canvas.drawRightString(PAGE_WIDTH - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    s = styles()
    doc = BaseDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=20 * mm,
        title="Program Matematika Indonesia - Panduan singkat / Quick start",
        author="Program Matematika Indonesia",
        subject="Bilingual learner-start guide",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", showBoundary=0)
    from reportlab.platypus import PageTemplate

    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_chrome)])

    stat_data = [
        [paragraph("40", s["stat"]), paragraph("25", s["stat"]), paragraph("83", s["stat"]), paragraph("40/40", s["stat"])],
        [
            paragraph("published course roles", s["statlabel"]),
            paragraph("HTML learner gateways", s["statlabel"]),
            paragraph("prerequisite links", s["statlabel"]),
            paragraph("common semantic adapters", s["statlabel"]),
        ],
    ]
    stats = Table(stat_data, colWidths=[doc.width / 4] * 4, rowHeights=[9 * mm, 9 * mm])
    stats.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_INDIGO),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))

    start_steps = [
        ("1", "Pilih bahasa / Choose a language", "Use one of the two public entrances above. You can switch language at any time."),
        ("2", "Pilih mata kuliah / Choose a course", "Use the course cards or the learning map to follow prerequisites and choose a sensible next step."),
        ("3", "Baca atau unduh / Read or download", "Open the hosted reader when available, or use the PDF, EPUB, HTML, and ZIP options shown on the course card."),
        ("4", "Tetap terhubung / Stay connected", "Course readers expose routes back to the program. The hub also keeps a prominent link to each authoritative original."),
    ]
    step_rows = []
    for number, heading, body in start_steps:
        number_cell = paragraph(f'<font color="#5145CD"><b>{number}</b></font>', s["stat"])
        text_cell = paragraph(f"<b>{heading}</b><br/>{body}", s["body"])
        step_rows.append([number_cell, text_cell])
    steps = Table(step_rows, colWidths=[12 * mm, doc.width - 12 * mm], rowHeights=[19 * mm] * 4)
    steps.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))

    link_table = Table([
        [LinkCard("Bahasa Indonesia", "Mulai dari antarmuka utama", ID_URL, INDIGO),
         LinkCard("English", "Start from the English interface", EN_URL, TEAL)]
    ], colWidths=[(doc.width - 6 * mm) / 2] * 2)
    link_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    story = [
        Banner("Program Matematika Indonesia", "Panduan singkat / Quick start"),
        Spacer(1, 6 * mm),
        paragraph(
            "Satu pintu masuk publik untuk kurikulum matematika modular. "
            "One public entrance for a modular mathematics curriculum, with readable course routes, downloads, and original-source links.",
            s["lead"],
        ),
        link_table,
        Spacer(1, 6 * mm),
        stats,
        Spacer(1, 6 * mm),
        paragraph("Cara memulai / How to start", s["section"]),
        steps,
        PageBreak(),
        paragraph("Yang tersedia / What the hub provides", s["section"]),
        paragraph(
            "<b>Hosted copy plus authoritative original.</b> When licensing and source structure allow it, the program presents a maintained hosted reader and a separate, prominent route to the upstream source. The mirror improves continuity; it does not erase provenance.",
            s["body"],
        ),
        paragraph(
            "<b>Multiple reading modes.</b> Course cards expose available HTML readers, PDFs, EPUBs, source archives, and offline packages. Formats vary honestly by course; the interface does not pretend every source has the same deliverables.",
            s["body"],
        ),
        paragraph(
            "<b>Portable navigation.</b> The release archive contains the bilingual maps, learner pages, checksums, rights and provenance records, and machine-readable course data needed for offline inspection and future language editions.",
            s["body"],
        ),
        Spacer(1, 3 * mm),
        paragraph("Scope yang jujur / Honest scope", s["section"]),
        Table(
            [[paragraph(
                "All 40 course roles are published in the central learner interface, and all 40 have a validated common semantic adapter. Native capability parity is currently verified for <b>12 of 40</b> roles. The common exchange layer is complete; native backend convergence is still continuing.",
                s["callout"],
            )]],
            colWidths=[doc.width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE_TEAL),
                ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
            ]),
        ),
        Spacer(1, 6 * mm),
        paragraph("Tautan permanen / Permanent links", s["section"]),
        KeepTogether([
            paragraph(f'<b>Program repository:</b> <link href="{REPO_URL}" color="#5145CD">{REPO_URL}</link>', s["link"]),
            paragraph(f'<b>Preservation DOI:</b> <link href="{DOI_URL}" color="#5145CD">{DOI_URL}</link>', s["link"]),
            paragraph(f'<b>Bahasa Indonesia:</b> <link href="{ID_URL}" color="#5145CD">{ID_URL}</link>', s["link"]),
            paragraph(f'<b>English:</b> <link href="{EN_URL}" color="#0E7490">{EN_URL}</link>', s["link"]),
        ]),
        Spacer(1, 8 * mm),
        paragraph(
            "Prepared with OpenAI Codex gpt-5.6-sol, Ultra, acting on the user's instructions. All inherited source, author, and human-contributor credits remain attached to their respective works.",
            s["small"],
        ),
    ]
    doc.build(story, canvasmaker=DeterministicCanvas)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.output.resolve())


if __name__ == "__main__":
    main()
