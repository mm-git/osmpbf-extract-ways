# osmpbf-extract-ways

This is a python sample code for extracting ways from osm.pbf file.

## CAUTION

This code uses very very huge size of memory. It is more than 36GB.
However physical memory is not necessary so much.
After running this code, s large size of paging file will be created.

## Requirements

- macOS 10.11+ (I've checked this code only 10.11[El Capitan])
- Python 2.7
- packages(ConfigParser, imposm)
- To install imposm, you have to do `brew install tokyo-cabinet`
- SSD. (It is important.)

## How to run.

1. You have to download osm.pbf file from the distribution site.
> [geofabrik.de](http://download.geofabrik.de/index.html)
2. Edit `way.conf` file.
3. run `python main.py`

- It will take 3 hours to finish extracting data in case of asia_latest.osm.pbf. Europe might be more than 10 hour.
- To get to know the code detail, read main.py.

## LICENSE

This code is MIT LICENSE. See LICENSE file.

