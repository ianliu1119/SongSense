"""Matching engine.

Phase 1: text matching via sentence-transformers.

Each song is turned into one descriptive string (title, artist, genre, moods,
lyric snippet, description) and embedded once at startup. A query (genre + lyric
+ extra info, concatenated) is embedded the same way and ranked by cosine
similarity.

Phase 2 hook: `score_hum()` is stubbed. When melody matching is built, blend its
score into `final_score` with a weight.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

import db

_MODEL_NAME = "all-MiniLM-L6-v2"   # small, fast, free, ~80MB
_model = None
_song_ids = []
_song_matrix = None   # (n_songs, dim) normalized embeddings


def _song_to_text(s):
    parts = [
        s["title"],
        s["artist"],
        " ".join(s["genre"]),
        " ".join(s["mood_keywords"]),
        s["lyric_snippet"] or "",
        s["description"] or "",
    ]
    return ". ".join(p for p in parts if p)


def _normalize(mat):
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def load_model():
    """Load the model and precompute song embeddings. Call once at startup."""
    global _model, _song_ids, _song_matrix
    _model = SentenceTransformer(_MODEL_NAME)
    songs = db.all_songs()
    _song_ids = [s["id"] for s in songs]
    texts = [_song_to_text(s) for s in songs]
    emb = _model.encode(texts, convert_to_numpy=True)
    _song_matrix = _normalize(emb)


def _build_query_text(genre, lyric, extra):
    parts = [genre or "", lyric or "", extra or ""]
    return ". ".join(p.strip() for p in parts if p and p.strip())


def score_text(genre, lyric, extra, top_k=5):
    """Return [(song_id, score)] for the top_k best text matches."""
    query = _build_query_text(genre, lyric, extra)
    if not query:
        return []
    q = _model.encode([query], convert_to_numpy=True)
    q = _normalize(q)[0]
    sims = _song_matrix @ q                      # cosine, since both normalized
    order = np.argsort(-sims)[:top_k]
    return [(_song_ids[i], float(sims[i])) for i in order]


def score_hum(audio_path, top_k=5):
    """Phase 2 stub. Returns [] so text-only ranking is used for now."""
    return []


def search(genre, lyric, extra, audio_path=None, top_k=5):
    """Combine available signals and return ranked song dicts with scores."""
    text_scores = dict(score_text(genre, lyric, extra, top_k=len(_song_ids)))
    hum_scores = dict(score_hum(audio_path, top_k=len(_song_ids))) if audio_path else {}

    # Weighted blend. With humming stubbed, this is text-only.
    w_text, w_hum = 1.0, 0.0
    combined = {}
    for sid in _song_ids:
        combined[sid] = w_text * text_scores.get(sid, 0.0) + w_hum * hum_scores.get(sid, 0.0)

    ranked = sorted(combined.items(), key=lambda kv: -kv[1])[:top_k]
    ids = [sid for sid, _ in ranked]
    songs = {s["id"]: s for s in db.songs_by_ids(ids)}
    out = []
    for sid, sc in ranked:
        s = dict(songs[sid])
        s["score"] = round(sc, 4)
        out.append(s)
    return out
