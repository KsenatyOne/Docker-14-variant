"""Backend «Музыкальный каталог» (Вариант 14).

REST API на FastAPI:
  * CRUD-операции над пользовательскими плейлистами (СУБД PostgreSQL);
  * интеграция с Web-сервисом поиска треков/исполнителей (web-service).
"""

import os
import time

import psycopg2
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "musicdb")
DB_USER = os.getenv("DB_USER", "musicuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "musicpass")
WEB_SERVICE_URL = os.getenv("WEB_SERVICE_URL", "http://web-service:8080").rstrip("/")

app = FastAPI(title="Music Catalog Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )


@app.on_event("startup")
def wait_for_db() -> None:
    """Ожидание готовности БД (дополнительно к depends_on/healthcheck)."""
    last_error = None
    for _ in range(30):
        try:
            conn = get_conn()
            conn.close()
            return
        except psycopg2.OperationalError as exc:  # pragma: no cover
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Database is not available: {last_error}")


class PlaylistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = ""


class TrackAdd(BaseModel):
    title: str = Field(..., min_length=1)
    artist: str = Field(..., min_length=1)
    album: str | None = None
    year: int | None = None
    duration_sec: int | None = None


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "music-backend"}


# --- Кнопка 1: данные из внутренней БД -------------------------------------

@app.get("/api/playlists")
def list_playlists():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.id,
                   p.name,
                   p.description,
                   p.created_at,
                   COUNT(pt.track_id) AS tracks_count
            FROM playlists p
            LEFT JOIN playlist_tracks pt ON pt.playlist_id = p.id
            GROUP BY p.id
            ORDER BY p.id
            """
        )
        return cur.fetchall()


@app.post("/api/playlists", status_code=201)
def create_playlist(payload: PlaylistCreate):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO playlists (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description, created_at
            """,
            (payload.name, payload.description),
        )
        row = cur.fetchone()
        conn.commit()
        return row


@app.delete("/api/playlists/{playlist_id}")
def delete_playlist(playlist_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM playlists WHERE id = %s", (playlist_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Playlist not found")
        conn.commit()
    return {"deleted": playlist_id}


@app.get("/api/playlists/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT t.id,
                   t.title,
                   a.name AS artist,
                   t.album,
                   t.release_year AS year,
                   t.duration_sec
            FROM playlist_tracks pt
            JOIN tracks t ON t.id = pt.track_id
            JOIN artists a ON a.id = t.artist_id
            WHERE pt.playlist_id = %s
            ORDER BY pt.added_at
            """,
            (playlist_id,),
        )
        return cur.fetchall()


# --- Кнопка 2: интеграция с Web-сервисом -----------------------------------

@app.get("/api/search")
def search(q: str = ""):
    """Проксирует запрос в Web-сервис поиска треков и исполнителей."""
    try:
        response = requests.get(
            f"{WEB_SERVICE_URL}/search", params={"q": q}, timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:  # pragma: no cover
        raise HTTPException(
            status_code=502, detail=f"Web-service unavailable: {exc}"
        )


@app.post("/api/playlists/{playlist_id}/tracks", status_code=201)
def add_track_to_playlist(playlist_id: int, track: TrackAdd):
    """Добавляет найденный во внешнем сервисе трек в плейлист пользователя.

    Исполнитель и трек при необходимости создаются в БД (upsert),
    после чего связываются с плейлистом.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM playlists WHERE id = %s", (playlist_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cur.execute(
            """
            INSERT INTO artists (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (track.artist,),
        )
        artist_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO tracks (title, artist_id, album, release_year, duration_sec)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, artist_id)
            DO UPDATE SET album = EXCLUDED.album
            RETURNING id
            """,
            (track.title, artist_id, track.album, track.year, track.duration_sec),
        )
        track_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO playlist_tracks (playlist_id, track_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (playlist_id, track_id),
        )
        conn.commit()

    return {"playlist_id": playlist_id, "track_id": track_id}
