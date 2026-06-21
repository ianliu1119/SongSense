"""FastAPI backend for SongFinder.

Endpoints:
  POST /search            run a search, store it in history, return top 5
  GET  /history           list past searches (label + time)
  GET  /history/{id}      re-fetch the top 5 results from a past search
  GET  /saved             list saved songs
  POST /saved/{song_id}   bookmark a song
  DELETE /saved/{song_id} remove a bookmark
  GET  /songs             full catalog (debug / demo)

Run:  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import db
import matcher

app = FastAPI(title="SongFinder API")

# Allow the Expo app (any origin in dev) to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.init_db()
    matcher.load_model()




@app.post("/search")
async def search(
    genre: str = Form(""),
    lyric: str = Form(""),
    extra: str = Form(""),
    audio: UploadFile | None = File(None),
):
    audio_path = None
    if audio is not None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
        with tmp as f:
            shutil.copyfileobj(audio.file, f)
        audio_path = tmp.name

    results = matcher.search(genre, lyric, extra, audio_path=audio_path, top_k=5)

    if audio_path:
        Path(audio_path).unlink(missing_ok=True)

    db.add_history(
        label=matcher.generate_label(genre, lyric, extra),
        genre=genre, lyric=lyric, extra=extra,
        had_audio=audio is not None,
        result_ids=[r["id"] for r in results],
    )
    return {"results": results}


@app.get("/history")
def history():
    return {"history": db.list_history()}


@app.get("/history/{history_id}")
def history_results(history_id: int):
    return {"results": db.get_history_results(history_id)}


@app.delete("/history/{history_id}")
def delete_history(history_id: int):
    db.delete_history(history_id)
    return {"ok": True}


@app.get("/saved")
def saved():
    return {"saved": db.list_saved()}


@app.post("/saved/{song_id}")
def save(song_id: int):
    db.save_song(song_id)
    return {"ok": True}


@app.delete("/saved/{song_id}")
def unsave(song_id: int):
    db.unsave_song(song_id)
    return {"ok": True}


@app.get("/songs")
def songs():
    return {"songs": db.all_songs()}
