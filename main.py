import dash
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from classes.data_handler import DataHandler
from classes.pie_chart_handler import PieChartHandler
from classes.ag_grid_handler import AgGridHandler
from classes.scatter_plot_handler import ScatterHandler
from classes.choropleth_map_handler import ChoroplethHandler
from classes.hover_template_handler import HoverTemplateHandler
from classes.time_series_handler import TimeSeriesHandler
from classes.dynamic_card_handler import DynamicCardHandler


roboto_font_url = "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"
external_stylesheets = [dbc.themes.BOOTSTRAP, roboto_font_url]

# Initialising DataHandler
data_handler = DataHandler(
    json_url='https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json',
    whois_v4_pop_csv='whois_v4_pop.csv',
    population_csv='wpopdata.csv'
)

data_handler.fetch_json_data()
data_handler.fetch_whois_ipv4_data()


# Instantiating Handlers
hover_template_handler = HoverTemplateHandler(data_handler)
pie_chart_handler = PieChartHandler(data_handler, hover_template_handler)
ag_grid_handler = AgGridHandler(data_handler)
scatter_plot_handler = ScatterHandler(data_handler)
choropleth_map_handler = ChoroplethHandler(data_handler, hover_template_handler)
time_series_handler = TimeSeriesHandler(data_handler)
dynamic_card_handler = DynamicCardHandler(data_handler)

# Prepping data for the ag_grid
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

'''----------Fetch and store dataset----------'''
# This logic will fetch and prep the data for use in the application
@app.callback(
    Output('active-dataset', 'data'),
    [Input('ipv4', 'n_clicks'), Input('whoisv6', 'n_clicks'), Input('whoisv4', 'n_clicks')],
    [State('active-dataset', 'data')]
)
def update_dataset(n_ipv4, n_whoisv6, n_whoisv4, data):
    ctx = callback_context # Used to determine which button has been clicked

    if not ctx.triggered: # ctx.triggered(list) keeps track of all button clicks
        if data is None or 'dataset' not in data: # Returns the standard dataset
            return {'dataset': 'ipv4','data': data_handler.whois_ipv4_df.to_json(date_format='iso', orient='split')}
    
    # fetches the first input in the list where the prop(btn) that was clicked is stored.
    # the input in the list will be ipv4.n_clicks, it's then split at the dot and,
    # the button_id variable will now hold either ipv4 or whoisv6/4
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Data fetched and converted for compatability with dcc.Store.
    # The dict contains the dictionary data, as well as an entry denoting which dataset it is,
    # for the update_graphs function, which needs to know which dataset is active
    # to be able to choose which case to display.
    if button_id == "ipv4":
        data_handler.fetch_json_data()
        return {'dataset': 'ipv4','data': data_handler.json_df.to_json(date_format='iso', orient='split')}
    elif button_id == "whoisv6":
        return None
        data_handler.fetch_whoisv6_data()
        return {'dataset': 'whoisv6','data': data_handler.whoisv6_df.to_json(date_format='iso', orient='split')}
    elif button_id == "whoisv4":
        data_handler.fetch_whois_ipv4_data()
        return {'dataset': 'whoisv4','data': data_handler.whois_ipv4_df.to_json(date_format='iso', orient='split')}

'''----------Choropleth Map Stuff----------'''
@app.callback(
        Output('the-choropleth-map', 'figure'),
        [Input('active-dataset', 'data'), Input('graph-tabs', 'value'), Input('color-scale-dropdown', 'value')],
)
def update_choropleth_map(active_dataset, active_tab, color_scale_dropdown):
    if not active_dataset or 'dataset' not in active_dataset or active_tab != 'choropleth-tab':
        raise dash.exceptions.PreventUpdate
    
    return choropleth_map_handler.generate_figure(color_scale_dropdown)

'''----------AG Grid Stuff----------'''
@app.callback(
    [Output('the-ag-grid', 'rowData'), Output('the-ag-grid', 'columnDefs')],
    Input('active-dataset', 'data')
)
def update_columns(active_dataset):
    if not active_dataset or 'data' not in active_dataset:
        return [], []

    dataset = active_dataset['dataset']
    data = active_dataset['data']
    row_data = []
    column_defs = []

    if dataset == 'ipv4':
        row_data = ag_grid_handler.format_json_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('json')
    elif dataset == 'whoisv6':
        row_data = ag_grid_handler.format_whois6_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('whoisv6')
    elif dataset == 'whoisv4':
        row_data = ag_grid_handler.format_whois4_data_for_aggrid()
        column_defs = ag_grid_handler.generate_column_definitions('whoisv4')
    return row_data, column_defs

