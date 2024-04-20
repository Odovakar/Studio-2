import pandas as pd
import chardet
import numpy as np

def process_new_dataframe():
    ipv4_df = pd.read_csv('ipv4_allocations.csv')
    population_df = pd.read_csv('wpopdata.csv')

    print(ipv4_df.head())
    print(population_df.head())

    #Converting wpop.csv to long - saving it as a new csv because of data integrity
    long_population_df = convert_wpop_to_long(population_df)
    return long_population_df, ipv4_df


def convert_wpop_to_long(population_df):

    # Transform the DataFrame from wide to long format
    df_long = pd.melt(population_df, id_vars=['Country', 'ISO-3'], var_name='Year', value_name='Population')

    # Convert the 'Year' column to integer if it's in a format like '1982', '1983', etc.
    df_long['Year'] = df_long['Year'].astype(int)

    # Save the transformed DataFrame to a new CSV file
    df_long.to_csv('wpopdata_long_format.csv', mode='w', index=False)
    return df_long

def check_naming_inconsitencies():
    ipv4_df = pd.read_csv('ipv4_allocations.csv')
    long_population_df = pd.read_csv('wpopdata_long_format_cleaned.csv')
    # Get the unique ISO-3 codes from both datasets
    iso3_df1 = set(ipv4_df['ISO-3'].unique())
    iso3_df2 = set(long_population_df['ISO-3'].unique())

    # Find the differences in ISO-3 codes between the two datasets
    diff_df1 = iso3_df1 - iso3_df2  # ISO-3 codes in df1 not in df2
    diff_df2 = iso3_df2 - iso3_df1  # ISO-3 codes in df2 not in df1

    # Print the differences
    print("ISO-3 codes in df1 not in df2:", diff_df1)
    print("ISO-3 codes in df2 not in df1:", diff_df2)

#check_naming_inconsitencies()

def process_and_save_datasets(input_csv_path):
    df_long = pd.read_csv(input_csv_path)

    # Rename 'CHI' to 'GGY'
    df_long['ISO-3'] = df_long['ISO-3'].replace('CHI', 'GGY')

    # Aggregate and special codes
    aggregate_and_special_codes = {
        'EUU', 'HPC', 'TSA', 'IDA', 'SAS', 'SST', 'IBT', 'ARB', 'FCS', 'AFE', 'EAP', 'CSS', 'WLD', 'OED', 'OSS', 'PRE', 
        'MIC', 'LTE', 'IDX', 'PST', 'EAS', 'LMY', 'TEC', 'LMC', 'IDB', 'UMC', 'AFW', 'LDC', 'IBD', 'LIC', 'INX', 
        'TMN', 'PSS', 'TSS', 'SSF', 'LAC', 'MEA', 'MNA', 'CEB', 'SSA', 'ECS', 'EMU', 'TEA', 'TLA', 'NAC', 'HIC', 
        'ECA', 'EAR', 'LCN'
    }
    
    # Filter the DataFrame for aggregate and special codes
    df_aggregate = df_long[df_long['ISO-3'].isin(aggregate_and_special_codes)]

    df_aggregate.to_csv(input_csv_path.replace('.csv', '_aggregate_nationality_long.csv'), index=False)

    # Remove the aggregate and special codes entries from the original DataFrame
    df_cleaned = df_long[~df_long['ISO-3'].isin(aggregate_and_special_codes)]

    df_cleaned.to_csv(input_csv_path.replace('.csv', '_cleaned.csv'), index=False)

#process_and_save_datasets('wpopdata_long_format.csv')



def check_naming_inconsitencies():
    df_long_format = pd.read_csv('wpopdata_long_format.csv')

    # Filter for rows with the ISO-3 code 'INX'
    inx_rows = df_long_format[df_long_format['ISO-3'] == 'INX']

    print(inx_rows)
    wpop_df = 'wpopdata_long_format.csv'
    whois_ipv4_df = 'ipv4_allocations.csv'

    df1 = pd.read_csv(wpop_df)
    df2 = pd.read_csv(whois_ipv4_df)

    # Check if 'CHI' is present in both datasets
    chi_in_df1 = 'CHI' in df1['ISO-3'].unique()
    chi_in_df2 = 'CHI' in df2['ISO-3'].unique()

    print(f"'CHI' in dataset 1:", chi_in_df1)
    print(f"'CHI' in dataset 2:", chi_in_df2)

