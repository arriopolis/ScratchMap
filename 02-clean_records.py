import shapefile,json,os
import dateutil.parser,datetime,pytz

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ALLOWED_RULES = ['ignore','ignore_range','ignore_time_range']

# Read the config file
print("Reading the config file...")
CONFIG = {}
with open('config.txt') as f:
    for line in f:
        s = line.split('#')[0]
        if '=' not in s: continue
        k,v = s.strip().split('=')
        CONFIG[k.strip()] = v.strip()

if not os.path.exists(CONFIG['clean_rules_filename']): print("No cleaning rules file found.")
else:
    print("Reading the cleaning rules in", CONFIG['clean_rules_filename'], "...")
    RULES = {}
    with open(CONFIG['clean_rules_filename']) as f:
        for line in f:
            s = line.split('#')[0].strip()
            if not s: continue
            op = s.split(' ')[0].strip()
            assert op in ALLOWED_RULES
            if op not in RULES: RULES[op] = set()
            vals = ''.join(s.split(' ')[1:])
            RULES[op].add(tuple(map(int,vals.split(','))))

filename = CONFIG['parsed_filename']
print("Reading", filename, "...")
with open(filename) as f:
    locations = json.load(f)
print("Number of locations read:", len(locations))
locations.sort(key = lambda x : x[2])

print("Removing consecutive duplicate locations:")
lastx,lasty = None,None
unique_locations = []
for x,y,t in locations:
    if lastx != x or lasty != y:
        unique_locations.append((x,y,t))
        lastx,lasty = x,y
locations = unique_locations
print("Number of unique locations:", len(locations))

cleaned_locations = []
for i,(y,x,t) in enumerate(locations):
    d = dateutil.parser.parse(t)
    if i%1000 == 999:
        print(i+1, '/', len(locations), MONTHS[d.month-1], '-', d.year, end = '\r')

    # Check the clean rules
    if 'ignore' in RULES:
        if (x,y) in RULES['ignore']: continue
    if 'ignore_range' in RULES:
        if any(xmin <= x <= xmax and ymin <= y <= ymax for xmin,xmax,ymin,ymax in RULES['ignore_range']): continue
    if 'ignore_time_range' in RULES:
        if any(datetime.datetime(*timerange[:6], tzinfo=pytz.UTC) <= d <= datetime.datetime(*timerange[6:], tzinfo=pytz.UTC) for timerange in RULES['ignore_time_range']): continue

    # Check if it is a weird outlier
    if 0 < i < len(locations)-1:
        prevy,prevx,_ = locations[i-1]
        nexty,nextx,_ = locations[i+1]
        if int(CONFIG['outlier_multiplier'])*((prevy-nexty)**2 + (prevx-nextx)**2) <= (prevy-y)**2 + (prevx-x)**2 + (nexty-y)**2 + (nextx-x)**2: continue

    # Add it
    cleaned_locations.append((y,x,(d.year, d.month, d.day, d.hour, d.minute, d.second)))

# Read the extra locations
if not os.path.exists(CONFIG['extra_locations_filename']): print("No extra locations found.")
else:
    print("Reading the extra locations in", CONFIG['extra_locations_filename'], "...")
    day,month,year = 1,1,1970
    hour,minute,second = 0,0,0
    ctr = 0
    num_interpol = 0
    lasty,lastx = None,None
    with open(CONFIG['extra_locations_filename']) as f:
        for line in f:
            s = line.split('#')[0].strip()
            if not s: continue
            op = s.split(' ')[0].strip()
            vals = ''.join(s.split(' ')[1:])
            assert op in ['year','month','day','hour','minute','second','add','interpol']
            if op == 'add':
                y,x = map(float,vals.split(','))
                if num_interpol > 0:
                    for i in range(1,num_interpol+1):
                        newy = lasty + i*(y-lasty)/(num_interpol+1)
                        newx = lastx + i*(x-lastx)/(num_interpol+1)
                        cleaned_locations.append((int(newy*1e7), int(newx*1e7), (year,month,day,hour,minute,second)))
                        ctr += 1
                cleaned_locations.append((int(y*1e7), int(x*1e7), (year,month,day,hour,minute,second)))
                ctr += 1
                num_interpol = 0
                lasty,lastx = y,x
            elif op == 'interpol': num_interpol = int(vals)
            elif op == 'year': year = int(vals)
            elif op == 'month': month = MONTHS.index(vals.strip())+1
            elif op == 'day': day = int(vals)
            elif op == 'hour': hour = int(vals)
            elif op == 'minute': minute = int(vals)
            elif op == 'second': second = int(vals)
    print("Number of locations added:", ctr)

print("Total number of locations:", len(cleaned_locations))

filename = CONFIG['cleaned_filename']
print("Writing to", filename, "...")
with open(filename, 'w') as f:
    json.dump(cleaned_locations, f)
print("Done!")
