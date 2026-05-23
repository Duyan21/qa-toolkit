import sqlite3

conn = sqlite3.connect("qa_data.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY,
    run_date TEXT,
    module TEXT,
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    duration_seconds INTEGER
);

INSERT INTO test_runs VALUES
(1, '2024-01-10', 'auth', 50, 48, 2, 120),
(2, '2024-01-10', 'payment', 30, 25, 5, 200),
(3, '2024-01-11', 'auth', 50, 50, 0, 115),
(4, '2024-01-11', 'payment', 30, 28, 2, 190),
(5, '2024-01-12', 'auth', 50, 45, 5, 130),
(6, '2024-01-12', 'payment', 30, 20, 10, 220),
(7, '2024-01-13', 'auth', 50, 49, 1, 118),
(8, '2024-01-13', 'payment', 30, 30, 0, 185),
(9, '2024-01-14', 'auth', 50, 44, 6, 135),
(10, '2024-01-14', 'payment', 30, 18, 12, 230);
""")

conn.commit()
conn.close()
print("Database created successfully")