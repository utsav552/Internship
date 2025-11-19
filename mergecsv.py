import csv

def read_file(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader) 
        for row in reader:
            yield float(row[0]), row[1] 

power_dict  = dict(read_file("power.csv"))
energy_dict = dict(read_file("energy.csv"))

all_epochs = sorted(power_dict.keys() | energy_dict.keys())

def merged_rows():
    yield ["epoch_time", "Power", "Energy"]
    for epoch in all_epochs:
        yield [
            epoch,
            power_dict.get(epoch, "N/A"),
            energy_dict.get(epoch, "N/A"),
        ]

with open("merged.csv", "w", newline="") as fm:
    writer = csv.writer(fm)
    writer.writerows(merged_rows())

print("merged.csv created successfully!")
