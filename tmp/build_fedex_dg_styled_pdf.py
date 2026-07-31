from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path("/Users/ashokkumarn/Documents/Pluginhive/AILearning/MCSLDomainExpert/out/FedEx_DG_Support_Requirement_Styled.pdf")

TITLE = "Support FedEx Dangerous Goods (DG) Options"
SUBTITLE = "Flow"
DESCRIPTION = (
    "As part of the new API changes in the FedEx app, we implemented the REST API integration. "
    "During implementation, FedEx Dangerous Goods (DG) support was not added."
)

SCENARIOS = [
    {
        "title": "Scenario: Display Dangerous Goods option in Product Settings",
        "lines": [
            "Given the customer opens the FedEx app Product Settings",
            "When adding product-specific settings",
            "Then an option called \"Is Dangerous Goods\" should be displayed in the UI.",
        ],
    },
    {
        "title": "Scenario: Display DG type options",
        "lines": [
            "Given the customer enables the \"Is Dangerous Goods\" option",
            "Then the following options should be listed:",
            "• LIMITED_QUANTITIES_COMMODITIES",
            "• HAZARDOUS_MATERIALS",
            "• ORM_D",
        ],
    },
    {
        "title": "Scenario: Include DG details in Rate and Label APIs",
        "lines": [
            "Given a customer generates a label for an order that has Dangerous Goods enabled",
            "Then the Rate and Label API requests should include the specific Dangerous Goods nodes/details based on the selected DG type.",
        ],
    },
]


def header(canvas, doc):
    canvas.saveState()
    page_width, page_height = LETTER

    canvas.setFillColor(colors.HexColor("#f4f7fb"))
    canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    canvas.setFillColor(colors.HexColor("#16324f"))
    canvas.rect(0, page_height - 0.9 * inch, page_width, 0.9 * inch, stroke=0, fill=1)

    canvas.setFont("Helvetica-Bold", 16)
    canvas.setFillColor(colors.white)
    canvas.drawString(doc.leftMargin, page_height - 0.55 * inch, "FedEx DG Requirement")

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#5b6575"))
    canvas.drawString(doc.leftMargin, 0.42 * inch, "Styled requirement document")
    canvas.drawRightString(page_width - doc.rightMargin, 0.42 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def build_card(story_parts, width):
    card = Table([[story_parts]], colWidths=[width])
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d7deea")),
                ("LINEBEFORE", (0, 0), (0, 0), 4, colors.HexColor("#2f6b9a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return card


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.HexColor("#16324f"),
    )
    small_caps = ParagraphStyle(
        "SmallCaps",
        parent=styles["BodyText"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#667085"),
        spaceAfter=2,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=4,
    )
    scenario = ParagraphStyle(
        "Scenario",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#173f5f"),
        spaceAfter=6,
    )
    intro_style = ParagraphStyle(
        "Intro",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#16324f"),
        alignment=TA_CENTER,
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=1.15 * inch,
        bottomMargin=0.7 * inch,
    )

    content_width = 6.65 * inch
    story = [
        Spacer(1, 0.15 * inch),
        Paragraph(TITLE, title),
        Spacer(1, 0.06 * inch),
        Paragraph(SUBTITLE, small_caps),
        Spacer(1, 0.18 * inch),
    ]

    intro = Table([[Paragraph(TITLE, intro_style)]], colWidths=[content_width])
    intro.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d7deea")),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.extend([intro, Spacer(1, 0.18 * inch)])

    desc_parts = [Paragraph("Description", scenario), Paragraph(DESCRIPTION, body)]
    story.append(KeepTogether([build_card(desc_parts, content_width), Spacer(1, 0.14 * inch)]))

    for item in SCENARIOS:
        parts = [Paragraph(item["title"], scenario)]
        for line in item["lines"]:
            parts.append(Paragraph(line, body))
        story.append(KeepTogether([build_card(parts, content_width), Spacer(1, 0.14 * inch)]))

    doc.build(story, onFirstPage=header, onLaterPages=header)
    print(OUTPUT)


if __name__ == "__main__":
    main()
