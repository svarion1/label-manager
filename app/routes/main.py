from flask import Blueprint, render_template, request
from  app import models

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    tab = request.args.get("tab", "generate")
    return render_template(
        "index.html",
        active_tab=tab,
        places=models.list_places(),
        rooms=models.list_rooms(),
        categories=models.list_categories(),
    )

@bp.route("/l/<uuid>")
def place_by_uuid(uuid):
    place = models.get_place_by_uuid(uuid)
    if not place:
        return render_template(
            "error.html", code=404,
            message="No place found for this label.",
        ), 404
    items = models.list_items_for_place(place["id"])
    categories = models.list_categories()
    return render_template(
        "place_detail.html",
        place=place,
        items=items,
        categories=categories,
    )