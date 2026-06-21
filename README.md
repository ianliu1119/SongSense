# SongFinder

A Shazam-style mobile app that finds songs from **a hummed tune, lyrics, genre, or freeform keywords** — matched against a 20-song demo catalog.

- **Frontend:** Expo / React Native — three tabs (Search · History · Saved)
- **Backend:** FastAPI + SQLite
- **Matching:** `sentence-transformers` text embeddings (cosine similarity)
- **Humming:** stubbed in phase 1, melody-matching planned for phase 2

---

## Project layout

```
backend/
  main.py          FastAPI app & endpoints
  db.py            SQLite schema, seeding, history/saved persistence
  matcher.py       embedding-based ranking engine
  songs_seed.py    the 20-song catalog
  requirements.txt
frontend/
  App.js           tab navigator
  screens/         SearchScreen, HistoryScreen, SavedScreen
  components/       shared result row + saved card
  lib/api.js       backend client
  package.json
```

## The 20-song catalog

Songs come in two kinds because **copyright** and **the right to play audio** are separate:

| Type | Examples | Searchable text | Playable preview |
|------|----------|-----------------|------------------|
| Public-domain classical | Mozart, Beethoven, Debussy, Vivaldi | yes | **yes** — composition is public domain; use free Musopen / IMSLP recordings |
| Modern copyrighted | Michael Jackson, Queen, Adele, Kendrick | yes | **no** — metadata only; hosting the recording would infringe |

Modern songs are still recognizable and fully searchable; they just show "preview unavailable." For the 10 classical entries, replace the `"PD_AUDIO"` placeholder in `songs_seed.py` with a URL to a hosted royalty-free clip.

---

## Running the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

First launch downloads the embedding model (~80 MB) and seeds `songfinder.db`.

## Running the frontend

```bash
cd frontend
npm install
npx expo start
```

Then scan the QR code with the Expo Go app.

> **Testing on a physical phone:** `localhost` in `lib/api.js` points at the *phone*, not your computer. Change `BASE_URL` to your computer's LAN IP, e.g. `http://192.168.1.42:8000`, and make sure both devices are on the same Wi-Fi.

---

## Phase 2 — query by humming

The hardest part, deliberately deferred. Real audio fingerprinting (what Shazam does) won't match a hum because a hum has no timbre or production — only melody. Plan:

1. **Reference melodies.** Give each of the 20 songs a `melody_contour`: a normalized pitch sequence of its main theme. Cleanest source is hand-made or extracted MIDI.
2. **Hum → contour.** Extract the pitch curve from the uploaded hum with `librosa` or `torchcrepe` (CREPE), normalize for key and tempo.
3. **Compare.** Use **DTW (dynamic time warping)** to align the hum contour against each song's reference contour; lower distance = better match.
4. **Blend.** Implement `score_hum()` in `matcher.py` and raise `w_hum` in the weighted blend so hum + text combine.

For 20 songs this is very feasible without any model training. An alternative is a hosted query-by-humming API (e.g. ACRCloud) if you'd rather not build melody extraction.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/search` | run a search (multipart: genre, lyric, extra, optional audio), store in history, return top 5 |
| GET | `/history` | list past searches |
| GET | `/history/{id}` | re-fetch a past search's top 5 |
| GET | `/saved` | list saved songs |
| POST | `/saved/{id}` | bookmark a song |
| DELETE | `/saved/{id}` | remove a bookmark |
| GET | `/songs` | full catalog (debug) |
