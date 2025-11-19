import time
from datetime import datetime, timedelta
import csv
import random

start_time = datetime(year=2025, month=11, day=1, hour=1, minute=0)

def generate_clean_rows(col2_name):
    header = ["epoch_time", col2_name]
    yield header

    for i in range(60):
        if random.random() >= 0.25:
            current_time = start_time + timedelta(minutes=i)
            v = (100+i) if col2=="power" else 200+(i*5)
            yield [current_time.timestamp(), v]


files = {
    "Power": "power.csv",
    "Energy": "energy.csv"
}

for col2 in files:  
    with open(files[col2], "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(generate_clean_rows(col2))

    print(f"Created: {files[col2]} ")
