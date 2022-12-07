import os
from country_consolidation import run
from datetime import datetime
import logging

YEARS = [2019,2020,2021,2022]
MONTHS = range(1,13,1)
OUTPUT_FNAME =  'country_consolidation_scores_{start_date}_{end_date}.txt'

def compute_consolidation(force=False):
    success = True
    for year in YEARS:
        for month in MONTHS:
            try:
                start_date = '{year}-{month:02d}-01T00:00'.format(year=year, month=month)
                end_date = '{year}-{month:02d}-07T00:00'.format(year=year, month=month)

                output = OUTPUT_FNAME.format( start_date=start_date, end_date=end_date)

                # Compute country consolidation
                if not os.path.exists(output) or force:
                    run(start_date, end_date)

            except Exception as e:
                success = False
                logging.error(f'Could not do {year}/{month:02d}')
                logging.error(e)

    return success

def compute_csv():

    # CSV file name is composed of the first and last analyzed date
    start_date = '{year}-{month:02d}-01T00:00'.format(year=YEARS[0], month=MONTHS[0])
    end_date = '{year}-{month:02d}-07T00:00'.format(year=YEARS[-1], month=MONTHS[-1])
    out_fname = OUTPUT_FNAME.format(start_date=start_date, end_date=end_date).rpartition('.')[0]+'.csv'
    csv = open( out_fname, 'w' )
    header = False

    for year in YEARS:
        for month  in MONTHS:

            start_date = '{year}-{month:02d}-01T00:00'.format(year=year, month=month)
            end_date = '{year}-{month:02d}-07T00:00'.format(year=year, month=month)

            in_fname = OUTPUT_FNAME.format( start_date=start_date, end_date=end_date)
            with open(in_fname, 'r') as fp:
                for i, line in enumerate(fp.readlines()):

                    if i == 0 :
                        # Write file header
                        if not header:
                            header = True
                            #csv.write(','.join(['date']+line.split())+'\n')
                            csv.write('cc,consolidation_as,consolidation_pop,nb_stub_as,transit_as,transit_pop,max_pop_asn\n')

                        # Skip header
                        continue

                    # Write data
                    csv.write(','.join([f'{year}/{month:02d}/07']+line.split())+'\n')


if __name__ == '__main__':
    logging.basicConfig(filename='longitudinal_consolidation.log', encoding='utf-8', level=logging.WARNING)
    logging.warning(f'Start analysis on {datetime.today()}')

    if compute_consolidation():
        compute_csv()

    logging.warning(f'End analysis on {datetime.today()}')



