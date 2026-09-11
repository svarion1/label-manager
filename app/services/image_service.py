"""
Image processing: convert uploads to WebP and generate thumbnails.

Design goals:
- Never store the raw upload; always store the processed WebP.
- Cap the longest edge at MAX_IMAGE_DIM so a 40-megapixel phone photo
  doesn't eat disk.
- Generate a small thumbnail for list views.
- Preserve transparency (PNG/WebP with alpha stays RGBA).
- Animated GIFs: we keep only the first frame (inventory photos don't need
  motion, and animated WebP is much larger).
"""
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from flask import current_app


def _open_normalized(src_stream) -> Image.Image:
    """
    Open an uploaded file, apply EXIF orientation, and normalize to
    RGB or RGBA so WebP encoding always succeeds.
    """
    img = Image.open(src_stream)
    img = ImageOps.exif_transpose(img)

    # If it has alpha, keep it; otherwise flatten to RGB.
    if img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    ):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    return img


def _resize_to_max(img: Image.Image, max_dim: int) -> Image.Image:
    """Scale so the longest side <= max_dim. No-op if already smaller."""
    w, h = img.size
    longest = max(w, h)
    if longest <= max_dim:
        return img
    scale = max_dim / longest
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS)


def _save_webp(img: Image.Image, dest: Path, quality: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "WEBP", quality=quality, method=6)


def process_upload(file_storage, base_name: str):
    """
    Given a Werkzeug FileStorage, produce two files in UPLOAD_DIR:
        <base_name>.webp       - the full-size processed image
        <base_name>_thumb.webp - the thumbnail

    Returns:
        (main_filename, thumb_filename)  -- the names only, not paths.
    """
    cfg = current_app.config
    upload_dir = Path(cfg["UPLOAD_DIR"])

    img = _open_normalized(file_storage.stream)
    img = _resize_to_max(img, cfg["MAX_IMAGE_DIM"])

    main_name = f"{base_name}.webp"
    thumb_name = f"{base_name}_thumb.webp"

    _save_webp(img, upload_dir / main_name, cfg["WEBP_QUALITY"])

    # Thumbnail: proportional resize to THUMB_WIDTH on the long side.
    w, h = img.size
    if w >= h:
        tw = cfg["THUMB_WIDTH"]
        th = max(1, int(h * tw / w))
    else:
        th = cfg["THUMB_WIDTH"]
        tw = max(1, int(w * th / h))
    thumb = img.resize((tw, th), Image.LANCZOS)
    _save_webp(thumb, upload_dir / thumb_name, cfg["THUMB_QUALITY"])

    return main_name, thumb_name