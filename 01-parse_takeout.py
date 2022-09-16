import json, ijson

# Read the config file
print("Reading the config file...")
CONFIG = {}
with open('config.txt') as f:
    for line in f:
        s = line.split('#')[0]
        if '=' not in s: continue
        k,v = s.strip().split('=')
        CONFIG[k.strip()] = v.strip()

filename = CONFIG['src_filename']
print("Reading from file", filename, "...")

locations = []
ctr = 0
with open(filename) as f:
    for rec in ijson.items(f, 'locations.item'):
        lat, lon = rec['latitudeE7'], rec['longitudeE7']
        t = rec['timestamp']
        locations.append((lat, lon, t))
        ctr += 1
        if ctr%1000 == 0:
            print(ctr, "records read.", end = '\r')
print("Number of locations read:", len(locations))

filename = CONFIG['parsed_filename']
print("Writing to", filename, "...")
with open(filename, 'w') as f:
    json.dump(locations, f)
print("Done.")
