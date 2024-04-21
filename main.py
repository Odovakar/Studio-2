import dash
from dash import Dash, html, dcc, Input, Output, State, callback_context
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
data_handler.fetch_whois_ipv4_data()


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
# @app.callback(
#     [Output('the-ag-grid', 'rowData'), Output('the-ag-grid', 'columnDefs')],
#     [Input("ipv4", "n_clicks"), Input("ipv6", "n_clicks"), Input("whoisv4", "n_clicks")]
# )
# def update_columns(ipv4_clicks, ipv6_clicks, whois_clicks):
#     ctx = dash.callback_context
    
#     # Default action is to set to 'ipv4', assuming it's the default or fallback scenario
#     if not ctx.triggered:
#         button_id = 'ipv4'  # Default to 'ipv4' if nothing has been clicked yet
#     else:
#         button_id = ctx.triggered[0]['prop_id'].split('.')[0]

#     row_data = []
#     column_defs = []

#     if button_id == 'ipv4':
#         row_data = ag_grid_handler.format_json_data_for_aggrid()
#         column_defs = ag_grid_handler.generate_column_definitions('json')
#     elif button_id == 'ipv6':
#         # Define how to handle IPv6 data update if necessary
#         pass
#     elif button_id == 'whoisv4':
#         row_data = ag_grid_handler.format_whois4_data_for_aggrid()
#         column_defs = ag_grid_handler.generate_column_definitions('whoisv4')

#     return row_data, column_defs


@app.callback(
    Output('the-animated-scatter-plot', 'figure'),
    Input('selected_value', 'value') 
)
def update_animated_scatter_plot(selected_value):
    return time_series_handler.generate_figure(selected_value)


@app.callback(
    [
        Output("ipv4", "className"),
        Output("ipv6", "className"),
        Output("whoisv4", "className"),
        Output('the-ag-grid', 'rowData'),
        Output('the-ag-grid', 'columnDefs')
    ],
    [
        Input("ipv4", "n_clicks"),
        Input("ipv6", "n_clicks"),
        Input("whoisv4", "n_clicks")
    ]
)
def update_content_and_styles(ipv4_clicks, ipv6_clicks, whoisv4_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'ipv4'
    
    # Default button styles
    styles = {
        "ipv4": "btn-outline-primary",
        "ipv6": "btn-outline-primary",
        "whoisv4": "btn-outline-primary"
    }

    # Update the style for the triggered button
    if triggered_id in styles:
        styles[triggered_id] = "btn-primary"

    # Update data based on the button pressed
    row_data, column_defs = [], []
    if triggered_id == 'ipv4':
        row_data = ag_grid_handler.format_json_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('json')
    elif triggered_id == 'ipv6':
        # You need to define how to handle IPv6 data update if necessary
        pass
    elif triggered_id == 'whoisv4':
        row_data = ag_grid_handler.format_whois4_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('whoisv4')
    
    return styles["ipv4"], styles["ipv6"], styles["whoisv4"], row_data, column_defs

@app.callback(
    Output('dynamic-card-content', 'children'),
    Input('tabs-example', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dbc.Col(dcc.Dropdown(
                id='scale-selector',
                options=[ # TODO: Fix log scale for the pie chart since everything is squashed.
                    {'label': 'Normal Visualisation', 'value': 'normal'},
                    {'label': 'Logarithmic Visualisation', 'value': 'log'}
                ],
                value='log',
                clearable=False,
            )),
        ])
    elif tab == 'tab-2':
        return html.Div([
            dbc.Col(dcc.Dropdown(
                id='scale-selector',
                options=[ # TODO: Fix log scale for the pie chart since everything is squashed.
                    {'label': 'Normal Visualisation', 'value': 'normal'},
                    {'label': 'Logarithmic Visualisation', 'value': 'log'}
                ],
                value='log',
                clearable=False,
            )),
        ])
    elif tab == 'tab-3':
        return html.Div([
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
        ])
    else:
        return html.Div("Select a tab")  # Default message or content

'''----------Render the application----------'''    
# App Layout
app.layout = html.Div([
    dbc.Row([
        dbc.Col([  # Column for left-aligned heading
            html.H3('Internet Protocol Allocation Visualisation Model'),
        ], style={'display': 'flex', 'align-items': 'center'}, width={'size': 7, 'offset': 1}),  # Center heading vertically
        dbc.Col([  # Column for right-aligned buttons
            dbc.ButtonGroup(
                [
                    dbc.Button("IPv4 Pool Data", id="ipv4", outline=True, className="btn-primary", n_clicks=0),
                    dbc.Button("WHOIS v6", id="ipv6", outline=True, className="btn-outline-primary", n_clicks=0),
                    dbc.Button("WHOIS v4", id="whoisv4", outline=True, className="btn-outline-primary", n_clicks=0),
                ],
                className="mb-3",
            )
        ], className='d-flex justify-content-end align-items-center', width={'size': 3}),  # Align buttons & center vertically
        dbc.Col([], width={'size': 1})
    ], style={'height': '10%', 'display': 'flex', 'flex-direction': 'row'}),
    dbc.Row([
        dbc.Col([
            dbc.Card(id='dynamic-card-content', style={'padding': '10px', 'height': '97%', 'background-color': '#f2f2f2'}),
        ], width={'size': 2, 'offset': 1}),
        dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Tabs(id='tabs-example', children=[
                    dcc.Tab(label='Choropleth Map', children=[
                        dcc.Graph(id='the-choropleth-map')
                    ]),
                    dcc.Tab(label='Scatter Plot', children=[
                        dcc.Graph(id='the-scatter-plot')
                    ]),
                    dcc.Tab(label='Pie Figure', children=[
                        dcc.Graph(id='the-pie-figure')
                    ]),
                ])
            ])
        ], style={'marginBottom': 20, 'height': '55%'}),
        ], style={'height': '100%'}),
        dbc.Col([], width={'size':1})
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                    dbc.CardBody([
                        dag.AgGrid(
                            id='the-ag-grid',
                            rowData=[],
                            columnDefs=[],
                            className='ag-theme-balham',
                            dashGridOptions={'pagination': True, 'paginationAutoPageSize': True},
                            defaultColDef={
                                'flex': 1,
                                'minWidth': 100,
                            },
                            style={'height': '100%', 'width': '100%'},
                        )
                    ])
                ], style={'height': '40%'}),
        ], width={'size': 10, 'offset': 1}),
    ], style={'height': '90%'}),
], className='container-fluid', style={'height': '100vh', 'width': '100%'})

if __name__ == '__main__':
    app.run_server(debug=True)
