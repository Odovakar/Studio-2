from dash import Dash, html, dcc, Input, Output, State
#import dash_ag_grid as dag
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

    json_df = pd.DataFrame(transformed_data)
    json_df['ipv4'] = pd.to_numeric(json_df['ipv4'], errors='coerce')
    json_df['pop'] = pd.to_numeric(json_df['pop'], errors='coerce')
    json_df = json_df[(json_df['pop'] > 800) & (json_df['name'] != 'World')]
    json_df['ipv4_grouping'] = json_df['ipv4'].apply(assign_ipv4_grouping)
    json_df['log_ipv4'] = np.log10(json_df['ipv4'] + 1)
    json_df['marker_size'] = json_df['log_ipv4'].apply(assign_marker_size)

    if transformed_data:
        column_defs = [{'field': col, 'sortable': True, 'filter': True} for col in transformed_data[0].keys()]
    else:
        column_defs = []

    return transformed_data, column_defs, json_df

def assign_marker_size(log_value):
    # Define size values for each log interval
    size_mapping = {0: 1, 1: 10, 2: 15, 3: 30, 4: 60, 5: 120, 6: 240, 7: 480, 8: 960, 9: 960*2}
    log_interval = int(np.floor(log_value))
    # Assign size based on the log interval
    return size_mapping.get(log_interval, 55)  # Default to the largest size

# JSON ip_alloca data processing calls to data_processing folder script
json_raw_data_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json'
transformed_data, column_defs, json_df = fetch_and_transform_json_data(json_raw_data_url)
# Convert ISO Alpha-2 codes to ISO Alpha-3 codes
json_df['iso_alpha_3'] = json_df['country_code'].apply(alpha2_to_alpha3)
#print("json_df columns:", json_df.columns.tolist())

#print(json_df.head())
#usa_row_by_iso_alpha_3 = json_df.loc[json_df['iso_alpha_3'] == 'USA']
#print(usa_row_by_iso_alpha_3)

# After creating json_df from the JSON data

#print(json_df['iso_alpha_3'].unique())

customdata = np.stack((
    json_df['name'],          # Country name
    json_df['ipv4'],          # IPv4 address count
    json_df['pop'],           # Population size
    json_df['percentv4'],     # Percent of IPv4 pool
    json_df['pcv4'],          # IPv4 per capita percentage
    json_df['log_ipv4']       # Log of IPv4 for the logarithmic map
), axis=-1)

# App Initialisation
app = Dash(__name__, external_stylesheets=external_stylesheets)

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

hover_template='<b>%{customdata[0]}</b><br>' + \
                'IPv4: %{customdata[1]:,.0f}<br>' + \
                'Population: %{customdata[2]:,.0f}<br>' + \
                'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                '<extra>Log IPv4: %{customdata[5]:.2f}</extra>'

'''Scatter Plot Figure'''
# Instiantiating the scatter figure object
@app.callback(
    Output('the-scatter-plot', 'figure'),
    [Input('scale-selector', 'value')]
)
def update_scatter_plot(scale_type):
    if scale_type=='grouped':
        colors=get_colorscale(scale_type)
        scatter_fig = px.scatter(
            data_frame=json_df,
            x='pop',
            y='ipv4_grouping',
            color='ipv4_grouping',
            color_discrete_map=colors,
            hover_name="name",
            size_max=150,
            size='marker_size',  # Use the new marker sizes
            hover_data={
                'name':True,
                'ipv4': True,
                'pop': True,
                'percentv4': ':.2f',
                'pcv4': ':.2f',
                'iso_alpha_3': False,
                'ipv4_grouping': False,
                'log_ipv4': False,
            },
            category_orders={"ipv4_grouping": ["0-10k", "10k-100k", "100k-1M", "1M-10M", "10M-100M", "100M-1B", "1B+"]}
        )
        scatter_fig.update_layout(
            legend=dict(
                title="IPv4 Groups",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.25,
                yanchor="bottom",
                itemsizing="constant"
            ),
            margin={"r":20, "t":20, "l":20, "b":10}
        )
        scatter_fig.update_xaxes(type='log', title_text='Population Size (Log Scale)')
        scatter_fig.update_yaxes(type='category', title_text='Number of IPv4 Addresses (Log Scale)')
        desired_max_marker_size = 2000
        sizeref = max(json_df['marker_size']) / (desired_max_marker_size)
        scatter_fig.update_traces(
            marker=dict(sizemode='area', sizeref=sizeref, sizemin=5),
            hovertemplate=hover_template,
            customdata=customdata
        )
    elif scale_type=='log':
        scatter_fig = px.scatter(
            data_frame=json_df,
            x='pop',
            y='ipv4',
            color='log_ipv4',
            color_continuous_scale=px.colors.sequential.Viridis,
            hover_name="name",
            size_max=150,
            size='marker_size',  # Use the new marker sizes
            hover_data={
                'name':True,
                'ipv4': True,
                'pop': True,
                'percentv4': ':.2f',
                'pcv4': ':.2f',
                'iso_alpha_3': False,
                'ipv4_grouping': False,
                'log_ipv4': False,
            }
        )
        scatter_fig.update_layout(
                    coloraxis_colorbar=dict(
                        title="Log IPv4",
                        orientation="h",
                        x=0.5,
                        xanchor="center",
                        y=-0.3,
                        yanchor="bottom",
                        thicknessmode="pixels",
                        thickness=20,
                        len=0.8  # Adjusts the length of the colorbar to 80% of the axis length
                    ),
                    margin={"r":20, "t":20, "l":20, "b":20}
                )
        scatter_fig.update_xaxes(type='log', title_text='Population Size (Log Scale)')
        scatter_fig.update_yaxes(type='log', title_text='Number of IPv4 Addresses (Log Scale)')
        desired_max_marker_size = 2000
        sizeref = max(json_df['marker_size']) / (desired_max_marker_size)
        scatter_fig.update_traces(
            marker=dict(sizemode='area', sizeref=sizeref, sizemin=5),
            hovertemplate=hover_template,
            customdata=customdata
        )
    return scatter_fig

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
                options=[
                    {'label': 'Logarithmic Scale', 'value': 'log'},
                    {'label': 'Grouped Scale', 'value': 'grouped'}
                ],
                value='log',
                clearable=False,
            ), width=4, className='justify-content-end'),
        ],
        className='align-items-center',  # Vertically align the columns if they wrap on smaller screens
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id='the-scatter-plot'), width=12)  # This displays the scatter plot
    ]),
], className='container-fluid')

if __name__ == '__main__':
    app.run_server(debug=True)
