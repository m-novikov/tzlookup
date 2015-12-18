import sys
import sqlite3
from array import array
from json import dump
from subprocess import call

# TODO: Parallel execution
# TODO: Sea tz (Etc/*) must be mapped if possible to nearest known timezone
# possible second iteration

TIMEZONE_INTERNATIONAL_LIST = [
    "Etc/GMT+12", "Etc/GMT+11", "Etc/GMT+10", "Etc/GMT+9",  "Etc/GMT+8",
    "Etc/GMT+7",  "Etc/GMT+6",  "Etc/GMT+5",  "Etc/GMT+4",  "Etc/GMT+3",
    "Etc/GMT+2",  "Etc/GMT+1",  "Etc/GMT",    "Etc/GMT-1",  "Etc/GMT-2",
    "Etc/GMT-3",  "Etc/GMT-4",  "Etc/GMT-5",  "Etc/GMT-6",  "Etc/GMT-7",
    "Etc/GMT-8",  "Etc/GMT-9",  "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12"
]

QUERY = """
SELECT tzid
FROM tz_world, (
    SELECT PolyFromText('POLYGON((%(min_lon)s %(min_lat)s, %(max_lon)s %(min_lat)s, %(max_lon)s %(max_lat)s, %(min_lon)s %(max_lat)s, %(min_lon)s %(min_lat)s))') as geometry
) as polygon
WHERE tz_world.ROWID IN (
    SELECT pkid
    FROM idx_tz_world_Geometry
    WHERE xmin <= %(min_lon)s AND
          ymin <= %(min_lat)s AND
          xmax >= %(max_lon)s AND
          ymax >= %(max_lat)s
) AND ST_Intersects(tz_world.geometry, polygon.geometry)
"""

QUERY_PRECISE = """
SELECT tzid
FROM tz_world, (
    SELECT PolyFromText('POLYGON((%(min_lon)s %(min_lat)s, %(max_lon)s %(min_lat)s, %(max_lon)s %(max_lat)s, %(min_lon)s %(max_lat)s, %(min_lon)s %(min_lat)s))') as geometry
) as polygon
WHERE tzid IN (%(tzids)s)
ORDER BY Area(Intersection(tz_world.geometry, polygon.geometry)) DESC
LIMIT 1
"""

QUERY_TZID = "SELECT DISTINCT tzid FROM tz_world"


def drange(start, stop, step):
    r = start
    while r > stop:
        yield r
        r += step


def get_db(folder):
    db = sqlite3.connect(':memory:')
    db.enable_load_extension(1)
    db.load_extension('mod_spatialite')
    db.execute('SELECT InitSpatialMetaData()')
    db.execute('CREATE VIRTUAL TABLE tz_world_tmp USING VirtualShape("%s/tz_world", CP1252, 4326)' % folder)
    db.execute('CREATE TABLE tz_world AS SELECT * FROM tz_world_tmp')
    db.execute('SELECT RecoverGeometryColumn("tz_world", "Geometry", 4326, "POLYGON", 2)')
    db.execute('SELECT CreateSpatialIndex("tz_world", "Geometry")')
    return db


def build_box(lat, lon):
    res = {}
    if lon < 0:
        res['min_lon'] = lon + 0.05
        res['max_lon'] = lon - 0.05
    else:
        res['min_lon'] = lon - 0.05
        res['max_lon'] = lon + 0.05

    if lat < 0:
        res['min_lat'] = lat + 0.05
        res['max_lat'] = lat - 0.05
    else:
        res['min_lat'] = lat - 0.05
        res['max_lat'] = lat + 0.05

    return res


def get_tz_name(db, lat, lon):
    bounds = build_box(lat, lon)
    cursor = db.execute(QUERY % bounds)
    res = cursor.fetchall()
    if res:
        if len(res) == 1:
            return res[0][0]
        else:
            tzids = ','.join(["'%s'" % tzid for tzid in res])
            bounds['tzids'] = tzids
            cursor = db.execute(QUERY_PRECISE % bounds)
            res = cursor.fetchone()
            return res[0]
    else:
        return TIMEZONE_INTERNATIONAL_LIST[int(round((180.0 + lon) / 15.0))]


def print_usage():
    print "%s <tz_world folder>" % sys.argv[0]


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    db = get_db(sys.argv[1])
    cur = db.execute(QUERY_TZID)
    TZ = [elem[0] for elem in cur.fetchall()]
    TZ.extend(TIMEZONE_INTERNATIONAL_LIST)
    TZ.sort()

    with open('./names.json', 'w+') as out_names:
        dump(TZ, out_names)
    print "Total timezones %s" % len(TZ)

    res = array('H')
    for lat in drange(90.0, -90.0, -0.1):
        for lon in drange(180.0, -180.0, -0.1):
            name = get_tz_name(db, lat, lon)
            res.append(TZ.index(name))
        percentage = (10 * (90.0 - lat) / 1801)
        sys.stdout.write(
            'Progress: {:7.2%} Current lat: {:6.1f}\r'.format(percentage, lat)
        )
        sys.stdout.flush()

    with open('./array', 'w+') as out_arr:
        res.tofile(out_arr)

    return 0

if __name__ == '__main__':
    exit(main())
