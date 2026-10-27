"""Local SQLite store for manually imported OLX listing links."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("chilipir.sqlite3")

@contextmanager
def connect(path=DB_PATH):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('arta','foto')),
            price_ron REAL NOT NULL CHECK(price_ron >= 0),
            reference_price_ron REAL,
            confidence REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        yield db
        db.commit()
    finally:
        db.close()

def save_listing(item, path=DB_PATH):
    with connect(path) as db:
        db.execute("""INSERT INTO listings
            (url,title,category,price_ron,reference_price_ron,confidence)
            VALUES (:url,:title,:category,:price_ron,:reference_price_ron,:confidence)
            ON CONFLICT(url) DO UPDATE SET title=excluded.title,
            price_ron=excluded.price_ron,reference_price_ron=excluded.reference_price_ron,
            confidence=excluded.confidence""", item)
        return db.execute("SELECT id FROM listings WHERE url=?", (item["url"],)).fetchone()[0]

def list_listings(path=DB_PATH):
    with connect(path) as db:
        return [dict(r) for r in db.execute("SELECT * FROM listings ORDER BY created_at DESC, id DESC")]
