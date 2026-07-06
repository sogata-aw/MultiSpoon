CREATE TABLE Guild
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

CREATE TABLE Verified
(
    user_id  INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE Trigger_Voice_Channel
(
    channel_id INTEGER NOT NULL,
    guild_id   INTEGER NOT NULL,
    PRIMARY KEY (channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE Temp_Channel
(
    id       INTEGER PRIMARY KEY,
    guild_id INTEGER      NOT NULL,
    name     VARCHAR(255) NOT NULL,
    category INTEGER,
    type     VARCHAR(255) NOT NULL,
    duree    VARCHAR(255) NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE Triggered_Voice_Channel
(
    voice_channel_id INTEGER NOT NULL,
    guild_id         INTEGER NOT NULL,
    PRIMARY KEY (voice_channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE Role
(
    id       INTEGER PRIMARY KEY,
    guild_id INTEGER      NOT NULL,
    name     VARCHAR(255) NOT NULL,
    duree    VARCHAR(255) NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);

CREATE TABLE White_List
(
    channel_id INTEGER NOT NULL,
    guild_id   INTEGER NOT NULL,
    PRIMARY KEY (channel_id, guild_id),
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE

);

CREATE TABLE Link
(
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id        INTEGER NOT NULL,
    guild_id          INTEGER NOT NULL,
    linked_channel_id INTEGER NOT NULL,
    linked_guild_id   INTEGER NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES Guild (id) ON DELETE CASCADE,
    FOREIGN KEY (linked_guild_id) REFERENCES Guild (id) ON DELETE CASCADE
);
