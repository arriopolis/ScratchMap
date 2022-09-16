# ScratchMap
-------

This tool allows you to make a scratch map from your Google Timeline history.

**Quick setup instructions:**

1. Download your location data from Google Takeout, and save to your computer (unzip if necessary etc.).
2. Locate the file `Records.json`.
3. Make sure the `src_filename` field in `config.txt` points to this file.
4. Run `01-parse_takeout.py`. This will read the data from the Google Takeout repository.
5. Run `02-clean_records.py`. This will clean the data (remove duplicate entries, outliers, etc.)
6. *Optional:* Run `03-investigate_records.py`. This allows you to get a month-by-month preview of the data points extracted from the repository.
7. Run `04-plot_locations.py`. This will generate the picture for you.

Changing the settings in `config.txt` allows you to play with how the image looks.

Additionally, you can manually add extra locations by supplying the file `extra_locations.txt`. An example of what this file could look like:

    # Holiday to Greece
    year 2012
    month Jul
    add 37.98397974428001, 23.731033808396617     # Athens
    add 38.25804743845491, 21.724896197015667     # Patras
    add 40.701352533079174, 22.89230887119319     # Thessaloniki
    add 35.422479845257534, 25.12070029516918     # Heraklion

Similarly, you can manually ignore locations by supplying the file `clean_rules.txt`. An example of what this file could look like is listed below:

    # Null island
    ignore 0,0

    # Weird rounded points
    ignore 60000000,519999999
    ignore 60000000,520000000

    # Flights to and from Albania
    ignore_time_range 2015,8,21,19,36,47,2015,8,21,19,39,11
    ignore_time_range 2015,8,30,20,47,19,2015,8,30,20,56,58

Feel free to play around and experiment with these files.
