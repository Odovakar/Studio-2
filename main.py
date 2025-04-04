import dash
from dash import Dash, html, dcc, Input, Output, State, callback_context, clientside_callback, Patch
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from io import StringIO

from classes.data_handler import DataHandler
from classes.pie_chart_handler import PieChartHandler
from classes.ag_grid_handler import AgGridHandler
from classes.scatter_plot_handler import ScatterHandler
from classes.choropleth_map_handler import ChoroplethHandler
from classes.hover_template_handler import HoverTemplateHandler
from classes.dynamic_card_handler import DynamicCardHandler
from classes.bar_chart_handler import BarChartHandler
from classes.custom_chart_handler import CustomChartHandler

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
    whois_v4_pop_csv='whoisv4_pop_gdp.csv',
    population_csv='wpopdata.csv',
    whoisv6_allocation_csv='ipv6_allocations.csv'
    
)

data_handler.fetch_json_data()
data_handler.fetch_whois_ipv4_data()
data_handler.create_time_series_df()
data_handler.create_allocation_bar_df()
data_handler.fetch_whois_ipv6_data()

# Instantiating Handlers
hover_template_handler = HoverTemplateHandler(data_handler)
pie_chart_handler = PieChartHandler(data_handler, hover_template_handler)
ag_grid_handler = AgGridHandler(data_handler)
scatter_plot_handler = ScatterHandler(data_handler)#, hover_template_handler
choropleth_map_handler = ChoroplethHandler(data_handler, hover_template_handler)
dynamic_card_handler = DynamicCardHandler(data_handler)
bar_chart_handler = BarChartHandler(data_handler)
custom_chart_handler = CustomChartHandler(data_handler)

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
    [State('ipv4-time-series-dataset', 'data')]
)
def update_ipv4_time_series_dataset(n_whoisv4, ipv4_ts_dataset):
    if n_whoisv4 is None:
        raise dash.exceptions.PreventUpdate

    # Fetch the data
    data_handler.create_time_series_df()
    ipv4_ts_dataset = {
        'dataset': 'ipv4_time_series',
        'data': data_handler.ipv4_ts_df.to_json(date_format='iso', orient='split')
    }
    return ipv4_ts_dataset

