import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from generate_labels import generate_pdf

DB_PATH = "places.db"
OUTPUT_DIR = Path("output")
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open("schema.sql") as f:
        conn.executescript(f.read())
    columns = {row[1] for row in conn.execute("PRAGMA table_info(places)")}
    if "room" not in columns:
        conn.execute("ALTER TABLE places ADD COLUMN room TEXT")
    if "category" not in columns:
        conn.execute("ALTER TABLE places ADD COLUMN category TEXT")
    if "subcategory" not in columns:
        conn.execute("ALTER TABLE places ADD COLUMN subcategory TEXT")
    image_columns = {row[1] for row in conn.execute("PRAGMA table_info(images)")}
    if "title" not in image_columns:
        conn.execute("ALTER TABLE images ADD COLUMN title TEXT")
    if "category" not in image_columns:
        conn.execute("ALTER TABLE images ADD COLUMN category TEXT")
    if "subcategory" not in image_columns:
        conn.execute("ALTER TABLE images ADD COLUMN subcategory TEXT")
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    category = request.args.get("category", "").strip()
    subcategory = request.args.get("subcategory", "").strip()
    room = request.args.get("room", "").strip()
    place_id = request.args.get("place_id", "").strip()
    query = """
        SELECT images.*, places.name AS place_name, places.uuid,
               places.room
        FROM images
        JOIN places ON places.id = images.place_id
        WHERE 1=1
    """
    params = []
    if category:
        query += " AND images.category = ?"
        params.append(category)
    if subcategory:
        query += " AND images.subcategory = ?"
        params.append(subcategory)
    if room:
        query += " AND places.room = ?"
        params.append(room)
    if place_id:
        query += " AND places.id = ?"
        params.append(place_id)
    query += " ORDER BY images.category, images.subcategory, images.title, images.id DESC"
    objects = [dict(row) for row in conn.execute(query, params).fetchall()]
    for obj in objects:
        obj["filename"] = Path(obj["filepath"]).name
    categories = conn.execute(
        "SELECT DISTINCT category FROM images WHERE category IS NOT NULL AND category != '' ORDER BY category"
    ).fetchall()
    subcategories = conn.execute(
        "SELECT DISTINCT subcategory FROM images WHERE subcategory IS NOT NULL AND subcategory != '' ORDER BY subcategory"
    ).fetchall()
    rooms = conn.execute(
        "SELECT DISTINCT room FROM places WHERE room IS NOT NULL AND room != '' ORDER BY room"
    ).fetchall()
    places = conn.execute(
        "SELECT id, name, room FROM places ORDER BY name"
    ).fetchall()
    conn.close()
    return render_template(
        "index.html", objects=objects, categories=categories,
        subcategories=subcategories, selected_category=category,
        rooms=rooms, places=places, selected_room=room,
        selected_place_id=place_id, selected_subcategory=subcategory,
    )

@app.route("/add", methods=["POST"])
def add_place():
    names_raw = request.form.get("names", "")
    names = [n.strip() for n in names_raw.splitlines() if n.strip()]
    room = request.form.get("room", "").strip() or None
    conn = get_db()
    for name in names:
        conn.execute(
            "INSERT INTO places (uuid, name, room) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), name, room),
        )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:place_id>", methods=["GET", "POST"])
def edit_place(place_id):
    conn = get_db()
    place = conn.execute("SELECT * FROM places WHERE id = ?", (place_id,)).fetchone()
    if not place:
        conn.close()
        return "Place not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        room = request.form.get("room", "").strip() or None
        if name:
            conn.execute(
                "UPDATE places SET name = ?, room = ? WHERE id = ?",
                (name, room, place_id),
            )
            conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_place.html", place=place)

@app.route("/edit-object/<int:image_id>", methods=["GET", "POST"])
def edit_object(image_id):
    conn = get_db()
    image = conn.execute(
        "SELECT images.*, places.name AS place_name, places.uuid "
        "FROM images JOIN places ON places.id = images.place_id WHERE images.id = ?",
        (image_id,),
    ).fetchone()
    if not image:
        conn.close()
        return "Object not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip() or None
        subcategory = request.form.get("subcategory", "").strip() or None
        if title:
            conn.execute(
                "UPDATE images SET title = ?, category = ?, subcategory = ? WHERE id = ?",
                (title, category, subcategory, image_id),
            )
            conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_object.html", image=image)

@app.route("/delete/<int:place_id>", methods=["POST"])
def delete_place(place_id):
    conn = get_db()
    conn.execute("DELETE FROM places WHERE id = ?", (place_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/generate", methods=["POST"])
def generate():
    conn = get_db()
    places = conn.execute("SELECT * FROM places ORDER BY id ASC").fetchall()
    conn.close()
    pdf_path = OUTPUT_DIR / "labels.pdf"
    generate_pdf(places, str(pdf_path))
    return redirect(url_for("download_pdf"))

@app.route("/download")
def download_pdf():
    return send_from_directory(OUTPUT_DIR, "labels.pdf", as_attachment=True)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# === SCANNER MOBILE ===

@app.route("/scan")
def scan_page():
    return render_template("scan.html")

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json() or {}
    scanned_uuid = data.get("uuid", "").strip()
    if not scanned_uuid:
        return jsonify({"ok": False, "error": "No UUID provided"}), 400

    conn = get_db()
    place = conn.execute(
        "SELECT * FROM places WHERE uuid = ?", (scanned_uuid,)
    ).fetchone()
    conn.close()

    if not place:
        return jsonify({"ok": False, "error": "Place not found"}), 404

    return jsonify({
        "ok": True,
        "place": {
            "id": place["id"],
            "uuid": place["uuid"],
            "name": place["name"],
        }
    })

@app.route("/upload/<uuid>", methods=["GET", "POST"])
def upload_page(uuid):
    conn = get_db()
    place = conn.execute(
        "SELECT * FROM places WHERE uuid = ?", (uuid,)
    ).fetchone()
    conn.close()

    if not place:
        return "Place not found", 404

    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            return redirect(url_for("upload_page", uuid=uuid))

        # Salva file con nome sicuro
        filename = file.filename or "image.jpg"
        ext = Path(filename).suffix.lower() or ".jpg"
        safe_name = f"{uuid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = UPLOAD_DIR / safe_name
        file.save(str(filepath))
        title = request.form.get("title", "").strip() or filename
        category = request.form.get("category", "").strip() or None
        subcategory = request.form.get("subcategory", "").strip() or None

        # Inserisci record in DB
        conn = get_db()
        conn.execute(
            "INSERT INTO images (place_id, filepath, title, category, subcategory) VALUES (?, ?, ?, ?, ?)",
            (place["id"], str(filepath), title, category, subcategory),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("upload_success", uuid=uuid))

    return render_template("upload.html", place=place)

@app.route("/upload/<uuid>/success")
def upload_success(uuid):
    conn = get_db()
    place = conn.execute(
        "SELECT * FROM places WHERE uuid = ?", (uuid,)
    ).fetchone()
    images = [dict(row) for row in conn.execute(
        "SELECT * FROM images WHERE place_id = ? ORDER BY created_at DESC",
        (place["id"],)
    ).fetchall()]
    for image in images:
        image["filename"] = Path(image["filepath"]).name
    conn.close()
    return render_template("upload_success.html", place=place, images=images)

if __name__ == "__main__":
    init_db()

    app.run(debug=True, port=5050, host="0.0.0.0", ssl_context="adhoc")