from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr as rl_qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


# Avery-style grid: 3 cols x 8 rows on A4
COLS = 3
ROWS = 8
PAGE_W, PAGE_H = A4
MARGIN_X = 8 * mm
MARGIN_Y = 12 * mm
LABEL_W = (PAGE_W - 2 * MARGIN_X) / COLS
LABEL_H = (PAGE_H - 2 * MARGIN_Y) / ROWS


def _draw_label(c, x, y, w, h, place, base_url):
    # Border
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.3)
    c.rect(x, y, w, h)

    # QR code
    url = f"{base_url}/l/{place['uuid']}"
    qr_widget = rl_qr.QrCodeWidget(url)
    b = qr_widget.getBounds()
    qr_native_w = b[2] - b[0]
    qr_native_h = b[3] - b[1]

    qr_size = min(w, h) * 0.55
    qr_x = x + (w - qr_size) / 2
    qr_y = y + h - qr_size - 3 * mm

    d = Drawing(qr_size, qr_size, transform=[
        qr_size / qr_native_w, 0, 0, qr_size / qr_native_h, 0, 0
    ])
    d.add(qr_widget)
    renderPDF.draw(d, c, qr_x, qr_y)

    # Short code (readable, printed below the QR)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + w / 2, y + h - qr_size - 7 * mm,
                        place["short_code"])

    # Name
    c.setFont("Helvetica", 8)
    name = (place["name"] or "")[:28]
    c.drawCentredString(x + w / 2, y + 4 * mm, name)

    # Room
    if place["room"]:
        c.setFont("Helvetica-Oblique", 6.5)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        room = place["room"][:32]
        c.drawCentredString(x + w / 2, y + 1.5 * mm, room)


def build_pdf(places, base_url: str) -> BytesIO:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    idx = 0
    total = len(places)

    while idx < total:
        for row in range(ROWS):
            for col in range(COLS):
                if idx >= total:
                    break
                place = places[idx]
                x = MARGIN_X + col * LABEL_W
                y = PAGE_H - MARGIN_Y - (row + 1) * LABEL_H
                _draw_label(c, x, y, LABEL_W, LABEL_H, place, base_url)
                idx += 1
        c.showPage()

    c.save()
    buf.seek(0)
    return buf