import json, ijson
parse_lat_lon = lambda s : map(lambda x : float(x.rstrip('°')), s.split(', '))

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
data = json.load(open(filename))

locations = []
print("Parsing semantic segments...")
for rec in data['semanticSegments']:
    if 'timelinePath' in rec:
        for p in rec['timelinePath']:
            lat,lon = parse_lat_lon(p['point'])
            t = p['time']
            locations.append((lat,lon,t))
    elif 'visit' in rec:
        lat,lon = parse_lat_lon(rec['visit']['topCandidate']['placeLocation']['latLng'])
        t = rec['startTime']
        locations.append((lat,lon,t))
    elif 'activity' in rec:
        lat,lon = parse_lat_lon(rec['activity']['start']['latLng'])
        t = rec['startTime']
        locations.append((lat,lon,t))
        lat,lon = parse_lat_lon(rec['activity']['end']['latLng'])
        t = rec['endTime']
        locations.append((lat,lon,t))

print("Parsing raw signals...")
for rec in data['rawSignals']:
    if 'position' in rec:
        lat,lon = parse_lat_lon(rec['position']['LatLng'])
        t = rec['position']['timestamp']
        locations.append((lat,lon,t))
print("Number of locations:", len(locations))

filename = CONFIG['parsed_filename']
print("Writing to", filename, "...")
with open(filename, 'w') as f:
    json.dump(locations, f)
print("Done.")
