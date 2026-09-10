CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    room TEXT,
    category TEXT,
    subcategory TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id INTEGER NOT NULL,
    filepath TEXT NOT NULL,
    title TEXT,
    category TEXT,
    subcategory TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (place_id) REFERENCES places(id)
);