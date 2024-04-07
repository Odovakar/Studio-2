import pandas as pd
import requests
import pycountry

# Function to convert alpha-2 to alpha-3 country codes
def alpha2_to_alpha3(alpha_2):
    if alpha_2 == 'XK':
        return 'XKX'
    try:
        country = pycountry.countries.get(alpha_2=alpha_2)
        return country.alpha_3
    except AttributeError:
        return 'Unknown'

# URLs for the extended delegation files of the five RIRs
rir_urls = {
    'afrinic': 'https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest',
    'apnic': 'https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest',
    'arin': 'https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest',
    'lacnic': 'https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest',
    'ripe': 'https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest'
}

def fetch_and_process_rir_data(url):
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    data = [line.split("|") for line in lines if line.count('|') >= 7]
    df = pd.DataFrame(data, columns=['Registry', 'Country', 'Type', 'Start', 'Value', 'Date', 'Status', 'Extensions'])
    
    # Convert 'Country' from alpha-2 to alpha-3
    df['Country'] = df['Country'].apply(alpha2_to_alpha3)
    
    df['Value'] = df['Value'].astype(int)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')
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
ipv4_combined_df.to_csv('ipv4_allocations.csv', index=False)
ipv6_combined_df.to_csv('ipv6_allocations.csv', index=False)

print("Data processing complete. Files saved: ipv4_allocations.csv, ipv6_allocations.csv")
