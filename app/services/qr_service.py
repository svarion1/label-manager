import uuid
import secrets
from io import BytesIO

import qrcode
from qrcode.image.svg import SvgPathImage

# No ambiguous characters (0/O, 1/I/L)
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_uuid() -> str:
    return str(uuid.uuid4())


def new_short_code(length: int = 6) -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(length))
    return f"{raw[:3]}-{raw[3:]}"


def qr_png(data: str, box_size: int = 10, border: int = 2) -> BytesIO:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def qr_svg(data: str) -> BytesIO:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=SvgPathImage)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf