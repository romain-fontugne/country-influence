from collections import Counter
import requests_cache

START_DATE = '2022-05-01T00:00'
END_DATE = '2022-05-31T00:00'
CC_ISPS = 'ES'
API_ISPS = "https://ihr.iijlab.net/ihr/api/hegemony/countries/?timebin__lte={end_date}&timebin__gte={start_date}&country={country_isp}&hege__gte=0.01&format=json"
API_DEPENDENT = "https://ihr.iijlab.net/ihr/api/hegemony/countries/?timebin__lte={end_date}&timebin__gte={start_date}&asn={asns}&transitonly=false&format=json"

OUTPUT_AS = f'{CC_ISPS}_{START_DATE}_{END_DATE}_dependent_countries_as.txt'
OUTPUT_EYEBALL = f'{CC_ISPS}_{START_DATE}_{END_DATE}_dependent_countries_eyeball.txt'

# Find the main ISPs for the given country
session = requests_cache.CachedSession()
isp_url = API_ISPS.format(start_date=START_DATE, end_date=END_DATE, country_isp=CC_ISPS)
print(isp_url)
resp = session.get(isp_url)

isps = set()
if resp.ok:
    isp_data = resp.json()
    for result in isp_data['results']: 
        if result['hege'] > 0.01 and result['asn_name'].endswith(CC_ISPS):
            isps.add(str(result['asn']))

    print(f'Found {len(isps)} ISPs in {CC_ISPS}\n')
else:
    print(f'ERROR: Could not find ISPs in {CC_ISPS}\n')

# Find countries depending on found ISPs
unique_dates = set()
country_counts = {'as': Counter(), 'eyeball': Counter()}
resp = session.get(API_DEPENDENT.format(start_date=START_DATE, end_date=END_DATE, asns=','.join(isps)))

if resp.ok:
    isp_data = resp.json()
    for result in isp_data['results']: 
        unique_dates.add(result['timebin'])
        country_counts[result['weightscheme']][result['country']] += result['hege']

with open(OUTPUT_AS, 'w') as fp:
    for cc, hege in country_counts['as'].most_common():
        fp.write(f'{cc} {hege/len(unique_dates):02f}\n')

with open(OUTPUT_EYEBALL, 'w') as fp:
    for cc, hege in country_counts['eyeball'].most_common():
        fp.write(f'{cc} {hege/len(unique_dates):02f}\n')