#check_naming_inconsitencies()
#process_new_dataframe()

def check_code_consistency():
    ipv4_df = pd.read_csv('ipv4_allocations.csv')
    long_population_df = pd.read_csv('wpopdata_long_format_cleaned.csv')

    # Check specific cases
    channel_islands_df1 = {'GGY', 'JEY'}.intersection(set(ipv4_df['ISO-3'].unique()))
    channel_islands_df2 = {'GGY', 'JEY'}.intersection(set(long_population_df['ISO-3'].unique()))
    
    print("Channel Islands in df1:", channel_islands_df1)
    print("Channel Islands in df2:", channel_islands_df2)
    
    # Example of checking for Taiwan
    taiwan_in_df1 = 'TWN' in ipv4_df['ISO-3'].unique()
    taiwan_in_df2 = 'TWN' in long_population_df['ISO-3'].unique()
    
    print("Taiwan in df1:", taiwan_in_df1)
    print("Taiwan in df2:", taiwan_in_df2)
    
    # Add similar checks for other special cases

# Usage
#check_code_consistency()

def append_two_pop_csvs():
    df1 = pd.read_csv('wpopdata_long_format_cleaned.csv')

    # Load the manual additions
    df2 = pd.read_csv('manual_additions_population.csv', encoding='ISO-8859-1')

    # Concatenate the two DataFrames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Save the combined data back to the original file
    # or to a new file if you want to preserve the original separately
    combined_df.to_csv('wpopdata_long_format_cleaned.csv', index=False)#

#append_two_pop_csvs()

def get_encoding():
    file_path = 'manual_additions_population.csv'
    with open(file_path, 'rb') as file:
        return chardet.detect(file.read())['encoding']
    

#encoding = get_encoding()
#print("Detected encoding:", encoding)

#ipv4 = pd.read_csv('ipv4_allocations.csv')
#unique_countries = ipv4['Country'].unique()
#print(unique_countries)

def process_and_merge_datasets(pop_data_path, ipv4_data_path, output_path):
    # Load the datasets
    wpop_data = pd.read_csv(pop_data_path)
    ipv4_data = pd.read_csv(ipv4_data_path)

    # Define codes to drop and skip
    codes_to_drop = ['ALA', 'EUR', 'IOT', 'TKL', 'GLP', 'BES']
    codes_to_skip = ['RES', 'UNK']

    # Drop entries with certain ISO-3 codes from population data
    wpop_data = wpop_data[~wpop_data['ISO-3'].isin(codes_to_drop + codes_to_skip)]
    
    # Drop entries with certain ISO-3 codes from IPv4 data
    ipv4_data = ipv4_data[~ipv4_data['ISO-3'].isin(codes_to_drop + codes_to_skip)]

    # Merge the cleaned datasets
    combined_data = pd.merge(wpop_data, ipv4_data, on=['ISO-3', 'Year'], how='outer')

    # Sort data to prepare for forward filling
    combined_data.sort_values(by=['ISO-3', 'Year'], inplace=True)

    # Forward fill data for each country
    combined_data.groupby('ISO-3').apply(lambda group: group.fillna(method='ffill'))

    # Optionally, backfill or handle remaining nulls if needed
    combined_data.fillna(method='bfill', inplace=True)  # This line is optional based on the requirement

    # Save or return the processed data
    combined_data.to_csv(output_path, index=False)
    return combined_data

# Example usage
#processed_data = process_and_merge_datasets('wpopdata_long_format_cleaned.csv', 'ipv4_allocations.csv', 'combined_dataset.csv')

