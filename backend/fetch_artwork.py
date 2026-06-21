"""Fetch album artwork URLs from iTunes for all songs and store in DB.

Run:  python3 fetch_artwork.py
"""

import json, sqlite3, time, urllib.request, urllib.parse
from pathlib import Path

DB_PATH = Path(__file__).parent / "songfinder.db"


def fetch_artwork(title, artist):
    term = urllib.parse.quote(f"{artist} {title}")
    url = f"https://api.deezer.com/search?q={term}&limit=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SongSense/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        for track in data.get("data", []):
            art = track.get("album", {}).get("cover_xl")
            if art and title.lower() in track.get("title", "").lower():
                return art
        for track in data.get("data", []):
            art = track.get("album", {}).get("cover_xl")
            if art:
                return art
    except Exception as e:
        print(f"  error: {e}")
    return None


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, title, artist, artwork_url FROM songs ORDER BY id").fetchall()
    missing = [(r[0], r[1], r[2]) for r in rows if not r[3]]
    print(f"{len(missing)} songs need artwork (out of {len(rows)} total)\n")

    for song_id, title, artist in missing:
        print(f"[{song_id}] {title} – {artist} ...", end=" ", flush=True)
        url = fetch_artwork(title, artist)
        print("✓" if url else "✗")
        if url:
            conn.execute("UPDATE songs SET artwork_url = ? WHERE id = ?", (url, song_id))
            conn.commit()
        time.sleep(0.3)

    total = conn.execute("SELECT COUNT(*) FROM songs WHERE artwork_url IS NOT NULL").fetchone()[0]
    print(f"\nDone! {total}/{len(rows)} songs have artwork.")
    conn.close()


if __name__ == "__main__":
    main()
