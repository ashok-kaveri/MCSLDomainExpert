"""Render a Markdown test-scenarios document to a styled PDF.

Tailored for the MCSL TC markdown shape:
  # Title
  ## SECTION
  ### TC-n: title
  **Type:** / **Priority:** / **Preconditions:** / **Steps:**
  - bullet
  Given/When/And/Then lines

Usage:
  python scripts/md_test_scenarios_to_pdf.py <input.md> <output.pdf> ["Doc Title"] ["Subtitle"]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#1F345B")
GREY = colors.HexColor("#5A6273")
LIGHT = colors.HexColor("#EEF1F6")

TYPE_COLORS = {
    "Positive": colors.HexColor("#1B7F4B"),
    "Negative": colors.HexColor("#B23B3B"),
    "Edge Case": colors.HexColor("#B5791F"),
    "Edge": colors.HexColor("#B5791F"),
}
PRIORITY_COLORS = {
    "High": colors.HexColor("#B23B3B"),
    "Medium": colors.HexColor("#B5791F"),
    "Low": colors.HexColor("#1B7F4B"),
}


_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002190-\U000021FF️⬀-⯿]"
)


def esc(text: str) -> str:
    text = _EMOJI.sub("", text).strip()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # `code` -> mono
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" color="#1F345B">\1</font>', text)
    # **bold**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def build_styles():
    ss = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold",
                                fontSize=22, textColor=NAVY, leading=26, spaceAfter=4),
        "subtitle": ParagraphStyle("st", parent=ss["BodyText"], fontName="Helvetica-Oblique",
                                   fontSize=11, textColor=GREY, leading=15, spaceAfter=4),
        "meta": ParagraphStyle("m", parent=ss["BodyText"], fontName="Helvetica",
                               fontSize=9, textColor=GREY, leading=13),
        "section": ParagraphStyle("sec", parent=ss["Heading1"], fontName="Helvetica-Bold",
                                  fontSize=15, textColor=colors.white, leading=19,
                                  spaceBefore=6, spaceAfter=6, leftIndent=6),
        "tc": ParagraphStyle("tc", parent=ss["Heading2"], fontName="Helvetica-Bold",
                            fontSize=12, textColor=NAVY, leading=16, spaceBefore=10, spaceAfter=4),
        "label": ParagraphStyle("lbl", parent=ss["BodyText"], fontName="Helvetica-Bold",
                               fontSize=9.5, textColor=NAVY, leading=14, spaceBefore=2),
        "body": ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica",
                              fontSize=10, textColor=colors.HexColor("#222831"), leading=14),
        "bullet": ParagraphStyle("bl", parent=ss["BodyText"], fontName="Helvetica",
                                fontSize=10, textColor=colors.HexColor("#222831"),
                                leading=14, leftIndent=16, bulletIndent=4),
        "step": ParagraphStyle("step", parent=ss["BodyText"], fontName="Helvetica",
                              fontSize=10, textColor=colors.HexColor("#222831"),
                              leading=15, leftIndent=14),
    }
    return styles


def section_bar(text, styles):
    t = Table([[Paragraph(text, styles["section"])]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def badge_row(type_val, prio_val, styles):
    cells = []
    widths = []
    if type_val:
        c = TYPE_COLORS.get(type_val.strip(), GREY)
        cells.append(Paragraph(f'<font color="white"><b>{esc(type_val)}</b></font>', styles["meta"]))
        widths.append(1.5 * inch)
    if prio_val:
        cells.append(Paragraph(f'<font color="white"><b>Priority: {esc(prio_val)}</b></font>', styles["meta"]))
        widths.append(1.7 * inch)
    if not cells:
        return None
    t = Table([cells], colWidths=widths, hAlign="LEFT")
    style = [("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
             ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    col = 0
    if type_val:
        style.append(("BACKGROUND", (col, 0), (col, 0), TYPE_COLORS.get(type_val.strip(), GREY)))
        col += 1
    if prio_val:
        style.append(("BACKGROUND", (col, 0), (col, 0), PRIORITY_COLORS.get(prio_val.strip(), GREY)))
    t.setStyle(TableStyle(style))
    return t


def render(md_path: Path, pdf_path: Path, doc_title: str, subtitle: str):
    styles = build_styles()
    lines = md_path.read_text().splitlines()
    story = []

    story.append(Paragraph(esc(doc_title), styles["title"]))
    if subtitle:
        story.append(Paragraph(esc(subtitle), styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceBefore=4, spaceAfter=10))

    pending_type = None
    pending_prio = None

    def flush_badges():
        nonlocal pending_type, pending_prio
        if pending_type or pending_prio:
            br = badge_row(pending_type, pending_prio, styles)
            if br:
                story.append(Spacer(1, 2))
                story.append(br)
            pending_type = None
            pending_prio = None

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or set(stripped) <= {"-", "_", "*"} and len(stripped) >= 3:
            # horizontal rule or blank
            continue
        if stripped.startswith("# ") and not stripped.startswith("## "):
            # top title in md — skip, we use our own
            continue
        if stripped.startswith("## "):
            flush_badges()
            txt = re.sub(r"^##\s*", "", stripped)
            txt = re.sub(r"^SECTION\s*\d+[:.]?\s*", "", txt, flags=re.I)
            story.append(Spacer(1, 8))
            story.append(section_bar(esc(txt), styles))
            story.append(Spacer(1, 4))
            continue
        if stripped.startswith("### "):
            flush_badges()
            txt = re.sub(r"^###\s*", "", stripped)
            story.append(Paragraph(esc(txt), styles["tc"]))
            continue
        m = re.match(r"\*\*Type:\*\*\s*(.+)", stripped)
        if m:
            pending_type = m.group(1).strip()
            continue
        m = re.match(r"\*\*Priority:\*\*\s*(.+)", stripped)
        if m:
            pending_prio = m.group(1).strip()
            flush_badges()
            continue
        m = re.match(r"\*\*(Preconditions|Steps|Expected Result|Test Data):\*\*\s*(.*)", stripped)
        if m:
            flush_badges()
            story.append(Paragraph(f"{m.group(1)}:", styles["label"]))
            if m.group(2).strip():
                story.append(Paragraph(esc(m.group(2).strip()), styles["body"]))
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            story.append(Paragraph(esc(stripped[2:]), styles["bullet"], bulletText="•"))
            continue
        if re.match(r"^(Given|When|And|Then|But)\b", stripped):
            kw = re.match(r"^(\w+)", stripped).group(1)
            rest = stripped[len(kw):]
            story.append(Paragraph(f'<font color="#1F345B"><b>{kw}</b></font> {esc(rest)}', styles["step"]))
            continue
        story.append(Paragraph(esc(stripped), styles["body"]))

    flush_badges()

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=doc_title,
    )

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)
        canvas.drawString(0.7 * inch, 0.45 * inch, doc_title)
        canvas.drawRightString(A4[0] - 0.7 * inch, 0.45 * inch, f"Page {d.page}")
        canvas.setStrokeColor(LIGHT)
        canvas.line(0.7 * inch, 0.6 * inch, A4[0] - 0.7 * inch, 0.6 * inch)
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("PDF written:", pdf_path)


if __name__ == "__main__":
    inp = Path(sys.argv[1])
    outp = Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else "Test Scenarios"
    sub = sys.argv[4] if len(sys.argv) > 4 else ""
    outp.parent.mkdir(parents=True, exist_ok=True)
    render(inp, outp, title, sub)