# This one might be successful
def merging_attempt():
    # Load the datasets
    ipv4_allocations = pd.read_csv('ipv4_allocations.csv', parse_dates=['Date'])
    wpopdata = pd.read_csv('wpopdata_long_format_cleaned.csv')

    # Generate a full range of years from 1982 to 2023 for each unique ISO-3 code
    all_years = range(1982, 2024)
    all_countries = ipv4_allocations['ISO-3'].unique()
    full_index = pd.MultiIndex.from_product([all_countries, all_years], names=['ISO-3', 'Year'])
    full_ipv4_allocations = pd.DataFrame(index=full_index).reset_index()

    # Merge the original ipv4 data into the full index, using an outer join to keep all rows
    full_ipv4_allocations = pd.merge(full_ipv4_allocations, ipv4_allocations, on=['ISO-3', 'Year'], how='left')

    # Define default values for missing entries
    defaults = {
        'Registry': 'none', 'Code': 'none', 'Type': 'none', 'Start': 0, 'Value': 0,
        'Date': pd.NaT, 'Status': 'unallocated', 'Extensions': 'none', 'Prefix': 0,
        'Country': 'Unknown'
    }

    # Apply defaults to fill in missing data
    for column, default in defaults.items():
        if full_ipv4_allocations[column].dtype == 'object':
            full_ipv4_allocations[column].fillna(default, inplace=True)
        else:
            full_ipv4_allocations[column].fillna(0, inplace=True)  # For numerical columns like Start, Value, Prefix

    # Merge population data
    final_dataset = pd.merge(full_ipv4_allocations, wpopdata, on=['ISO-3', 'Year'], how='left')
    final_dataset['Population'].fillna(0, inplace=True)  # Assuming missing population should be zero

    # Save the final dataset to CSV
    final_dataset.to_csv('final_ipv4_with_population.csv', index=False)

    # Optionally print some rows to verify the contents
    print(final_dataset.head())

#merging_attempt()

def testing_for_discrepancies(final_dataset):
    # Check for any missing values in critical columns
    print("Missing values per column:")
    print(final_dataset.isnull().sum())

    # Verify the range of years and count of unique countries
    print("Unique years in dataset:", final_dataset['Year'].unique())
    print("Number of unique countries:", final_dataset['ISO-3'].nunique())

    # Random samples to visually inspect the data
    print(final_dataset.sample(10))
    
    # Verify population data by comparing known values
    known_values = {
        (1985, 'ZAF'): 30000000,  # Example known value: 30 million in 1985 for South Africa
        (1990, 'USA'): 250000000  # Example known value: 250 million in 1990 for USA
    }

    for (year, country), population in known_values.items():
        actual_population = final_dataset[(final_dataset['Year'] == year) & (final_dataset['ISO-3'] == country)]['Population'].iloc[0]
        print(f"Population for {country} in {year}: {actual_population} (Expected: {population})")

final_dataset = pd.read_csv('final_ipv4_with_population.csv')
#testing_for_discrepancies(final_dataset)


import pandas as pd

def load_and_clean_data(filepath):
    # Define data types for known columns if possible
    dtype_dict = {
        'ISO-3': str,
        'Year': int,
        'Registry': str,
        'Type': str,
        'Start': str,
        'Value': float,
        'Date': str,
        'Status': str,
        'Prefix': float,
        'Country': str,
        'Population': float  # Assuming population is numeric
    }
    
    # Load the dataset with specified data types and low memory option
    df = pd.read_csv(filepath, dtype=dtype_dict, low_memory=False)
    
    # Set all entries in the 'Type' column to 'ipv4'
    df['Type'] = 'ipv4'
    
    return df

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath, low_memory=False)
    # Convert problematic columns to numeric, handling errors
    for column in ['Value', 'Population']:  # Add or adjust columns based on your dataset specifics
        df[column] = pd.to_numeric(df[column], errors='coerce')
    df['Type'] = 'ipv4'  # Ensuring 'Type' column is uniformly set
    return df

def refine_and_clean_dataset(df):
    # Determine the most common 'Registry' for each country
    common_rir = df[df['Registry'] != 'none'].groupby('ISO-3')['Registry'].agg(lambda x: pd.Series.mode(x)[0])

    # Function to infer the RIR for rows where 'Registry' is 'none'
    def infer_rir(row):
        if row['Registry'] == 'none':
            # Get the most common RIR for that country from the precomputed series
            return common_rir.get(row['ISO-3'], 'none')
        else:
            return row['Registry']
    
    # Efficiently apply the function only to rows where 'Registry' is 'none'
    mask = df['Registry'] == 'none'
    df.loc[mask, 'Registry'] = df.loc[mask].apply(infer_rir, axis=1)

    # Columns to drop
    columns_to_drop = ['Code', 'Extensions', 'Country_x']
    df.drop(columns=columns_to_drop, axis=1, inplace=True)

    return df

