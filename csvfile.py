import csv
import random
from datetime import datetime, timedelta, UTC

start_time = datetime(year=2025, month=11, day=1, hour=0 ,minute=0, tzinfo=UTC)

def generate_clean_rows(col2_name):
    yield ["epoch_time", "gmt_datetime", col2_name]

    for i in range(60):
        if random.random() >= 0.25:

            current_time = start_time + timedelta(minutes=i)

            if col2_name == "Power":
                v = 100 + i
            else:
                v = 200 + (i * 5)

            gmt_dt = (current_time).strftime("%Y-%m-%d %H:%M:%S")

            yield [int(current_time.timestamp() * 1000), gmt_dt, v]

files = {
    "Power": "power.csv",
    "Energy": "energy.csv"
}

for col2 in files:
    with open(files[col2], "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(generate_clean_rows(col2))

    print(f"Created: {files[col2]}")
