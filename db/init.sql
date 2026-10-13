-- Инициализация базы данных «Музыкальный каталог» (Вариант 14)
-- Таблицы предметной области + демонстрационные данные.

CREATE TABLE IF NOT EXISTS artists (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(200) NOT NULL UNIQUE,
    genre   VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS tracks (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    artist_id     INTEGER NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    album         VARCHAR(200),
    release_year  INTEGER,
    duration_sec  INTEGER,
    UNIQUE (title, artist_id)
);

CREATE TABLE IF NOT EXISTS playlists (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    track_id    INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (playlist_id, track_id)
);

-- Демонстрационные данные
INSERT INTO artists (name, genre, country) VALUES
    ('Queen',                'Rock',       'UK'),
    ('Daft Punk',            'Electronic', 'France'),
    ('Michael Jackson',      'Pop',        'USA'),
    ('Nirvana',              'Grunge',     'USA'),
    ('Miyagi & Andy Panda',  'Hip-Hop',    'Russia')
ON CONFLICT (name) DO NOTHING;

INSERT INTO tracks (title, artist_id, album, release_year, duration_sec) VALUES
    ('Bohemian Rhapsody',    1, 'A Night at the Opera',     1975, 355),
    ('Don''t Stop Me Now',   1, 'Jazz',                     1978, 209),
    ('Get Lucky',            2, 'Random Access Memories',   2013, 369),
    ('Around the World',     2, 'Homework',                 1997, 429),
    ('Billie Jean',          3, 'Thriller',                 1982, 294),
    ('Smells Like Teen Spirit', 4, 'Nevermind',             1991, 301),
    ('Utopia',               5, 'Utopia',                   2020, 180)
ON CONFLICT (title, artist_id) DO NOTHING;

INSERT INTO playlists (name, description) VALUES
    ('Rock Classics', 'Классика рока'),
    ('Party Mix',     'Треки для вечеринок');

INSERT INTO playlist_tracks (playlist_id, track_id) VALUES
    (1, 1),
    (1, 6),
    (2, 3),
    (2, 5)
ON CONFLICT DO NOTHING;