@app.callback(
    Output('whois-ipv4-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    [State('whois-ipv4-dataset', 'data')]
)
def update_whoisv4_dataset(n_whoisv4, whois_ipv4_dataset):
    if n_whoisv4 is None:
        raise dash.exceptions.PreventUpdate

    # Fetch the data
    data_handler.fetch_whois_ipv4_data()
    whois_ipv4_dataset = {'dataset': 'whois_ipv4', 'data': data_handler.whois_ipv4_df.to_json(date_format='iso', orient='split')}
    return whois_ipv4_dataset

@app.callback(
    Output('allocation-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    [State('allocation-dataset', 'data')]
)
def update_allocation_bar_dataset(n_whoisv4, allocation_dataset):
    if n_whoisv4 is None:
        raise dash.exceptions.PreventUpdate

    # Fetch the data
    data_handler.create_allocation_bar_df()
    allocation_dataset = {
        'dataset': 'v4_allocation',
        'data': data_handler.allocation_df.to_json(orient='split')
    }
    return allocation_dataset

@app.callback(
    Output('ipv4-dataset', 'data'),
    [Input('whoisv4', 'n_clicks')],
    State('ipv4-dataset', 'data')
)
def update_ipv4_dataset(n_whoisv4, data):
    if n_whoisv4 is None:
        raise dash.exceptions.PreventUpdate

    # Fetch the data regardless of the current state
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
def update_ipv6_dataset(n_whoisv6, ipv6_dataset):
    if n_whoisv6 is None:
        raise dash.exceptions.PreventUpdate

    # Fetch the data
    data_handler.fetch_whois_ipv6_data()
    ipv6_dataset = {'dataset': 'whois_ipv6', 'data': data_handler.whoisv6_df.to_json(date_format='iso', orient='split')}
    return ipv6_dataset

'''----------Choropleth Map Stuff----------'''
# Main bossmeng logic for the choropleth map, this will take in data from all related stores and callbacks and
# return the correct graph logic based on the arguments the class has been served
@app.callback(
        Output('the-choropleth-map', 'figure'),
        [Input('ipv4-dataset', 'data'),
        #Input('whois-ipv4-dataset', 'data'),
        #Input('ipv6-dataset', 'data'),
        Input('graph-tabs', 'value'),
        Input('choropleth-accordion-selector', 'active_item'),
        Input('switch', 'value'),
        Input('v4v6-button-store', 'data')],
)
def update_choropleth_map(ipv4_dataset, active_tab, active_item, switch_on, allocation_version):
    if active_tab != 'choropleth-tab':
        raise dash.exceptions.PreventUpdate
    
    #df = pd.read_json(ipv4_dataset['data'], orient='split')
    #print(df.head(), 'main choropleth function')
    #print(active_item)
    active_dataset = None
    # Debug prints
    # print(f"allocation_version: {allocation_version}")
    # print(f"active_item: {active_item}")
    # print(f"active_tab: {active_tab}")
    # print(f"dataset: {ipv4_dataset}")
    #if allocation_version['allocation_type'] == 'ipv4':
    if allocation_version['allocation_type'] == 'ipv4':
        if active_item in ['normal','log']:
            active_dataset = ipv4_dataset
    if allocation_version['allocation_type'] == 'ipv6':
        if active_item == 'v6log':
            active_dataset = ipv4_dataset

    # df = pd.read_json(active_dataset['data'], orient='split')
    # print(df.head(), 'main choropleth function')

    #print(active_dataset.get('data'))
    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
    #df = pd.read_json(active_dataset['data'], orient='split')
    #print(df.head(), 'main choropleth function')

    return choropleth_map_handler.generate_figure(active_item, active_dataset, switch_on, allocation_version)

'''----------Scatter Plot----------'''
# Main bossmeng logic for the scatter plot, this will take in data from all related stores and callbacks and
# return the correct graph logic based on the arguments the class has been served
@app.callback(
    Output('the-scatter-plot', 'figure'),
    [Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('ipv4-time-series-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('scatter-selector-accordion', 'active_item'),
     Input('switch', 'value')],
    #prevent_initial_call=True,
)
def update_scatter_plots(ipv4_data, whois_ipv4_data, ipv6_data, time_series_data, active_tab, scatter_selector_accordion, switch_on):
    if active_tab != 'scatter-tab':
        raise dash.exceptions.PreventUpdate
    
    # Determine which dataset is currently active based on UI controls or other logic
    active_dataset = None
    if scatter_selector_accordion in ['log', 'normal', 'v6log']:
        active_dataset = ipv4_data
    if scatter_selector_accordion == 'animated':
        active_dataset = time_series_data
        print(active_dataset.get('dataset'))

    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
    # Assuming scatter_plot_handler can accept a dataset directly
    return scatter_plot_handler.generate_figure(scatter_selector_accordion, active_dataset, switch_on)

'''----------Pie Chart----------'''
# Main bossmeng logic for the pie chart, this will take in data from all related stores and callbacks and
# return the correct graph logic based on the arguments the class has been served
@app.callback(
    Output('the-pie-chart', 'figure'),
    [Input('pie-selector-accordion', 'active_item'),
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('allocation-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('switch', 'value'),
     Input('v4v6-button-store', 'data'),
     Input('toggle-legend-store', 'data'),
     Input('view-mode-store', 'data'),
     Input('log-scale-store', 'data')],
     prevent_initial_call=True
)
def update_pie_figure(active_item, ipv4_data, whois_ipv4_data, ipv6_data, allocation_data, active_tab, switch_on, allocation_version, show_legend, view_mode_data, log_scale_data):# , show_legendn_clicks, , show_legend
    if active_tab != 'pie-tab':
        raise dash.exceptions.PreventUpdate
    #print('initial view mode data in the update_pie_figure in main', view_mode_data)
    #print(allocation_version)
    active_dataset = None
    if active_item == 'TotalPool' or 'RIR' or 'RIPENCC' or 'ARIN' or 'APNIC' or 'LACNIC' or 'SUNBURST':
        active_dataset = ipv4_data

    elif active_item == 'ipv6':
        active_dataset = ipv6_data

    if active_item == 'UNVSALLOCATED':
        active_dataset = allocation_data
        #print('we made it')

    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
        # Check for None in inputs
    if show_legend is None:
        show_legend = True
    if view_mode_data is None:
        view_mode_data = {'view_mode': 'all'}

    log_scale_active = log_scale_data['log_scale_active'] if log_scale_data else False
    #print('Log scale active state received in update pie chart callback:', log_scale_active)
    #print(allocation_version, 'end of update pie in main')
    #print('Updating Store with:', {'active_item': active_item})
    view_mode = view_mode_data['view_mode']
    figure = pie_chart_handler.generate_figure(active_item, active_dataset, switch_on, allocation_version, show_legend, view_mode, log_scale_active) #, allocation_versionshow_legendshow_legend, , opacity, show_legend
    return figure#, {'active_item': active_item}


@app.callback(
    Output('pie-accordion-store', 'data'),
    [Input('pie-selector-accordion', 'active_item'),
     Input('graph-tabs', 'value')],
     prevent_initial_call=True
)
def update_pie_active_item_store(pie_active_item, active_tab):
    # This is an atomic function doing exactly what it says. The reasoning for the repetetiveness is because
    # having two inputs writing to the same store and serving different outputs is not DASH/Plotly's strong suit
    # the faster option was to write two similar functions instead of importing outside state libraries for handling this issue.
    if active_tab == 'pie-tab' and pie_active_item is not None:
            #print(f'Updating store from Pie: {pie_active_item}')
            return {'active_item': pie_active_item}

    return dash.no_update

'''----------Bar Chart----------'''
# Main bossmeng logic for the bar chart, this will take in data from all related stores and callbacks and
# return the correct graph logic based on the arguments the class has been served
@app.callback(
    Output('the-bar-chart', 'figure'),
    [Input('bar-selector-accordion', 'active_item'),
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('allocation-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('switch', 'value'),
     Input('v4v6-button-store', 'data'),
     Input('view-mode-store', 'data'),
     Input('log-scale-store', 'data')],
    prevent_initial_call=True,
)
def update_bar_chart(active_item, ipv4_data, whois_ipv4_data, ipv6_data, allocation_data, active_tab, switch_on, allocation_version, view_mode_data, log_scale_data):
    if active_tab != 'bar-tab':
        raise dash.exceptions.PreventUpdate
    #print(allocation_version, 'gotem')
    #df = pd.read_json(allocation_data['data'], orient='split')
    #print('works',df.head())
    #print(log_scale_data, 'top of bar chart callback')
    #print(active_item, 'in the good ole update_bar_chart function')
    active_dataset = None
    print(allocation_data)
    if active_item in ['TotalPool', 'RIR', 'RIPENCC', 'ARIN', 'APNIC', 'AFRINIC', 'GLOBALBAR' 'LACNIC', 'RIRV6', 'RIPENCCV6', 'ARINV6', 'APNICV6', 'LACNICV6']:
        active_dataset = ipv4_data
        #df = pd.read_json(active_dataset['data'], orient='split')
        #print(df.head())
    elif active_item == 'ipv6':
        active_dataset = ipv6_data

    if active_item == 'UNVSALLOCATED':
        print('before the dataset')
        active_dataset = allocation_data
        #for key in active_dataset:
        #    print(key)
        #print('within the conditional in bar chart main')
        #df = pd.read_json(active_dataset['data'], orient='split')
        #print(df.head())

    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
    log_scale_active = log_scale_data['log_scale_active'] if log_scale_data else False
    #print('Log scale active state received in update bar chart callback:', log_scale_active)

    view_mode = view_mode_data['view_mode']
    figure = bar_chart_handler.generate_figure(active_item, active_dataset, switch_on, allocation_version, log_scale_active, view_mode)
    return figure

@app.callback(
    Output('bar-accordion-store', 'data'),
    [Input('bar-selector-accordion', 'active_item'),
     Input('graph-tabs', 'value')],
)
def update_bar_active_item_store(bar_active_item, active_tab):
    if active_tab == 'bar-tab' and bar_active_item is not None:
            #print(f'Updating store from Bar: {bar_active_item}')
            return {'active_item': bar_active_item}

    return dash.no_update

'''----------Custom Graph Stuff----------'''
@app.callback(
    Output('the-custom-chart', 'figure'),
    [Input('the-ag-grid', 'virtualRowData'),
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('v4v6-button-store', 'data'),
     Input('graph-tabs', 'value'),
     Input('custom-graph-accordion', 'active_item'),
     Input('switch', 'value')]
)
def update_custom_graph(virtual_row_data, ipv4_data, whois_ipv4_data, ipv6_data, allocation_version, active_tab, active_item, switch_on):
    if active_tab != 'custom-tab':
        raise dash.exceptions.PreventUpdate
    if ipv4_data == None:
        print('dataset none')

    print(allocation_version)
    #print(ipv4_data) 
    #print(active_tab, 'cust graph callback') this is good
    active_dataset = None
    if virtual_row_data:
        if active_item == 'TEST':
            active_dataset = ipv4_data
            #print(active_dataset)
    return custom_chart_handler.generate_figure(virtual_row_data, active_item, active_dataset, switch_on)

'''----------AG Grid Stuff----------'''
@app.callback(
    [Output('the-ag-grid', 'rowData'),
     Output('the-ag-grid', 'columnDefs')],
    [Input('ag-switch', 'value'),
     Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('v4v6-button-store', 'data')],
    prevent_initial_call=True
)
def update_columns(switch_value, ipv4_data, whois_ipv4_data, ipv6_data, allocation_version):
    row_data = []
    column_defs = []
    
    #print(switch_value, 'ag grid main')

    #print(allocation_version, 'ag grid main')

    #active_dataset = whois_ipv4_data if not switch_value else ipv4_data
        
    # if not switch_value:
    #     if ipv4_data:
    #         row_data = ag_grid_handler.format_json_data_for_aggrid()
    #         column_defs = ag_grid_handler.generate_column_definitions('json')
    # else:
    #     if whois_ipv4_data:
    #         row_data = ag_grid_handler.format_whois4_data_for_aggrid()
    #         column_defs = ag_grid_handler.generate_column_definitions('whoisv4')

    if allocation_version['allocation_type'] == 'ipv4':
        if switch_value:
            #active_dataset = whois_ipv4_data
            row_data = ag_grid_handler.format_whois4_data_for_aggrid()
            column_defs = ag_grid_handler.generate_column_definitions('whoisv4')#active_dataset = ipv4_data

        else:
            row_data = ag_grid_handler.format_json_data_for_aggrid()
            column_defs = ag_grid_handler.generate_column_definitions('v4_pool')
    if allocation_version['allocation_type'] == 'ipv6':
        if switch_value:
            active_dataset = ipv6_data
            #print(active_dataset.keys())
            #print(active_dataset['dataset'])
            row_data = ag_grid_handler.format_whoisv6_data_for_aggrid(active_dataset)
            column_defs = ag_grid_handler.generate_column_definitions('whoisv6')
        else:
            row_data = ag_grid_handler.format_json_data_for_aggrid()
            column_defs = ag_grid_handler.generate_column_definitions('v6_pool')
            #print(column_defs)

    return row_data, column_defs

# Ag-grid pagination logic
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
# NOTE: This handles most of the element UI logic that can be regarded as having a general function.
# If the UI logic is very closely linked to a specific chart or the ag-grid it will be present in the section
# of their respective "parent"

# This function will display information related to the graph that's currently on display in the graph tab.
@app.callback(
    Output('dynamic-card-content', 'children'),
    [Input('ipv4-dataset', 'data'),
     Input('whois-ipv4-dataset', 'data'),
     Input('ipv4-time-series-dataset', 'data'),
     Input('ipv6-dataset', 'data'),
     Input('graph-tabs', 'value'),
     Input('v4v6-button-store', 'data')],
    prevent_initial_call=True,
)
def update_dynamic_card_content(ipv4_data, whois_ipv4_data, ipv4_time_series_data, ipv6_data, active_tab, allocation_version):#, store_data
    # Determine which dataset to display based on which data is currently available
    active_dataset = ipv4_data if ipv4_data is not None else (
        whois_ipv4_data if whois_ipv4_data is not None else (
            ipv4_time_series_data if ipv4_time_series_data is not None else ipv6_data
        )
    )
    #print(allocation_version)

    if not active_dataset:
        raise dash.exceptions.PreventUpdate
    
    return dynamic_card_handler.get_content(active_dataset, active_tab, allocation_version)

# Fetches the toggle-button(s) that are/is shown below the accordion based on the case it is served
@app.callback(
    Output('dynamic-button-div', 'children'),
    [Input('pie-accordion-store', 'data'),
     Input('bar-accordion-store', 'data'),
     Input('graph-tabs', 'value')],
)
def update_dynamic_toggle_button(pie_store_data, bar_store_data, active_tab):
    #print('Store Data Received:', store_data)
    #print('Active Tab:', active_tab)

    if not pie_store_data or 'active_item' not in pie_store_data:
        #print('Data store is empty or incorrect structure.')
        return html.Div('No item selected or incorrect data store format.')
    if active_tab == 'pie-tab':
        active_item = pie_store_data['active_item']
        return dynamic_card_handler.get_control_buttons(active_item, active_tab)
    elif active_tab == 'bar-tab':
        #print('bar store data is', bar_store_data)
        #print(active_tab)
        active_item = bar_store_data['active_item']
        #print(active_item)
        return dynamic_card_handler.get_control_buttons(active_item, active_tab)
    else:
        return html.Div()

# Does what the function name says
@app.callback(
    [Output('toggle-legend-store', 'data'),
     Output('toggle-legend-button', 'className')],
    [Input('toggle-legend-button', 'n_clicks')],
    [State('toggle-legend-store', 'data')],
    prevent_initial_call=True
)
def toggle_legend_visibility(n_clicks, current_legend_state):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    new_legend_state = not current_legend_state if current_legend_state is not None else True
    button_style = 'btn-primary' if new_legend_state else 'btn-outline-primary'

    return new_legend_state, button_style

# Updates the graph display if the top/bottom 10 buttons have been clicked
@app.callback(
    [Output('view-mode-store', 'data'),
     Output('top10-button', 'className'),
     Output('bottom10-button', 'className')],
    [Input('top10-button', 'n_clicks'),
     Input('bottom10-button', 'n_clicks')],
    [State('view-mode-store', 'data')],
    prevent_initial_call=True
)
def update_view_mode(top10_clicks, bottom10_clicks, current_view_mode):
    if not current_view_mode:
        current_view_mode = {'view_mode': 'all'}
        return current_view_mode, 'btn-outline-primary', 'btn-outline-primary'

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    top10_class = 'btn-outline-primary'
    bottom10_class = 'btn-outline-primary'
    
    if button_id == 'top10-button':
        if current_view_mode.get('view_mode') == 'top10':
            new_mode = {'view_mode': 'all'}
        else:
            new_mode = {'view_mode': 'top10'}
            top10_class = 'btn-primary'
    elif button_id == 'bottom10-button':
        if current_view_mode.get('view_mode') == 'bottom10':
            new_mode = {'view_mode': 'all'}
        else:
            new_mode = {'view_mode': 'bottom10'}
            bottom10_class = 'btn-primary'
    else:
        return dash.no_update
    return new_mode, top10_class, bottom10_class

# Does what the function name says
@app.callback(
    [Output('log-scale-store', 'data'),
     Output('toggle-log-button', 'className')],
    [Input('toggle-log-button', 'n_clicks')],
    [State('log-scale-store', 'data')],
    prevent_initial_call=True
)
def toggle_log_scale(n_clicks, log_scale_state):
    #print(f'Log scale toggle button clicks: {n_clicks}')
    #print(f'Current log scale state from store: {log_scale_state}')

    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    current_state = log_scale_state['log_scale_active'] if log_scale_state else False
    new_state = not current_state

    button_style = 'btn-primary' if new_state else 'btn-outline-primary'

    # Return the new state and button style
    return {'log_scale_active': new_state}, button_style

@app.callback(
    [Output('v4v6-button-store', 'data'),
     Output('whoisv4', 'className'),
     Output('whoisv6', 'className'),
     Output('pool-data-text', 'children'),
     Output('whois-data-text', 'children')],
    [Input('whoisv4', 'n_clicks'),
     Input('whoisv6', 'n_clicks')],
     State('v4v6-button-store', 'data')
)
def update_v4v6_view_mode(n_whoisv4, n_whoisv6, current_allocation_type):
    if current_allocation_type is None:
        current_allocation_type = {'allocation_type': 'ipv4'}
    
    ctx = dash.callback_context

    # Default button classes
    whoisv4_button = 'btn-outline-primary'
    whoisv6_button = 'btn-outline-primary'
    new_allocation_type = current_allocation_type['allocation_type']

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'whoisv4' and n_whoisv4:
        new_allocation_type = 'ipv4'
        whoisv4_button = 'btn-primary'
        whoisv6_button = 'btn-outline-primary'
    elif button_id == 'whoisv6' and n_whoisv6:
        new_allocation_type = 'ipv6'
        whoisv6_button = 'btn-primary'
        whoisv4_button = 'btn-outline-primary'

    new_version_view = {'allocation_type': new_allocation_type}

    # Update H6 text based on the selected allocation type
    pool_data_text = 'IPv4 Pool Data' if new_allocation_type == 'ipv4' else 'IPv6 Pool Data'
    whois_data_text = 'IPv4 WHOIS Data' if new_allocation_type == 'ipv4' else 'IPv6 WHOIS Data'

    #print(new_version_view)
    return new_version_view, whoisv4_button, whoisv6_button, pool_data_text, whois_data_text


# Light/Dark Mode logic
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
    # State Storages
    dcc.Store(id='v4v6-button-store', data={'allocation_type': 'ipv4'}),
    dcc.Store(id='ipv4-dataset', storage_type='memory'),
    dcc.Store(id='whois-ipv4-dataset', storage_type='memory'),
    dcc.Store(id='ipv4-time-series-dataset', storage_type='memory'),
    dcc.Store(id='ipv6-dataset', storage_type='memory'),
    dcc.Store(id='allocation-dataset', storage_type='memory'),
    dcc.Store(id='intermediate-data-from-grid', storage_type='memory'),
    dcc.Store(id='pie-accordion-store', data={'active_item': 'log'}),
    dcc.Store(id='bar-accordion-store', data={'active_item': 'linear'}),
    dcc.Store(id='toggle-legend-store', data=False),
    dcc.Store(id='view-mode-store', data={'view_mode': 'top10'}),
    dcc.Store(id='log-scale-store', data={'log_scale_active': False}),
    # State Debugging:
    dcc.Store(id='button-state-store', data={'top10_clicked': 0, 'legend_clicked': 0, 'log_clicked': 0, 'bottom10_clicked': 0}),

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
            ], className='sec1-button-column', style={'padding-right': '0.7rem', 'padding-bottom': '0.3rem'}),
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
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='dynamic-card-content', className='dynamic-card'),
                    html.Div(id='dynamic-button-div', className='dynamic-button')
                ]),
            ], className='sec2-dynamic-card'),
        ], width={'size': 2, 'offset': 1}),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Tabs(
                        id='graph-tabs',
                        value='choropleth-tab',
                        children=[
                            dcc.Tab(label='Choropleth Map', value='choropleth-tab', children=[dcc.Loading(dcc.Graph(id='the-choropleth-map', style={'height':'45vh'}, className='dbc'))], className='tab-content dbc'),
                            dcc.Tab(label='Scatter Plot', value='scatter-tab', children=[dcc.Loading(dcc.Graph(id='the-scatter-plot', style={'height':'45vh'}, className='dbc'))], className='tab-content dbc'),
                            dcc.Tab(label='Pie Chart', value='pie-tab', children=[dcc.Loading(dcc.Graph(id='the-pie-chart', style={'height':'45vh'}))], className='tab-content'),
                            dcc.Tab(label='Bar Chart', value='bar-tab', children=[dcc.Loading(dcc.Graph(id='the-bar-chart', style={'height':'45vh'}))], className='tab-content'),
                            dcc.Tab(label='Custom Graph', value='custom-tab', children=[dcc.Loading(dcc.Graph(id='the-custom-chart', figure={}))], className='tab-content dbc'),
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
                                html.H6(id='pool-data-text', children='IPv4 Pool Data'),
                                dbc.Switch(id='ag-switch', value=True, className='d-inline-block ms-1', persistence=True),
                                html.H6(id='whois-data-text', children='IPv4 WHOIS Data'),
                            ], className='sec1-button-column', style={'padding-right': '0.5rem', 'padding-bottom': '0.2rem'}),
                        ]),
                    ]),  

                    dbc.Container([
                        dcc.Loading(
                            id='loading-1',
                            type='default',
                            children=html.Div([
                                dag.AgGrid(
                                    id='the-ag-grid',
                                    rowData=[],
                                    columnDefs=[],
                                    className='ag-theme-alpine',
                                    style={'height': '25vh'},
                                    columnSize='sizeToFit',
                                    dashGridOptions={
                                        'pagination': True,
                                        #'paginationAutoPageSize': True,
                                        'rowHeight': 28,
                                        'headerHeight': 35,
                                        'suppressPaginationPanel': True,
                                        'rowSelection': 'multiple',
                                        'animateRows': False,
                                        'suppressScrollOnNewData':True,
                                    },
                                    defaultColDef={
                                        'flex': 1,
                                        'minWidth': 100,
                                        'filter': True,
                                    },
                                )
                            ])
                        ),

                    ],fluid=True, className='dbc-ag-grid grid-container')
                ])
            ], className='h-100')
        ], width={'size': 10, 'offset': 1})
    ], className='section-3-container'),

], fluid=True, className='main-container dbc')

if __name__ == '__main__':
    app.run_server(debug=True)