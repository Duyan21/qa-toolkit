# log_generator.py
import time
import random
from datetime import datetime

log_entries = [
    "INFO  App is running normally",
    "INFO  User login successful",
    "INFO  Payment processed",
    "WARNING Response time high: 850ms",
    "ERROR Database connection failed: timeout",
    "ERROR Auth service unreachable",
    "ERROR Payment gateway timeout",
    "INFO  Health check passed",
]

with open("live_app.log", "a") as f:
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 70% chance INFO/WARNING, 30% chance ERROR
        entry = random.choices(
            log_entries,
            weights=[20, 20, 20, 10, 10, 10, 10, 10]
        )[0]
        
        line = f"{timestamp} {entry}\n"
        f.write(line)
        f.flush()  # immediately write to file
        
        print(f"Generated: {line.strip()}")
        time.sleep(1)  # wait 1 second before generating next log entry