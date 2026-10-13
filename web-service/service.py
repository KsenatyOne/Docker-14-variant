"""Web-сервис предметной области «Музыкальный каталог» (Вариант 14).

Локальный микросервис-эмулятор: предоставляет поиск музыкальных треков
и исполнителей по ключевому слову. Разрешён условиями практикума
(«внешний общедоступный API или локальный микросервис-эмулятор»).
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Music Catalog Web-Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTISTS = [
    {"id": 1, "name": "Queen", "genre": "Rock", "country": "UK"},
    {"id": 2, "name": "Daft Punk", "genre": "Electronic", "country": "France"},
    {"id": 3, "name": "Michael Jackson", "genre": "Pop", "country": "USA"},
    {"id": 4, "name": "Nirvana", "genre": "Grunge", "country": "USA"},
    {"id": 5, "name": "Miyagi & Andy Panda", "genre": "Hip-Hop", "country": "Russia"},
    {"id": 6, "name": "The Weeknd", "genre": "R&B", "country": "Canada"},
    {"id": 7, "name": "Linkin Park", "genre": "Nu-Metal", "country": "USA"},
    {"id": 8, "name": "Adele", "genre": "Soul", "country": "UK"},
]

ARTIST_BY_ID = {a["id"]: a for a in ARTISTS}

TRACKS = [
    {"id": 1, "title": "Bohemian Rhapsody", "artist_id": 1, "album": "A Night at the Opera", "year": 1975, "duration_sec": 355},
    {"id": 2, "title": "Don't Stop Me Now", "artist_id": 1, "album": "Jazz", "year": 1978, "duration_sec": 209},
    {"id": 3, "title": "We Will Rock You", "artist_id": 1, "album": "News of the World", "year": 1977, "duration_sec": 122},
    {"id": 4, "title": "Get Lucky", "artist_id": 2, "album": "Random Access Memories", "year": 2013, "duration_sec": 369},
    {"id": 5, "title": "Around the World", "artist_id": 2, "album": "Homework", "year": 1997, "duration_sec": 429},
    {"id": 6, "title": "Billie Jean", "artist_id": 3, "album": "Thriller", "year": 1982, "duration_sec": 294},
    {"id": 7, "title": "Beat It", "artist_id": 3, "album": "Thriller", "year": 1982, "duration_sec": 258},
    {"id": 8, "title": "Smells Like Teen Spirit", "artist_id": 4, "album": "Nevermind", "year": 1991, "duration_sec": 301},
    {"id": 9, "title": "Come As You Are", "artist_id": 4, "album": "Nevermind", "year": 1991, "duration_sec": 219},
    {"id": 10, "title": "Utopia", "artist_id": 5, "album": "Utopia", "year": 2020, "duration_sec": 180},
    {"id": 11, "title": "I Love You So", "artist_id": 5, "album": "Buster Keaton", "year": 2022, "duration_sec": 197},
    {"id": 12, "title": "Blinding Lights", "artist_id": 6, "album": "After Hours", "year": 2020, "duration_sec": 200},
    {"id": 13, "title": "Save Your Tears", "artist_id": 6, "album": "After Hours", "year": 2020, "duration_sec": 215},
    {"id": 14, "title": "In the End", "artist_id": 7, "album": "Hybrid Theory", "year": 2000, "duration_sec": 216},
    {"id": 15, "title": "Numb", "artist_id": 7, "album": "Meteora", "year": 2003, "duration_sec": 185},
    {"id": 16, "title": "Rolling in the Deep", "artist_id": 8, "album": "21", "year": 2010, "duration_sec": 228},
    {"id": 17, "title": "Hello", "artist_id": 8, "album": "25", "year": 2015, "duration_sec": 295},
]


def _enrich(track: dict) -> dict:
    """Дополняет трек именем исполнителя и жанром."""
    artist = ARTIST_BY_ID[track["artist_id"]]
    return {
        **track,
        "artist": artist["name"],
        "genre": artist["genre"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "music-web-service"}


@app.get("/search")
def search(
    q: str = Query("", description="Поисковый запрос: трек, исполнитель, альбом или жанр"),
    limit: int = Query(20, ge=1, le=100),
):
    """Поиск музыкальных треков и исполнителей по ключевому слову."""
    query = (q or "").strip().lower()
    results = []
    for track in TRACKS:
        item = _enrich(track)
        haystack = " ".join(
            str(v) for v in (item["title"], item["album"], item["artist"], item["genre"])
        ).lower()
        if not query or query in haystack:
            results.append(item)
    return {"query": q, "count": len(results[:limit]), "results": results[:limit]}


@app.get("/artists/{artist_id}")
def get_artist(artist_id: int):
    """Информация об исполнителе и список его треков."""
    artist = ARTIST_BY_ID.get(artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    tracks = [_enrich(t) for t in TRACKS if t["artist_id"] == artist_id]
    return {**artist, "tracks": tracks}
