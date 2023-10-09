DROP TABLE IF EXISTS commanders;

CREATE TABLE commanders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_url TEXT NOT NULL,
    post_url TEXT NOT NULL,
    ups INT,
    is_un BOOL NOT NULL,
    mana_cost TEXT,
    type TEXT,
    oracle_text TEXT,
    power INTEGER,
    toughness INTEGER
);