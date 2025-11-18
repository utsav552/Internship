import time
from datetime import datetime , timedelta
import csv
import random

start_time= datetime(year =2025 , month = 11, day = 1, hour = 1, minute= 0)

rec = [
    ["epoch_time", "Energy"]
]

for i in range(60):
    current_time = start_time + timedelta(minutes=i)
    epoch_time = current_time.timestamp()
    Energy=300+i

    if random.random():
        Energy="N/A"
        
    rec.append([epoch_time, Energy])

with open("b.csv" , mode= 'w' , newline= '') as file:
    writer = csv.writer(file)
    writer.writerows(rec)


print ( "csv file is created")

