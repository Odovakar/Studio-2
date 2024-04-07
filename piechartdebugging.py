from dash import Dash, html, dcc, Input, Output, State
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import pycountry

external_stylesheets = [dbc.themes.BOOTSTRAP]

'''----------json dataframe processing and enhancing----------'''
def alpha2_to_alpha3(alpha_2):
    # Special case for Kosovo, which dash didn't manage
    if alpha_2 == 'XK':
        return 'XKX'
    # Handle other cases using pycountry
    try:
        country = pycountry.countries.get(alpha_2=alpha_2)
        return country.alpha_3
    except AttributeError:
        # Return if no Alpha-3 code is found
        return 'Unknown'

# Grouping the respective countries in order to add a RIR column
def alpha3_to_rir(alpha_3):
    # Mapping based on regions
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

# Grouping ipv4 for 'grouped scale'
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

# Fetching raw data from github repository
def fetch_json_data(json_raw_data_url):
    response = requests.get(json_raw_data_url)
    return response.json()

# Transforming JSON data from nested into something readable by the grid (table)
def transform_json_data(json_data):
    transformed_data = []
    for country_code, details in json_data.items():
        if country_code == "EU":  # Skip the EU entry, this bugger is creating problems
            continue
        details['country_code'] = country_code  # Add country_code to the details dict
        transformed_data.append(details)
    return transformed_data

# Dataframe creation and initial processing
def create_and_process_dataframe(transformed_data):
    json_df = pd.DataFrame(transformed_data)
    json_df['ipv4'] = pd.to_numeric(json_df['ipv4'], errors='coerce') # str to int
    json_df['pop'] = pd.to_numeric(json_df['pop'], errors='coerce') # str to int
    return json_df[(json_df['pop'] > 800) & (json_df['name'] != 'World')] # skip world entry, row is creating problems. (could possibly be moved to )

# Trickery to add columns for visualisation purposes:
def enhance_dataframe(json_df):
    json_df['iso_alpha_3'] = json_df['country_code'].apply(alpha2_to_alpha3) # upgrading from iso-2 to 3 because dash doesn't work with i2
    json_df['ipv4_grouping'] = json_df['ipv4'].apply(assign_ipv4_grouping) # Creating grouping for the grouped scale
    json_df['RIR'] = json_df['iso_alpha_3'].apply(alpha3_to_rir) # Adding a 
    json_df['log_ipv4'] = np.log10(json_df['ipv4'] + 1)
    json_df['log_percentv4'] = np.log10(json_df['percentv4'] + 1) # This creates the column from the get go.
    return json_df

# def create_log_percentv4_column(data_frame):
#     data_frame['log_percentv4'] = np.log10(data_frame['percentv4'] + 1)
#     return data_frame

# Column definitions for ag-grid
def generate_column_definitions(json_df):
    return [{'field': col, 'sortable': True, 'filter': True} for col in json_df.columns]

# big boi cookpot to pull all things together before utilisation in the app
def fetch_and_transform_json_data(json_raw_data_url):
    json_data = fetch_json_data(json_raw_data_url)
    transformed_data = transform_json_data(json_data)
    json_df = create_and_process_dataframe(transformed_data)
    json_df = enhance_dataframe(json_df)
    column_defs = generate_column_definitions(json_df)
    return transformed_data, column_defs, json_df

# JSON ip_alloca data processing calls to data_processing folder script
json_raw_data_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json'
transformed_data, column_defs, json_df = fetch_and_transform_json_data(json_raw_data_url)

'''----------Netlist Data Processing----------'''
# Fetching data from github repository
def fetch_netlist_data(url):
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    data = [line.split(maxsplit=3) for line in lines if line]
    netlist_df = pd.DataFrame(data, columns=['Start', 'End', 'RIR', 'Description'])
    return netlist_df

# Function to tidy up and better granularity of the netlist data
def process_netlist_data(netlist_df):
    # Splitting Description column into multiple columns
    netlist_df[['Status', 'IP']] = netlist_df['Description'].str.split(n=1, expand=True)
    # Further split IP column into IP address and Prefix columns
    netlist_df[['IP Address', 'Prefix']] = netlist_df['IP'].str.split("/", expand=True)
    # Dropping unnecessary columns
    netlist_df.drop(columns=['Description', 'IP'], inplace=True)
    # Convert 'Start' and 'End' columns to UInt64
    netlist_df['Start'] = netlist_df['Start'].astype('UInt64')
    netlist_df['End'] = netlist_df['End'].astype('UInt64')
    # Calculate aggregate as the difference between 'End' and 'Start'
    netlist_df['Nr of IPs'] = netlist_df['End'] - netlist_df['Start']
    return netlist_df

