from country_consolidation import run
from datetime import datetime
import logging

years = [2022]
months = range(1,12,1)

logging.basicConfig(filename='longitudinal_consolidation.log', encoding='utf-8', level=logging.WARNING)
logging.warning(f'Start analysis on {datetime.today()}')

for year in years:
    for month in months:
        try:
            start_date = '{year}-{month:02d}-01T00:00'.format(year=year, month=month)
            end_date = '{year}-{month:02d}-07T00:00'.format(year=year, month=month)

            run(start_date, end_date)
        except Exception as e:
            logging.error(f'Could not do {year}/{month:02d}')
            logging.error(e)


logging.warning(f'End analysis on {datetime.today()}')
