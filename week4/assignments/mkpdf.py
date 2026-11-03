"""Tiny helper: build a PDF from a list of blocks. Used for the written deliverables."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from PIL import Image as PILImage


def build(path, blocks, base=9.5, margin=1.8):
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=base, leading=base * 1.28, spaceAfter=3)
    h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=base + 6, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=base + 2, spaceBefore=6, spaceAfter=2)
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=margin * cm, rightMargin=margin * cm,
                            topMargin=margin * cm, bottomMargin=margin * cm)
    W = A4[0] - 2 * margin * cm
    out = []
    for b in blocks:
        k = b[0]
        if k == "h1": out.append(Paragraph(b[1], h1))
        elif k == "h2": out.append(Paragraph(b[1], h2))
        elif k == "p": out.append(Paragraph(b[1], body))
        elif k == "img":
            w, h = PILImage.open(b[1]).size
            iw = W * (b[2] if len(b) > 2 else 1.0)
            out.append(Image(b[1], width=iw, height=iw * h / w))
        elif k == "table":
            t = Table([[Paragraph(str(c), body) for c in r] for r in b[1]], colWidths=b[2] if len(b) > 2 else None)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            out.append(t)
        elif k == "sp": out.append(Spacer(1, b[1]))
        elif k == "pb": out.append(PageBreak())
    doc.build(out)
    return path
