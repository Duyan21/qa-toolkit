import sqlite3 as sqlite

conn = sqlite.connect("qa_data.db")
cursor = conn.cursor()

def run_query(cursor, title, sql: str, format_fn):
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"\n{title}")
    for row in rows:
        print(format_fn(row))

run_query(
    cursor,
    "Failure rates ranked by module:",
    """
    WITH failure_rates AS (
    SELECT 
        module,
        run_date,
        failed,
        total_tests,
        ROUND(CAST(failed AS FLOAT) / total_tests * 100, 1) as failure_rate
    FROM test_runs
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY module 
            ORDER BY failure_rate DESC
        ) as rank
    FROM failure_rates
)
SELECT * FROM ranked
""",
    lambda row: f"Module: {row[0]} | Date: {row[1]} | Failed: {row[2]} | Total: {row[3]} | Failure rate: {row[4]}% | Rank: {row[5]}"
)

run_query(
    cursor,
    "Failure rates ranked by module:",
    """
    WITH failure_rates AS (
    SELECT 
        module,
        run_date,
        failed,
        total_tests,
        ROUND(CAST(failed AS FLOAT) / total_tests * 100, 1) as failure_rate
    FROM test_runs
),
ranked AS (
    SELECT *,
        RANK() OVER (
            PARTITION BY module 
            ORDER BY failure_rate DESC
        ) as rank
    FROM failure_rates
)
SELECT * FROM ranked
""",
    lambda row: f"Module: {row[0]} | Date: {row[1]} | Failed: {row[2]} | Total: {row[3]} | Failure rate: {row[4]}% | Rank: {row[5]}"
)

conn.close()