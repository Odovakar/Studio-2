import pandas as pd

def load_and_prepare_data():
    # Load WHOIS IPv4 data
    ipv4_df = pd.read_csv('ipv4_allocations.csv')

    # Load population data, assuming the first row is headers with the country names
    population_df = pd.read_csv('wpopdata.csv', header=0)

    # Rename columns based on the header (assuming the year columns are labeled as such, e.g., '1982', '1983', ...)
    year_columns = [str(year) for year in range(1982, 2024)]  # Update the years range accordingly
    population_df.columns = ['Country', 'ISO-3'] + year_columns

    # Convert wide format (years as columns) to long format (years as a single column)
    population_df = population_df.melt(id_vars=["Country", "ISO-3"], 
                                       var_name="Year", 
                                       value_name="Population")
    # Convert 'Year' to integer
    population_df['Year'] = population_df['Year'].astype(int)

    # Merge WHOIS IPv4 data with population data on 'ISO-3' and 'Year'
    combined_df = pd.merge(ipv4_df, population_df, on=['ISO-3', 'Year'], how='outer')
    combined_df.sort_values(by=['ISO-3', 'Year'], inplace=True)

    # Forward fill missing data within each 'ISO-3' group
    combined_df['Registry'] = combined_df.groupby('ISO-3')['Registry'].ffill()
    combined_df['Value'] = combined_df.groupby('ISO-3')['Value'].ffill()
    combined_df['Prefix'] = combined_df.groupby('ISO-3')['Prefix'].ffill()
    combined_df['Type'] = combined_df.groupby('ISO-3')['Type'].ffill()
    combined_df['Population'] = combined_df.groupby('ISO-3')['Population'].ffill()

    # Drop any rows that still have NaN values in essential columns
    combined_df.dropna(subset=['Population', 'Registry', 'Value', 'ISO-3'], inplace=True)

    # Remove any columns that are not needed for the final output
    combined_df.drop(columns=['Code', 'Status'], inplace=True)  # Add or remove columns based on your needs

    return combined_df

def save_processed_data(df):
    # Save the processed DataFrame to CSV
    df.to_csv('processed_ipv4_population_data.csv', index=False)
    print("Data processing complete. File saved: processed_ipv4_population_data.csv")

# Execute the processing
processed_data = load_and_prepare_data()
save_processed_data(processed_data)
