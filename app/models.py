from app.db import get_db


# ---------- Categories ----------

def list_categories():
    return get_db().execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()


def create_category(name, color="#6c757d"):
    db = get_db()
    cur = db.execute(
        "INSERT INTO categories (name, color) VALUES (?, ?)",
        (name.strip(), color),
    )
    db.commit()
    return cur.lastrowid


# ---------- Places ----------
def list_places(include_deleted=False, room=None):
    db = get_db()
    sql = """
        SELECT p.*,
               (SELECT COUNT(*) FROM items i
                 WHERE i.place_id = p.id AND i.deleted_at IS NULL) AS item_count
        FROM places p
        WHERE 1 = 1
    """
    params = []
    if not include_deleted:
        sql += " AND p.deleted_at IS NULL"
    if room:
        sql += " AND p.room = ?"
        params.append(room)
    sql += " ORDER BY p.room, p.name"
    return db.execute(sql, params).fetchall()


def get_place(place_id, include_deleted=False):
    sql = "SELECT * FROM places WHERE id = ?"
    if not include_deleted:
        sql += " AND deleted_at IS NULL"
    return get_db().execute(sql, (place_id,)).fetchone()


def get_place_by_uuid(uuid):
    return get_db().execute(
        "SELECT * FROM places WHERE uuid = ? AND deleted_at IS NULL",
        (uuid,),
    ).fetchone()


def create_place(uuid, short_code, name, room=None, notes=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO places (uuid, short_code, name, room, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (uuid, short_code, name.strip(), room, notes),
    )
    db.commit()
    return cur.lastrowid


def update_place(place_id, **fields):
    allowed = {"name", "room", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    db = get_db()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE places SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        list(updates.values()) + [place_id],
    )
    db.commit()


def soft_delete_place(place_id):
    db = get_db()
    db.execute("UPDATE places SET deleted_at = datetime('now') WHERE id = ?",
               (place_id,))
    db.commit()


def restore_place(place_id):
    db = get_db()
    db.execute("UPDATE places SET deleted_at = NULL WHERE id = ?", (place_id,))
    db.commit()


def list_rooms():
    rows = get_db().execute(
        """SELECT DISTINCT room FROM places
           WHERE room IS NOT NULL AND room != '' AND deleted_at IS NULL
           ORDER BY room"""
    ).fetchall()
    return [r["room"] for r in rows]


# ---------- Items ----------

def list_items_for_place(place_id, include_deleted=False):
    db = get_db()
    sql = """
        SELECT i.*, c.name AS category_name, c.color AS category_color,
               (SELECT id FROM item_photos p
                 WHERE p.item_id = i.id
                 ORDER BY p.position, p.id LIMIT 1) AS first_photo_id
        FROM items i
        LEFT JOIN categories c ON c.id = i.category_id
        WHERE i.place_id = ?
    """
    if not include_deleted:
        sql += " AND i.deleted_at IS NULL"
    sql += " ORDER BY i.created_at DESC"
    return db.execute(sql, (place_id,)).fetchall()


def get_item(item_id, include_deleted=False):
    sql = """SELECT i.*, c.name AS category_name, c.color AS category_color
             FROM items i LEFT JOIN categories c ON c.id = i.category_id
             WHERE i.id = ?"""
    if not include_deleted:
        sql += " AND i.deleted_at IS NULL"
    return get_db().execute(sql, (item_id,)).fetchone()


def create_item(place_id, title=None, category_id=None,
                subcategory=None, notes=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO items (place_id, title, category_id, subcategory, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (place_id, title, category_id, subcategory, notes),
    )
    db.commit()
    return cur.lastrowid


def update_item(item_id, **fields):
    allowed = {"title", "category_id", "subcategory", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    db = get_db()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE items SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        list(updates.values()) + [item_id],
    )
    db.commit()

def soft_delete_item(item_id):
    db = get_db()
    db.execute("UPDATE items SET deleted_at = datetime('now') WHERE id = ?",
               (item_id,))
    db.commit()


# ---------- Photos ----------

def add_photo(item_id, filepath, thumb_path=None, position=0):
    db = get_db()
    cur = db.execute(
        """INSERT INTO item_photos (item_id, filepath, thumb_path, position)
           VALUES (?, ?, ?, ?)""",
        (item_id, filepath, thumb_path, position),
    )
    db.commit()
    return cur.lastrowid


def get_photo(photo_id):
    return get_db().execute(
        "SELECT * FROM item_photos WHERE id = ?", (photo_id,)
    ).fetchone()


def delete_photo(photo_id):
    db = get_db()
    db.execute("DELETE FROM item_photos WHERE id = ?", (photo_id,))
    db.commit()