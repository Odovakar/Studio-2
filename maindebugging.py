from dash import Dash, html, dcc, Input, Output, State
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import pycountry

external_stylesheets = [dbc.themes.BOOTSTRAP]

def alpha2_to_alpha3(alpha_2):
    # Handle special case for Kosovo
    if alpha_2 == 'XK':
        return 'XKX'
    # Handle other cases using pycountry
    try:
        country = pycountry.countries.get(alpha_2=alpha_2)
        return country.alpha_3
    except AttributeError:
        # Return None or some other placeholder if no Alpha-3 code is found
        return 'Unknown'

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

# Fetching data from github repository
def fetch_and_transform_json_data(json_raw_data_url):
    response = requests.get(json_raw_data_url)
    json_data = response.json()

    transformed_data = []
    for country_code, details in json_data.items():
        # Skip the EU entry
        if country_code == "EU":
            continue
        country_data = {"country_code": country_code, **details}
        transformed_data.append(country_data)

    json_df = pd.DataFrame(transformed_data)  # Correctly initializing json_df
    json_df['ipv4'] = pd.to_numeric(json_df['ipv4'], errors='coerce')
    json_df['pop'] = pd.to_numeric(json_df['pop'], errors='coerce')
    json_df = json_df[(json_df['pop'] > 800) & (json_df['name'] != 'World')]

    json_df['log_ipv4'] = np.log10(json_df['ipv4'] + 1)  # Correct reference to json_df

    if transformed_data:
        column_defs = [{'field': col, 'sortable': True, 'filter': True} for col in transformed_data[0].keys()]
    else:
        column_defs = []

    return transformed_data, column_defs, json_df

# Netlist data initialisation
netlist_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/netlist.txt'
netlist_data_frame = fetch_netlist_data(netlist_url)
netlist_data_frame = process_netlist_data(netlist_data_frame)

# JSON ip_alloca data processing calls to data_processing folder script
json_raw_data_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json'
transformed_data, column_defs, json_df = fetch_and_transform_json_data(json_raw_data_url)
# Convert ISO Alpha-2 codes to ISO Alpha-3 codes in your DataFrame
json_df['iso_alpha_3'] = json_df['country_code'].apply(alpha2_to_alpha3)
#print("json_df columns:", json_df.columns.tolist())

# After creating json_df from the JSON data
#print(json_df.columns)
#print(json_df['iso_alpha_3'].unique())


# App Initialisation
app = Dash(__name__, external_stylesheets=external_stylesheets)

@app.callback(
    Output('the-choropleth-map', 'figure'),
    [Input('scale-selector', 'value')]
)
def update_map(scale_type):
    common_bottom_margin = 80  # Adjust this value as needed

    customdata = np.stack((
        json_df['name'],          # Country name
        json_df['ipv4'],          # IPv4 address count
        json_df['pop'],           # Population size
        json_df['percentv4'],     # Percent of IPv4 pool
        json_df['pcv4'],          # IPv4 per capita percentage
        json_df['log_ipv4']       # Log of IPv4 for the logarithmic map
    ), axis=-1)

    hover_template = '<b>%{customdata[0]}</b><br>' + \
                    'IPv4: %{customdata[1]:,.0f}<br>' + \
                    'Population: %{customdata[2]:,.0f}<br>' + \
                    'Percent of IPv4: %{customdata[3]:.2f}%<br>' + \
                    'IPv4 per Capita: %{customdata[4]:.2f}%<extra></extra>'

                    
    customdata = np.nan_to_num(customdata, nan=0.0)
    
    if scale_type == 'log':
        color = 'log_ipv4'
        map_fig = px.choropleth(
            data_frame=json_df,
            locations='iso_alpha_3',
            color=color,
            color_continuous_scale=px.colors.sequential.Viridis,
            range_color=[json_df[color].min(), json_df[color].max()],
            locationmode='ISO-3',
            hover_name='name',
            hover_data={
                'ipv4': ':,.0f',
                'iso_alpha_3': False,  # This correctly excludes the iso_alpha_3 field from hover data
                'pop': ':,.0f',
                'percentv4': ':.2f',
                'pcv4': ':.2f',
                'log_ipv4': False
            }
        )
        map_fig.update_layout(
            coloraxis_colorbar=dict(
                title="Log IPv4",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.1,
                yanchor="bottom",
                thicknessmode="pixels",
                thickness=20,
                len=0.8  # Adjusts the length of the colorbar to 80% of the axis length
            ),
            margin={"r":20, "t":20, "l":20, "b":common_bottom_margin}
        )
        #map_fig.update_traces(hovertemplate=hover_template, customdata=customdata) 
        #print("json_df columns:", json_df.columns.tolist())
        #print(customdata[0])
        (customdata[0], customdata[1], customdata[2], customdata[3], customdata[4], customdata[5], customdata[6])

    else:
        json_df['ipv4_category'] = pd.cut(
            json_df['ipv4'],
            bins=[0, 10**4, 10**5, 10**6, 10**7, 10**8, 10**9, json_df['ipv4'].max() + 1],
            labels=['< 10K', '10K - 100K', '100K - 1M', '1M - 10M', '10M - 100M', '100M - 1B', '> 1B'],
            include_lowest=True,
            right=False
        )

        colors = {
            '< 10K': 'rgb(71, 203, 255)',
            '10K - 100K': 'rgb(95, 187, 255)',
            '100K - 1M': 'rgb(140, 166, 255)',
            '1M - 10M': 'rgb(187, 138, 255)',
            '10M - 100M': 'rgb(226, 104, 220)',
            '100M - 1B': 'rgb(251, 63, 168)',
            '> 1B': 'rgb(255, 25, 106)'
        }   

        map_fig = px.choropleth(
            data_frame=json_df,
            locations='iso_alpha_3',
            color='ipv4_category',
            color_discrete_map=colors,
            locationmode='ISO-3',
            hover_name='name',
            hover_data={
                'ipv4': ':,.0f',
                'iso_alpha_3': False,  # This correctly excludes the iso_alpha_3 field from hover data
                'pop': ':,.0f',
                'percentv4': ':.2f',
                'pcv4': ':.2f',
                'ipv4_category': False,
                'log_ipv4': False
            }
        )
        map_fig.update_layout(
            legend=dict(
                title="IPv4 Groups",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.1,
                yanchor="bottom",
                itemsizing="constant"
            ),
            margin={"r":20, "t":20, "l":20, "b":common_bottom_margin}
        )

    map_fig.update_geos(showframe=False, projection_type='equirectangular', lonaxis_range=[-180, 180], lataxis_range=[-60, 90])
    map_fig.update_layout(
        autosize=True,
    )
    map_fig.update_traces(hovertemplate=hover_template, customdata=customdata)
    print(customdata[0], customdata[1], customdata[2], customdata[3], customdata[4], customdata[5], customdata[6])
    return map_fig




