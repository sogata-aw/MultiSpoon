CREATE TABLE IF NOT EXISTS Guild
(
    id                   INTEGER PRIMARY KEY,
    name                 VARCHAR(255) NOT NULL,
    verification_channel INTEGER DEFAULT 0,
    role_before          INTEGER DEFAULT 0,
    role_after           INTEGER DEFAULT 0,
    timeout              INTEGER DEFAULT 300,
    log_channel          INTEGER DEFAULT 0,
    white_list_active    BOOL    DEFAULT false,
    on_create_channel    BOOL    DEFAULT false,
    spoon_pot            INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Verified
(
    user_id  INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Trigger_Voice_Channel
(
    channel_id INTEGER NOT NULL,
    guild_id   INTEGER NOT NULL,
    PRIMARY KEY (channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Temp_Channel
(
    id       INTEGER PRIMARY KEY,
    guild_id INTEGER      NOT NULL,
    name     VARCHAR(255) NOT NULL,
    category INTEGER,
    type     VARCHAR(255) NOT NULL,
    duree    VARCHAR(255) NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Triggered_Voice_Channel
(
    voice_channel_id INTEGER NOT NULL,
    guild_id         INTEGER NOT NULL,
    PRIMARY KEY (voice_channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Role
(
    id       INTEGER PRIMARY KEY,
    guild_id INTEGER      NOT NULL,
    name     VARCHAR(255) NOT NULL,
    duree    VARCHAR(255) NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS White_List
(
    channel_id INTEGER NOT NULL,
    guild_id   INTEGER NOT NULL,
    PRIMARY KEY (channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS Link
(
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id        INTEGER NOT NULL,
    guild_id          INTEGER NOT NULL,
    linked_channel_id INTEGER NOT NULL,
    linked_guild_id   INTEGER NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE,
    FOREIGN KEY (linked_guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Seance
(
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id           INTEGER NOT NULL,
    title              VARCHAR(255) NOT NULL,
    date               VARCHAR(255) NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Movie
(
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id            INTEGER NOT NULL UNIQUE,
    seance_id          INTEGER NOT NULL,
    title              VARCHAR(255) NOT NULL,
    description        TEXT NOT NULL,
    note               TEXT,
    image              VARCHAR(255) NOT NULL,
    proposed_by        INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (seance_id) REFERENCES Seance (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Genre
(
    id                 INTEGER PRIMARY KEY,
    name               VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Movie_Genre
(
    movie_id           INTEGER NOT NULL,
    genre_id           INTEGER NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movie (id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre (id) ON DELETE CASCADE
);
