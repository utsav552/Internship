import time
from datetime import datetime , timedelta
import csv
import random

start_time= datetime(year =2025 , month = 11, day = 1, hour = 1, minute= 0)

rec = [
    ["epoch_time", "power"]
]

for i in range(60):
    current_time = start_time + timedelta(minutes=i)
    epoch_time = current_time.timestamp()
    power=100+i

    if random.random() < 0.25:
        power="N/A"
        
    rec.append([epoch_time, power])

clean = [["epoch_time", "power"]]   

for row in rec[1:]:   
    power = row[1]
    if power != "" and str(power).upper() != "N/A":
        clean.append(row)

with open("a.csv" , mode= 'w' , newline= '') as file:
    writer = csv.writer(file)
    writer.writerows(rec)


print ( "csv file is created")

