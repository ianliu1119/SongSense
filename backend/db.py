"""SQLite persistence layer.

One file, three tables:
  - songs           : the 20-song catalog (seeded once from songs_seed.py)
  - search_history  : every search the user runs (inputs + the 5 result ids)
  - saved_songs     : songs the user bookmarked

For a 20-song demo SQLite is plenty; the schema maps 1:1 onto Postgres later.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from songs_seed import SONGS

DB_PATH = Path(__file__).parent / "songfinder.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id            INTEGER PRIMARY KEY,
            title         TEXT NOT NULL,
            artist        TEXT NOT NULL,
            year          INTEGER,
            genre         TEXT,           -- json array
            lyric_snippet TEXT,
            mood_keywords TEXT,           -- json array
            description   TEXT,
            preview_url   TEXT,           -- null when no playable audio
            melody_contour TEXT,          -- json array, phase 2
            artwork_url   TEXT            -- album/single cover art
        )
    """)
    # migrate existing DBs that pre-date artwork_url
    cols = [r[1] for r in cur.execute("PRAGMA table_info(songs)").fetchall()]
    if "artwork_url" not in cols:
        cur.execute("ALTER TABLE songs ADD COLUMN artwork_url TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            label       TEXT,             -- short display label e.g. "80s jazz"
            genre       TEXT,
            lyric       TEXT,
            extra       TEXT,
            had_audio   INTEGER DEFAULT 0,
            result_ids  TEXT,             -- json array of song ids, in rank order
            created_at  TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_songs (
            song_id   INTEGER PRIMARY KEY,
            saved_at  TEXT,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
    """)

    conn.commit()
    _seed_songs(conn)
    conn.close()


def _seed_songs(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM songs")
    if cur.fetchone()["n"] > 0:
        return
    for s in SONGS:
        cur.execute(
            """INSERT INTO songs
               (id, title, artist, year, genre, lyric_snippet,
                mood_keywords, description, preview_url, melody_contour)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                s["id"], s["title"], s["artist"], s["year"],
                json.dumps(s["genre"]), s["lyric_snippet"],
                json.dumps(s["mood_keywords"]), s["description"],
                s["preview_url"], json.dumps(s["melody_contour"]),
            ),
        )
    conn.commit()


def _row_to_song(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "artist": row["artist"],
        "year": row["year"],
        "genre": json.loads(row["genre"] or "[]"),
        "lyric_snippet": row["lyric_snippet"],
        "mood_keywords": json.loads(row["mood_keywords"] or "[]"),
        "description": row["description"],
        "preview_url": row["preview_url"],
        "artwork_url": row["artwork_url"],
    }


def all_songs():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM songs ORDER BY id").fetchall()
    conn.close()
    return [_row_to_song(r) for r in rows]


def songs_by_ids(ids):
    if not ids:
        return []
    conn = get_conn()
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT * FROM songs WHERE id IN ({placeholders})", ids
    ).fetchall()
    conn.close()
    by_id = {r["id"]: _row_to_song(r) for r in rows}
    return [by_id[i] for i in ids if i in by_id]  # preserve rank order


# ---------- history ----------

def add_history(label, genre, lyric, extra, had_audio, result_ids):
    conn = get_conn()
    conn.execute(
        """INSERT INTO search_history
           (label, genre, lyric, extra, had_audio, result_ids, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (label, genre, lyric, extra, int(had_audio),
         json.dumps(result_ids), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def list_history():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM search_history ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "label": r["label"],
            "result_ids": json.loads(r["result_ids"] or "[]"),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def delete_history(history_id):
    conn = get_conn()
    conn.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()


def get_history_results(history_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT result_ids FROM search_history WHERE id = ?", (history_id,)
    ).fetchone()
    conn.close()
    if not row:
        return []
    return songs_by_ids(json.loads(row["result_ids"] or "[]"))


# ---------- saved ----------

def save_song(song_id):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO saved_songs (song_id, saved_at) VALUES (?, ?)",
        (song_id, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def unsave_song(song_id):
    conn = get_conn()
    conn.execute("DELETE FROM saved_songs WHERE song_id = ?", (song_id,))
    conn.commit()
    conn.close()


def list_saved():
    conn = get_conn()
    rows = conn.execute(
        """SELECT s.* FROM saved_songs sv
           JOIN songs s ON s.id = sv.song_id
           ORDER BY sv.saved_at DESC"""
    ).fetchall()
    conn.close()
    return [_row_to_song(r) for r in rows]
