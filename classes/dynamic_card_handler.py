from dash import html, dcc
import dash_bootstrap_components as dbc

class DynamicCardHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    #
    def get_card(self, card_contents):
        return html.Div([
            dbc.Card([
                html.P(card_contents)
            ], style={'padding': '10px'})
        ], style={'margin-top': 'auto', 'height': '33%'})

    def get_dropdown(self, title, id, dropdown_options, **kwargs):
        return html.Div([
            html.H4(f'{title}'),
            dcc.Dropdown(
                id=id,
                options=dropdown_options,
                **kwargs
            ),
        ])

    # NOTE: When passing i.e., dropdown_options in an array, make sure to omit trailing commas,
    # so that it's interpreted as a list and not a tuple.
    def get_content(self, active_dataset, active_tab):
        if not active_dataset or 'data' not in active_dataset:
            return "Please select a dataset and ensure data is loaded."
        
        dataset = active_dataset.get('dataset')
        if active_tab == 'choropleth-tab':
            # Intantianiating Keywords
            title='Choropleth Map Options'
            id = 'color-scale-dropdown'
            dropdown_options = [
                {'label': 'Logarithmic Visualisation', 'value': 'log'},
                {'label': 'Normal Visualisation', 'value': 'normal'}
            ]

            # Instantiating Contents
            card_controls = self.get_dropdown(title, id, dropdown_options, value = 'log', clearable = False)
            card_contents = self.get_card('Stuff about the choropleth map')

            # Returning Contents
            return html.Div([
                card_controls,
                card_contents
            ], className='dynamic-card-content')
        elif active_tab == 'scatter-tab':
            if dataset == 'ipv4':
                # Intantianiating Keywords
                title='Scatter Plot Options'
                id = 'color-scale-dropdown'
                dropdown_options = [
                    {'label': 'Logarithmic Visualisation', 'value': 'log'},
                    {'label': 'Normal Visualisation', 'value': 'normal'}
                ]
                
                # Instantiating Contents
                card_controls = self.get_dropdown(title, id, dropdown_options, value = 'log', clearable = False)
                card_contents = self.get_card('Stuff about the choropleth map')

                # Returning Contents
                return html.Div([
                    card_controls,
                    card_contents
                ], className='dynamic-card-content')
        elif active_tab == 'pie-tab':
            if dataset == 'ipv4':
                return None
        elif active_tab == 'bar-tab':
            return html.Div([html.H4("IPv4 Bar Chart Insights"), html.P("Details and actions related to the IPv4 Bar Chart.")])
        elif active_tab == 'custom-tab':
            return html.Div([html.H4("IPv4 Custom Chart Insights"), html.P("Details and actions related to the IPv4 Custom Chart.")])
        return "Invalid tab selection."