import numpy as np
import shapefile
import json
import matplotlib.pyplot as plt
import dateutil.parser
import datetime
import pytz
import sys

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Read the config file
print("Reading the config file...")
CONFIG = {}
with open('config.txt') as f:
    for line in f:
        s = line.split('#')[0]
        if '=' not in s: continue
        k,v = s.strip().split('=')
        CONFIG[k.strip()] = v.strip()

# Load the locations
filename = CONFIG['cleaned_filename']
print("Reading", filename, "...")
with open(filename) as f:
    locations = json.load(f)
print("Number of locations read:", len(locations))

# Sort the locations chronologically
locations.sort(key = lambda x : x[2])

# Figure out the ranges of the months
print("Finding the available months...")
months = {}
for i,(_,_,t) in enumerate(locations):
    idx = tuple(t[:2])
    months[idx] = i+1
months_idxs = [(None,0)] + sorted(months.items())

# Parse the country borders
print("Reading country data...")
countries = []
with shapefile.Reader('data/country_borders/ne_10m_admin_0_countries') as shp:
    shapes = shp.shapes()
    for shape in shapes:
        borders = []
        parts = list(shape.parts) + [len(shape.points)]
        for sp,ep in zip(parts[:-1], parts[1:]):
            contour = shape.points[sp:ep]
            borders.append(contour)
        countries.append(borders)

print("USAGE:")
print("Click a data point on the map. Its properties are printed in the console.")
print()
for (_,start),((year,month),end) in zip(months_idxs[:-1],months_idxs[1:]):
    print("Visualize", MONTHS[month-1], "-", year, "?")
    print("Type n to skip this month:", end = ' ')
    s = input()
    if s.strip().lower() == 'n': continue

    xs,ys,ts,iss = [],[],[],[]
    print("Reading", MONTHS[month-1], "-", year, "...")
    for i,(y,x,t) in list(enumerate(locations))[start:end]:
        xs.append(x)
        ys.append(y)
        ts.append(t)
        iss.append(i)

    xs = [x/1e7 for x in xs]
    ys = [y/1e7 for y in ys]
    min_xs, max_xs = min(xs), max(xs)
    min_ys, max_ys = min(ys), max(ys)
    width = max_xs - min_xs
    height = max_ys - min_ys

    fig = plt.figure()
    ax = fig.gca()
    for borders in countries:
        for contour in borders:
            ax.plot(*zip(*contour), color = 'k')
    ax.plot(xs, ys, marker = '.', linestyle = ':')
    ax.set_title("Data points for " + str(MONTHS[month-1]) + " - " + str(year))
    ax.set_xlim((min_xs - .1*width, max_xs + .1*width))
    ax.set_ylim((min_ys - .1*height, max_ys + .1*height))
    ax.set_aspect('equal')

    def onclick(event):
        closest = (float('inf'), None, None, None, None)
        for x,y,t,i in zip(xs,ys,ts,iss):
            d = np.sqrt((x - event.xdata)**2 + (y - event.ydata)**2)
            closest = min(closest, (d,x,y,t,i))
        _,x,y,t,i = closest
        print(x,y,t,i)
        print(locations[i-1])
        print(locations[i])
        print(locations[i+1])

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()
