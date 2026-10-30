from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pathlib import Path


def render_pdf(content, output_path):

    Path(output_path).parent.mkdir(
        parents=True, exist_ok=True
    )

    doc = SimpleDocTemplate(
        output_path,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(content["title"], styles["Title"])
    )

    story.append(Spacer(1, 20))

    for section in content["sections"]:

        story.append(
            Paragraph(section["heading"], styles["Heading2"])
        )

        story.append(Spacer(1, 8))

        for paragraph in section.get("paragraphs", []):
            story.append(
                Paragraph(paragraph, styles["BodyText"])
            )
            story.append(Spacer(1, 10))

        if "table" in section:

            table = Table(section["table"])

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#1F4E78")),
                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5,
                 colors.grey),
                ("PADDING", (0, 0), (-1, -1), 8)
            ]))

            story.append(table)
            story.append(Spacer(1, 15))

    doc.build(story)

    return output_path