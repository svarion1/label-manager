from flask import Blueprint, render_template, jsonify, request
from  app import models

bp = Blueprint("scan", __name__)


def _normalize_uuid(value: str) -> str:
    if "/l/" in value:
        return value.rsplit("/l/", 1)[-1].strip()
    return value.strip()


@bp.route("/")
def scan_page():
    return render_template("scan.html")


@bp.route("/api/lookup")
def api_lookup():
    raw = request.args.get("uuid", "")
    uuid = _normalize_uuid(raw)
    if not uuid:
        return jsonify({"error": "missing uuid"}), 400
    place = models.get_place_by_uuid(uuid)
    if not place:
        return jsonify({"error": "not found", "uuid": uuid}), 404
    items = models.list_items_for_place(place["id"])
    return jsonify({
        "place": dict(place),
        "items": [dict(i) for i in items],
    })


@bp.route("/api/add_item", methods=["POST"])
def api_add_item():
    data = request.get_json(silent=True) or {}
    uuid = _normalize_uuid(data.get("uuid", ""))
    if not uuid:
        return jsonify({"error": "missing uuid"}), 400
    place = models.get_place_by_uuid(uuid)
    if not place:
        return jsonify({"error": "place not found"}), 404
    item_id = models.create_item(
        place["id"],
        title=data.get("title"),
        category_id=data.get("category_id"),
        notes=data.get("notes"),
    )
    return jsonify({"ok": True, "item_id": item_id})