netlist_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/netlist.txt'
netlist_df = fetch_netlist_data(netlist_url)
netlist_df = process_netlist_data(netlist_df)

afrinic_url = 'https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest'

def fetch_afrinic_data(afrinic_url):
    response = requests(afrinic_url)
    lines = response.text.strip().split('\n')

#print(netlist_df)

'''stuff for bug squashing'''
#print("json_df columns:", json_df.columns.tolist())
#print(json_df.head())
#usa_row_by_iso_alpha_3 = json_df.loc[json_df['iso_alpha_3'] == 'USA']
#print(usa_row_by_iso_alpha_3)
#print(json_df['iso_alpha_3'].unique())
#unknown_rir_orig = json_df.loc[json_df['RIR'] == 'Unknown']
#print("Original DataFrame with Unknown RIR:")
#print(unknown_rir_orig[['country_code','iso_alpha_3', 'name', 'RIR']])
#print(json_df['percentv4'].dtype)

# Fetching Data for Hoverlabel
customdata = np.stack((
    json_df['name'],          # Country name
    json_df['ipv4'],          # IPv4 address count
    json_df['pop'],           # Population size
    json_df['percentv4'],     # Percent of IPv4 pool
    json_df['pcv4'],          # IPv4 per capita percentage
    #json_df['log_ipv4']       # Log of IPv4 for the logarithmic map
), axis=-1)

# App Initialisation
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Different templates for different graphs/visualisations
def get_hovertemplate(scale_type):
    if scale_type=='grouped':
        hover_template='<b>%{customdata[0]}</b><br>' + \
                       'IPv4: %{customdata[1]:,.0f}<br>' + \
                       'Population: %{customdata[2]:,.0f}<br>' + \
                       'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                       'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                       '<extra>IPv4 Grouping: %{customdata[6]}</extra>'
        return hover_template
    elif scale_type=='log':
        hover_template='<b>%{customdata[0]}</b><br>' + \
                       'IPv4: %{customdata[1]:,.0f}<br>' + \
                       'Population: %{customdata[2]:,.0f}<br>' + \
                       'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                       'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                       '<extra>Log IPv4: %{customdata[7]:.2f}</extra>'
        return hover_template

# Color scale in function for easier code reusability -- Might add some more conditionals later when scaling for other graphs
def get_colorscale(scale_type):
    if scale_type == 'grouped':
        colors = {
            '0-10K': 'rgb(15, 246, 228)',
            '10K-100K': 'rgb(0, 229, 255)',
            '100K-1M': 'rgb(0, 208, 255)',
            '1M-10M': 'rgb(86, 187, 255)',
            '10M-100M': 'rgb(141, 160, 255)',
            '100M-1B': 'rgb(207, 104, 255)',
            '1B+': 'rgb(250, 0, 196)'
        }
        return colors

# Formatting for the ag-grid
def format_json_data_for_aggrid(df):
    formatted_df = df.copy()

    # If 'ipv4' is already an integer, format it for display as a string with separators
    formatted_df['ipv4'] = formatted_df['ipv4'].apply(lambda x: "{:,.0f}".format(x))
    formatted_df['log_ipv4'] = formatted_df['log_ipv4'].apply(lambda x: "{:,.1f}".format(x))
    # Ensure percentage fields are formatted as strings with percentage signs
    formatted_df['pcv4'] = formatted_df['pcv4'].apply(lambda x: "{:.1f}%".format(x))
    formatted_df['percentv4'] = formatted_df['percentv4'].apply(lambda x: "{:.1f}%".format(x))

    return formatted_df.to_dict('records')

def format_netlist_data_for_aggrid(df):
    formatted_df = df.copy()
    formatted_df['Start'] = formatted_df['Start'].apply(lambda x: "{:,.0f}".format(x))
    formatted_df['End'] = formatted_df['End'].apply(lambda x: "{:,.0f}".format(x))
    formatted_df['Nr of IPs'] = formatted_df['Nr of IPs'].apply(lambda x: "{:,.0f}".format(x))
    return formatted_df.to_dict('records')

# Calculating percentages for RIR display on the pie chart
# AFRINIC APNIC ARIN LACNIC RIPE NCC
def calculate_rir_percentages(df):
    rir_percentages = df.groupby('RIR')['percentv4'].sum().reset_index()
    return rir_percentages

