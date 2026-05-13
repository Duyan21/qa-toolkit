import sqlite3

conn = sqlite3.connect("qa_data.db")
cursor = conn.cursor()

def run_query(cursor, title, sql: str, format_fn):
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"\n{title}")
    for row in rows:
        print(format_fn(row))

# Query 1: Tổng số test runs theo từng module
run_query(
    cursor,
    "Total failed tests by module:",
    """
    SELECT module, SUM(failed) as total_failed
    FROM test_runs
    GROUP BY module
    ORDER BY total_failed DESC
    """,
    lambda row: f"Module: {row[0]} | Total failed: {row[1]}"
)

# Query 2: Failed tests theo từng ngày, từng module
run_query(
    cursor,
    "Failed tests by date and module:",
    """
    SELECT run_date, module, failed
    FROM test_runs
    ORDER BY run_date ASC, module ASC
    """,
    lambda row: f"Date: {row[0]} | Module: {row[1]} | Failed: {row[2]}"
)

# Query 3: Failure rate theo module theo ngày (%)
run_query(
    cursor,
    "Failure rate by date:",
    """
    SELECT 
        run_date,
        module,
        failed,
        total_tests,
        ROUND(CAST(failed AS FLOAT) / total_tests * 100, 1) as failure_rate
    FROM test_runs
    ORDER BY run_date ASC, module ASC
    """,
    lambda row: f"Date: {row[0]} | Module: {row[1]} | Failed: {row[2]} | Total: {row[3]} | Failure rate: {row[4]}%"
)

conn.close()