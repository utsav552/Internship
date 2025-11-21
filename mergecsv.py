import csv

def read_file(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            yield int(row[0]), row[1], row[2]   

power = read_file("power.csv")
energy = read_file("energy.csv")

p = next(power, None)
e = next(energy, None)

with open("merged.csv", "w", newline="") as fm:
    writer = csv.writer(fm)
    writer.writerow(["epoch_time", "gmt_dt", "Power", "Energy"])

    while p or e:

        if e is None or(p and p[0] < e[0]):
            writer.writerow([p[0], p[1], p[2], "N/A"])
            p = next(power, None)

        elif p is None or (e and e[0] < p[0]):
            writer.writerow([e[0], e[1], "N/A", e[2]])
            e = next(energy, None)

        else:
            writer.writerow([p[0], p[1], p[2], e[2]])
            p = next(power, None)
            e = next(energy, None)

print("merged.csv created successfully!")