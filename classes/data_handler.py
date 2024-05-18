import requests
import pandas as pd
import numpy as np
import pycountry
from datetime import datetime

# JSON Conversion is prioritised because of its compatability with dash/JS
class DataHandler:
    def __init__(self, json_url, whois_v4_pop_csv, population_csv, whoisv6_allocation_csv): #netlist_url, 
        self.json_url = json_url
        self.whois_v4_pop_csv = whois_v4_pop_csv
        self.population_csv = population_csv
        self.whoisv6_allocation_csv = whoisv6_allocation_csv
        self.json_df = None
        self.whois_ipv4_df = None
        self.ipv4_ts_df = None
        self.allocation_df = None
        self.whoisv6_df = None

        self.fetch_json_data()
        self.fetch_whois_ipv4_data()
        #self.process_whois_ipv4_data()
        self.allocation_df = self.create_allocation_bar_df()
        self.create_time_series_df()
        self.fetch_whois_ipv6_data()

    def fetch_whois_ipv6_data(self):
        try:
            self.whoisv6_df = pd.read_csv(self.whoisv6_allocation_csv, low_memory=False)
            expected_columns = ['Registry','Code','Type','Start','Value','Date','Status','Extensions','Prefix','ISO-3','Country','Year']
            if not all(col in self.whoisv6_df.columns for col in expected_columns):
                raise ValueError('WHOIS IPv6 data missing expected columns.')
            self.whoisv6_df['Date'] = pd.to_datetime(self.whoisv6_df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            self.whoisv6_df['Year'] = self.whoisv6_df['Year'].astype(int)
            total_fields = self.whoisv6_df.shape[0] * self.whoisv6_df.shape[1]  # where df.shape[0] is the number of rows and df.shape[1] is the number of columns

            print("Total number of fields in the DataFrame:", total_fields)
            return self.whoisv6_df
        except Exception as e:
            print(f'Failed to load or process WHOIS IPv6 data: {e}')

    def fetch_json_data(self):
        response = requests.get(self.json_url)
        if response.status_code == 200:
            data = response.json()
            print('Data fetched successfully')
            self.json_df = self.create_and_process_dataframe(self.transform_json_data(data))
            self.enhance_dataframe(self.json_df)
            if not self.json_df.empty:
                print('DataFrame processed and populated.')
            else:
                print('DataFrame is empty after processing.')
        else:
            print('Failed to fetch data: HTTP', response.status_code)

    def load_population_data(self):
        try:
            pop_df = pd.read_csv(self.population_csv)
            # Transforming the DataFrame from wide to long format
            pop_df_long = pd.melt(pop_df, id_vars=['Country Name', 'Country Code'],
                                var_name='Year', value_name='Population')
            # Extracting year and converting to integer, handling NaN values first
            pop_df_long['Year'] = pop_df_long['Year'].str.extract('(\d{4})')
            pop_df_long = pop_df_long.dropna(subset=['Year'])  # Dropping rows where 'Year' is NaN
            pop_df_long['Year'] = pop_df_long['Year'].astype(int)

            return pop_df_long
        except Exception as e:
            print(f'Error loading population data: {e}')
            return None

    def fetch_whois_ipv4_data(self):
        try:
            self.whois_ipv4_df = pd.read_csv(self.whois_v4_pop_csv, low_memory=False)
            expected_columns = ['ISO-3', 'Year', 'Registry', 'Type', 'Start', 'Value', 'Date', 'Status', 'Prefix', 'Country', 'Population']
            if not all(col in self.whois_ipv4_df.columns for col in expected_columns):
                raise ValueError('WHOIS IPv4 data missing expected columns.')
            self.whois_ipv4_df['Date'] = pd.to_datetime(self.whois_ipv4_df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            self.whois_ipv4_df['Year'] = self.whois_ipv4_df['Year'].astype(int)
            self.whois_ipv4_df['Population'] = pd.to_numeric(self.whois_ipv4_df['Population'], errors='coerce')
            #print('WHOIS IPv4 data loaded successfully.')
            return self.whois_ipv4_df
        except Exception as e:
            print(f'Failed to load or process WHOIS IPv4 data: {e}')

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
        #json_df['ipv6'] = pd.to_numeric(json_df['ipv6'], errors='coerce').astype('int64')
        #print(json_df['ipv6'])

        #json_df['ipv6'] = pd.to_numeric(json_df['ipv6'], errors='coerce').fillna(0).astype('uint64')
        #print(json_df['ipv6'])
        return json_df[(json_df['pop'] > 800) & (json_df['name'] != 'World')]

    def enhance_dataframe(self, json_df):
        json_df['iso_alpha_3'] = json_df['country_code'].apply(self.alpha2_to_alpha3)
        json_df['ipv4_grouping'] = json_df['ipv4'].apply(self.assign_ipv4_grouping)
        json_df['RIR'] = json_df['iso_alpha_3'].apply(self.alpha3_to_rir)
        json_df['log_ipv4'] = np.log10(json_df['ipv4'].where(json_df['ipv4'] > 0, np.nan) + 1)
        #json_df['ipv6'] = json_df['ipv6'].apply(lambda x: x if x > 0 else 1.26)
        #json_df['ipv6'] = json_df['ipv6'].astype(str)
        #json_df['log_ipv6'] = np.log10(json_df['ipv6'])
        json_df['log_percentv4'] = np.log10(json_df['percentv4'] + 1)
        #print(json_df.columns.tolist())
        #print(json_df['log_percentv4'].tail(10))
        #print(json_df.nsmallest(5, 'percentv4')[['name', 'percentv4', 'log_percentv4']])
        #print(json_df.dtypes)
        #invalid_values = json_df['log_ipv6'].isna()
        #print(json_df.dtypes)
        # Display the result
        #print(invalid_values)

        # Count the number of zero or negative values
        #invalid_count = invalid_values.sum()
        #print(f"There are {invalid_count} zero or negative values in the 'log_ipv6' column.")
        json_df.to_csv("json_df.csv", index=False)
        return json_df

    def create_time_series_df(self):
        # Starting with the original DataFrame
        ipv4_ts_df = self.whois_ipv4_df
        
        # Grouping by Country and Year and aggregating necessary fields
        ipv4_ts_df = ipv4_ts_df.groupby(['Country', 'Year']).agg({
            'ISO-3': 'first', 
            'Registry': 'first', 
            'Date': 'first',
            'Value': 'sum',
            'Population': 'first',
            'GDPPerCap': 'first'
        }).reset_index()

        # Dropping unnecessary columns
        ipv4_ts_df.drop(columns=['Registry', 'Date'], axis=1, inplace=True)

        # Convert ISO-3 to RIR if needed
        ipv4_ts_df['RIR'] = ipv4_ts_df['ISO-3'].apply(self.alpha3_to_rir)
        
        # Ensure data is sorted by Country and Year for correct cumulative calculation
        ipv4_ts_df.sort_values(by=['Country', 'Year'], ascending=[True, True], inplace=True)

        # Calculate cumulative sum of 'Value' within each 'Country' group
        ipv4_ts_df['Cumulative Value'] = ipv4_ts_df.groupby('Country')['Value'].cumsum()
        ipv4_ts_df['Size'] = np.sqrt(ipv4_ts_df['Cumulative Value'])
        # Assigning back to class attribute if needed
        self.ipv4_ts_df = ipv4_ts_df

        # Optionally, return the DataFrame
        return ipv4_ts_df

    def create_allocation_bar_df(self):
        df = self.whois_ipv4_df
        #df = df[df['Registry'] != 'none']
        columns_to_drop = ['Population', 'Year', 'ISO-3', 'Date']
        allocation_df = df.drop(columns=columns_to_drop)
        filtered_df = allocation_df[allocation_df['Status'].isin(['allocated', 'assigned'])]
        allocation_df = filtered_df.groupby(['Registry', 'Status'], as_index=False)['Value'].sum()
        return allocation_df


    @staticmethod
    def calculate_prefix(value):
        if value == 1:
            return 32
        prefix = 32 - int(np.log2(value))
        return prefix

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
        'AFRINIC': ['DZA', 'AGO', 'BEN', 'BWA', 'BFA', 'BDI', 'CMR', 'CPV', 'CAF', 'COD', 'TCD', 'COM', 'COG', 'DJI', 'EGY', 'GNQ', 'ERI', 'ETH', 'GAB', 'GMB', 'GHA', 'GIN', 'GNB', 'CIV', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG', 'MWI', 'MLI', 'MRT', 'MUS', 'MYT', 'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'REU', 'RWA', 'SHN', 'STP', 'SEN', 'SYC', 'SLE', 'SOM', 'ZAF', 'SSD', 'SDN', 'SWZ', 'TZA', 'TGO', 'TUN', 'UGA', 'ZMB', 'ZWE', 'ESH'],
        'APNIC': ['AFG', 'AUS', 'BGD', 'BTN', 'BRN', 'KHM', 'CHN', 'CXR', 'CCK', 'COK', 'IOT', 'FJI', 'HKG', 'IND', 'IDN', 'JPN', 'KAZ', 'PRK', 'KOR', 'KGZ', 'LAO', 'MAC', 'MYS', 'MDV', 'MNG', 'MMR', 'NPL', 'NCL', 'NZL', 'NIU', 'NFK', 'PAK', 'PLW', 'PNG', 'PHL', 'PCN', 'SGP', 'SLB', 'LKA', 'TWN', 'TJK', 'THA', 'TLS', 'TKL', 'TON', 'TUV', 'VUT', 'VNM', 'WLF', 'ASM', 'GUM', 'KIR', 'MHL', 'FSM', 'NRU', 'PLW', 'PYF', 'PNY', 'WSM'],
        'ARIN': ['AIA', 'ATG', 'ABW', 'BHS', 'BRB', 'BLM', 'BMU', 'BES', 'CAN', 'CYM', 'CUW', 'DMA', 'DOM', 'GLP', 'GRD', 'GRL', 'GTM', 'HTI', 'HND', 'JAM', 'MTQ', 'MEX', 'MSR', 'SXM', 'KNA', 'LCA', 'MAF', 'MNP', 'SPM', 'VCT', 'TTO', 'TCA', 'USA', 'VGB', 'VIR', 'PRI'],
        'LACNIC': ['ARG', 'BOL', 'BRA', 'BLZ', 'CHL', 'COL', 'CRI', 'CUB', 'CUW', 'DMA', 'ECU', 'SLV', 'FLK', 'GUF', 'GTM', 'GUY', 'HND', 'JAM', 'MTQ', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'PRI', 'BLM', 'KNA', 'LCA', 'SPM', 'VCT', 'SGS', 'SUR', 'TTO', 'URY', 'VEN', 'BES', 'SXM', 'ABW'],
        'RIPE NCC': ['ALA', 'ALB', 'AND', 'ARM', 'AUT', 'AZE', 'BHR', 'BLR', 'BEL', 'BIH', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FRO', 'FIN', 'FRA', 'GEO', 'DEU', 'GIB', 'GRC', 'GGY', 'VAT', 'HUN', 'ISL', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JEY', 'JOR', 'KWT', 'LVA', 'LBN', 'LIE', 'LTU', 'LUX', 'MLT', 'MDA', 'MCO', 'MNE', 'NLD', 'MKD', 'NOR', 'OMN', 'PSE', 'POL', 'PRT', 'QAT', 'ROU', 'RUS', 'SMR', 'SAU', 'SRB', 'SVK', 'SVN', 'ESP', 'SJM', 'SWE', 'CHE', 'SYR', 'TUR', 'UKR', 'UZB', 'ARE', 'GBR', 'YEM', 'KOS', 'TKM', 'XKX', ],
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
        '''Convert ISO-3166-1 alpha-3 code to a country name using the pycountry library.'''
        country = pycountry.countries.get(alpha_3=code)
        if country:
            return country.name
        else:
            return 'Unknown'