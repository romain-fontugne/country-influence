import argparse
from collections import defaultdict
from statistics import mean
import requests_cache

API_ASES = "https://ihr.iijlab.net/ihr/api/hegemony/countries/?timebin__lte={end_date}&timebin__gte={start_date}&country={country}&format=json"
API_ACTIVE_ASES = "https://ihr.iijlab.net/ihr/api/hegemony/?originasn=0&af=4&timebin={end_date}"


COUNTRIES = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR",
"AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
"BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO",
"BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD",
"CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI",
"HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG",
"SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF",
"PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD",
"GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN",
"HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT",
"JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG",
"LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK",
"MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT",
"MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA",
"NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP",
"NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN",
"PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN",
"LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC",
"SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES",
"LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ",
"TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV",
"UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN",
"VG", "VI", "WF", "EH", "YE", "ZM", "ZW"]

TIER1 = [174,209,286,701,1239,1299,2828,2914,3257,3320,3356,3491,5511,6453,6461,6762,6830,6939,7018,12956]

consolidation_scores = {}

def run(start_date, end_date):

    OUTPUT_FNAME = f'country_consolidation_scores_{start_date}_{end_date}.txt'

    for cc in COUNTRIES:
        # Find eyeball networks
        session = requests_cache.CachedSession()
        url = API_ASES.format(start_date=start_date, end_date=end_date, country=cc)
        print(url)
        resp = session.get(url)

        transit_ases = {'eyeball': defaultdict(list), 'as': defaultdict(list)}
        stub_ases = {'eyeball': defaultdict(list), 'as': defaultdict(list)}
        if resp.ok:
            country_hege = resp.json()
            for result in country_hege['results']: 

                # Keep total eyeball hegemony score
                if( not result['transitonly'] and result['asn_name'].endswith(cc)
                    and result['asn'] not in TIER1 ):
                    transit_ases[result['weightscheme']][result['asn']].append(result['hege'])

                # Track all eyeball networks 
                if( result['weight'] > 0 and result['asn_name'].endswith(cc) 
                    and result['asn'] not in TIER1 ):
                    stub_ases[result['weightscheme']][result['asn']].append(result['weight']/100)


            print(f'Found {len(stub_ases["eyeball"])} eyeball ASes in {cc}')

            if len(stub_ases['eyeball']) == 0 or len(stub_ases['as']) == 0:
                continue
        else:
            print(f'ERROR: Could not find ISPs in {cc}\n')

        # Find stub ASes in the country
        url = API_ACTIVE_ASES.format(end_date=end_date)
        resp = session.get(url)

        if resp.ok:
            global_graph = resp.json()
            for result in global_graph['results']: 

                # Keep total eyeball hegemony score
                if( result['asn_name'].endswith(cc)
                    and result['asn'] not in TIER1
                    and result['asn'] not in stub_ases['as']):
                        stub_ases['as'][result['asn']] = [0]


            print(f'Found {len(stub_ases["as"])} ASes in {cc}\n')

            if len(stub_ases['eyeball']) == 0 or len(stub_ases['as']) == 0:
                continue
        else:
            print(f'ERROR: Could not find ISPs in {cc}\n')

        # Find the main bottleneck in the country
        max_hege_asn = {}
        max_hege = {key:0 for key in transit_ases.keys()}
        for weightscheme in transit_ases.keys():
            for asn, heges in transit_ases[weightscheme].items():
                mean_hege = mean(heges)

                if mean_hege > max_hege[weightscheme] and asn not in TIER1:
                    max_hege[weightscheme] = mean_hege
                    max_hege_asn[weightscheme] = asn

        # Find the main eyeball in the country
        max_pop_asn = 0
        max_pop = 0
        for asn, pop in stub_ases['eyeball'].items():
            mean_pop = mean(pop)

            if mean_pop > max_pop:
                max_pop = mean_pop
                max_pop_asn = asn

        # Consolidation scores computation
        stats = {}
        stats['cc'] = cc
        stats['consolidation_pop'] = max_hege['eyeball'] - max_pop
        stats['consolidation_as']  = max_hege['as'] - 1/len(stub_ases['as'])
        stats['max_hege_asn'] = max_hege_asn
        stats['max_pop_asn'] = max_pop_asn
        stats['nb_stub_as'] = len(stub_ases['as'])

        # Keep results for this country
        consolidation_scores[cc] = stats

    with open(OUTPUT_FNAME, 'w') as fp:
        fp.write(
                '\t'.join([
                    'cc',
                    'consolidation_as',
                    'consolidation_pop',
                    'nb_stub_as'
                    'transit_as',
                    'transit_pop',
                    'max_pop_asn\n',
                    ])
        )
        for stats in sorted(consolidation_scores.values(), key=lambda x: x['consolidation_as']):
            fp.write(
                    '\t'.join([
                        stats['cc'], 
                        f"{stats['consolidation_as']:0.2f}",
                        f"{stats['consolidation_pop']:0.2f}", 
                        f"{stats['nb_stub_as']}",
                        f"AS{stats['max_hege_asn']['as']}",
                        f"AS{stats['max_hege_asn']['eyeball']}",
                        f"AS{stats['max_pop_asn']}\n",
                        ])
                    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("year", help="Year to analyze", type=int)
    parser.add_argument("month", help="Month to analyze", type=int)
    args = parser.parse_args()

    start_date = '{year}-{month}-01T00:00'.format(year=args.year, month=args.month)
    end_date = '{year}-{month}-07T00:00'.format(year=args.year, month=args.month)

    run(start_date, end_date)
