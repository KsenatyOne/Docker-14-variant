-- Инициализация базы данных «Музыкальный каталог» (Вариант 14)
-- Таблицы предметной области + демонстрационные данные.
-- Каталог: 15 исполнителей, 41 трек, 5 пользовательских плейлистов.

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

-- Исполнители (id зафиксированы для однозначной связи с треками)
INSERT INTO artists (id, name, genre, country) VALUES
    (1,  'Queen',                'Rock',             'UK'),
    (2,  'Daft Punk',            'Electronic',       'France'),
    (3,  'Michael Jackson',      'Pop',              'USA'),
    (4,  'Nirvana',              'Grunge',           'USA'),
    (5,  'Miyagi & Andy Panda',  'Hip-Hop',          'Russia'),
    (6,  'The Weeknd',           'R&B',              'Canada'),
    (7,  'Linkin Park',          'Nu-Metal',         'USA'),
    (8,  'Adele',                'Soul',             'UK'),
    (9,  'The Beatles',          'Rock',             'UK'),
    (10, 'Pink Floyd',           'Progressive Rock', 'UK'),
    (11, 'Billie Eilish',        'Pop',              'USA'),
    (12, 'Eminem',               'Hip-Hop',          'USA'),
    (13, 'Imagine Dragons',      'Pop Rock',         'USA'),
    (14, 'Red Hot Chili Peppers','Funk Rock',        'USA'),
    (15, 'Depeche Mode',         'Synth-pop',        'UK')
ON CONFLICT (id) DO NOTHING;

-- Треки
INSERT INTO tracks (id, title, artist_id, album, release_year, duration_sec) VALUES
    (1,  'Bohemian Rhapsody',          1,  'A Night at the Opera',      1975, 355),
    (2,  'Don''t Stop Me Now',         1,  'Jazz',                      1978, 209),
    (3,  'We Will Rock You',           1,  'News of the World',         1977, 122),
    (4,  'Somebody to Love',           1,  'A Day at the Races',        1976, 296),
    (5,  'Get Lucky',                  2,  'Random Access Memories',    2013, 369),
    (6,  'Around the World',           2,  'Homework',                  1997, 429),
    (7,  'One More Time',              2,  'Discovery',                 2000, 320),
    (8,  'Billie Jean',                3,  'Thriller',                  1982, 294),
    (9,  'Beat It',                    3,  'Thriller',                  1982, 258),
    (10, 'Thriller',                   3,  'Thriller',                  1982, 357),
    (11, 'Smells Like Teen Spirit',    4,  'Nevermind',                 1991, 301),
    (12, 'Come As You Are',            4,  'Nevermind',                 1991, 219),
    (13, 'Lithium',                    4,  'Nevermind',                 1991, 257),
    (14, 'Utopia',                     5,  'Utopia',                    2020, 180),
    (15, 'I Love You So',              5,  'Buster Keaton',             2022, 197),
    (16, 'Kosandra',                   5,  'Kosandra',                  2018, 205),
    (17, 'Blinding Lights',            6,  'After Hours',               2020, 200),
    (18, 'Save Your Tears',            6,  'After Hours',               2020, 215),
    (19, 'Starboy',                    6,  'Starboy',                   2016, 230),
    (20, 'In the End',                 7,  'Hybrid Theory',             2000, 216),
    (21, 'Numb',                       7,  'Meteora',                   2003, 185),
    (22, 'Faint',                      7,  'Meteora',                   2003, 162),
    (23, 'Rolling in the Deep',        8,  '21',                        2010, 228),
    (24, 'Hello',                      8,  '25',                        2015, 295),
    (25, 'Someone Like You',           8,  '21',                        2011, 285),
    (26, 'Hey Jude',                   9,  'Hey Jude',                  1968, 431),
    (27, 'Let It Be',                  9,  'Let It Be',                 1970, 243),
    (28, 'Come Together',              9,  'Abbey Road',                1969, 259),
    (29, 'Another Brick in the Wall',  10, 'The Wall',                  1979, 239),
    (30, 'Wish You Were Here',         10, 'Wish You Were Here',        1975, 334),
    (31, 'Comfortably Numb',           10, 'The Wall',                  1979, 382),
    (32, 'bad guy',                    11, 'When We All Fall Asleep',   2019, 194),
    (33, 'Happier Than Ever',          11, 'Happier Than Ever',         2021, 298),
    (34, 'Lose Yourself',              12, '8 Mile',                    2002, 326),
    (35, 'The Real Slim Shady',        12, 'The Marshall Mathers LP',   2000, 224),
    (36, 'Believer',                   13, 'Evolve',                    2017, 204),
    (37, 'Thunder',                    13, 'Evolve',                    2017, 187),
    (38, 'Californication',            14, 'Californication',           1999, 321),
    (39, 'Under the Bridge',           14, 'Blood Sugar Sex Magik',     1991, 264),
    (40, 'Enjoy the Silence',          15, 'Violator',                  1990, 256),
    (41, 'Personal Jesus',             15, 'Violator',                  1989, 235)
ON CONFLICT (id) DO NOTHING;

-- Синхронизация последовательностей после вставки с явными id
SELECT setval('artists_id_seq', (SELECT MAX(id) FROM artists));
SELECT setval('tracks_id_seq',  (SELECT MAX(id) FROM tracks));

-- Пользовательские плейлисты
INSERT INTO playlists (id, name, description) VALUES
    (1, 'Rock Classics', 'Классика рока'),
    (2, 'Party Mix',     'Треки для вечеринок'),
    (3, 'Chill Vibes',   'Спокойная музыка для отдыха'),
    (4, 'Hip-Hop Hits',  'Лучшее из хип-хопа'),
    (5, 'Road Trip',     'Плейлист для долгой дороги')
ON CONFLICT (id) DO NOTHING;

SELECT setval('playlists_id_seq', (SELECT MAX(id) FROM playlists));

-- Наполнение плейлистов треками
INSERT INTO playlist_tracks (playlist_id, track_id) VALUES
    (1, 1),  (1, 2),  (1, 3),  (1, 26), (1, 29), (1, 31), (1, 38), (1, 39),
    (2, 5),  (2, 8),  (2, 17), (2, 36), (2, 37),
    (3, 24), (3, 25), (3, 30), (3, 33), (3, 40),
    (4, 14), (4, 15), (4, 34), (4, 35),
    (5, 2),  (5, 6),  (5, 7),  (5, 20), (5, 21), (5, 27)
ON CONFLICT DO NOTHING;
