import sqlite3
import sys
import matplotlib.pyplot as plt


def visualize_failure_rates(db_file):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            run_date,
            module,
            ROUND(CAST(failed AS FLOAT) / total_tests * 100, 1) as failure_rate
        FROM test_runs
        ORDER BY run_date ASC
        """)
        rows = cursor.fetchall()

    # Split data into separate lists for auth and payment modules
    auth_dates, auth_rates = [], []
    payment_dates, payment_rates = [], []

    for run_date, module, failure_rate in rows:
        if module == "auth":
            auth_dates.append(run_date)
            auth_rates.append(failure_rate)
        else:
            payment_dates.append(run_date)
            payment_rates.append(failure_rate)

    # Visualize the failure rates over time for both modules
    plt.figure(figsize=(10, 6))
    plt.plot(auth_dates, auth_rates, marker="o", label="auth")
    plt.plot(payment_dates, payment_rates, marker="o", label="payment")

    plt.title("Failure Rate by Module Over Time")
    plt.xlabel("Date")
    plt.ylabel("Failure Rate (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("failure_rate_chart.png")
    plt.show()

    print("Chart saved: failure_rate_chart.png")

if __name__ == "__main__":
    dbpath = sys.argv[1] if len(sys.argv) > 1 else "qa_data.db"
    visualize_failure_rates(dbpath)