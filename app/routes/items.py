import uuid as uuid_lib
from pathlib import Path

from flask import (Blueprint, request, redirect, url_for, flash,
                   abort, send_from_directory)
from app import models
from config import Config

bp = Blueprint("items", __name__)


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in Config.ALLOWED_EXTENSIONS


def _save_upload(file_storage):
    ext = Path(file_storage.filename).suffix.lower()
    name = f"{uuid_lib.uuid4().hex}{ext}"
    Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = Config.UPLOAD_DIR / name
    file_storage.save(dest)
    return name


@bp.route("/create", methods=["POST"])
def create_item():
    place_id = request.form.get("place_id", type=int)
    if not place_id or not models.get_place(place_id):
        flash("Invalid place.", "danger")
        return redirect(url_for("main.index", tab="closet"))

    item_id = models.create_item(
        place_id,
        title=(request.form.get("title") or "").strip() or None,
        category_id=request.form.get("category_id", type=int),
        subcategory=(request.form.get("subcategory") or "").strip() or None,
        notes=(request.form.get("notes") or "").strip() or None,
    )

    for f in request.files.getlist("photos"):
        if f and f.filename and _allowed(f.filename):
            models.add_photo(item_id, filepath=_save_upload(f))

    flash("Item added.", "success")
    return redirect(request.referrer or url_for("main.index", tab="closet"))


@bp.route("/<int:item_id>/edit", methods=["POST"])
def edit_item(item_id):
    if not models.get_item(item_id):
        abort(404)

    models.update_item(
        item_id,
        title=(request.form.get("title") or "").strip() or None,
        category_id=request.form.get("category_id", type=int),
        subcategory=(request.form.get("subcategory") or "").strip() or None,
        notes=(request.form.get("notes") or "").strip() or None,
    )
    for f in request.files.getlist("photos"):
        if f and f.filename and _allowed(f.filename):
            models.add_photo(item_id, filepath=_save_upload(f))

    flash("Item updated.", "success")
    return redirect(request.referrer or url_for("main.index", tab="edit"))


@bp.route("/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    models.soft_delete_item(item_id)
    flash("Item deleted.", "warning")
    return redirect(request.referrer or url_for("main.index", tab="edit"))


@bp.route("/photo/<int:photo_id>")
def serve_photo(photo_id):
    photo = models.get_photo(photo_id)
    if not photo:
        abort(404)
    return send_from_directory(Config.UPLOAD_DIR, photo["filepath"])


@bp.route("/photo/<int:photo_id>/delete", methods=["POST"])
def delete_photo(photo_id):
    photo = models.get_photo(photo_id)
    if not photo:
        abort(404)
    try:
        (Config.UPLOAD_DIR / photo["filepath"]).unlink(missing_ok=True)
    except Exception:
        pass
    models.delete_photo(photo_id)
    flash("Photo removed.", "success")
    return redirect(request.referrer or url_for("main.index", tab="edit"))