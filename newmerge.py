import csv

def read_file(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader) 
        for row in reader:
            gmt_dt= (row[0])
            epoch = int (row[1])
            value = row[2]
            yield epoch, gmt_dt, value

power = read_file("p.csv")
energy = read_file("e.csv")

p = next(power, None)
e = next(energy, None)

with open("m.csv", "w", newline="") as fm:
    writer = csv.writer(fm)
    writer.writerow(["gmt_dt", "epoch_time", "Power", "Energy"])

    while p or e:

        if e is None or (p and p[0] < e[0]):
            writer.writerow([p[1], p[0], p[2], "N/A"])
            p = next(power, None)

        elif p is None or (e and e[0] < p[0]):
            writer.writerow([e[1], e[0], "N/A", e[2]])
            e = next(energy, None)

        else:
            writer.writerow([p[1], p[0], p[2], e[2]])
            p = next(power, None)
            e = next(energy, None)

print("merged.csv created successfully!")
