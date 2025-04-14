CREATE TABLE results (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