def calculate_rir_country_data(df, selected_value):
    if selected_value == 'ARIN':
        arin_data = df[df['RIR'] == 'ARIN']
        return arin_data
    elif selected_value == 'APNIC':
        apnic_data = df[df['RIR'] == 'APNIC']
        return apnic_data
    elif selected_value == 'RIPENCC':
        ripencc_data = df[df['RIR'] == 'RIPE NCC']
        return ripencc_data
    elif selected_value == 'LACNIC':
        lacnic_data = df[df['RIR'] == 'LACNIC']
        return lacnic_data
    elif selected_value == 'AFRINIC':
        afrinic_data = df[df['RIR'] == 'AFRINIC']
        return afrinic_data
    else:
        return None

def generate_pie_figure(data_frame, values, names, **args):

    pie_fig = px.pie(
        data_frame=data_frame,
        values=values,
        names=names
    )
    return pie_fig


'''----------pie stuff----------'''
@app.callback(
    Output('the-pie-figure', 'figure'),
    [Input('pie_selector', 'value'), Input('dataset_selector', 'value')]
)
def update_pie_figure(selected_value, dataset_selector):
    if selected_value=='TotalPool':
        if dataset_selector=='IPv4':
            pie_fig = generate_pie_figure(json_df, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50),)
            return pie_fig
        elif dataset_selector=='WHOIS':
            pie_fig = generate_pie_figure(netlist_df, 'Nr of IPs', 'RIR')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50),)
            return pie_fig

    elif selected_value=='RIR':
        rir_percentages = calculate_rir_percentages(json_df)
        if dataset_selector=='IPv4':
            pie_fig = generate_pie_figure(rir_percentages, 'percentv4', 'RIR')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50),)
            return pie_fig
        elif dataset_selector=='WHOIS':
            pie_fig = generate_pie_figure(netlist_df, 'Nr of IPs', 'RIR')
            pie_fig.update_layout(
                legend=dict(
                    title="IPv4 Groups",
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.25,
                    yanchor="bottom",
                    itemsizing="constant"
                ),
                margin=dict(t=50, b=50, l=50, r=50),
            )
            return pie_fig
        # pie_fig = generate_pie_figure(rir_percentages, 'percentv4', 'RIR')
        # pie_fig.update_traces(textposition='inside')
        # pie_fig.update_layout(
        #     legend=dict(
        #         title="IPv4 Groups",
        #         orientation="h",
        #         x=0.5,
        #         xanchor="center",
        #         y=-0.25,
        #         yanchor="bottom",
        #         itemsizing="constant"
        #     ),
        #     margin=dict(t=50, b=50, l=50, r=50),
        # )
        # return pie_fig
    elif selected_value == 'ARIN':
        arin_data = calculate_rir_country_data(json_df, 'ARIN')
        if arin_data is not None:
            pie_fig = generate_pie_figure(arin_data, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50))
            return pie_fig
    elif selected_value == 'APNIC':
        apnic_data = calculate_rir_country_data(json_df, 'APNIC')
        if apnic_data is not None:
            pie_fig = generate_pie_figure(apnic_data, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50))
            return pie_fig
    elif selected_value == 'RIPENCC':
        ripencc_data = calculate_rir_country_data(json_df, 'RIPENCC')
        if ripencc_data is not None:
            pie_fig = generate_pie_figure(ripencc_data, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50))
            return pie_fig
    elif selected_value == 'LACNIC':
        lacnic_data = calculate_rir_country_data(json_df, 'LACNIC')
        if lacnic_data is not None:
            pie_fig = generate_pie_figure(lacnic_data, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50))
            return pie_fig
    elif selected_value == 'AFRINIC':
        afrinic_data = calculate_rir_country_data(json_df, 'AFRINIC')
        if afrinic_data is not None:
            pie_fig = generate_pie_figure(afrinic_data, 'percentv4', 'name')
            pie_fig.update_traces(textposition='inside')
            pie_fig.update_layout(showlegend=False, margin=dict(t=50, b=50, l=50, r=50))
            return pie_fig


ipv4_group_to_ticks = {
    '0-10k': 0-10000,        # Midpoint of the range as representative value
    '10k-100k': 55000,
    '100k-1M': 550000,
    '1M-10M': 5500000,
    '10M-100M': 55000000,
    '100M-1B': 550000000,
    '1B+': 1500000000
}

