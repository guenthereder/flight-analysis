#!/usr/bin/env python3

import sqlite3
from sqlite3 import Error
import datetime as dt

""" datetime, pilot, launch, length, points, airtime, glider """
DEFAULT_TABLE = """CREATE TABLE IF NOT EXISTS flights (
                                    year int NOT NULL,
                                    month int NOT NULL,
                                    day int NOT NULL,
                                    pilot text NOT NULL,
                                    launch text NOT NULL, 
                                    length real NOT NULL, 
                                    points real NOT NULL, 
                                    hours int NOT NULL, 
                                    minutes int NOT NULL, 
                                    glider text NOT NULL,
                                    pilot_link text NOT NULL, 
                                    launch_link text NOT NULL, 
                                    flight_link text NOT NULL,
                                    PRIMARY KEY (flight_link)
                                );"""


class Flight:
    def __init__(self, datetime, pilot, launch, length, points, airtime, glider,
                 pilot_link, launch_link, flight_link):
        self.datetime, self.pilot, self.launch, self.length, self.points, self.airtime, self.glider, self.pilot_link, self.launch_link, self.flight_link = datetime, pilot, launch, length, points, airtime, glider, pilot_link, launch_link, flight_link

    def __str__(self):
        return self.datetime.strftime("%d.%m.%Y") + ", " + self.pilot + ", " + self.launch + ", " + str(self.length) \
               + ", " + str(self.points) + ", " + self.airtime.strftime("%H:%M") + ", " + self.glider

    def db(self):
        return dt.datetime(self.datetime).year, dt.datetime(self.datetime).month, dt.datetime(self.datetime).day, self.pilot, self.launch, self.length, self.points, \
               dt.datetime(self.airtime).hour, dt.datetime(self.airtime).minute, self.glider, self.pilot_link, self.launch_link, self.flight_link


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql=DEFAULT_TABLE):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_flight(conn, flight):
    """
    Create a new task
    :param conn:
    :param flight:
    :return:
    """

    sql = ''' INSERT OR IGNORE INTO flights(year, month, day, pilot, launch, length, points, hours, minutes, glider, pilot_link, launch_link, flight_link)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, flight)
    conn.commit()

    return cur.lastrowid


def select_flights(conn, logic='AND', **args):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param logic: connection logic in query
    :param args: list of query arguments:
    :return:
    """

    # TODO!  build query from args and logic
    query = ''
    if len(args) > 0:
        query = ' WHERE '

        for a in args:
            query += a + '=? ' + logic

        query = query.split(' ')[:-1]
        print(query)

    cur = conn.cursor()
    cur.execute("SELECT * FROM flights" + query, ([x for x in args]))

    rows = cur.fetchall()

    for row in rows:
        print(row)
