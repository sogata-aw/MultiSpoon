ALTER TABLE Movie RENAME TO old_movie;
CREATE TABLE Movie(
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id            INTEGER NOT NULL UNIQUE,
    seance_id          INTEGER NOT NULL,
    title              VARCHAR(255) NOT NULL,
    description        TEXT NOT NULL,
    image              VARCHAR(255) NOT NULL,
    proposed_by        INTEGER NOT NULL,
    note               TEXT,
    FOREIGN KEY (seance_id) REFERENCES Seance (id) ON DELETE CASCADE
);
INSERT INTO Movie (id, tmdb_id, seance_id, title, description, image, proposed_by, note) SELECT id, tmdb_id, seance_id, title, description, image, proposed_by, note FROM old_movie;
