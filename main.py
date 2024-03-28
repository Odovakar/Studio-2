from dash import Dash, html, dcc, Input, Output, State
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import requests

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

# App Initialisation
app = Dash(__name__)

@app.callback(
    Output('the-choropleth-map', 'figure'),
    [Input('scale-selector', 'value')]
)
def update_map(scale_type):
    # Creating a template for the hoverlabel
    hover_template = '<b>%{customdata[1]}</b><br>' + \
                     'IPv4: %{customdata[0]:,.0f}<br>' + \
                     '<extra>Log IPv4: %{customdata[2]:.2f}</extra>'
    
    custom_color_sequence = [
        # Using more distinct colors to improve distinguishability
        "rgb(233, 30, 99)",   # Pink
        "rgb(76, 175, 80)",   # Green
        "rgb(33, 150, 243)",  # Blue
        "rgb(255, 235, 59)",  # Yellow
        "rgb(156, 39, 176)",  # Purple
        "rgb(255, 87, 34)",   # Deep Orange
        "rgb(0, 188, 212)",   # Cyan
        "rgb(96, 125, 139)",  # Blue Grey
        "rgb(255, 152, 0)"    # Orange
    ]


    if scale_type == 'log':
        color = json_df['log_ipv4']
        map_fig = px.choropleth(
            data_frame=json_df,
            locations='name',
            locationmode='country names',
            color=color,
            color_continuous_scale='viridis',
            range_color=(0, json_df['log_ipv4'].max()),
            projection='equirectangular',
            hover_name=json_df['name'],
            hover_data={'ipv4': True}
        )
    else:  # Custom Scale
        bins = [0, 1, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 9999999999]
        labels = ['0', '1-999', '1000-9999', '10000-99999', '100000-999999', 
                  '1000000-9999999', '10000000-99999999', '100000000-999999999', '1000000000-9999999999']
        json_df['ipv4_group'] = pd.cut(json_df['ipv4'], bins=bins, labels=labels, right=False)
        map_fig = px.choropleth(
            data_frame=json_df,
            locations='name',
            locationmode='country names',
            color='ipv4_group',
            category_orders={"ipv4_group": labels},
            color_discrete_sequence=custom_color_sequence,
            projection='equirectangular',
            hover_name=json_df['name'],
            hover_data={'ipv4': True}
        )

    # Configuration shared by both types of scales
    map_fig.update_geos(showframe=False, lonaxis_range=[-180, 180], lataxis_range=[-60, 90])
    map_fig.update_layout(dragmode=False, hoverlabel=dict(bgcolor='white', font_size=16))

    map_fig.update_layout(
        dragmode=False, # Make the map non-draggable
        coloraxis_colorbar=dict( # This controls the attributes of the legend/colorbar
            title='IPv4',
            len=0.7,
            nticks=10
        ),
        autosize=True, # Some trickery to make the autoscaling actually work
        margin=dict( # --"--
            l=0,
            r=0,
            b=0,
            t=0,
            pad=4,
            autoexpand=True
        ),
        hoverlabel=dict( # Label styling
            bgcolor='white',
            font_size=16,
        )
    )

    map_fig.update_traces(
    hovertemplate=hover_template,
    customdata=np.stack((json_df['ipv4'], json_df['name'], json_df['log_ipv4']), axis=-1)
    )   
    return map_fig

# Instantiating & Configuring Scatter Object
scatter_fig = px.scatter(
    data_frame=json_df,
    x='pop',
    y='ipv4',
    color='country_code',
    hover_name="name",
    size_max=60,
    title='Population Size vs. Number of IPv4 Addresses by Country',
    labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
    size="ipv4"  # Using population for the bubble size
)

# Adjusting the axes to a log scale for better visibility in case of wide range
scatter_fig.update_xaxes(type='log', title_text='Population Size (Log Scale)')
scatter_fig.update_yaxes(type='log', title_text='Number of IPv4 Addresses (Log Scale)')
#scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=2.*max(json_df['ipv4'])/(40.**2), sizemin=4))
max_ipv4 = json_df['ipv4'].max()
desired_max_marker_size = 100
# Calculate sizeref for the 'ipv4' values
sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 2)
scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=sizeref, sizemin=4))

scale_selector = dcc.Dropdown(
    id='scale-selector',
    options=[
        {'label': 'Logarithmic Scale', 'value': 'log'},
        {'label': 'Custom Scale', 'value': 'custom'}
    ],
    value='log', 
    style={'width': '50%', 'padding': '20px', 'minWidth': '300px'}
)

# App Layout
app.layout=html.Div([
    dbc.Row(dbc.Col(scale_selector, width={'size': 4, 'offset': 4})),
    dbc.Row(dbc.Col(html.H1("IPv4 Allocation Data", style={'textAlign': 'center'}), width=12)),
    dbc.Row([
        dbc.Col(dcc.Graph(id='the-choropleth-map'), width=12),  # This will display the choropleth map
        dbc.Col(dcc.Graph(id='the-scatter-plot', figure=scatter_fig), width=12)  # This displays the scatter plot
    ]),
    html.H1("JSON Data in AgGrid", style={'textAlign': 'center'}),
    html.Div(
        dag.AgGrid(
            id='json-data-grid',
            columnDefs=column_defs,
            rowData=transformed_data,  # Use the transformed data
            style={'height': '600px', 'width': '80%'},  # Adjust the size as needed
            className='ag-theme-balham',  # Theme
        ),
        style={'display': 'flex', 'justifyContent': 'center'}
    ),
    html.H1("Netlist Data in Ag-Grid", style={'textAlign': 'center'}),
    html.Div(
        dag.AgGrid(
            id='netlist-grid',
            columnDefs=[{"headerName": col, "field": col} for col in netlist_data_frame.columns],
            rowData=netlist_data_frame.to_dict('records'),
            style={'height': '600px', 'width': '80%'},
        ),
        style={'display': 'flex', 'justifyContent': 'center'}
    ), 
])

if __name__ == '__main__':
    app.run_server(debug=True)
