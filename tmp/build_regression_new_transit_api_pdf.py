from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path("/Users/ashokkumarn/Documents/Pluginhive/AILearning/MCSLDomainExpert/out/Regression_cases_New_Transit_API.pdf")

TITLE = "Regression cases: New Transit API"

SCENARIOS = [
    {
        "title": "Scenario: International shipment uses new transit API for multi-package shipment",
        "lines": [
            "Given the FedEx REST rate changes feature toggle is ON",
            "And the shipment is international",
            "And max quantity handling is enabled",
            "When the customer requests shipping rates at checkout with multiple items in cart",
            "Then the new FedEx transit API should be called",
            "And the shipment should be split into multiple packages correctly",
            "And valid international shipping rates should be returned successfully",
            "And the order summary should match the checkout rate",
        ],
    },
    {
        "title": "Scenario: International shipment checkout rate matches order summary",
        "lines": [
            "Given the FedEx REST rate changes feature toggle is ON",
            "And the shipment is international",
            "When the customer requests shipping rates at checkout",
            "And places the order using an international carrier service",
            "Then the shipping charge in the order summary should match the checkout rate",
            "And the selected carrier service should remain unchanged after order creation",
        ],
    },
    {
        "title": "Scenario: International shipment with rate automation rule for products priced greater than or equal to 100",
        "lines": [
            "Given the FedEx REST rate changes feature toggle is ON",
            "And the shipment is international",
            "And a rate automation rule exists for the carrier",
            "When the customer requests international shipping rates for products priced greater than or equal to 100",
            "Then the new FedEx transit API should be called",
            "And shipping rates should be returned successfully",
            "And insured value or declared value should be included in the request",
        ],
    },
    {
        "title": "Scenario: International shipment label generation with delivery confirmation special service",
        "lines": [
            "Given the FedEx REST rate changes feature toggle is ON",
            "And the shipment is international",
            "And the product is configured with a delivery confirmation special service",
            "When the order is imported into the MCSL app",
            "And the merchant generates the shipping label",
            "Then the new FedEx transit API should be called",
            "And the label should be generated successfully",
            "And the request XML should contain the correct delivery confirmation or signature details based on the configured product setting",
            "And the shipment should be processed successfully",
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
    canvas.drawString(doc.leftMargin, page_height - 0.55 * inch, TITLE)

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#5b6575"))
    canvas.drawString(doc.leftMargin, 0.42 * inch, "BDD scenarios formatted for sharing")
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

    for item in SCENARIOS:
        parts = [Paragraph(item["title"], scenario)]
        for line in item["lines"]:
            parts.append(Paragraph(line, body))
        story.append(KeepTogether([build_card(parts, content_width), Spacer(1, 0.14 * inch)]))

    doc.build(story, onFirstPage=header, onLaterPages=header)
    print(OUTPUT)


if __name__ == "__main__":
    main()
