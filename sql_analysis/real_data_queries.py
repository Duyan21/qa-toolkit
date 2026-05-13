import sqlite3

conn = sqlite3.connect("qa_data.db")
cursor = conn.cursor()

# Total number of issues in the dataset
cursor.execute("SELECT COUNT(*) FROM github_issues")
total_issues = cursor.fetchone()[0]

# Issues without any label — stored as "(no label)" in issue_labels
# These are issues that have not been triaged by the team yet
cursor.execute("""
    SELECT COUNT(*) FROM issue_labels 
    WHERE label_name = '(no label)'
""")
unlabeled_count = cursor.fetchone()[0]

# Issues with at least one real label
# Use DISTINCT to avoid counting the same issue multiple times
# (one issue can have multiple labels)
cursor.execute("""
    SELECT COUNT(DISTINCT issue_id) 
    FROM issue_labels 
    WHERE label_name != '(no label)'
""")
labeled_count = cursor.fetchone()[0]

# All labels and their counts, sorted by most common first
# Used for labeled breakdown section
cursor.execute("""
    SELECT label_name, COUNT(*) as count
    FROM issue_labels
    GROUP BY label_name
    ORDER BY count DESC
    """)
rows = cursor.fetchall()

print("=== VSCode Issues Health Report ===")
print(f"Total issues: {total_issues}")
print(f"Unlabeled issues: {unlabeled_count} ({unlabeled_count / total_issues * 100:.2f}%)")
print(f"Labeled issues: {labeled_count} ({labeled_count / total_issues * 100:.2f}%)")

# Show breakdown of labeled issues only
# Percentage is calculated against labeled_count, not total_issues
# This answers: "Among triaged issues, what types are most common?"
print("=== Labeled breakdown ===")
for row in rows:
    if row[0] != "(no label)":
        print(f"{row[0]}: {row[1]} ({row[1] / labeled_count * 100:.2f}%)")

conn.close()