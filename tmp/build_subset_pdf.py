from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path("/Users/ashokkumarn/Documents/Pluginhive/AILearning/MCSLDomainExpert/out/fedex_new_transit_api_subset_styled.pdf")

LINES = [
    "FedEx: New Transit API",
    "",
    "Scenario: International shipment uses new transit API with duties and taxes disabled",
    "Given the FedEx REST rate changes feature toggle is ON",
    "And the shipment is international",
    "And the merchant has disabled estimated duties and taxes",
    "When the customer requests shipping rates at checkout",
    "Then the new FedEx transit API should be called",
    "And `edtRequestType` should be sent as `NONE`",
    "And the checkout rate should be returned successfully without duties and taxes added",
    "And the order summary should match the checkout rate",
    "",
    "Scenario: International shipment uses new transit API with duties and taxes enabled",
    "Given the FedEx REST rate changes feature toggle is ON",
    "And the shipment is international",
    "And the merchant has enabled estimated duties and taxes",
    "When the customer requests shipping rates at checkout",
    "Then the new FedEx transit API should be called",
    "And `edtRequestType` should be sent as `ALL`",
    "And duties and taxes should be included in the returned rating data",
    "And the shipping charge shown at checkout should reflect the returned duties and taxes behavior correctly",
    "And the order summary should match the checkout rate",
    "",
    "Scenario: One Rate inclusion setting ON returns lower-rate selection behavior",
    "Given the FedEx REST rate changes feature toggle is ON",
    "And the shipment is domestic",
    "And the merchant has enabled the One Rate related carrier setting",
    "When the customer requests shipping rates at checkout",
    "Then the rate display option sent to FedEx should be `LOWER_RATE`",
    "And the returned service price should follow the lower-rate selection logic",
    "And checkout and order summary should match the selected returned rate",
    "",
    "Scenario: One Rate inclusion setting OFF excludes F1R rates",
    "Given the FedEx REST rate changes feature toggle is ON",
    "And the shipment is domestic",
    "And the merchant has disabled the One Rate related carrier setting",
    "When the customer requests shipping rates at checkout",
    "Then the rate display option sent to FedEx should be `SELECTED_RATES_EXCLUDING_F1R`",
    "And FedEx One Rate results should not be returned",
    "And checkout and order summary should match the selected returned rate",
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
    canvas.drawString(doc.leftMargin, page_height - 0.55 * inch, "FedEx: New Transit API")

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#5b6575"))
    canvas.drawString(doc.leftMargin, 0.42 * inch, "BDD scenarios formatted for sharing")
    canvas.drawRightString(page_width - doc.rightMargin, 0.42 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#16324f"),
    )
    scenario = ParagraphStyle(
        "Scenario",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#173f5f"),
        spaceBefore=0,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=4,
        leftIndent=14,
        textColor=colors.HexColor("#1f2937"),
    )

    story = [
        Spacer(1, 0.15 * inch),
        Paragraph("FedEx: New Transit API", title),
        Spacer(1, 0.22 * inch),
    ]

    intro = Table(
        [[Paragraph(LINES[0], ParagraphStyle(
            "Intro",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#16324f"),
            alignment=TA_CENTER,
        ))]],
        colWidths=[6.65 * inch],
    )
    intro.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d7deea")),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.extend([intro, Spacer(1, 0.18 * inch)])

    current_block = []
    for line in LINES[2:] + [""]:
        if line:
            current_block.append(line)
            continue
        if not current_block:
            continue
        block_story = []
        for idx, block_line in enumerate(current_block):
            if idx == 0:
                block_story.append(Paragraph(block_line, scenario))
            else:
                block_story.append(Paragraph(block_line, body))
        card = Table([[block_story]], colWidths=[6.65 * inch])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d7deea")),
            ("LINEBEFORE", (0, 0), (0, 0), 4, colors.HexColor("#2f6b9a")),
            ("LEFTPADDING", (0, 0), (-1, -1), 18),
            ("RIGHTPADDING", (0, 0), (-1, -1), 18),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(KeepTogether([card, Spacer(1, 0.14 * inch)]))
        current_block = []

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=1.15 * inch,
        bottomMargin=0.7 * inch,
    )
    doc.build(story, onFirstPage=header, onLaterPages=header)
    print(OUTPUT)


if __name__ == "__main__":
    main()
