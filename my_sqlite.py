#!/usr/bin/env python3

import sqlite3
from sqlite3 import Error

""" datetime, pilot, launch, length, points, airtime, glider """
DEFAULT_TABLE = """CREATE TABLE IF NOT EXISTS flights (
                                    date text NOT NULL,
                                    pilot text NOT NULL,
                                    launch text NOT NULL, 
                                    length real NOT NULL, 
                                    points real NOT NULL, 
                                    airtime text NOT NULL, 
                                    glider text NOT NULL,
                                    pilot_link text NOT NULL, 
                                    launch_link text NOT NULL, 
                                    flight_link text NOT NULL,
                                    PRIMARY KEY (flight_link)
                                );"""


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

    sql = ''' INSERT OR IGNORE INTO flights(date, pilot, launch, length, points, airtime, glider, pilot_link, launch_link, flight_link)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, flight)
    conn.commit()

    return cur.lastrowid
