import dash
from dash import Dash, html, dcc, Input, Output, State, callback_context, clientside_callback, Patch
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template
import json

from classes.data_handler import DataHandler
from classes.pie_chart_handler import PieChartHandler
from classes.ag_grid_handler import AgGridHandler
from classes.scatter_plot_handler import ScatterHandler
from classes.choropleth_map_handler import ChoroplethHandler
from classes.hover_template_handler import HoverTemplateHandler
from classes.dynamic_card_handler import DynamicCardHandler
from classes.bar_chart_handler import BarChartHandler

load_figure_template(['bootstrap', 'bootstrap_dark'])
dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'
roboto_font_url = 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap'
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.FONT_AWESOME,
    roboto_font_url,
    dbc_css
]

# Initialising DataHandler
data_handler = DataHandler(
    json_url='https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json',
    whois_v4_pop_csv='whois_v4_pop.csv',
    population_csv='wpopdata.csv'
)

data_handler.fetch_json_data()
data_handler.fetch_whois_ipv4_data()
data_handler.create_time_series_df()

# Instantiating Handlers
hover_template_handler = HoverTemplateHandler(data_handler)
pie_chart_handler = PieChartHandler(data_handler, hover_template_handler)
ag_grid_handler = AgGridHandler(data_handler)
scatter_plot_handler = ScatterHandler(data_handler)
choropleth_map_handler = ChoroplethHandler(data_handler, hover_template_handler)
dynamic_card_handler = DynamicCardHandler(data_handler)
bar_chart_handler = BarChartHandler(data_handler)

# Prepping data for the ag_grid
ag_grid_data = ag_grid_handler.format_json_data_for_aggrid()

'''stuff for bug squashing'''
#print('json_df columns:', json_df.columns.tolist())
#print(json_df.head())
#usa_row_by_iso_alpha_3 = json_df.loc[json_df['iso_alpha_3'] == 'USA']
#print(usa_row_by_iso_alpha_3)
#print(json_df['iso_alpha_3'].unique())
#unknown_rir_orig = json_df.loc[json_df['RIR'] == 'Unknown']
#print('Original DataFrame with Unknown RIR:')
#print(unknown_rir_orig[['country_code','iso_alpha_3', 'name', 'RIR']])
#print(json_df['percentv4'].dtype)


# App Initialisation
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

