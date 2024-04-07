import pandas as pd
import requests
import pycountry
import numpy as np

# Initialize a set to collect ISO-2 country codes that are converted to custom values
custom_country_codes = set()

rir_urls = {
    'afrinic': 'https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest',
    'apnic': 'https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest',
    'arin': 'https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest',
    'lacnic': 'https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest',
    'ripe': 'https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest'
}

# Enhanced function to handle special cases and convert ISO-2 to ISO-3
def alpha2_to_alpha3(alpha_2):
    # Define custom replacements
    custom_replacements = {
        '': 'UNK',  # Empty strings to 'UNK' for Unknown
        'ZZ': 'RES',  # 'ZZ' to 'RES' for Reserved
        'AP': 'ITU',  # 'AP' to 'ITU' for ITU (International Telecommunication Union)
        'EU': 'EUR'  # 'EU' to 'EUR' for Europe
    }
    
    if alpha_2 in custom_replacements:
        custom_country_codes.add(alpha_2)
        return custom_replacements[alpha_2]
    
    if alpha_2 == 'XK':
        return 'XKX'  # Special case for Kosovo
    
    try:
        country = pycountry.countries.get(alpha_2=alpha_2)
        if country:
            return country.alpha_3
        else:
            return 'UNK'  # Use 'UNK' for unhandled unknown cases
    except AttributeError:
        return 'UNK'

def fetch_and_process_rir_data(url):
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    data = [line.split("|") for line in lines if line.count('|') >= 7]
    df = pd.DataFrame(data, columns=['Registry', 'Country', 'Type', 'Start', 'Value', 'Date', 'Status', 'Extensions'])
    
    # Convert 'Country' from alpha-2 to adjusted codes or alpha-3
    df['Country'] = df['Country'].apply(alpha2_to_alpha3)
    
    return df

ipv4_dfs = []
ipv6_dfs = []

for rir, url in rir_urls.items():
    print(f"Processing data from {rir.upper()}")
    df = fetch_and_process_rir_data(url)
    ipv4_dfs.append(df[df['Type'] == 'ipv4'])
    ipv6_dfs.append(df[df['Type'] == 'ipv6'])

# Combine the IPv4 and IPv6 dataframes
ipv4_combined_df = pd.concat(ipv4_dfs, ignore_index=True)
ipv6_combined_df = pd.concat(ipv6_dfs, ignore_index=True)

# Save to CSV
ipv4_combined_df.to_csv('ipv4_allocations.csv', mode='a', index=False)
ipv6_combined_df.to_csv('ipv6_allocations.csv', mode='a', index=False)

print("Data processing complete. Files saved: ipv4_allocations.csv, ipv6_allocations.csv")

# Print out the special ISO-2 country codes that were converted
print("Special ISO-2 country codes converted:", custom_country_codes)