# Usage
# filepath = 'final_ipv4_with_population.csv'
# final_dataset = load_and_clean_data(filepath)
# final_dataset = refine_and_clean_dataset(final_dataset)
# final_dataset.to_csv('final_ipv4_with_population_refined.csv', index=False)



#refine_and_clean_dataset(final_dataset)


def diagnose_and_handle_mixed_types(filepath):
    # Load the dataset with low_memory=False to avoid initial DtypeWarnings
    df = pd.read_csv(filepath, low_memory=False)
    
    # Identify columns with mixed types
    mixed_type_columns = []
    for column in df.columns:
        try:
            # Attempt to convert each column to float
            pd.to_numeric(df[column], errors='raise')
        except Exception as e:
            # If an exception is raised, this column likely has mixed types
            mixed_type_columns.append(column)

    print("Columns with mixed types:", mixed_type_columns)

    # Handling mixed-type columns
    for column in mixed_type_columns:
        # Show unique values to understand what might be causing issues
        print(f"Unique values in '{column}':", df[column].unique())
        
        # Optionally, convert to numeric and coerce errors to NaN
        # Uncomment the next line if you want to automatically handle it
        # df[column] = pd.to_numeric(df[column], errors='coerce')

    return df

# Usage
# filepath = 'final_ipv4_with_population.csv'
# df = diagnose_and_handle_mixed_types(filepath)

# def clean_dataset(filepath):
#     # Define expected data types for non-numeric columns that could be mixed type
#     dtype_spec = {
#         'ISO-3': str,
#         'Registry': str,
#         'Code': str,
#         'Type': str,
#         'Start': str,
#         'Status': str,
#         'Extensions': str,
#         'Country_x': str,
#         'Country_y': str
#     }

#     # Load the dataset with specified data types for non-numeric columns
#     df = pd.read_csv(filepath, dtype=dtype_spec, low_memory=False)

#     # Convert numeric columns, coerce errors to NaN
#     df['Population'] = pd.to_numeric(df['Population'], errors='coerce')

#     # Attempt to convert 'Date' column with a known format or handle diverse formats
#     try:
#         df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
#     except ValueError:
#         # If a uniform format can't be found, parse dates element-wise
#         df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

#     # Handle 'none' and other placeholders in categorical fields
#     for column in dtype_spec.keys():
#         df[column] = df[column].replace({'none': np.nan, '0': np.nan, '..': np.nan})

#     return df

# # Usage
# filepath = 'final_ipv4_with_population.csv'
# df = clean_dataset(filepath)
# df.to_csv('final_ipv4_with_population_cleaned.csv', index=False)

# def load_and_diagnose_dataset(filepath):
#     # Load the dataset without specifying dtypes to see what data it contains
#     df = pd.read_csv(filepath, low_memory=False)

#     # Identify the problematic column by index and print unique values to diagnose the issues
#     problematic_column = df.columns[13]  # Adjust the index based on zero-indexing
#     print("Problematic Column: ", problematic_column)
#     print("Unique values in the problematic column:", df[problematic_column].unique())

#     return df

# # Use this function to specifically diagnose the issues in column 13
# filepath = 'final_ipv4_with_population.csv'
# df = load_and_diagnose_dataset(filepath)

def diagnose_column_data_types(df, column_name):
    # Check data types present in the column
    data_types = df[column_name].apply(type).value_counts()
    print(f"Data types in column '{column_name}':")
    print(data_types)
    
    # Optionally, display examples of different data types
    for data_type in data_types.index:
        sample_value = df[df[column_name].apply(lambda x: isinstance(x, data_type))][column_name].iloc[0]
        print(f"Example of type {data_type}: {sample_value}")

# Usage of the function
# filepath = 'final_ipv4_with_population.csv'
# df = pd.read_csv(filepath, low_memory=False)
# diagnose_column_data_types(df, 'Population')