'''----------Fetch and store dataset----------'''
@app.callback(
    Output('ipv4-time-series-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    State('ipv4-time-series-dataset', 'data')
)
def update_ipv4_time_series_dataset(n_whoisv4, data):
    ctx = dash.callback_context
    if not ctx.triggered:
        if data is None or 'dataset' not in data:
            data_handler.create_time_series_df()
            ipv4_ts_df = {
                'dataset': 'ipv4_time_series',
                'data': data_handler.ipv4_ts_df.to_json(date_format='iso', orient='split')
            }
            #print(ipv4_ts_df.get('dataset'), 'time series worked as well')
            return ipv4_ts_df

@app.callback(
    Output('whois-ipv4-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    State('whois-ipv4-dataset', 'data')
)
def update_ipv4_dataset(n_whoisv4, data):
    ctx = callback_context
    if not ctx.triggered:
        if data is None or 'dataset' not in data:
            data_handler.fetch_whois_ipv4_data()
            whois_ipv4_dataset = {'dataset': 'whois_ipv4', 'data': data_handler.whois_ipv4_df.to_json(date_format='iso', orient='split')}
            #print(whois_ipv4_dataset.get('dataset'), 'successfully populated')
            return whois_ipv4_dataset

@app.callback(
    Output('ipv4-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    State('ipv4-dataset', 'data')
)
def update_ipv4_dataset(n_whoisv4, data):
    ctx = callback_context
    if not ctx.triggered:
        if data is None or 'dataset' not in data:
            data_handler.fetch_json_data()
            ipv4_dataset = {'dataset': 'ipv4', 'data': data_handler.json_df.to_json(date_format='iso', orient='split')}
            #print(ipv4_dataset.get('dataset'), 'successfully populated')
            return ipv4_dataset

@app.callback(
    Output('ipv6-dataset', 'data'),
    [Input('whoisv6', 'n_clicks')],
    [State('ipv6-dataset', 'data')],
    prevent_initial_call=True
)
def update_ipv6_dataset(n_whoisv6, ipv6_data):
    if not ipv6_data:
        ipv6_data = data_handler.fetch_whoisv6_data()  # Your method to fetch data
        ipv6_data = ipv6_data.to_json(date_format='iso', orient='split')
    return ipv6_data

'''----------Choropleth Map Stuff----------'''
@app.callback(
        Output('the-choropleth-map', 'figure'),
        [Input('ipv4-dataset', 'data'),
        Input('whois-ipv4-dataset', 'data'),
        Input('ipv6-dataset', 'data'),
        Input('graph-tabs', 'value'),
        Input('choropleth-accordion-selector', 'active_item'),
        Input('switch', 'value')],
)
def update_choropleth_map(ipv4_dataset, whois_ipv4_data, ipv6_data, active_tab, active_item, switch_on):
    if active_tab != 'choropleth-tab':
        raise dash.exceptions.PreventUpdate
    
    #print(active_item)

    active_dataset = None
    if active_item == 'normal':
        active_dataset = ipv4_dataset
    elif active_item == 'log':
        active_dataset = ipv4_dataset

    #print(active_tab, 'in the choropleth map function')

    #print(active_dataset.get('data'))
    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    #theme = theme_data['theme']
    #print(active_item, 'active_item in choropleth callback function')
    return choropleth_map_handler.generate_figure(active_item, active_dataset, switch_on)

'''----------Scatter Plot----------'''
@app.callback(
    Output('the-scatter-plot', 'figure'),
    [Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('scatter-selector-accordion', 'active_item'),
     Input('switch', 'value')],
    #prevent_initial_call=True,
)
def update_scatter_plots(ipv4_data, whois_ipv4_data, ipv6_data, active_tab, scatter_selector_accordion, switch_on):
    if active_tab != 'scatter-tab':
        raise dash.exceptions.PreventUpdate
    
    # Determine which dataset is currently active based on UI controls or other logic
    active_dataset = None
    if scatter_selector_accordion == 'log':
        active_dataset = ipv4_data
    elif scatter_selector_accordion == 'normal':
        active_dataset = ipv4_data

    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
    # Assuming scatter_plot_handler can accept a dataset directly
    return scatter_plot_handler.generate_figure(scatter_selector_accordion, active_dataset, switch_on)

'''----------Pie Chart----------'''
@app.callback(
    Output('the-pie-chart', 'figure'),
    [Input('pie-selector-accordion', 'active_item'),  # Consider this as the selector for dataset types if possible
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('toggle-legend-button', 'n_clicks'),
     Input('graph-tabs', 'value'),
     Input('switch', 'value')],
)
def update_pie_figure(active_item, ipv4_data, whois_ipv4_data, ipv6_data, n_clicks, active_tab, switch_on):
    if active_tab != 'pie-tab':
        raise dash.exceptions.PreventUpdate

    # Determine which dataset is currently active based on UI controls or other logic
    active_dataset = None
    if active_item == 'TotalPool' or 'RIR' or 'RIPENCC' or 'ARIN' or 'APNIC' or 'LACNIC' or 'SUNBURST':
        active_dataset = ipv4_data
    # elif active_item == 'RIR':
    #     active_dataset = whois_ipv4_data
    elif active_item == 'ipv6':
        active_dataset = ipv6_data

    if not active_dataset:
        raise dash.exceptions.PreventUpdate

    # Toggle the legend display based on button clicks
    show_legend = n_clicks % 2 == 1 if n_clicks is not None else False
    opacity = 0.5 if show_legend else 1.0

    # Assuming pie_chart_handler can accept a dataset directly
    return pie_chart_handler.generate_figure(active_item, active_dataset, switch_on, show_legend, opacity)

'''----------Bar Chart----------'''
@app.callback(
    Output('the-bar-chart', 'figure'),
    [Input('bar-selector-accordion', 'active_item'),  # This could be used to choose dataset type
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('toggle-xaxis-scale-button', 'n_clicks'),
     Input('switch', 'value')],
    prevent_initial_call=True,
)
def update_bar_chart(active_item, ipv4_data, whois_ipv4_data, ipv6_data, active_tab, n_clicks, switch_on):
    if active_tab != 'bar-tab':
        raise dash.exceptions.PreventUpdate

    # Determine which dataset is currently active based on UI controls or other logic
    active_dataset = None
    if active_item == 'TotalPool' or 'RIR' or 'RIPENCC' or 'ARIN' or 'APNIC' or 'LACNIC':
        active_dataset = ipv4_data
    # elif active_item == 'whois_ipv4':
    #     active_dataset = whois_ipv4_data
    elif active_item == 'ipv6':
        active_dataset = ipv6_data

    if not active_dataset:
        raise dash.exceptions.PreventUpdate

    # Toggle the x-axis type based on the number of clicks on the toggle button
    toggle_xaxis_type = 'log' if n_clicks and n_clicks % 2 == 1 else 'linear'

    # Assuming bar_chart_handler can accept a dataset directly
    return bar_chart_handler.generate_figure(active_item, active_dataset, toggle_xaxis_type, switch_on)

'''----------AG Grid Stuff----------'''
@app.callback(
    [Output('the-ag-grid', 'rowData'),
     Output('the-ag-grid', 'columnDefs')],
    [Input('ag-switch', 'value'),
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data')],
    prevent_initial_call=True
)
def update_columns(switch_value, ipv4_data, whois_ipv4_data):
    row_data = []
    column_defs = []

    dataset = whois_ipv4_data if not switch_value else ipv4_data
    # if dataset and 'data' in dataset:
    #     data_string = dataset['data']
    #     # Check if the data stored is a string and needs parsing
    #     if isinstance(data_string, str):
    #         data = json.loads(data_string)
    #     else:
    #         data = data_string
        
    if not switch_value:
        if ipv4_data:
            row_data = ag_grid_handler.format_json_data_for_aggrid()
            column_defs = ag_grid_handler.generate_column_definitions('json')
    else:
        if whois_ipv4_data:
            row_data = ag_grid_handler.format_whois4_data_for_aggrid()
            column_defs = ag_grid_handler.generate_column_definitions('whoisv4')

    return row_data, column_defs

@app.callback(
    Output('ag-pagination-component', 'max_value'),
    Input('the-ag-grid', 'paginationInfo')
)
def update_pagination_control(pagination_info):
    if pagination_info is None:
        return dash.no_update
    return pagination_info['totalPages']

@app.callback(
    Output('the-ag-grid', 'paginationGoTo'),
    Input('ag-pagination-component', 'active_page'),
    prevent_initial_call=True
)
def goto_page(n):
    if n is None or n ==1:
        return 'first'
    return n - 1

'''----------UI Element Logic----------'''
# NOTE: The logic for the dynamic control card displayed on the left of the UI is handled in the
# appropriate handler becuase of it's size

# This function will display information related to the graph that's currently on display in the graph tab.
@app.callback(
    Output('dynamic-card-content', 'children'),
    [Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv4-time-series-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('graph-tabs', 'value')],
    prevent_initial_call=True,
)
def update_dynamic_card_content(ipv4_data, whois_ipv4_data, ipv4_time_series_data, ipv6_data, active_tab):
    # Determine which dataset to display based on which data is currently available
    # Assuming the first non-null dataset is the one related to the active button
    active_dataset = ipv4_data if ipv4_data is not None else (
        whois_ipv4_data if whois_ipv4_data is not None else (
            ipv4_time_series_data if ipv4_time_series_data is not None else ipv6_data
        )
    )

    print(active_tab, 'dyn_card_callback main')

    if not active_dataset:
        raise dash.exceptions.PreventUpdate

    # Use the dynamic card handler to get the content for the active tab and dataset
    return dynamic_card_handler.get_content(active_dataset, active_tab)

# This handles the button outline based on which button is pressed and not.
@app.callback(
    [Output('whoisv4', 'className'),
     Output('whoisv6', 'className'),],
    [Input('whoisv4', 'n_clicks'),
     Input('whoisv6', 'n_clicks'),],
    prevent_initial_call=True,
)
def update_button_styles(n_whoisv6, n_whoisv4):
    ctx = callback_context
    if not ctx.triggered:
        # When the app loads, set the initial style
        return ['btn-primary', 'btn-outline-primary']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'whoisv4':
            return ['btn-primary', 'btn-outline-primary']
        elif button_id == 'whoisv6':
            return ['btn-outline-primary', 'btn-primary']

# Light/Dark Mode
clientside_callback(
    '''
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    ''',
    Output('switch', 'id'),
    Input('switch', 'value'),
)

'''----------Render the application----------'''    
# App Layout
app.layout = dbc.Container([
    dcc.Store(id='ipv4-dataset', storage_type='memory'),
    dcc.Store(id='whois-ipv4-dataset', storage_type='memory'),
    dcc.Store(id='ipv4-time-series-dataset', storage_type='memory'),
    dcc.Store(id='ipv6-dataset', storage_type='memory'),

    # Header section
    dbc.Row([
        dbc.Col([
            html.H3('Internet Protocol Allocation Visualisation Model'),

        ], width={'size': 7, 'offset': 1}),
        dbc.Col([
            html.Div([
                dbc.Label(className='fa fa-moon', html_for='switch'),
                dbc.Switch(id='switch', value=True, className='d-inline-block ms-1', persistence=True),
                dbc.Label(className='fa fa-sun', html_for='switch')
            ], className='sec1-button-column', style={'padding-right': '0.5rem', 'padding-bottom': '0.2rem'}),
            dbc.ButtonGroup([
                dbc.Button('IPv4', id='whoisv4', outline=True, className='btn-primary', n_clicks=0),
                dbc.Button('IPv6', id='whoisv6', outline=True, className='btn-outline-primary', n_clicks=0),
                #dbc.Button('WHOIS v4', id='whoisv4', outline=True, className='btn-outline-primary', n_clicks=0),
            ], className='mb-3')
        ], className='sec1-button-column', width={'size': 3}),
    ], className='section-1-container'),  # Adjusting header to take 8% of the height
    
    # Main content section
    dbc.Row([
        dbc.Col([
            dbc.Card(id='dynamic-card-content', className='sec2-dynamic-card'),#, style={'padding': '20px'}
        ], width={'size': 2, 'offset': 1}),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Tabs(
                        id='graph-tabs',
                        value='choropleth-tab',
                        children=[
                            dcc.Tab(label='Choropleth Map', value='choropleth-tab', children=[dcc.Graph(id='the-choropleth-map', style={'height':'45vh'}, className='dbc')], className='tab-content dbc'),
                            dcc.Tab(label='Scatter Plot', value='scatter-tab', children=[dcc.Graph(id='the-scatter-plot', style={'height':'45vh'}, className='dbc')], className='tab-content dbc'),
                            dcc.Tab(label='Pie Chart', value='pie-tab', children=[dcc.Graph(id='the-pie-chart', style={'height':'45vh'})], className='tab-content'),
                            dcc.Tab(label='Bar Chart', value='bar-tab', children=[dcc.Graph(id='the-bar-chart', style={'height':'45vh'})], className='tab-content'),
                            dcc.Tab(label='Custom Graph', value='custom-tab', children=[dcc.Graph(id='the-custom-chart')], className='tab-content dbc'),
                        ], className='sec2-graph-tabs')  # Classname sets tab width
                ], className='sec2-card-body')
            ], className='sec2-tab-card'),
        ], width={'size': 8}),
        dbc.Col([], width={'size': 1}, className='h-100'),
    ], className='section-2-container'),

    # Bottom section for the AG-Grid
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Pagination(
                                id='ag-pagination-component',
                                first_last=True,
                                previous_next=True,
                                size='sm',
                                fully_expanded=False,
                                max_value=1
                            )
                        ]),
                        dbc.Col([
                            html.Div([
                                html.H6('IPv4 Pool Data'),
                                dbc.Switch(id='ag-switch', value=True, className='d-inline-block ms-1', persistence=True),
                                html.H6('IPv4 WHOIS Data'),
                            ], className='sec1-button-column', style={'padding-right': '0.5rem', 'padding-bottom': '0.2rem'}),
                        ]),
                    ]),  

                    dbc.Container([
                        dag.AgGrid(
                            id='the-ag-grid',
                            rowData=[],
                            columnDefs=[],
                            className='ag-theme-alpine',
                            style={'height': '27vh'},
                            dashGridOptions={
                                'pagination': True,
                                'paginationAutoPageSize': True,
                                'rowHeight': 28,
                                'headerHeight': 40,
                                'suppressPaginationPanel': True
                            },
                            defaultColDef={
                                'flex': 1,
                                'minWidth': 100,
                            },
                        )
                    ],fluid=True, className='dbc-ag-grid grid-container')
                ])
            ], className='h-100')
        ], width={'size': 10, 'offset': 1})
    ], className='section-3-container'),

], fluid=True, className='main-container dbc')

if __name__ == '__main__':
    app.run_server(debug=True)