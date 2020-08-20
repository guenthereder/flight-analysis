#!/usr/bin/env python3

import sqlite3
from sqlite3 import Error
import datetime as dt
from datetime import timedelta

""" datetime, pilot, launch, length, points, airtime, glider """
FLIGHTS_TABLE = """CREATE TABLE IF NOT EXISTS flights (
                                    year integer NOT NULL,
                                    month integer NOT NULL,
                                    day integer NOT NULL,
                                    pilot text NOT NULL,
                                    launch text NOT NULL, 
                                    length real NOT NULL, 
                                    points real NOT NULL, 
                                    hours integer NOT NULL, 
                                    minutes integer NOT NULL, 
                                    glider text NOT NULL,
                                    pilot_link text NOT NULL, 
                                    launch_link text NOT NULL, 
                                    flight_link text NOT NULL,
                                    PRIMARY KEY (flight_link),
                                    FOREIGN KEY(launch_link) REFERENCES sites(site_link)
                                );"""

LAUNCH_SITES_TABLE = """CREATE TABLE IF NOT EXISTS sites (
                                    site text NOT NULL,
                                    site_link text primary key
                                );"""


class Flight:
    def __init__(self, datetime, pilot, launch, length, points, airtime, glider,
                 pilot_link, launch_link, flight_link):
        self.datetime, self.pilot, self.launch, self.length, self.points, self.airtime, self.glider, self.pilot_link, self.launch_link, self.flight_link = datetime, pilot, launch, length, points, airtime, glider, pilot_link, launch_link, flight_link

    def __str__(self):
        return self.datetime.strftime("%d.%m.%Y") + ", " + self.pilot + ", " + self.launch + ", " + str(self.length) \
               + ", " + str(self.points) + ", " + str(self.airtime) + ", " + self.glider

    def db_site(self):
        return self.launch, self.launch_link

    def db_flight(self):
        return self.datetime.year, self.datetime.month, self.datetime.day, self.pilot, self.launch, self.length, self.points, \
               self.airtime.hour, self.airtime.minute, self.glider, self.pilot_link, self.launch_link, self.flight_link


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql=[FLIGHTS_TABLE, LAUNCH_SITES_TABLE]):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    for table in create_table_sql:
        try:
            c = conn.cursor()
            c.execute(table)
        except Error as e:
            print(e)


def create_flight(conn, flight):
    """
    Create a new task
    :param conn:
    :param flight:
    :return:
    """
    sql1 = ''' INSERT OR IGNORE INTO sites(site, site_link) VALUES(?,?) '''
    sql2 = ''' INSERT OR IGNORE INTO flights(year, month, day, pilot, launch, length, points, hours, minutes, glider, 
                                pilot_link, launch_link, flight_link) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql1, flight.db_site())
    conn.commit()

    cur = conn.cursor()
    cur.execute(sql2, flight.db_flight())
    conn.commit()

    return cur.lastrowid


def query_flights(conn, logic='AND', **args):
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

        print(query)
        query = query.rsplit(' ', 1)[0]
        print(query)

    cur = conn.cursor()
    cur.execute("SELECT * FROM flights" + query, ([args[x] for x in args]))

    for a in args:
        print(a, args[a])

    rows = cur.fetchall()

    flights = []
    for flight in rows:
        f_date = dt.datetime(year=flight[0], month=flight[1], day=flight[2])
        f_airtime = timedelta(hours=flight[7], minutes=flight[8])
        flights.append(Flight(f_date, flight[3], flight[4], flight[5], flight[6], f_airtime, flight[9], flight[10], flight[11], flight[12]))

    return flights