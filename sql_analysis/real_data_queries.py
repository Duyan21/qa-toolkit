import sqlite3


def run_query(cursor, sql, fetch="one"):
    cursor.execute(sql)
    return cursor.fetchone() if fetch == "one" else cursor.fetchall()


with sqlite3.connect("qa_data.db") as conn:
    cursor = conn.cursor()

    total_issues = run_query(cursor, "SELECT COUNT(*) FROM github_issues")[0]

    unlabeled_count = run_query(cursor, """
        SELECT COUNT(*) FROM issue_labels 
        WHERE label_name = '(no label)'
    """)[0]

    # DISTINCT prevents double-counting issues that have multiple labels
    labeled_count = run_query(cursor, """
        SELECT COUNT(DISTINCT issue_id) 
        FROM issue_labels 
        WHERE label_name != '(no label)'
    """)[0]

    rows = run_query(cursor, """
        SELECT label_name, COUNT(*) as count
        FROM issue_labels
        GROUP BY label_name
        ORDER BY count DESC
    """, fetch="all")

    print("=== VSCode Issues Health Report ===")
    print(f"Total issues: {total_issues}")
    print(f"Unlabeled issues: {unlabeled_count} ({unlabeled_count / total_issues * 100:.2f}%)")
    print(f"Labeled issues: {labeled_count} ({labeled_count / total_issues * 100:.2f}%)")

    print("=== Labeled breakdown ===")
    for label, count in rows:
        if label != "(no label)":
            print(f"{label}: {count} ({count / labeled_count * 100:.2f}%)")

    fastest, slowest, average = run_query(cursor, """
        SELECT 
            MIN(ROUND((JULIANDAY(closed_at) - JULIANDAY(created_at)) * 24, 1)),
            MAX(ROUND((JULIANDAY(closed_at) - JULIANDAY(created_at)) * 24, 1)),
            ROUND(AVG((JULIANDAY(closed_at) - JULIANDAY(created_at)) * 24), 1)
        FROM github_issues
        WHERE closed_at IS NOT NULL
    """)

    print("=== Resolution time ===")
    print(f"Fastest issue: {fastest} hours")
    print(f"Slowest issue: {slowest} hours")
    print(f"Average issue: {average} hours")

    print("=== The date in a week with the most issues created ===")
    busiest_day = run_query(cursor, """
        SELECT strftime('%w', created_at) as weekday, COUNT(*) as count
        FROM github_issues
        GROUP BY weekday
        ORDER BY count DESC
        LIMIT 1
    """)
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    print(f"{days[int(busiest_day[0])]} with {busiest_day[1]} issues created")
