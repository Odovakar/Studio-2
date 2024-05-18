import pandas as pd



def gdppc_long():
    df = pd.read_csv('gpd.csv')

    long_df = pd.melt(df, id_vars=['Country', 'ISO-3'], var_name='Year', value_name='GPDPerCap')

    long_df.to_csv("gdppc_long.csv", index=False)

#gdppc_long()

def drop_aggregates():
    # List of entries to be removed
    df = pd.read_csv('gdppc_long.csv')
    entries_to_remove = [
        "Africa Eastern and Southern",
        "Arab World",
        "Central Europe and the Baltics",
        "East Asia & Pacific (excluding high income)",
        "Euro area",
        "Europe & Central Asia (excluding high income)",
        "European Union",
        "Heavily indebted poor countries (HIPC)",
        "IDA & IBRD total",
        "IDA only",
        "Late-demographic dividend",
        "Latin America & Caribbean (excluding high income)",
        "Least developed countries: UN classification",
        "Lower middle income",
        "Middle East & North Africa (excluding high income)",
        "Middle income",
        "Not classified",
        "Other small states",
        "Post-demographic dividend",
        "Small states",
        "South Asia (IDA & IBRD)",
        "Sub-Saharan Africa (excluding high income)",
        "Upper middle income"
    ]

    # Remove entries from the DataFrame
    cleaned_df = df[~df['Country'].isin(entries_to_remove)]

    # Display the cleaned DataFrame
    cleaned_df.to_csv("gdppc_long2.csv", index=False)
#drop_aggregates()

def check_check_for_discrepancies():
    df = pd.read_csv('whois_v4_pop.csv')
    print(df.nunique())

    df2 = pd.read_csv('gdppc_long2.csv')
    print(df2.nunique())

#check_check_for_discrepancies()

def finding_out_which_rows_to_drop():
    df = pd.read_csv('whois_v4_dropped.csv')
    #print(df.nunique())

    df2 = pd.read_csv('gdp_dropped.csv')
    #print(df2.nunique())
    iso3_set1 = set(df['ISO-3'])
    iso3_set2 = set(df2['ISO-3'])

    # ISO-3 entries present in the first dataset but not in the second
    iso3_unique_to_set1 = iso3_set1 - iso3_set2

    # ISO-3 entries present in the second dataset but not in the first
    iso3_unique_to_set2 = iso3_set2 - iso3_set1

    # Display the ISO-3 entries unique to each dataset
    print("ISO-3 entries unique to the first dataset:", iso3_unique_to_set1)
    print("ISO-3 entries unique to the second dataset:", iso3_unique_to_set2)

#finding_out_which_rows_to_drop()


def dropping_smaller_countries():
    # ISO-3 entries to drop from the first dataset
    df1 = pd.read_csv('whois_v4_pop.csv', low_memory=False)
    df2 = pd.read_csv('gdppc_long2.csv')
    iso3_to_drop_first = {'MYT', 'MSR', 'WLF', 'GLP', 'REU', 'NFK', 'GUF', 'BLM', 'BES', 'IOT', 'TKL', 'UNK', 'VAT', 'JEY', 'MTQ', 'GGY', 'ALA', 'TWN', 'AIA', 'COK', 'FLK', 'NIU', 'SPM'}

    # ISO-3 entries to drop from the second dataset
    iso3_to_drop_second = {'XKX', 'CHI'}

    # Drop entries from the first dataset
    cleaned_df1 = df1[~df1['ISO-3'].isin(iso3_to_drop_first)]

    # Drop entries from the second dataset
    cleaned_df2 = df2[~df2['ISO-3'].isin(iso3_to_drop_second)]

    # Write the cleaned DataFrames to new CSV files
    cleaned_df1.to_csv("whois_v4_dropped.csv", index=False)
    cleaned_df2.to_csv("gdp_dropped.csv", index=False)

#dropping_smaller_countries()

def find_double_dots(cleaned_df2):
    #cleaned_df2 = pd.read_csv('gdp_dropped.csv')
    # Find entries with double dots (..) in the 'GPDPerCap' column
    entries_with_double_dots = cleaned_df2[cleaned_df2['GPDPerCap'] == '..']

    # Display the entries with double dots
    print(entries_with_double_dots)

    # Handle missing values (for example, by dropping these rows)
    cleaned_df2 = cleaned_df2[cleaned_df2['GPDPerCap'] != '..']

#find_double_dots()

