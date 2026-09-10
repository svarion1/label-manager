import sqlite3
from flask import current_app, g

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
    color      TEXT DEFAULT '#6c757d',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS places (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid        TEXT NOT NULL UNIQUE,
    short_code  TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    room        TEXT,
    notes       TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now')),
    deleted_at  TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id     INTEGER NOT NULL REFERENCES places(id),
    title        TEXT,
    category_id  INTEGER REFERENCES categories(id),
    subcategory  TEXT,
    notes        TEXT,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now')),
    deleted_at   TEXT
);

CREATE TABLE IF NOT EXISTS item_photos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id    INTEGER NOT NULL REFERENCES items(id),
    filepath   TEXT NOT NULL,
    thumb_path TEXT,
    position   INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_places_uuid    ON places(uuid);
CREATE INDEX IF NOT EXISTS idx_places_deleted ON places(deleted_at);
CREATE INDEX IF NOT EXISTS idx_items_place    ON items(place_id);
CREATE INDEX IF NOT EXISTS idx_photos_item    ON item_photos(item_id);
"""

DEFAULT_CATEGORIES = [
    ("Tools",       "#e67e22"),
    ("Books",       "#3498db"),
    ("Clothes",     "#9b59b6"),
    ("Electronics", "#2ecc71"),
    ("Documents",   "#f1c40f"),
    ("Kitchen",     "#e74c3c"),
    ("Other",       "#6c757d"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DB_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) AS c FROM categories").fetchone()["c"] == 0:
        db.executemany(
            "INSERT INTO categories (name, color) VALUES (?, ?)",
            DEFAULT_CATEGORIES,
        )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()