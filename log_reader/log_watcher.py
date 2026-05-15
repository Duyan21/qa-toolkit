from collections import defaultdict
from datetime import datetime
import time
import sys
from collections import deque

ERROR_KEYWORD = "ERROR"
THRESHOLD = 5
WINDOW = 60
SUMMARY_INTERVAL = 60

def tail_log(filepath: str) -> None:
    error_counts: dict[str, int] = defaultdict(int)
    total_errors = 0
    start_time = datetime.now()
    error_times = deque()
    last_summary_time = start_time

    print(f"--- File log: {filepath} ---")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with open(filepath, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                if ERROR_KEYWORD in line:
                    now = datetime.now()
                    total_errors += 1
                    message = line.split(ERROR_KEYWORD, 1)[1].strip()
                    error_counts[message] += 1

                    error_times.append(now)

                    # Delete timestamps outside the window
                    while error_times and (now - error_times[0]).seconds > WINDOW:
                        error_times.popleft()

                    # Check threshold
                    if len(error_times) >= THRESHOLD:
                        print(
                            f"🚨 ALERT: {len(error_times)} errors in {WINDOW} seconds")
                        print(
                            f"   From: {error_times[0].strftime('%H:%M:%S')} → {error_times[-1].strftime('%H:%M:%S')}")
                        error_times.clear()
                # Print summary every SUMMARY_INTERVAL seconds
                if (datetime.now() - last_summary_time).seconds >= SUMMARY_INTERVAL:
                    print(f"--- Summary at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                    print(f"Total errors: {total_errors}")
                    for message, count in error_counts.items():
                        print(f"  - {message} (x{count})")
                    last_summary_time = datetime.now()
    except KeyboardInterrupt:
        stop_time = datetime.now()
        print(f"Stopped at: {stop_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"=== Log Analysis Report ===")
        print(
            f"Total runtime: {(stop_time - start_time).total_seconds():.2f} seconds")
        print(f"Total error occurrences: {total_errors}")
        for message, count in error_counts.items():
            print(f"  - {message} (x{count})")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "live_app.log"
    tail_log(filepath)
