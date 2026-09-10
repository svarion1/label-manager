from flask import Blueprint, request, send_file, redirect, url_for, flash
from app import models
from app.services import pdf_service
from config import Config

bp = Blueprint("labels", __name__)


@bp.route("/generate", methods=["POST"])
def generate_pdf():
    ids = [int(i) for i in request.form.getlist("place_ids") if i.isdigit()]

    if ids:
        places = [models.get_place(i) for i in ids]
        places = [p for p in places if p]
    else:
        places = models.list_places()

    if not places:
        flash("No places to print.", "warning")
        return redirect(url_for("main.index", tab="generate"))

    buf = pdf_service.build_pdf(places, Config.BASE_URL)
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="labels.pdf",
    )