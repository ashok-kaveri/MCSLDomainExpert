from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
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


OUTPUT_PATH = Path(
    "/Users/ashokkumarn/Documents/Pluginhive/AILearning/MCSLDomainExpert/output/support_guides/fedex_one_rate_support_guide.pdf"
)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="GuideTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.HexColor("#1F345B"),
            leading=26,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideSubtitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=12,
            textColor=colors.HexColor("#5A6273"),
            leading=16,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=colors.HexColor("#1F345B"),
            leading=19,
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            textColor=colors.HexColor("#1F345B"),
            leading=16,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
        )
    )
    styles.add(
        ParagraphStyle(
            name="GuideFooter",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#6B7280"),
        )
    )
    return styles


def bullet_list(items, style):
    return ListFlowable(
        [
            ListItem(Paragraph(item, style), leftIndent=0)
            for item in items
        ],
        bulletType="bullet",
        leftIndent=18,
        bulletFontName="Helvetica",
        bulletFontSize=9,
    )


def numbered_list(items, style):
    return ListFlowable(
        [
            ListItem(Paragraph(item, style), value=index + 1)
            for index, item in enumerate(items)
        ],
        bulletType="1",
        leftIndent=18,
    )


def add_page(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(doc.leftMargin, height - 0.45 * inch, "FedEx One Rate Support Guide")
    canvas.setStrokeColor(colors.HexColor("#D5DBE6"))
    canvas.setLineWidth(0.8)
    canvas.line(doc.leftMargin, height - 0.52 * inch, width - doc.rightMargin, height - 0.52 * inch)
    canvas.drawRightString(width - doc.rightMargin, 0.45 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def build_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        topMargin=0.9 * inch,
        bottomMargin=0.8 * inch,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
    )

    story = [
        Paragraph("Support Guide", styles["GuideTitle"]),
        Paragraph(
            "FedEx One Rate: One rate inclusion logic for domestic and international",
            styles["GuideSubtitle"],
        ),
    ]

    meta_data = [
        [Paragraph("<b>Card</b>", styles["GuideMeta"]), Paragraph("Trello card 6jBLYcry", styles["GuideMeta"])],
        [Paragraph("<b>Ticket</b>", styles["GuideMeta"]), Paragraph("Zendesk #382425", styles["GuideMeta"])],
        [Paragraph("<b>Area</b>", styles["GuideMeta"]), Paragraph("FedEx rating / label-generation settings", styles["GuideMeta"])],
        [Paragraph("<b>Audience</b>", styles["GuideMeta"]), Paragraph("Support and QA teams", styles["GuideMeta"])],
    ]
    meta_table = Table(meta_data, colWidths=[1.6 * inch, 5.1 * inch], hAlign="LEFT")
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E9EEF7")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D5DBE6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([meta_table, Spacer(1, 0.18 * inch)])

    story.extend(
        [
            Paragraph("Issue Summary", styles["GuideH1"]),
            Paragraph(
                "<b>Problem:</b> The FedEx One Rate setting and Duties & Taxes setting are currently tied to one shared toggle path. "
                "Because international rate requests are routed through the Transit API, enabling this shared behavior can cause international "
                "rate failures on stores where the toggle is enabled.",
                styles["GuideBody"],
            ),
            Paragraph(
                "<b>Goal of the change:</b> Split One Rate and Duties & Taxes into two independent settings so domestic One Rate behavior "
                "and international duties handling do not overlap.",
                styles["GuideBody"],
            ),
            Paragraph("Toggles", styles["GuideH1"]),
            bullet_list(
                [
                    "To enable/disable one rate - Enable carrier settings - Include One rate (no dependency with any toggles)",
                    'To enable Rates and trasmit rates api - <font name="Courier">"account-uudi.fedex.rest.rates.changes.enabled": true</font>',
                    "To get duties and taxes - enable toggle and enable carrier settings Include duties and taxes for rates",
                ],
                styles["GuideBody"],
            ),
            Paragraph("Support Understanding", styles["GuideH1"]),
            bullet_list(
                [
                    "One Rate should affect only eligible domestic FedEx flows.",
                    "Duties & Taxes should affect only international rating and label-generation behavior where customs handling is relevant.",
                    "Transit API international requests must not inherit One Rate logic accidentally.",
                    "The two settings must save, persist, and operate independently.",
                ],
                styles["GuideBody"],
            ),
            Spacer(1, 0.08 * inch),
            Paragraph("Recommended Support Workflow", styles["GuideH1"]),
            numbered_list(
                [
                    "Confirm whether the failing shipment is domestic or international.",
                    "Check the FedEx carrier settings and capture the current values for One Rate and Duties & Taxes separately.",
                    "If the issue is an international failure, verify whether One Rate is enabled and whether the failure started after that change.",
                    "Reproduce with one domestic order and one international order to confirm the settings are behaving independently.",
                    "Validate whether rates return successfully before and after toggling each setting individually.",
                    "Share request and error evidence with engineering if the international Transit API call still fails when Duties & Taxes is disabled or when only One Rate is enabled.",
                ],
                styles["GuideBody"],
            ),
            PageBreak(),
            Paragraph("Expected Fixed Behaviour", styles["GuideH1"]),
            bullet_list(
                [
                    "Domestic FedEx One Rate eligible orders continue to return One Rate services correctly.",
                    "International FedEx Transit API requests no longer fail because One Rate is enabled.",
                    "Duties & Taxes settings apply only to the intended international customs path.",
                    "Turning one setting on or off does not mutate or override the other setting.",
                    "Reopening FedEx carrier settings shows both saved values persisted independently.",
                ],
                styles["GuideBody"],
            ),
            Spacer(1, 0.08 * inch),
        ]
    )

    story.append(Paragraph("Support Notes", styles["GuideH1"]))
    note_table = Table(
        [[Paragraph(
            "Important: if a merchant reports only international rate failures after enabling a FedEx setting, "
            "verify that One Rate and Duties & Taxes are no longer sharing one implementation path. "
            "This card is specifically about separating those controls to avoid Transit API regressions.",
            styles["GuideBody"],
        )]],
        colWidths=[6.7 * inch],
        hAlign="LEFT",
    )
    note_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F9FC")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D5DBE6")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(note_table)

    doc.build(story, onFirstPage=add_page, onLaterPages=add_page)


if __name__ == "__main__":
    build_pdf()
