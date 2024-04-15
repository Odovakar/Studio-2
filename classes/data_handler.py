import requests
import pandas as pd
import numpy as np
import pycountry
from io import StringIO

class DataHandler:
    def __init__(self, json_url, netlist_url, whois_ipv4_url):
        self.json_url = json_url
        self.netlist_url = netlist_url
        self.whois_ipv4_url = whois_ipv4_url
        self.json_df = None
        self. netlist_df = None
        self.whois_ipv4_df = None

    def fetch_json_data(self):
        response = requests.get(self.json_url)
        if response.status_code == 200:
            data = response.json()
            print("Data fetched successfully")
            self.json_df = self.create_and_process_dataframe(self.transform_json_data(data))
            if not self.json_df.empty:
                print("DataFrame processed and populated.")
            else:
                print("DataFrame is empty after processing.")
        else:
            print("Failed to fetch data: HTTP", response.status_code)

    def fetch_netlist_data(self):
        response = requests.get(self.netlist_url)
        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            data = [line.split(maxsplit=3) for line in lines if line]
            self.netlist_df = pd.DataFrame(data, columns=['Start', 'End', 'RIR', 'Description'])
            self.process_netlist_data()
            if not self.netlist_df.empty:
                print("Netlist DataFrame processed and populated.")
            else:
                print("Netlist DataFrame is empty after processing.")
        else:
            print("Failed to fetch netlist data: HTTP", response.status_code)

    def fetch_whois_ipv4_data(self):
        response = requests.get(self.whois_ipv4_url)
        if response.status_code == 200:
            data = StringIO(response.text)
            self.whois_ipv4_df = pd.read_csv(data)
            self.process_whois_ipv4_data()
            if not self.whois_ipv4_df.empty:
                print("WHOIS IPv4 DataFrame processed and populated.")
            else:
                print("WHOIS IPv4 DataFrame is empty after processing.")
        else:
            print("Failed to fetch WHOIS IPv4 data: HTTP", response.status_code)

    # JSON_DF
    def transform_json_data(self, json_data):
        transformed_data = []
        for country_code, details in json_data.items():
            if country_code != 'EU': # Skip EU entry
                details['country_code'] = country_code
                transformed_data.append(details)
        return transformed_data
    
    def create_and_process_dataframe(self, transformed_data):
        json_df = pd.DataFrame(transformed_data)
        json_df['ipv4'] = pd.to_numeric(json_df['ipv4'], errors='coerce')
        json_df['pop'] = pd.to_numeric(json_df['pop'], errors='coerce')
        return json_df[(json_df['pop'] > 800) & (json_df['name'] != 'World')]

    def enhance_dataframe(self, json_df):
        json_df['iso_alpha_3'] = json_df['country_code'].apply(self.alpha2_to_alpha3)
        json_df['ipv4_grouping'] = json_df['ipv4'].apply(self.assign_ipv4_grouping)
        json_df['RIR'] = json_df['iso_alpha_3'].apply(self.alpha3_to_rir)
        json_df['log_ipv4'] = np.log10(json_df['ipv4'] + 1)
        json_df['log_percentv4'] = np.log10(json_df['percentv4'] + 1)
        return json_df

    # NETLIST_DF
    def process_netlist_data(self):
        self.netlist_df[['Status', 'IP']] = self.netlist_df['Description'].str.split(n=1, expand=True)
        self.netlist_df[['IP Address', 'Prefix']] = self.netlist_df['IP'].str.split("/", expand=True)
        self.netlist_df.drop(columns=['Description', 'IP'], inplace=True)
        self.netlist_df['Start'] = self.netlist_df['Start'].astype('UInt64')
        self.netlist_df['End'] = self.netlist_df['End'].astype('UInt64')
        self.netlist_df['Nr of IPs'] = self.netlist_df['End'] - self.netlist_df['Start']

    # WHOIS_IPv4
    def process_whois_ipv4_data(self):
        #self.whois_ipv4_df['Date'] = pd.to_datetime(self.whois_ipv4_df['Date'], format='%Y%m%d')
        self.whois_ipv4_df['Date'] = pd.to_datetime(self.whois_ipv4_df['Date'], format='%Y%m%d')

        self.whois_ipv4_df['Date'] = self.whois_ipv4_df['Date'].dt.strftime('%d-%m-%Y')
        self.whois_ipv4_df['Value'] = pd.to_numeric(self.whois_ipv4_df['Value'], errors='coerce').fillna(0).astype(int)
        self.whois_ipv4_df['Country'] = self.whois_ipv4_df['Code'].apply(self.alpha3_to_country_name)

    @staticmethod
    def alpha2_to_alpha3(alpha_2):
        if alpha_2 == 'XK':
            return 'XKX'
        try:
            country = pycountry.countries.get(alpha_2=alpha_2)
            return country.alpha_3
        except AttributeError:
            return 'Unknown'

    @staticmethod
    def alpha3_to_rir(alpha_3):
        rir_by_region = {
        'AFRINIC': ['DZA', 'AGO', 'BEN', 'BWA', 'BFA', 'BDI', 'CMR', 'CPV', 'CAF', 'COD', 'TCD', 'COM', 'COG', 'DJI', 'EGY', 'GNQ', 'ERI', 'ETH', 'GAB', 'GMB', 'GHA', 'GIN', 'GNB', 'CIV', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG', 'MWI', 'MLI', 'MRT', 'MUS', 'MYT', 'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'REU', 'RWA', 'SHN', 'STP', 'SEN', 'SYC', 'SLE', 'SOM', 'ZAF', 'SSD', 'SDN', 'SWZ', 'TZA', 'TGO', 'TUN', 'UGA', 'ZMB', 'ZWE', 'XKX', 'ESH'],
        'APNIC': ['AFG', 'AUS', 'BGD', 'BTN', 'BRN', 'KHM', 'CHN', 'CXR', 'CCK', 'COK', 'IOT', 'FJI', 'HKG', 'IND', 'IDN', 'JPN', 'KAZ', 'PRK', 'KOR', 'KGZ', 'LAO', 'MAC', 'MYS', 'MDV', 'MNG', 'MMR', 'NPL', 'NCL', 'NZL', 'NIU', 'NFK', 'PAK', 'PLW', 'PNG', 'PHL', 'PCN', 'SGP', 'SLB', 'LKA', 'TWN', 'TJK', 'THA', 'TLS', 'TKL', 'TON', 'TUV', 'VUT', 'VNM', 'WLF', 'ASM', 'GUM', 'KIR', 'MHL', 'FSM', 'NRU', 'PLW', 'PYF', 'PNY', 'WSM'],
        'ARIN': ['AIA', 'ATG', 'ABW', 'BHS', 'BRB', 'BLM', 'BMU', 'BES', 'CAN', 'CYM', 'CUW', 'DMA', 'DOM', 'GLP', 'GRD', 'GRL', 'GTM', 'HTI', 'HND', 'JAM', 'MTQ', 'MEX', 'MSR', 'SXM', 'KNA', 'LCA', 'MAF', 'MNP', 'SPM', 'VCT', 'TTO', 'TCA', 'USA', 'VGB', 'VIR', 'PRI'],
        'LACNIC': ['ARG', 'BOL', 'BRA', 'BLZ', 'CHL', 'COL', 'CRI', 'CUB', 'CUW', 'DMA', 'ECU', 'SLV', 'FLK', 'GUF', 'GTM', 'GUY', 'HND', 'JAM', 'MTQ', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'PRI', 'BLM', 'KNA', 'LCA', 'SPM', 'VCT', 'SGS', 'SUR', 'TTO', 'URY', 'VEN', 'BES', 'SXM', 'ABW'],
        'RIPE NCC': ['ALA', 'ALB', 'AND', 'ARM', 'AUT', 'AZE', 'BHR', 'BLR', 'BEL', 'BIH', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FRO', 'FIN', 'FRA', 'GEO', 'DEU', 'GIB', 'GRC', 'GGY', 'VAT', 'HUN', 'ISL', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JEY', 'JOR', 'KWT', 'LVA', 'LBN', 'LIE', 'LTU', 'LUX', 'MLT', 'MDA', 'MCO', 'MNE', 'NLD', 'MKD', 'NOR', 'OMN', 'PSE', 'POL', 'PRT', 'QAT', 'ROU', 'RUS', 'SMR', 'SAU', 'SRB', 'SVK', 'SVN', 'ESP', 'SJM', 'SWE', 'CHE', 'SYR', 'TUR', 'UKR', 'UZB', 'ARE', 'GBR', 'YEM', 'KOS', 'TKM'],
        }
        for rir, countries in rir_by_region.items():
            if alpha_3 in countries:
                return rir
        return 'Unknown'
    
    @staticmethod
    def assign_ipv4_grouping(value):
        if value <= 10000:
            return '0-10k'
        elif value <= 100000:
            return '10k-100k'
        elif value <= 1000000:
            return '100k-1M'
        elif value <= 10000000:
            return '1M-10M'
        elif value <= 100000000:
            return '10M-100M'
        elif value <= 1000000000:
            return '100M-1B'
        else:
            return '1B+'
    
    @staticmethod
    def alpha3_to_country_name(code):
        """Convert ISO-3166-1 alpha-3 code to a country name using the pycountry library."""
        country = pycountry.countries.get(alpha_3=code)
        if country:
            return country.name
        else:
            return 'Unknown'