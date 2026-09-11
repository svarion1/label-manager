import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR   = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
    DB_PATH    = DATA_DIR / "places.db"
    UPLOAD_DIR = DATA_DIR / "uploads"
    OUTPUT_DIR = DATA_DIR / "output"

    BASE_URL         = os.environ.get("BASE_URL", "http://localhost:5050")
    SECRET_KEY       = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    MAX_UPLOAD_SIZE  = int(os.environ.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Image processing
    MAX_IMAGE_DIM   = int(os.environ.get("MAX_IMAGE_DIM", 1920))   # longest side
    THUMB_WIDTH     = int(os.environ.get("THUMB_WIDTH", 400))
    WEBP_QUALITY    = int(os.environ.get("WEBP_QUALITY", 82))
    THUMB_QUALITY   = int(os.environ.get("THUMB_QUALITY", 75))

    @classmethod
    def init_dirs(cls):
        for d in (cls.DATA_DIR, cls.UPLOAD_DIR, cls.OUTPUT_DIR):
            d.mkdir(parents=True, exist_ok=True)