'''----------UI Element Logic----------'''
# This function will display information related to the graph that's currently on display in the graph tab.
# Same logic, different output-card.
@app.callback(
    Output('dynamic-card-content', 'children'),
    [Input('active-dataset', 'data'), Input('graph-tabs', 'value')],
    prevent_initial_call=True
)
def update_dynamic_card_content(active_dataset, active_tab):
    return dynamic_card_handler.get_content(active_dataset, active_tab)

# This handles the button outline based on which button is pressed and not.
@app.callback(
    [Output('ipv4', 'className'),
     Output('whoisv6', 'className'),
     Output('whoisv4', 'className')],
    [Input('ipv4', 'n_clicks'),
     Input('whoisv6', 'n_clicks'),
     Input('whoisv4', 'n_clicks')],
    prevent_initial_call=True
)
def update_button_styles(n_ipv4, n_whoisv6, n_whoisv4):
    ctx = callback_context
    if not ctx.triggered:
        # When the app loads, set the initial style
        return ["btn-primary", "btn-outline-primary", "btn-outline-primary"]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "ipv4":
            return ["btn-primary", "btn-outline-primary", "btn-outline-primary"]
        elif button_id == "whoisv6":
            return ["btn-outline-primary", "btn-primary", "btn-outline-primary"]
        elif button_id == "whoisv4":
            return ["btn-outline-primary", "btn-outline-primary", "btn-primary"]

'''----------Render the application----------'''    
# App Layout
app.layout = html.Div([
    dcc.Store(id='active-dataset', storage_type='memory'),
    dbc.Row([ # SECTION 1
        dbc.Col([  # Column for left-aligned heading
            html.H3('Internet Protocol Allocation Visualisation Model'),
        ], style={'display': 'flex', 'align-items': 'center'}, width={'size': 7, 'offset': 1}),  # Center heading vertically
        dbc.Col([  # Column for right-aligned buttons
            dbc.ButtonGroup(
                [
                    dbc.Button("IPv4 Pool Data", id="ipv4", outline=True, className="btn-primary", n_clicks=0),
                    dbc.Button("WHOIS v6", id="whoisv6", outline=True, className="btn-outline-primary", n_clicks=0),
                    dbc.Button("WHOIS v4", id="whoisv4", outline=True, className="btn-outline-primary", n_clicks=0),
                ],
                className="mb-3",
            ),
            
        ], className='d-flex justify-content-end align-items-center', width={'size': 3}),  # Align buttons & center vertically
        dbc.Col([], width={'size': 1}) # Filler to take up 1/12
    ], style={'height': '5%'}),
    dbc.Row([ # SECTION 2
        dbc.Col([
            dbc.Card(id='dynamic-card-content', class_name='card', style={'padding': '20px'}),
        ], width={'size': 2, 'offset': 1}),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Tabs(
                        id='graph-tabs',
                        value='choropleth-tab',
                        children=[
                            dcc.Tab(label='Choropleth Map',value='choropleth-tab',children=[dcc.Graph(id='the-choropleth-map')]),
                            dcc.Tab(label='Scatter Plot',value='scatter-tab',children=[dcc.Graph(id='the-scatter-plot')]),
                            dcc.Tab(label='Pie Chart', value='pie-tab',children=[dcc.Graph(id='the-pie-chart')]),
                            dcc.Tab(label='Bar Chart',value='bar-tab',children=[dcc.Graph(id='the-bar-chart')]),
                            dcc.Tab(label='Custom Graph',value='custom-tab',children=[dcc.Graph(id='the-custom-chart')]),
                    ], className='col-sm-12') # Classname sets tab width
                ], style={'height': '95%'})
            ], class_name='card'),
        ], width={'size': 8}),
        dbc.Col([], width={'size':1})
    ], style={'height': '55%'}),
    dbc.Row([ # SECTION 3
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
                ], class_name='bottom-card'),
        ], width={'size': 10, 'offset': 1}),
    ], style={'height': '40%'}),
], style={'height': '98vh', 'width': '100%'})

if __name__ == '__main__':
    app.run_server(debug=True)