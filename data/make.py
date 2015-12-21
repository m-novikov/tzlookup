#!/usr/bin/env python2
import fiona
import sys
from shapely.geometry import shape, box
import rtree
from multiprocessing import Pool, Array, cpu_count
from json import dump


TIMEZONE_INTERNATIONAL_LIST = [
    "Etc/GMT+12", "Etc/GMT+11", "Etc/GMT+10", "Etc/GMT+9",  "Etc/GMT+8",
    "Etc/GMT+7",  "Etc/GMT+6",  "Etc/GMT+5",  "Etc/GMT+4",  "Etc/GMT+3",
    "Etc/GMT+2",  "Etc/GMT+1",  "Etc/GMT",    "Etc/GMT-1",  "Etc/GMT-2",
    "Etc/GMT-3",  "Etc/GMT-4",  "Etc/GMT-5",  "Etc/GMT-6",  "Etc/GMT-7",
    "Etc/GMT-8",  "Etc/GMT-9",  "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12"
]


def get_bbox(lat, lon):
    return lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05


def drange(start, stop, step):
    r = start
    while r > stop:
        yield r
        r += step


class TZData(object):
    def __init__(self, shapefiles):
        self.tz_map = {}
        _tznames = set(TIMEZONE_INTERNATIONAL_LIST)
        idx = 0
        for shapefile in shapefiles:
            with fiona.open(shapefile, 'r') as tz_file:
                for tz_data in tz_file:
                    tzname = tz_data['properties']['TZID']
                    if tzname in ('uninhabited', 'unknown'):
                        continue

                    _tznames.add(tzname)
                    self.tz_map[idx] = {
                        'geometry': shape(tz_data['geometry']),
                        'tzname': tzname
                    }
                    idx += 1

        # Store timezones in sorted order
        self.tznames = sorted(_tznames)
        self.tzname_to_id = {
            tzname: idx
            for idx, tzname in enumerate(self.tznames)
        }

        def rtree_stream():
            for idx, item in self.tz_map.iteritems():
                yield idx, item['geometry'].bounds, idx

        self.index = rtree.index.Index(rtree_stream())

    def _get_tz_name(self, lat, lon):
        bbox = get_bbox(lat, lon)
        polygon = box(*bbox)
        max_area = 0
        tz_name = None
        timezones = list(self.index.intersection(bbox, objects='raw'))
        for idx in timezones:
            tz_poly = self.tz_map[idx]['geometry']

            if tz_poly.intersects(polygon):
                if len(timezones) == 1:
                    return self.tz_map[idx]['tzname']

                cur_area = tz_poly.intersection(polygon).area
                # More than a half or 0.1 x 0.1 cell
                if cur_area >= 0.005:
                    return self.tz_map[idx]['tzname']

                if cur_area > max_area:
                    max_area = cur_area
                    tz_name = self.tz_map[idx]['tzname']

        if not tz_name:
            return TIMEZONE_INTERNATIONAL_LIST[int(round((180.0 + lon) / 15.0))]

        return tz_name

    def get_tz_id(self, lat, lon):
        tzname = self._get_tz_name(lat, lon)
        return self.tzname_to_id[tzname]


arr = Array('H', 1801 * 3601, lock=False)
index = None


def print_usage():
    print "Run this program like %s <list of shapefiles>" % sys.argv[0]


def main():
    global index
    if len(sys.argv) < 2:
        print_usage()
        return 1
    index = TZData(sys.argv[1:])
    print "Index is ready"

    latlons = [(lat, lon)
               for lat in drange(90.0, -90.0, -0.1)
               for lon in drange(180.0, -180.0, -0.1)]
    pool = Pool(cpu_count())
    for idx, elem in enumerate(pool.imap(process, latlons)):
        sys.stdout.write('{:7.2%}\r'.format(idx / 6485401.0))
        sys.stdout.flush()

    with open('./names.json', 'w+') as out_names:
        dump(index.tznames, out_names)

    with open('./array', 'wb+') as out_arr:
        out_arr.write(arr)

    return 0


def process(latlon):
    lat, lon = latlon
    idx = int(3601 * (900 - round(lat * 10)) + (1800 - round(lon * 10)))
    arr[idx] = index.get_tz_id(lat, lon)

if __name__ == '__main__':
    exit(main())
