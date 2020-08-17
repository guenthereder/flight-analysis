#!/usr/bin/env python3

# SETUP
URL = 'https://www.xcontest.org/world/en/flights/'
SUB = '#flights[sort]=reg@filter[country]=AT@filter[detail_glider_catg]=FAI3@'
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

# handles sqlite interaction
import my_sqlite as db


class Flight:
    def __init__(self, datetime, pilot, launch, length, points, airtime, glider,
                 pilot_link, launch_link, flight_link):
        self.datetime, self.pilot, self.launch, self.length, self.points, self.airtime, self.glider, self.pilot_link, self.launch_link, self.flight_link = datetime, pilot, launch, length, points, airtime, glider, pilot_link, launch_link, flight_link

    def __str__(self):
        return self.datetime.strftime("%d.%m.%Y") + ", " + self.pilot + ", " + self.launch + ", " + str(self.length) \
               + ", " + str(self.points) + ", " + self.airtime.strftime("%H:%M") + ", " + self.glider

    def db(self):
        return self.datetime.strftime("%d.%m.%Y"), self.pilot, self.launch, self.length, self.points, \
               self.airtime.strftime("%H:%M"), self.glider, self.pilot_link, self.launch_link, self.flight_link


def scrap(args, url_base, url_sub):
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
                flight_link = []
                for atr in flight.find_all('td'):
                    flight_info.append(atr.text)
                    link = atr.find('a').get('href') if atr.find('a') is not None else None
                    if link is not None:
                        flight_link.append(link)

                f_datedate, f_time = flight_info[1].split(' ')[0], flight_info[1].split(' ')[1]
                f_date = f_datedate + ' ' + f_time.split(':')[0] + ':' + f_time.split(':')[1] + '00'

                try:
                    f_date = dt.datetime.strptime(f_date, '%d.%m.%y %H:%M=UTC%z')
                except ValueError:
                    try:
                        f_date = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%M00')
                    except ValueError:
                        f_date = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%M UTC')

                f_pilot = flight_info[2][2:]
                f_launch = flight_info[3][2:]
                f_km = float(flight_info[5][:-3])
                f_pnts = float(flight_info[6][:-3])
                f_airtime = dt.datetime.strptime(flight_info[7], ' %H : %M h').time()
                f_glider = flight_info[8]

                if len(flight_link) == 3:
                    f_pilot_link, f_launch_link, f_flight_link = flight_link[0], flight_link[1], flight_link[2]
                else:
                    print("Warning: len(flight_link) == ", len(flight_link))
                    f_pilot_link, f_launch_link, f_flight_link = " ", " ", " "

                # print(f_date,f_pilot,f_launch,f_km,f_pnts,f_airtime)
                flights.append(Flight(f_date, f_pilot, f_launch, f_km, f_pnts, f_airtime, f_glider, f_pilot_link,
                                      f_launch_link, f_flight_link)
                               )

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


def main():
    parser = argparse.ArgumentParser(description='XContest Flight Scrapper for science and non-commercial interests.')
    parser.add_argument('--num_flights', dest='num_flights', type=int, default=100, help='number of flights to scrap (default: 100)')
    parser.add_argument('--all', type=bool, dest='all', default=False, help='scrap all flights')
    parser.add_argument('--db-file', dest='db_file', default='xcontest_flights_at.db', help='DB file for storing data')
    parser.add_argument('--create-db', type=bool, dest='db_create', default=False, help='DB file for storing data')
    args = parser.parse_args()

    flights = scrap(args, URL, SUB)

    [print(x) for x in flights]

    conn = db.create_connection(args.db_file)

    # create tables
    if conn is not None:
        # create projects table
        db.create_table(conn)
        # insert data
        [db.create_flight(conn, flight.db()) for flight in flights]

        conn.close()

    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
