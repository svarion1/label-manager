from flask import (Blueprint, request, redirect, url_for, flash,
                   abort, send_file)
from app import models
from app.services import qr_service, pdf_service
from config import Config

bp = Blueprint("places", __name__)


@bp.route("/add", methods=["POST"])
def add_place():
    name = (request.form.get("name") or "").strip()
    room = (request.form.get("room") or "").strip() or None
    notes = (request.form.get("notes") or "").strip() or None

    if not name:
        flash("Place name cannot be empty.", "danger")
        return redirect(url_for("main.index", tab="generate"))

    place_uuid = qr_service.new_uuid()
    short_code = qr_service.new_short_code()
    models.create_place(
        uuid=place_uuid, short_code=short_code, name=name,
        room=room, notes=notes,
    )
    flash(f"Place '{name}' added (code {short_code}).", "success")
    return redirect(url_for("main.index", tab="generate"))


@bp.route("/categories/<int:category_id>/edit", methods=["POST"])
def edit_category(category_id):
    if not models.get_category(category_id):
        abort(404)
    name = (request.form.get("name") or "").strip()
    color = (request.form.get("color") or "#6c757d").strip()
    if not name:
        flash("Category name required.", "danger")
        return redirect(url_for("main.index", tab="edit"))
    try:
        models.update_category(category_id, name=name, color=color)
        flash(f"Category '{name}' updated.", "success")
    except Exception:
        flash("Another category already uses that name.", "warning")
    return redirect(url_for("main.index", tab="edit"))


@bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    cat = models.get_category(category_id)
    if not cat:
        abort(404)
    reassign_to = request.form.get("reassign_to", type=int)
    models.delete_category(category_id, reassign_to=reassign_to)
    if reassign_to:
        flash(f"'{cat['name']}' deleted, items moved.", "warning")
    else:
        flash(f"'{cat['name']}' deleted, items now uncategorized.", "warning")
    return redirect(url_for("main.index", tab="edit"))

@bp.route("/<int:place_id>/edit", methods=["POST"])
def edit_place(place_id):
    if not models.get_place(place_id):
        abort(404)
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Name cannot be empty.", "danger")
        return redirect(url_for("main.index", tab="edit"))

    models.update_place(
        place_id,
        name=name,
        room=(request.form.get("room") or "").strip() or None,
        notes=(request.form.get("notes") or "").strip() or None,
    )
    flash("Place updated.", "success")
    return redirect(url_for("main.index", tab="edit"))

@bp.route("/<int:place_id>/delete", methods=["POST"])
def delete_place(place_id):
    place = models.get_place(place_id)
    if not place:
        abort(404)
    models.soft_delete_place(place_id)
    flash(f"'{place['name']}' moved to trash.", "warning")
    return redirect(url_for("main.index", tab="edit"))


@bp.route("/<int:place_id>/restore", methods=["POST"])
def restore_place(place_id):
    models.restore_place(place_id)
    flash("Place restored.", "success")
    return redirect(url_for("main.index", tab="edit"))


@bp.route("/categories", methods=["POST"])
def add_category():
    name = (request.form.get("name") or "").strip()
    color = (request.form.get("color") or "#6c757d").strip()
    if not name:
        flash("Category name required.", "danger")
        return redirect(url_for("main.index", tab="edit"))
    try:
        models.create_category(name, color)
        flash(f"Category '{name}' created.", "success")
    except Exception:
        flash(f"Category '{name}' already exists.", "warning")
    return redirect(url_for("main.index", tab="edit"))


@bp.route("/<int:place_id>/qr.png")
def qr_png(place_id):
    place = models.get_place(place_id)
    if not place:
        abort(404)
    url = f"{Config.BASE_URL}/l/{place['uuid']}"
    return send_file(qr_service.qr_png(url), mimetype="image/png")