def clean_and_convert_population_column(filepath):
    # Load the dataset
    df = pd.read_csv(filepath, low_memory=False)
    
    # Convert the 'Population' column to integers
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce').astype('Int64')  # Use 'Int64' to handle NaN properly
    
    # Save the cleaned dataset
    df.to_csv('final_ipv4_with_population_cleaned.csv', index=False)

    # Check for any remaining missing values
    print(df.isnull().sum())

    # Review the dataset's summary to ensure everything looks as expected
    print(df.describe(include='all'))


    return df


# Usage
# filepath = 'final_ipv4_with_population.csv'
# df = clean_and_convert_population_column(filepath)


def finalize_dataset_cleanup(df):
    # Fill NaNs in 'Country_y' based on 'Country_x' or a predefined mapping
    # Example: If 'Country_x' can be used directly or adjusted
    df['Country_y'].fillna(df['Country_x'], inplace=True)

    # Fill NaNs in 'Population' with the median or another appropriate value
    median_population = df['Population'].median()
    df['Population'].fillna(median_population, inplace=True)

    return df

# Assuming df is your DataFrame after previous clean-up steps
#df = finalize_dataset_cleanup(df)

# Final check for NaNs
# df = 
# print(df.isnull().sum())

# Load the refined dataset
def load_and_clean_refined_dataset(filepath):
    df = pd.read_csv(filepath, low_memory=False)
    
    # Convert 'Population' column to integers, handling NaNs if necessary
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce').astype('Int64')
    
    # Handle missing values in 'Country_y' by filling with 'Country_x' if that makes sense contextually
    df['Country_y'].fillna(df['Country_x'], inplace=True)
    
    # Check data types and missing values again
    print("Data types and NaN counts:")
    print(df.dtypes)
    print(df.isnull().sum())
    
    return df

# # Filepath to the refined dataset
# filepath = 'final_ipv4_with_population_refined.csv'
# df = load_and_clean_refined_dataset(filepath)

# # Save the cleaned data back to a new CSV
# df.to_csv('final_ipv4_with_population_refined_cleaned.csv', index=False)

# # Final checks
# print(df.describe(include='all'))

def load_and_clean_dataset(filepath):
    # Load the dataset, specifying low_memory=False to handle data types more efficiently
    try:
        df = pd.read_csv(filepath, low_memory=False)
        print("Dataset loaded successfully.")
    except FileNotFoundError:
        print("File not found. Please check the filepath.")
        return None
    
    # Diagnose data types and check for mixed types
    print("Data types in each column:")
    print(df.dtypes)

    # Attempt to convert 'Population' to integers, handling NaNs if necessary
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce').astype('Int64')
    
    # Check for any other columns that might have mixed types and print unique values if needed
    for col in df.columns:
        if df[col].apply(type).nunique() > 1:
            print(f"Column {col} has mixed types.")
            print(f"Unique values in {col}: {df[col].unique()[:5]}")  # Show only first 5 unique values

    # Handle missing values in 'Country_y' by filling with 'Country_x' if appropriate
    if 'Country_y' in df.columns and 'Country_x' in df.columns:
        df['Country_y'].fillna(df['Country_x'], inplace=True)
    
    return df

def save_cleaned_data(df, output_filepath):
    if df is not None:
        df.to_csv(output_filepath, index=False)
        print(f"Cleaned data saved to {output_filepath}")
    else:
        print("No data to save.")

# File paths
input_filepath = 'final_ipv4_with_population_refined.csv'
output_filepath = 'final_ipv4_with_population_refined_cleaned.csv'

# Load, clean, and save the dataset
# df = load_and_clean_dataset(input_filepath)
# save_cleaned_data(df, output_filepath)

import pandas as pd

def clean_and_standardize_columns(df):
    # Ensure 'Country_y' is treated uniformly as string
    df['Country_y'] = df['Country_y'].astype(str)
    
    # Convert 'Population' to float to avoid any dtype issues with Int64
    df['Population'] = df['Population'].astype(float)

    # Diagnostics post conversion
    print("Post-cleaning data types:")
    print(df.dtypes)

    # Check for any remaining mixed types
    for col in ['Country_y', 'Population']:
        if df[col].apply(type).nunique() > 1:
            print(f"Column {col} still has mixed types.")
        else:
            print(f"Column {col} data type is now uniform.")

    return df