'''----------ag-grid----------'''
@app.callback(
    [Output('the-ag-grid', 'rowData'), Output('the-ag-grid', 'columnDefs')],
    [Input('dataset_selector', 'value')]
)
def update_columns(selected_value):
    row_data = format_json_data_for_aggrid(json_df)
    netlist_row_data =  format_netlist_data_for_aggrid(netlist_df)
    #print("Callback triggered, selected value:", selected_value)  # Debug print
    #test_formatted_data = format_json_data_for_aggrid(json_df.head())
    #print(test_formatted_data)
    if selected_value=='IPv4':  
        column_defs = [
            {'field': 'name', 'headerName': 'Country', 'sortable': True, 'filter': True, 'width': 150, 'flex': 1},
            {'field': 'ipv4', 'headerName': 'Nr of Addresses', 'sortable': True, 'filter': True, 'width': 130, 'flex': 1},
            {'field': 'pcv4', 'headerName': 'Pct per Cap', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'percentv4', 'headerName': 'Pct of Pool', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'ipv4_grouping', 'headerName': 'Grouping', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'RIR', 'headerName': 'RIR', 'sortable': True, 'filter': True, 'width': 90, 'flex': 1},
            {'field': 'log_ipv4', 'headerName': 'IPv4 Log', 'sortable': True, 'filter': True, 'width': 80, 'flex': 1},
        ]
        return row_data, column_defs
    elif selected_value=='IPv6':  # Assuming IPv6 data exists and is similarly structured
        column_defs = [
            {'field': 'name', 'headerName': 'Country', 'sortable': True, 'filter': True},
            # Define the rest according to your IPv6 data structure
            # This is just a placeholder to illustrate the approach
        ]
        return row_data, column_defs
    elif selected_value=='WHOIS':
        column_defs = [
            {'field': 'Start', 'headerName': 'Start', 'sortable': True, 'filter': True, 'width': 150, 'flex': 1},
            {'field': 'End', 'headerName': 'End', 'sortable': True, 'filter': True, 'width': 130, 'flex': 1},
            {'field': 'Nr of IPs', 'headerName': 'Nr of IPs', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'RIR', 'headerName': 'RIR', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'Status', 'headerName': 'Status', 'sortable': True, 'filter': True, 'width': 100, 'flex': 1},
            {'field': 'IP Address', 'headerName': 'IP Address', 'sortable': True, 'filter': True, 'width': 90, 'flex': 1},
            {'field': 'Prefix', 'headerName': 'Prefix', 'sortable': True, 'filter': True, 'width': 80, 'flex': 1},
        ]
        return netlist_row_data, column_defs


'''----------Render the application----------'''    
# App Layout
app.layout = html.Div([
    dbc.Row(
        [
            # Empty column to take up 1/3 of the screen space
            dbc.Col(width=4),
            # Header centered within its column, 4/12 spaces
            dbc.Col(html.H2('IPv4 Allocation Data', className='text-center'), width=4),
            # Dropdown aligned right, 4/12 spaces
            dbc.Col(dcc.Dropdown(
                id='scale-selector',
                options=[ # TODO: Fix log scale for the pie chart since everything is squashed.
                    {'label': 'Normal Visualisation', 'value': 'normal'},
                    {'label': 'Logarithmic Visualisation', 'value': 'log'}
                ],
                value='log',
                clearable=False,
            ), width=4, className='justify-content-end'),
        ],
        className='align-items-center',  # Vertically align the columns if they wrap on smaller screens
    ),
    dbc.Row([
    dbc.Col([
        dcc.RadioItems(
            id='pie_selector',
            options=[
                {'label': 'Total Pool', 'value': 'TotalPool'},
                {'label': 'RIR', 'value': 'RIR'},
                {'label': 'ARIN', 'value': 'ARIN'},
                {'label': 'APNIC', 'value': 'APNIC'},
                {'label': 'RIPE NCC', 'value': 'RIPENCC'},
                {'label': 'LACNIC', 'value': 'LACNIC'},
                {'label': 'AFRINIC', 'value': 'AFRINIC'}
            ],
            value='TotalPool',  # Default value
            labelStyle={'display': 'inline-block'}
        )
    ], width={'size': 12}, className='text-center'),
    ]),
    dbc.Row(
        dbc.Col(dcc.Graph(id='the-pie-figure'), width=12)
    ),
    dbc.Row([
    dbc.Col([
        dcc.RadioItems(
            id='dataset_selector',
            options=[
                {'label': 'IPv4', 'value': 'IPv4'},
                {'label': 'IPv6', 'value': 'IPv6'},
                {'label': 'WHOIS', 'value': 'WHOIS'}
            ],
            value='IPv4',  # Default value
            labelStyle={'display': 'inline-block'}
        )
    ], width={'size': 2, 'offset': 1}, className='text-center'),
    ]),
    dbc.Row(
        dbc.Col(dag.AgGrid(
            id='the-ag-grid',
            rowData=[],
            columnDefs=[],
            className='ag-theme-balham',
            dashGridOptions={'pagination': True, 'paginationAutoPageSize': True},
        ), width={'size':10, 'offset':1})
    ),
], className='container-fluid')

if __name__ == '__main__':
    app.run_server(debug=True)