# Instantiating & Configuring Scatter Object
# scatter_fig = px.scatter(
#     data_frame=json_df,
#     x='pop',
#     y='ipv4',
#     color='country_code',
#     hover_name="name",
#     size_max=60,
#     labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
#     size="ipv4"  # Using population for the bubble size
# )


# Adjusting the axes to a log scale for better visibility in case of wide range
# scatter_fig.update_xaxes(type='log', title_text='Population Size (Log Scale)')
# scatter_fig.update_yaxes(type='log', title_text='Number of IPv4 Addresses (Log Scale)')
#scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=2.*max(json_df['ipv4'])/(40.**2), sizemin=4))
# max_ipv4 = json_df['ipv4'].max()
# desired_max_marker_size = 100
# Calculate sizeref for the 'ipv4' values
# sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 2)
# scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=sizeref, sizemin=4))




# App Layout
app.layout = html.Div([
    dbc.Row(
        [
            # Empty column to take up 1/3 of the screen space
            dbc.Col(width=4),
            # Header centered within its column, 4/12 spaces
            dbc.Col(html.H1('IPv4 Allocation Data', className='text-center'), width=4),
            # Dropdown aligned right, 4/12 spaces
            dbc.Col(dcc.Dropdown(
                id='scale-selector',
                options=[
                    {'label': 'Logarithmic Scale', 'value': 'log'},
                    {'label': 'Custom Scale', 'value': 'custom'}
                ],
                value='log',
                clearable=False,
            ), width=4, className='justify-content-end'),
        ],
        className='align-items-center',  # Vertically align the columns if they wrap on smaller screens
    ),
    dbc.Row(
        dbc.Col(dcc.Graph(id='the-choropleth-map'), width=12)
    ),
        # dbc.Row(
        # [
        #     dbc.Col(html.Div(html.H1("IPv4 Allocation Data")), width='4'),
        #     dbc.Col(html.Div(dbc.DropdownMenu(
        #             id='scale-selector',
        #             children=[
        #                 dbc.DropdownMenuItem("Item 1"),
        #                 dbc.DropdownMenuItem("Item 2"),
        #             ],
        #             label='log',
        #         )), width='4',
        #     ),
        # ],
        # ),
    # dbc.Row(
    #     dbc.Col(dcc.Graph(id='the-choropleth-map'))
    # ),

    # html.H1("JSON Data in AgGrid", style={'textAlign': 'center'}),
    # html.Div(
    #     dag.AgGrid(
    #         id='json-data-grid',
    #         columnDefs=column_defs,
    #         rowData=transformed_data,  # Use the transformed data
    #         style={'height': '600px', 'width': '80%'},  # Adjust the size as needed
    #         className='ag-theme-balham',  # Theme
    #     ),
    #     style={'display': 'flex', 'justifyContent': 'center'}
    # ),
    # html.H1("Netlist Data in Ag-Grid", style={'textAlign': 'center'}),
    # html.Div(
    #     dag.AgGrid(
    #         id='netlist-grid',
    #         columnDefs=[{"headerName": col, "field": col} for col in netlist_data_frame.columns],
    #         rowData=netlist_data_frame.to_dict('records'),
    #         style={'height': '600px', 'width': '80%'},
    #     ),
    #     style={'display': 'flex', 'justifyContent': 'center'}
    # ), 
],className='container-fluid')

if __name__ == '__main__':
    app.run_server(debug=True)