# Load the dataset
# df = pd.read_csv('final_ipv4_with_population_refined.csv', low_memory=False)

# # Clean and standardize specific columns
# df = clean_and_standardize_columns(df)

# # Save the cleaned data back to a new CSV
# df.to_csv('final_ipv4_with_population_refined_cleaned.csv', index=False)
# print("Data saved successfully.")
# def test_uniform_data_types(df):
#     for col in df.columns:
#         unique_types = df[col].apply(type).nunique()
#         assert unique_types == 1, f"Column {col} has {unique_types} different types"
#         print(f"Column {col} passed with uniform data type.")

# ### 2. Test for No NaNs in Specific Columns
# #This test ensures that certain columns, such as 'Country_y' and 'Population', contain no NaN values if that's expected after cleaning.

# #```python
# def test_no_nans_in_important_columns(df, columns):
#     for col in columns:
#         nan_count = df[col].isnull().sum()
#         assert nan_count == 0, f"Column {col} has {nan_count} NaNs"
#         print(f"Column {col} passed with no NaNs.")

# df = pd.read_csv('final_ipv4_with_population_refined_cleaned.csv')
# test_uniform_data_types(df)


def test_uniform_data_types(df):
    for col in df.columns:
        unique_types = df[col].apply(type).nunique()
        assert unique_types == 1, f"Column {col} has {unique_types} different types"
        print(f"Column {col} passed with uniform data type.")

### 2. Test for No NaNs in Specific Columns
#This test ensures that certain columns, such as 'Country_y' and 'Population', contain no NaN values if that's expected after cleaning.

def test_no_nans_in_important_columns(df, columns):
    for col in columns:
        nan_count = df[col].isnull().sum()
        assert nan_count == 0, f"Column {col} has {nan_count} NaNs"
        print(f"Column {col} passed with no NaNs.")

def test_column_data_type(df, column_name, expected_type):
    actual_type = df[column_name].dtype
    assert actual_type == expected_type, f"Column {column_name} has incorrect type: {actual_type}, expected: {expected_type}"
    print(f"Column {column_name} passed with correct data type {expected_type}.")


def test_sample_values(df, column_name, expected_values):
    sample_values = df[column_name].dropna().unique()
    for value in expected_values:
        assert value in sample_values, f"Value {value} not found in {column_name}"
    print(f"All expected values are present in {column_name}.")


# Assuming df is your DataFrame after cleaning
df = pd.read_csv('final_ipv4_with_population_refined_cleaned.csv')

# Run tests
# test_uniform_data_types(df)
# test_no_nans_in_important_columns(df, ['Country_y', 'Population'])
# test_column_data_type(df, 'Population', 'float64')
# test_sample_values(df, 'Registry', ['arin', 'ripencc', 'apnic', 'lacnic', 'afrinic'])

# print("All tests passed successfully.")

def diagnose_column_types(df, column_name):
    print(f"Types in {column_name}:")
    print(df[column_name].apply(lambda x: type(x)).value_counts())

# Load the data
df = pd.read_csv('final_ipv4_with_population_refined_cleaned.csv')

# Diagnose types in 'Country_y'
# diagnose_column_types(df, 'Country_y')


def clean_country_column(df, column_name):
    # Convert all entries to strings, even NaNs and numeric placeholders
    df[column_name] = df[column_name].apply(lambda x: str(x) if not pd.isnull(x) else x)

    # Replace any known numeric placeholders or anomalies after conversion to string
    numeric_placeholders = ['nan', '999', '0']  # Add any other placeholders you know are used
    for placeholder in numeric_placeholders:
        df[column_name] = df[column_name].replace(placeholder, np.nan)

    # Check the transformation
    print(f"Transformed types in {column_name}:")
    print(df[column_name].apply(lambda x: type(x)).value_counts())

    return df

# Assuming df is already loaded from the previous code
# df = pd.read_csv('final_ipv4_with_population.csv')
# df = clean_country_column(df, 'Country_y')

# # Optional: Save the cleaned dataframe
# df.to_csv('final_ipv4_with_population_refined_cleaned.csv', index=False)


