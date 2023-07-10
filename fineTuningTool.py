import csv

data = {}
with open('test.csv', newline='') as csvfile:  # not available for Now
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        data[i] = row

print(data)
