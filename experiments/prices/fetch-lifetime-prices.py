#!/usr/bin/env python3
"""A script that will fetch missing prices.
"""
__copyright__ = "Copyright (C) 2015-2016  Martin Blais"
__license__ = "GNU GPLv2"

from dateutil.parser import parse as parse_datetime

from beancount.core.number import ZERO
from beancount.core.amount import Amount
from beancount import loader
from beancount.ops import lifetimes
from beancount.parser import printer
from beancount.core import data

from beancount.prices import find_prices
from beancount.prices import price

import datetime
from concurrent import futures
import functools

def main():
    parse_date = lambda s: parse_datetime(s).date()

    import argparse, logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('filename', help='Ledger filename')
    parser.add_argument('-c', '--compress-days', action='store', type=int, default=60,
                        help="The number of unused days to ignore.")
    parser.add_argument('-m', '--min-date', action='store', type=parse_date, default=None,
                        help="The minimum date to consider")
    args = parser.parse_args()

    # Load the ledger.
    entries, errors, options_map = loader.load_file(args.filename)

    # Build a map of existing price entries.
    price_map = {}
    for entry in entries:
        if isinstance(entry, data.Price):
            key = (entry.date, entry.currency, entry.amount.currency)
            price_map[key] = entry

    # Compute the lifetimes of currencies and compress them.
    lifetimes_map = lifetimes.get_commodity_lifetimes(entries)
    # lifetimes_map = lifetimes.compress_lifetimes_days(lifetimes_map, args.compress_days)

    # print('lifetimes_map: %s' % lifetimes_map)
    # Create price directives for missing prices.
    jobs = []
    price_entries = []
    # print('lifetimes_map: %s' % lifetimes_map)
    for key in lifetimes.required_daily_prices(lifetimes_map,
                                                entries[-1].date):
        # If the price entry is already in the ledger, ignore it.
        if key in price_map:
            continue
        date, currency, cost_currency = key

        if (currency != 'FNCNX'):
            continue
            # pass

        # Ignore entries too early.
        if args.min_date is not None and date < args.min_date:
            continue

        # Ignore entries with an empty cost currency.
        if cost_currency is None:
            continue

        print('key: %s:%s:%s' % (date, currency, cost_currency))
        # continue
        # print('date: %s' % (date))
        # Create a price directive.
        # 
        # jobs = find_prices.get_price_jobs_at_date(entries, date, undeclared_source=False)
        # job
        # for job in jobs:
        job = find_prices.DatedPrice(cost_currency, currency, date, find_prices.PriceSource(None, cost_currency, False))
        print('job: %s' % str(job))

        price_entry = price.fetch_price(job)
        # price_entries.extend(price_entry)
        print('price_entry: %s' % price_entry)
        # price = data.Price(data.new_metadata(__file__ ,0),
        #                    date, currency, Amount(ZERO, cost_currency))
        # prices.append(price)

    # For now, just print those out.
    printer.print_entries(jobs)

    # # Fetch all the required prices, processing all the jobs.
    executor = futures.ThreadPoolExecutor(max_workers=3)
    price_entries = filter(None, executor.map(
        functools.partial(price.fetch_price), jobs))
    print('jobs: %s' % jobs)
    # # Sort them by currency, regardless of date (the dates should be close
    # # anyhow, and we tend to put them in chunks in the input files anyhow).
    price_entries = sorted(price_entries, key=lambda e: e.currency)

    # # Avoid clobber, remove redundant entries.
    # if not args.clobber:
    #     price_entries, ignored_entries = filter_redundant_prices(price_entries, entries)
    #     for entry in ignored_entries:
    #         logging.info("Ignored to avoid clobber: %s %s", entry.date, entry.currency)

    # Print out the entries.
    # printer.print_entries(price_entries, dcontext=dcontext)


if __name__ == '__main__':
    main()
