#!/usr/bin/env python3

# SETUP
url_base = 'https://www.xcontest.org/world/en/flights/'
url_sub = '#flights[sort]=reg@filter[country]=AT@filter[detail_glider_catg]=FAI3@'
chrome_driver_path = '/localhome/gue/devel/flightAnalysis/chromedriver'

if __name__ == '__main__' and __package__ is None:
    import os
    __LEVEL = 1
    os.sys.path.append(os.path.abspath(os.path.join(*([os.path.dirname(__file__)] + ['..']*__LEVEL))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup
import datetime as dt
import argparse
import sqlite3
from sqlite3 import Error


class Flight:
    def __init__(self, datetime, pilot, launch, length, points, airtime, glider):
        self.datetime, self.pilot, self.launch, self.length, self.points, self.airtime, self.glider = datetime, pilot, launch, length, points, airtime, glider


def scrap(args,url_base,url_sub):
    """ SCRAP XContest for flights """
    flights = []

    chrome_options = Options()
    chrome_options.headless = True

    scrapping = True
    while scrapping:
        web_driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

        with web_driver as driver:

            wait = WebDriverWait(driver, 10)
            driver.get(url_base + url_sub)
            wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'pg-edge')))
            content = driver.page_source
            print("scrapping at url:", url_sub)

            soup = BeautifulSoup(content, "lxml")

            flight_list = soup.find('table', {"class": "XClist"}).find('tbody').find_all('tr')
            for flight in flight_list:
                flight_info = []
                for atr in flight.find_all('td'):
                    flight_info.append(atr.text)

                fdatedate, ftime = flight_info[1].split(' ')[0], flight_info[1].split(' ')[1]
                fdate = fdatedate + ' ' + ftime.split(':')[0] + ':' + ftime.split(':')[1] + '00'

                try:
                    fdate = dt.datetime.strptime(fdate, '%d.%m.%y %H:%M=UTC%z')
                except ValueError:
                    try:
                        fdate = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%M00')
                    except ValueError:
                        fdate = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%M UTC')

                fpilot = flight_info[2][2:]
                flaunch = flight_info[3][2:]
                fkm = float(flight_info[5][:-3])
                fpnts = float(flight_info[6][:-3])
                fairtime = dt.datetime.strptime(flight_info[7], ' %H : %M h').time()
                fglider = flight_info[8]

                # print(fdate,fpilot,flaunch,fkm,fpnts,fairtime)
                flights.append(Flight(fdate, fpilot, flaunch, fkm, fpnts, fairtime, fglider))

            driver.close()

        next_page_url = soup.find('a', {"title": "next page"})['href']
        from_flight_old = url_sub.split('=')[-1]
        from_flight_new = next_page_url.split('=')[-1]

        scrapping = (from_flight_old is not from_flight_new)
        url_sub = next_page_url

        print("next page url: ", next_page_url)

        if len(flights) >= args.num_flights and not args.all:
            scrapping = False

    print("number of flights:", len(flights))
    return flights


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return conn


def create_table(conn, create_table_sql):
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


def main():
    parser = argparse.ArgumentParser(description='XContest Flight Scrapper for science and non-commercial interests.')
    parser.add_argument('--num_flights', dest='num_flights', type=int, default=100, help='number of flights to scrap (default: 100)')
    parser.add_argument('--all', type=bool, dest='all', default=False, help='scrap all flights')
    parser.add_argument('--db-file', dest='db_file', default='xcontest_flights_at.db', help='DB file for storing data')
    parser.add_argument('--create-db', type=bool, dest='db_create', default=False, help='DB file for storing data')
    args = parser.parse_args()

    flights = scrap(args, url_base, url_sub)

    """ datetime, pilot, launch, length, points, airtime, glider """
    sql_create_flights_table = """CREATE TABLE IF NOT EXISTS flights (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""

    conn = create_connection(args.db_file)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_flights_table)

    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
