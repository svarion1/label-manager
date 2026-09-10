import qrcode
from fpdf import FPDF
from io import BytesIO

PAGE_W, PAGE_H = 210, 297  # A4 mm
MARGIN = 8
COLS, ROWS = 2, 11
LABELS_PER_PAGE = COLS * ROWS

CELL_W = (PAGE_W - 2 * MARGIN) / COLS
CELL_H = (PAGE_H - 2 * MARGIN) / ROWS

QR_SIZE = 24
PADDING = 2

def make_qr_image(data: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M, # type: ignore
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    # fpdf2 can misrender the 1-bit PNG returned by qrcode; use RGB instead.
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")  # type: ignore[attr-defined]
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf

def generate_pdf(places, output_path="output/labels.pdf"):
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.set_font("Helvetica", size=6)

    for i, place in enumerate(places):
        pos = i % LABELS_PER_PAGE
        if pos == 0:
            pdf.add_page()

        col = pos % COLS
        row = pos // COLS

        x = MARGIN + col * CELL_W
        y = MARGIN + row * CELL_H

        # Cell border
        pdf.rect(x, y, CELL_W, CELL_H)

        # QR code encodes only the UUID -> scanner app looks it up in DB
        qr_data = place["uuid"]
        qr_buf = make_qr_image(qr_data)
        pdf.image(qr_buf, x=x + PADDING, y=y + (CELL_H - QR_SIZE) / 2,
                   w=QR_SIZE, h=QR_SIZE)

        # Text area on the right
        text_x = x + QR_SIZE + PADDING * 2
        text_w = CELL_W - QR_SIZE - PADDING * 3
        pdf.set_xy(text_x, y + 5)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(text_w, 4, str(place["name"]), align="L")
        pdf.set_xy(text_x, y + CELL_H - 5)
        pdf.set_font("Helvetica", size=5)
        pdf.cell(text_w, 3, f"#{place['id']}", align="L")
        pdf.set_font("Helvetica", size=6)

    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    # Standalone test run without the UI
    class FakePlace(dict):
        def __getitem__(self, key):
            return dict.get(self, key)

    test_places = [
        FakePlace(id=i, uuid=f"test-uuid-{i}", name=f"Scatola {i}")
        for i in range(1, 65)
    ]
    generate_pdf(test_places, "output/labels_test.pdf")
    print("PDF generato in output/labels_test.pdf")