def testing_backfill():
    cleaned_df2 = pd.read_csv('gdp_dropped.csv')
    # Convert '..' to NaN
    cleaned_df2['GPDPerCap'] = cleaned_df2['GPDPerCap'].replace('..', pd.NA)

    # Sort the DataFrame by 'ISO-3' and 'Year'
    cleaned_df2.sort_values(by=['ISO-3', 'Year'], inplace=True)

    # Backfill missing values within each ISO-3 group
    cleaned_df2['GPDPerCap'] = cleaned_df2.groupby('ISO-3')['GPDPerCap'].fillna(method='bfill')

    # Replace remaining NaN values with '..'
    cleaned_df2['GPDPerCap'] = cleaned_df2['GPDPerCap'].fillna('..')

    # Display the updated DataFrame
    print(cleaned_df2.head(25))

    find_double_dots(cleaned_df2)
    cleaned_df2.to_csv("gdp_dropped_bkfill.csv", index=False)

#testing_backfill()

def testing_frontfill():
    cleaned_df2 = pd.read_csv('gdp_dropped_bkfill.csv')
    # Convert '..' to NaN
    cleaned_df2['GPDPerCap'] = cleaned_df2['GPDPerCap'].replace('..', pd.NA)

    # Sort the DataFrame by 'ISO-3' and 'Year'
    cleaned_df2.sort_values(by=['ISO-3', 'Year'], inplace=True)

    # Backfill missing values within each ISO-3 group
    cleaned_df2['GPDPerCap'] = cleaned_df2.groupby('ISO-3')['GPDPerCap'].fillna(method='bfill')

    # Front fill remaining missing values within each ISO-3 group
    cleaned_df2['GPDPerCap'] = cleaned_df2.groupby('ISO-3')['GPDPerCap'].fillna(method='ffill')

    # Replace remaining NaN values with '..'
    cleaned_df2['GPDPerCap'] = cleaned_df2['GPDPerCap'].fillna('..')

    # Display the updated DataFrame
    print(cleaned_df2.head)
    find_double_dots(cleaned_df2)
    cleaned_df2.to_csv("gdp_dropped_filled.csv", index=False)

#testing_frontfill()

def checking_the_last_double_dots():
    cleaned_df2 = pd.read_csv('gdp_dropped_filled.csv')
    # Find rows with double dots (..) in the 'GPDPerCap' column
    rows_with_double_dots = cleaned_df2[cleaned_df2['GPDPerCap'] == '..']

    # Print out the rows without abbreviation
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        print(rows_with_double_dots)

#checking_the_last_double_dots()

def checking_stuff_in_the_old_df(df):
    #cleaned_df2 = pd.read_csv('gdp_dropped_filled_nodots.csv')
    # Filter rows containing ISO-3 codes PRK, GIB, and VGB
    filtered_rows = df[df['ISO-3'].isin(['PRK', 'GIB', 'VGB'])]

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        print(filtered_rows)

#checking_stuff_in_the_old_df()

def setting_dots_to_zero():
    cleaned_df2 = pd.read_csv('gdp_dropped_filled.csv')
    # Replace '..' with 0 for GIB and VGB
    cleaned_df2.loc[(cleaned_df2['ISO-3'] == 'GIB') | (cleaned_df2['ISO-3'] == 'VGB'), 'GPDPerCap'] = cleaned_df2.loc[(cleaned_df2['ISO-3'] == 'GIB') | (cleaned_df2['ISO-3'] == 'VGB'), 'GPDPerCap'].replace('..', '0')

    # Display the updated DataFrame
    
    cleaned_df2.to_csv("gdp_dropped_filled_nodots.csv", index=False)

#setting_dots_to_zero()

def combining_the_two():
    cleaned_df1 = pd.read_csv('whois_v4_dropped.csv')
    cleaned_df2 = pd.read_csv('gdp_dropped_filled_nodots.csv')
    # Merge the two datasets on the 'ISO-3' and 'Year' columns
# Merge the two datasets on the 'ISO-3' and 'Year' columns
    merged_df = pd.merge(cleaned_df1, cleaned_df2, on=['ISO-3', 'Year'])

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv("whoisv4_pop_gdp.csv", index=False)

    # Display the merged DataFrame
    checking_stuff_in_the_old_df(merged_df)

#combining_the_two()

def last_cleanup():
    df = pd.read_csv('whoisv4_pop_gdp.csv')
    df.drop(columns=['Country_x'], inplace=True)
    df.rename(columns={'Country_y': 'Country', 'GPDPerCap': 'GDPPerCap'}, inplace=True)
    df.to_csv("whoisv4_pop_gdp2.csv", index=False)

    print(df.tail())
    print(df.head())

last_cleanup()
    