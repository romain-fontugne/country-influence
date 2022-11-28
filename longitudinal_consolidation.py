import os
from country_consolidation import run
from datetime import datetime
import logging

YEARS = [2022]
MONTHS = range(1,12,1)

def compute_consolidation():
    success = True
    for year in YEARS:
        for month in MONTHS:
            try:
                start_date = '{year}-{month:02d}-01T00:00'.format(year=year, month=month)
                end_date = '{year}-{month:02d}-07T00:00'.format(year=year, month=month)


                if not os.path.exists():
                    run(start_date, end_date)
            except Exception as e:
                success = False
                logging.error(f'Could not do {year}/{month:02d}')
                logging.error(e)

    return success

def compute_csv():


logging.basicConfig(filename='longitudinal_consolidation.log', encoding='utf-8', level=logging.WARNING)
logging.warning(f'Start analysis on {datetime.today()}')

if compute_consolidation():
    compute_csv()

logging.warning(f'End analysis on {datetime.today()}')



