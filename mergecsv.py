import csv

power_dict = {}
with open("a.csv", "r") as fa:
    reader_a = csv.reader(fa)
    next(reader_a)  
    for row in reader_a:
        epoch = row[0]
        power = row[1]
        power_dict[epoch] = power

energy_dict = {}
with open("b.csv", "r") as fb:
    reader_b = csv.reader(fb)
    next(reader_b)  
    for row in reader_b:
        epoch = row[0]
        energy = row[1]
        energy_dict[epoch] = energy

all_epochs = sorted(set(power_dict.keys()) | set(energy_dict.keys()), key=int)

merged = [["epoch_time", "power", "energy"]] 

for epoch in all_epochs:
    power = power_dict.get(epoch , "N/A")
    energy = energy_dict.get(epoch , "N/A")
    merged.append([epoch, power, energy])


with open("merged.csv", "w", newline="") as fm:
    writer = csv.writer(fm)
    writer.writerows(merged)

print("merged.csv created successfully!")

