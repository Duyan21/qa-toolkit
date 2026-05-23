import sqlite3
import json

with open("vscode_issues.json", "r", encoding="utf-8") as f:
    issues = json.load(f)

conn = sqlite3.connect("qa_data.db")
cursor = conn.cursor()

cursor.executescript("""
    DROP TABLE IF EXISTS github_issues;
    DROP TABLE IF EXISTS issue_labels;

    CREATE TABLE IF NOT EXISTS github_issues (
        id INTEGER PRIMARY KEY,
        number INTEGER,
        title TEXT,
        state TEXT,
        created_at TEXT,
        closed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS issue_labels (
        issue_id INTEGER,
        label_name TEXT,
        FOREIGN KEY (issue_id) REFERENCES github_issues(id)
    );
""")

for issue in issues:
    cursor.execute("""
        INSERT OR IGNORE INTO github_issues (id, number, title, state, created_at, closed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        issue["id"],
        issue["number"],
        issue["title"],
        issue["state"],
        issue["created_at"],
        issue["closed_at"],
    ))

    if len(issue["labels"]) == 0:
        cursor.execute("""
            INSERT INTO issue_labels (issue_id, label_name) VALUES (?, ?)
        """, (issue["id"], "(no label)"))
    else:
        for label in issue["labels"]:
            cursor.execute("""
                INSERT INTO issue_labels (issue_id, label_name) VALUES (?, ?)
            """, (issue["id"], label["name"]))

conn.commit()
conn.close()
print(f"Loaded {len(issues)} issues")
