#!/usr/bin/env python3

import my_sqlite as db
from my_sqlite import Flight
import argparse
import datetime as dt


def main():
    current_year = dt.datetime.now().year
    parser = argparse.ArgumentParser(description='XContest Flight Analyzer for science and non-commercial interests.')
    parser.add_argument('--flights', dest='num_flights', type=int, default=100, help='number of flights to scrap (default: 100)')
    parser.add_argument('--world', action="store_true", default=False, help='use world flight list, not country based (default: False)')
    parser.add_argument('--country', dest='country', default='AT', help='two letter country code (default: AT)')
    parser.add_argument('--all', action="store_true", default=False, help='scrap all flights')
    parser.add_argument('--year', type=int, dest='year', default=current_year, help='scrap flights of specific (default: current year)')
    parser.add_argument('--all-years', action="store_true", default=False, help='scrap flights of all years (default: False, first is 2007)')
    parser.add_argument('--status', action="store_true", default=False, help='print debug information')
    parser.add_argument('--verbose', action="store_true", default=False, help='print debug information')
    parser.add_argument('db_file', default='xcontest_flights.db', help='DB file data query (default: xcontest_flights.db)')
    args = parser.parse_args()

    conn = db.create_connection(args.db_file)

    # create tables
    if conn is not None:
        # query stuff
        logic = 'AND'


        select = {'year': current_year, 'country': args.country}

        flights = db.query_flights(conn, logic, **select)

        for f in flights:
            print(f)

        # insert data
        #[db.create_flight(conn, flight.db()) for flight in tqdm(flights)]

        conn.close()

        if args.verbose:
            print("... database updated")
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
