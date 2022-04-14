#!/usr/bin/env python3

### next time mechanical soup

from __credentials import *

GAIS_DAILY_SUB = "flights-search/?filter%5Bpoint%5D=13.10968+47.80302&filter%5Bradius%5D=5000&filter%5Bmode%5D=START&filter%5B" + \
                 "date_mode%5D=dmy&filter%5Bdate%5D={}&filter%5Bvalue_mode%5D=dst&filter%5Bmin_value_dst%5D=&filter%5Bcatg%5D=&filter%5B" + \
                 "route_types%5D=&filter%5Bavg%5D=&filter%5Bpilot%5D=&list%5Bsort%5D=pts&list%5Bdir%5D=down"

LOGIN = "https://www.xcontest.org/"

# SETUP
URL = 'https://www.xcontest.org/world/en/'
SUB = 'flights/#flights[sort]=points@filter[detail_glider_catg]=FAI3'
chrome_driver_path = './chromedriver'

# for years < current_year use 'https://www.xcontest.org/YEAR/world/en/flights/'

if __name__ == '__main__' and __package__ is None:
    import os
    __LEVEL = 1
    os.sys.path.append(os.path.abspath(os.path.join(*([os.path.dirname(__file__)] + ['..']*__LEVEL))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from tqdm import tqdm

from bs4 import BeautifulSoup
import datetime as dt
import argparse

# handles sqlite interaction
import my_sqlite as db
from my_sqlite import Flight
import string

chrome_options = Options()
chrome_options.headless = True
service = Service(chrome_driver_path)

prefs = {"download.default_directory" : "igc/"}
chrome_options.add_experimental_option("prefs",prefs)

driver = webdriver.Chrome(service=service, options=chrome_options)

def scrap(args, url_base, url_sub):
    """ SCRAP XContest for flights """
    flights = []

    scrapping = True
    while scrapping:
        #web_driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
        driver.set_page_load_timeout(30)

        if args.gais_daily != '':
            login(args, driver)

        wait = WebDriverWait(driver, 30)
        driver.get(url_base + url_sub)

        if args.gais_daily != '':
            wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'flights')))
        else:
            wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'pg-edge')))

        content = driver.page_source
        # print("scrapping at url:", url_sub)
        soup = BeautifulSoup(content, "lxml")

        if args.gais_daily != '':
            flight_list = soup.find('table', {"class": "flights"}).find('tbody').find_all('tr')
        else:
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
                    try:
                        f_date = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%M UTC')
                    except ValueError:
                        f_date = dt.datetime.strptime(flight_info[1], '%d.%m.%y %H:%MUTC+02:00')

            f_pilot = flight_info[2][2:]
            f_launch = flight_info[3][2:]
            f_km = float(flight_info[5][:-3])
            f_pnts = float(flight_info[6][:-3])
            try:
                f_airtime_str = ''.join([x if x in string.printable and x != ' ' else '' for x in flight_info[7]])
                f_airtime = dt.datetime.strptime(f_airtime_str, '%H:%Mh').time()
            except ValueError:
                #print("Airtime format error: ", f_airtime_str)
                f_airtime = ""

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

        next_page = soup.find('a', {"title": "next page"})
        if type(next_page) is not type(None):
            next_page_url = next_page['href']
            from_flight_old = url_sub.split('=')[-1]
            from_flight_new = next_page_url.split('=')[-1]

            scrapping = (from_flight_old is not from_flight_new)
            url_sub = next_page_url
        else:
            scrapping = False

        if len(flights) >= args.num_flights and not args.all:
            scrapping = False

    return flights


def url_for_year(url, year):
    if year == dt.datetime.now().year:
        return url

    new_base = url.split('world')
    return new_base[0] + str(year) + "/world" + new_base[1]


def url_country_mod(args, url, sub):
    if not args.world:
        sub += "@filter[country]=" + args.country

    return url, sub


def login(args, driver):
    wait = WebDriverWait(driver, 30)
    driver.get(LOGIN)
    wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'submit')))

    username_field = driver.find_element(by=By.ID, value="login-username")
    password_field = driver.find_element(by=By.ID, value="login-password")
    login = driver.find_element(by=By.CLASS_NAME, value="submit")

    username_field.send_keys(username)
    password_field.send_keys(password)
    login.click()


def write_db(args, flights):
    # write flights to db-file
    conn = db.create_connection(args.db_file)

    # create tables
    if conn is not None:
        # create projects table
        db.create_table(conn)

        # insert data
        [db.create_flight(conn, flight) for flight in tqdm(flights)]

        conn.close()

        if args.verbose:
            print("... database updated")
    else:
        print("Error! cannot create the database connection.")


def download_igc(args, flights):
    wait = WebDriverWait(driver, 30)
    for flight in flights:
        flight_url = f"https://www.xcontest.org{flight.flight_link}"
        driver.get(flight_url)
        wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'igc')))
        igc = driver.find_element(by=By.CLASS_NAME, value="igc")
        href=igc.find_element(by=By.TAG_NAME, value="a")

        if args.verbose:
            print(f"downloading {href.get_attribute('href')}")

        href.click()
        

def main():
    flights = []
    current_year = dt.datetime.now().year

    parser = argparse.ArgumentParser(description='XContest Flight Scrapper for science and non-commercial interests.')
    parser.add_argument('--write-db', action="store_true", default=False, help='write to db file')
    parser.add_argument('--flights', dest='num_flights', type=int, default=100, help='number of flights to scrap')
    parser.add_argument('--world', action="store_true", default=False, help='use world flight list, not country based (default: False)')
    parser.add_argument('--country', dest='country', default='AT', help='two letter country code (default: AT)')
    parser.add_argument('--all', action="store_true", default=False, help='scrap all flights')
    parser.add_argument('--db-file', dest='db_file', default='xcontest_flights.db', help='DB file for storing data (default: xcontest_flights.db)')
    parser.add_argument('--year', type=int, dest='year', default=current_year, help='scrap flights of all years (default: current year)')
    parser.add_argument('--all-years', action="store_true", default=False, help='scrap flights of all years (default: False, first is 2007)')
    parser.add_argument('--status', action="store_true", default=False, help='print debug information')
    parser.add_argument('--verbose', action="store_true", default=False, help='print debug information')

    '''extending'''
    parser.add_argument('--gais-daily', default='', help='crawl ONLY gaisberg flights for a given date (format yyyy-mm-dd)')
    parser.add_argument('--download', action="store_true", default=False, help='download igc files')

    args = parser.parse_args()

    # url modification based on parser arguments
    base, sub = url_country_mod(args, URL, SUB)

    if args.gais_daily != '':
        sub = GAIS_DAILY_SUB.format(args.gais_daily)
    
    # flight scrapping
    years = range(2007, current_year) if args.all_years else [args.year]
    for year in tqdm(years):
        l_base = url_for_year(base, year)
        new_flights = scrap(args, l_base, sub)
        flights += new_flights
        if args.verbose:
            [print(flight) for flight in new_flights]

    if args.verbose:
        print(len(flights), "flights scrapped")

    if args.write_db:
        write_db(args, flights)

    if args.download:
        download_igc(args,flights)

    driver.close()


if __name__ == '__main__':
    main()