# def check_country_column_types(filepath):
#     # Load the dataset
#     df = pd.read_csv(filepath)

#     # Print the data types of the country columns
#     country_x_type = df['Country_x'].dtype
#     country_y_type = df['Country_y'].dtype

#     print(f"Data type for Country_x: {country_x_type}")
#     print(f"Data type for Country_y: {country_y_type}")

#     # Optionally, you might want to see some sample values to understand the content better
#     print("Sample values from Country_x:", df['Country_x'].dropna().unique()[:5])  # show first 5 unique non-null values
#     print("Sample values from Country_y:", df['Country_y'].dropna().unique()[:5])  # show first 5 unique non-null values

# # Specify the path to your CSV file
# filepath = 'final_ipv4_with_population_refined_cleaned.csv'
# check_country_column_types(filepath)

import pandas as pd
import pycountry

def update_country_names(df, iso_col, country_cols):
    # Convert country columns to string in case they are not
    for col in country_cols:
        df[col] = df[col].astype(str)

    # Define a helper to get country names from ISO-3 codes
    def get_country_name(iso_code):
        try:
            return pycountry.countries.get(alpha_3=iso_code).name
        except AttributeError:
            return None

    # Update country columns based on ISO-3 codes
    for col in country_cols:
        df[col] = df[iso_col].apply(get_country_name).fillna(df[col])

    return df

# Example usage
# df = pd.read_csv('final_ipv4_with_population_refined_cleaned.csv')
# df = update_country_names(df, 'ISO-3', ['Country_x', 'Country_y'])
# df.to_csv('final_ipv4_with_population_updated.csv', index=False)


def check_country_iso_discrepancies(df, iso_col, country_cols):
    # Helper to get country names from ISO-3 codes
    def get_country_name(iso_code):
        try:
            return pycountry.countries.get(alpha_3=iso_code).name
        except AttributeError:
            return None

    discrepancies = {}
    for col in country_cols:
        # Checking for discrepancies
        expected_country = df[iso_col].apply(get_country_name)
        discrepancies[col] = df[df[col] != expected_country]

    # Print results
    for col, discrep_df in discrepancies.items():
        if discrep_df.empty:
            print(f"No discrepancies found in {col}.")
        else:
            print(f"Discrepancies found in {col}:")
            print(discrep_df[[iso_col, col]])
            print("\n")

    return discrepancies

# Example usage
df = pd.read_csv('final_ipv4_with_population_updated.csv')
#discrepancies = check_country_iso_discrepancies(df, 'ISO-3', ['Country_x', 'Country_y'])

import pandas as pd

def clean_and_adjust_dataset(filepath):
    # Load the dataset
    df = pd.read_csv(filepath)

    # Filter out rows where ISO-3 is 'RES' or 'EUR'
    df = df[~df['ISO-3'].isin(['RES', 'EUR'])]

    # Drop the 'Country_y' column
    df.drop('Country_y', axis=1, inplace=True)

    # Rename 'Country_x' to 'Country'
    df.rename(columns={'Country_x': 'Country'}, inplace=True)

    # Save the cleaned and adjusted DataFrame
    df.to_csv('final_ipv4_with_population_adjusted.csv', index=False)

    return df

# Specify the path to your CSV file
# filepath = 'final_ipv4_with_population_updated.csv'
# df = clean_and_adjust_dataset(filepath)

# # Optionally, print a summary to confirm the changes
# print("Data after cleaning and adjustments:")
# print(df.head())
# print(df['ISO-3'].value_counts())  # To confirm RES and EUR are removed

def clean_and_save_dataframe(filepath, output_file):
    # Load the dataset
    df = pd.read_csv(filepath)

    # Drop the 'Code' and 'Extensions' columns
    df.drop(['Code', 'Extensions'], axis=1, inplace=True)

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_file, index=False)

    return df

# Specify the path to your CSV file and the output file name
input_filepath = 'final_ipv4_with_population_adjusted.csv'
output_filepath = 'whois_v4_pop.csv'

# Clean the DataFrame and save it
df = clean_and_save_dataframe(input_filepath, output_filepath)

# Optionally, print a summary to confirm the changes
print("Data after dropping columns:")
print(df.head())