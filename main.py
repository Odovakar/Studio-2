from dash import Dash, html, dcc, Input, Output, State
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.express as px

from classes.data_handler import DataHandler
from classes.pie_chart_handler import PieChartHandler
from classes.ag_grid_handler import AgGridHandler
from classes.scatter_plot_handler import ScatterHandler
from classes.choropleth_map_handler import ChoroplethHandler
from classes.hover_template_handler import HoverTemplateHandler
from classes.time_series_handler import TimeSeriesHandler

roboto_font_url = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"

external_stylesheets = [dbc.themes.BOOTSTRAP, roboto_font_url]

# Initialising DataHandler
data_handler = DataHandler(
    json_url='https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json',
    whois_v4_pop_csv='whois_v4_pop.csv',
    population_csv='wpopdata.csv'
)

# Fething the dataframes from the DataHandler class
data_handler.fetch_json_data()
#data_handler.fetch_netlist_data()
#data_handler.fetch_whois_ipv4_data()


# Instantiating Handlers
hover_template_handler = HoverTemplateHandler(data_handler)
pie_chart_handler = PieChartHandler(data_handler, hover_template_handler)
ag_grid_handler = AgGridHandler(data_handler)
scatter_plot_handler = ScatterHandler(data_handler)
choropleth_map_handler = ChoroplethHandler(data_handler, hover_template_handler)
time_series_handler = TimeSeriesHandler(data_handler)




#data_handler = DataHandler(json_url, netlist_url, whois_ipv4_url)
data_handler.fetch_json_data()  # Populates json_df
data_handler.enhance_dataframe(data_handler.json_df)  # Adds necessary columns
ag_grid_data = ag_grid_handler.format_json_data_for_aggrid()


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


# App Initialisation
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


'''----------Choropleth Map----------'''
@app.callback(
    Output('the-choropleth-map', 'figure'),
    [Input('scale-selector', 'value')]
)
def update_map(scale_type):
    return choropleth_map_handler.generate_figure(scale_type)

'''----------Scatter Plot Figure----------'''
@app.callback(
    Output('the-scatter-plot', 'figure'),
    [Input('scale-selector', 'value')]
)
def update_scatter_plot(scale_type):
    return scatter_plot_handler.generate_figure(scale_type)

'''----------Pie Chart----------'''
@app.callback(
    Output('the-pie-figure', 'figure'),
    [Input('pie-selector', 'value'), Input('dataset_selector', 'value'), Input('toggle-legend-button', 'n_clicks')]
)
def update_pie_figure(selected_value, dataset_selector, n_clicks):
    show_legend = n_clicks % 2 == 1
    opacity = 0.5 if show_legend else 1.0
    return pie_chart_handler.generate_figure(dataset_selector, selected_value, show_legend, opacity)

'''----------AG Grid----------'''
@app.callback(
    [Output('the-ag-grid', 'rowData'), Output('the-ag-grid', 'columnDefs')],
    Input('dataset_selector', 'value')
)
def update_columns(selected_value):
    row_data = []
    column_defs = []
    
    if selected_value == 'IPv4':
        row_data = ag_grid_handler.format_json_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('json')
    elif selected_value == 'netlist':
        row_data = ag_grid_handler.format_netlist_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('netlist')
    elif selected_value == 'WHOIS':
        row_data = ag_grid_handler.format_whois4_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('WHOIS')
    #print(f"Row data: {row_data[:5]}")
    #print(f"Column defs: {column_defs}")
    #print(f"Selected dataset: {selected_value}, Row Data: {row_data}")
    return row_data, column_defs

@app.callback(
    Output('the-animated-scatter-plot', 'figure'),
    Input('selected_value', 'value') 
)
def update_animated_scatter_plot(selected_value):
    return time_series_handler.generate_figure(selected_value)


@app.callback(
    Output('graph-container', 'children'),
    Input('figure-selector', 'value')
)
def update_graph_display(selected_graph):
    if selected_graph == 'choropleth-map':
        return dbc.Col(dcc.Graph(id='the-choropleth-map'), width=12)
    elif selected_graph == 'scatter-plot':
        return dbc.Col(dcc.Graph(id='the-scatter-plot'), width=12)

'''----------Render the application----------'''    
# App Layout
app.layout = html.Div([
    dbc.Row(
    [
        dbc.Col(dcc.Dropdown(
            id='figure-selector',
            options=[ # TODO: Fix log scale for the pie chart since everything is squashed.
                {'label': 'Choropleth Map', 'value': 'choropleth-map'},
                {'label': 'Scatter Plot', 'value': 'scatter-plot'}
            ],
            value='choropleth-map',
            clearable=False,
        ), width={'size': 3, 'offset': 1}, className='justify-content-end'),
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
        ), width=3, className='justify-content-end'),
    ],
    className='align-items-center',  # Vertically align the columns if they wrap on smaller screens
    ),
    dbc.Row( 
        dbc.Col(html.Div(id='graph-container'), width=12)
    ),
    dbc.Row([
    dbc.Col([
        dcc.Dropdown(
            id='dataset_selector',
            options=[
                {'label': html.Div('IPv4', style={'padding-left': 3}), 'value': 'IPv4'},
                {'label': html.Div('IPv6', style={'padding-left': 3}), 'value': 'IPv6'},
                {'label': html.Div('WHOIS', style={'padding-left': 3}), 'value': 'WHOIS'}
            ],
            value='IPv4',  # Default value
            #labelStyle={'display': 'inline-flex', 'margin-right': '5px'},
        )
    ], width={'size': 4, 'offset': 1}, className='center'),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='pie-selector',
                options=[
                    {'label': html.Div('Total Pool', style={'padding-left': 3}), 'value': 'TotalPool'},
                    {'label': html.Div('RIR', style={'padding-left': 3}), 'value': 'RIR'},
                    {'label': html.Div('ARIN', style={'padding-left': 3}), 'value': 'ARIN'},
                    {'label': html.Div('APNIC', style={'padding-left': 3}), 'value': 'APNIC'},
                    {'label': html.Div('RIPE NCC', style={'padding-left': 3}), 'value': 'RIPENCC'},
                    {'label': html.Div('LACNIC', style={'padding-left': 3}), 'value': 'LACNIC'},
                    {'label': html.Div('AFRINIC', style={'padding-left': 3}), 'value': 'AFRINIC'}
                ],
                value='TotalPool',  # Default value
                labelStyle={'display': 'inline-flex', 'margin-right': '5px'},
            )
        ], width={'size': 8, 'offset': 1}, align='center'),
        dbc.Col([
            dbc.Button('Toggle Legend', id='toggle-legend-button', color='primary', n_clicks=0)
        ], width=3, align='center')  # Adjust width and alignment as needed
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='the-pie-figure'), width=12)
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
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='selected_value',
                options=[
                    {'label': 'RIR', 'value': 'rir'},
                    {'label': 'Global', 'value': 'global'},
                    ],
                value='rir',
            )
        ]),
    ]),
    dbc.Row([
    dbc.Col([
        dcc.Graph(id='the-animated-scatter-plot')
    ])
    ])

], className='container-fluid')

if __name__ == '__main__':
    app.run_server(debug=True)
