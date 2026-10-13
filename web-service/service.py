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
    {"id": 9, "name": "The Beatles", "genre": "Rock", "country": "UK"},
    {"id": 10, "name": "Pink Floyd", "genre": "Progressive Rock", "country": "UK"},
    {"id": 11, "name": "Billie Eilish", "genre": "Pop", "country": "USA"},
    {"id": 12, "name": "Eminem", "genre": "Hip-Hop", "country": "USA"},
    {"id": 13, "name": "Imagine Dragons", "genre": "Pop Rock", "country": "USA"},
    {"id": 14, "name": "Red Hot Chili Peppers", "genre": "Funk Rock", "country": "USA"},
    {"id": 15, "name": "Depeche Mode", "genre": "Synth-pop", "country": "UK"},
]

ARTIST_BY_ID = {a["id"]: a for a in ARTISTS}

TRACKS = [
    {"id": 1, "title": "Bohemian Rhapsody", "artist_id": 1, "album": "A Night at the Opera", "year": 1975, "duration_sec": 355},
    {"id": 2, "title": "Don't Stop Me Now", "artist_id": 1, "album": "Jazz", "year": 1978, "duration_sec": 209},
    {"id": 3, "title": "We Will Rock You", "artist_id": 1, "album": "News of the World", "year": 1977, "duration_sec": 122},
    {"id": 4, "title": "Somebody to Love", "artist_id": 1, "album": "A Day at the Races", "year": 1976, "duration_sec": 296},
    {"id": 5, "title": "Get Lucky", "artist_id": 2, "album": "Random Access Memories", "year": 2013, "duration_sec": 369},
    {"id": 6, "title": "Around the World", "artist_id": 2, "album": "Homework", "year": 1997, "duration_sec": 429},
    {"id": 7, "title": "One More Time", "artist_id": 2, "album": "Discovery", "year": 2000, "duration_sec": 320},
    {"id": 8, "title": "Billie Jean", "artist_id": 3, "album": "Thriller", "year": 1982, "duration_sec": 294},
    {"id": 9, "title": "Beat It", "artist_id": 3, "album": "Thriller", "year": 1982, "duration_sec": 258},
    {"id": 10, "title": "Thriller", "artist_id": 3, "album": "Thriller", "year": 1982, "duration_sec": 357},
    {"id": 11, "title": "Smells Like Teen Spirit", "artist_id": 4, "album": "Nevermind", "year": 1991, "duration_sec": 301},
    {"id": 12, "title": "Come As You Are", "artist_id": 4, "album": "Nevermind", "year": 1991, "duration_sec": 219},
    {"id": 13, "title": "Lithium", "artist_id": 4, "album": "Nevermind", "year": 1991, "duration_sec": 257},
    {"id": 14, "title": "Utopia", "artist_id": 5, "album": "Utopia", "year": 2020, "duration_sec": 180},
    {"id": 15, "title": "I Love You So", "artist_id": 5, "album": "Buster Keaton", "year": 2022, "duration_sec": 197},
    {"id": 16, "title": "Kosandra", "artist_id": 5, "album": "Kosandra", "year": 2018, "duration_sec": 205},
    {"id": 17, "title": "Blinding Lights", "artist_id": 6, "album": "After Hours", "year": 2020, "duration_sec": 200},
    {"id": 18, "title": "Save Your Tears", "artist_id": 6, "album": "After Hours", "year": 2020, "duration_sec": 215},
    {"id": 19, "title": "Starboy", "artist_id": 6, "album": "Starboy", "year": 2016, "duration_sec": 230},
    {"id": 20, "title": "In the End", "artist_id": 7, "album": "Hybrid Theory", "year": 2000, "duration_sec": 216},
    {"id": 21, "title": "Numb", "artist_id": 7, "album": "Meteora", "year": 2003, "duration_sec": 185},
    {"id": 22, "title": "Faint", "artist_id": 7, "album": "Meteora", "year": 2003, "duration_sec": 162},
    {"id": 23, "title": "Rolling in the Deep", "artist_id": 8, "album": "21", "year": 2010, "duration_sec": 228},
    {"id": 24, "title": "Hello", "artist_id": 8, "album": "25", "year": 2015, "duration_sec": 295},
    {"id": 25, "title": "Someone Like You", "artist_id": 8, "album": "21", "year": 2011, "duration_sec": 285},
    {"id": 26, "title": "Hey Jude", "artist_id": 9, "album": "Hey Jude", "year": 1968, "duration_sec": 431},
    {"id": 27, "title": "Let It Be", "artist_id": 9, "album": "Let It Be", "year": 1970, "duration_sec": 243},
    {"id": 28, "title": "Come Together", "artist_id": 9, "album": "Abbey Road", "year": 1969, "duration_sec": 259},
    {"id": 29, "title": "Another Brick in the Wall", "artist_id": 10, "album": "The Wall", "year": 1979, "duration_sec": 239},
    {"id": 30, "title": "Wish You Were Here", "artist_id": 10, "album": "Wish You Were Here", "year": 1975, "duration_sec": 334},
    {"id": 31, "title": "Comfortably Numb", "artist_id": 10, "album": "The Wall", "year": 1979, "duration_sec": 382},
    {"id": 32, "title": "bad guy", "artist_id": 11, "album": "When We All Fall Asleep", "year": 2019, "duration_sec": 194},
    {"id": 33, "title": "Happier Than Ever", "artist_id": 11, "album": "Happier Than Ever", "year": 2021, "duration_sec": 298},
    {"id": 34, "title": "Lose Yourself", "artist_id": 12, "album": "8 Mile", "year": 2002, "duration_sec": 326},
    {"id": 35, "title": "The Real Slim Shady", "artist_id": 12, "album": "The Marshall Mathers LP", "year": 2000, "duration_sec": 224},
    {"id": 36, "title": "Believer", "artist_id": 13, "album": "Evolve", "year": 2017, "duration_sec": 204},
    {"id": 37, "title": "Thunder", "artist_id": 13, "album": "Evolve", "year": 2017, "duration_sec": 187},
    {"id": 38, "title": "Californication", "artist_id": 14, "album": "Californication", "year": 1999, "duration_sec": 321},
    {"id": 39, "title": "Under the Bridge", "artist_id": 14, "album": "Blood Sugar Sex Magik", "year": 1991, "duration_sec": 264},
    {"id": 40, "title": "Enjoy the Silence", "artist_id": 15, "album": "Violator", "year": 1990, "duration_sec": 256},
    {"id": 41, "title": "Personal Jesus", "artist_id": 15, "album": "Violator", "year": 1989, "duration_sec": 235},
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
