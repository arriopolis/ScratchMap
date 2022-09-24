import numpy as np
import matplotlib.pyplot as plt
import shapefile, json
import datetime

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
print("Reading the locations from", filename, "...")
with open(filename) as f:
    locations = json.load(f)

# Parse the locations
xys = set()
for lat, lon, t in locations:
    xys.add((lon//1e5, lat//1e5))
xys = [(x/100,y/100) for x,y in xys]

# Parse the borders
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

# Define the mask
print("Calculating the mask...")
h,w = int(CONFIG['mask_height']),int(CONFIG['mask_width'])
s = int(CONFIG['kernel_size'])
overlay = np.zeros((h,w,4))

# Draw clouds
cloud_s = int(CONFIG['cloud_size'])
cloud_f = float(CONFIG['cloud_factor'])
overlay = np.zeros((h,w,4))
overlay[:,:,:4] = (.7,.7,.7,1.)
for _ in range(int(CONFIG['cloud_num'])):
    x = np.random.randint(0,w-1)
    y = np.random.randint(0,h-1)
    f = cloud_f * np.random.random()
    offset = f / (1 + (np.arange(-cloud_s,cloud_s+1)[:,np.newaxis]**2 + np.arange(-cloud_s,cloud_s+1)[np.newaxis,:]**2)**.25)

    ymin = max(0,y-cloud_s)
    ymax = min(h-1,y+cloud_s)
    xmin = max(0,x-cloud_s)
    xmax = min(w-1,x+cloud_s)
    overlay[ymin:ymax+1,xmin:xmax+1,:] += (offset[cloud_s-(y-ymin):cloud_s+(ymax-y+1),cloud_s-(x-xmin):cloud_s+(xmax-x+1)])[:,:,np.newaxis] * np.array([1,1,1,.5])[np.newaxis,np.newaxis,:]

for x,y in xys:
    cx,cy = int((x+180)*w)//360, int((90-y)*h)//180
    xmin,xmax = max(cx-s,0),min(cx+s+1,w)
    ymin,ymax = max(cy-s,0),min(cy+s+1,h)
    xoffl,xoffr = max(xmin-cx+s,0),max(cx+s+1-xmax,0)
    yofft,yoffb = max(ymin-cy+s,0),max(cy+s+1-ymax,0)
    mask = np.sqrt(np.linspace(-1,1,2*s+1)[:,np.newaxis]**2 + np.linspace(-1,1,2*s+1)[np.newaxis,:]**2)
    overlay[ymin:ymax,xmin:xmax,3] = np.minimum(overlay[ymin:ymax,xmin:xmax,3], mask[yofft:2*s+1-yoffb,xoffl:2*s+1-xoffr])

# Plot the picture
print("Generating the picture...")
fig = plt.figure(figsize = (16,8))
fig.patch.set_facecolor('lightblue')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax = fig.gca()
ax.axis('off')
ax.set_aspect('equal')
for borders in countries:
    for border in borders:
        ax.fill(*zip(*border), color = (.5,.3,.3))
        ax.plot(*zip(*border), color = 'k')
ax.imshow(overlay, extent = (-180,180,-90,90), zorder = 10)
ax.text(179, -89, 'Latest update: ' + datetime.date.today().strftime("%B %Y").capitalize(), ha = 'right', va = 'bottom', color = 'lightgray', zorder = 10)

print("Saving the image...")
plt.savefig(CONFIG['img_filename'], bbox_inches='tight')
print("Saved the image to", CONFIG['img_filename'])

print("Displaying the image...")
plt.show()

print("Done!")
