import sys
import time
from random import random

import psycopg2


def main(args=None):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect("dbname=test user=eocdb password=bdcoe")
        cursor = connection.cursor()

        initialize_database(connection, cursor)
        fill_database(connection, cursor)

    finally:
        clean_up_db(connection, cursor)

    return 0

def initialize_database(conn, cursor):
    print("initialize database ...")

    cursor.execute("CREATE TABLE in_situ_point (id SERIAL PRIMARY KEY, location geography(POINT), acquisition_time TIMESTAMP, description varchar);")
    conn.commit()

    print("done")

def fill_database(conn, cursor):
    num_entries = 10000
    print("fill database ({} values)...".format(num_entries))

    t_start = time.clock()

    try:

        for idx in range(0, num_entries):
            lon = 180.0 - (random() * 360.0)
            lat = 90.0 - (random() * 180.0)
            # point_wkt = 'POINT({0} {1})'.format(lon, lat)
            desc_text = "A random description, version " + str(idx)
            cursor.execute('''INSERT INTO in_situ_point(location, description) VALUES (ST_Point(%s, %s), %s);''', (lon, lat, desc_text, ))
    finally:
        conn.commit()

    print("done - ({} sec)".format(time.clock() - t_start))

def clean_up_db(connection, cursor):
    print("clean up database ...")

    cursor.execute("DROP TABLE IF EXISTS in_situ_point;")
    connection.commit()

    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

    print("done")


if __name__ == "__main__":
    sys.exit(main())
