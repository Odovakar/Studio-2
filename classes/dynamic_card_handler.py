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
            ])#, style={'padding': '10px'}
        ])#, style={'margin-top': 'auto', 'height': '33%'}

    def get_dropdown(self, title, id, dropdown_options, **kwargs):
        return html.Div([
            html.H4(f'{title}'),
            dcc.Dropdown(
                id=id,
                options=dropdown_options,
                **kwargs
            ),
        ])
    
    def get_toggle_button(self):
        return html.Div([
            dbc.Button('Toggle Legend', id='toggle-legend-button', className='toggle-legend-button', n_clicks=0)
        ])#, style={'justify-content': 'flex-end'}

    def get_toggle_group(self):
        return html.Div([
            dbc.ButtonGroup([
                dbc.Button('Top 5', id='top5', outline=True, className='btn-outline-primary', n_clicks=0),
                dbc.Button('Toggle Legend', id='toggle-legend-button', className='btn-primary', n_clicks=0),
                dbc.Button('Bottom 5', id='bottom5', outline=True, className='btn-outline-primary', n_clicks=0),
            ])
        ])

    def get_control_buttons(self, active_item, active_tab):
        print(f"Generating controls for {active_item} on {active_tab}")
        if active_tab == 'pie-tab':
            if active_item == 'SUNBURST':
                return html.Div("Sunburst specific controls")
            elif active_item in ['TotalPool', 'ARIN', 'RIPENCC', 'APNIC', 'LACNIC', 'AFRINIC', 'RIR']:
                return dbc.Button('Toggle Legend', id='toggle-legend-button')
            else:
                return html.Div("No specific controls available for this item.")
        return html.Div("This tab has no controls.")

    def get_accordion(self, title, id, accordion_options, **kwargs):
        return html.Div([
            html.H4(f'{title}'),#, style={'margin-bottom': '5px'}
            dbc.Accordion(
                accordion_options,
                id=id,
                **kwargs
            ),
        ])

    def get_scale_toggle_button(self):
        return html.Div([
            dbc.Button(
                "Toggle X-Axis Scale", 
                id='toggle-xaxis-scale-button', 
                className='mb-2',
                n_clicks=0
            ),
        ])
    
    def get_buttons(self, active_item, active_tab):
        active_item = active_item.get('active_item')
        #print(active_item, active_tab)
        if active_tab == 'pie-tab':
            if active_item == 'SUNBURST':
                return print('this works')

    def get_content(self, active_dataset, active_tab):
        if not active_dataset or 'data' not in active_dataset:
            return "Please select a dataset and ensure data is loaded."


        dataset = active_dataset.get('dataset')
        toggle_button = None


        # CHOROPLETH TAB
        if active_tab == 'choropleth-tab':
                # Intantianiating Keywords
                title = 'Choropleth Map Options'
                id = 'choropleth-accordion-selector'
                accordion_options = [
                    dbc.AccordionItem(
                        'If you hover over each country, a tooltip with IPv4 information related to that respective country will show. The coloring of the map is based on the amount of IPv4 addresses allocated to each respective country modified with a logarithmic scale for better visualisation.',
                        item_id = 'log',
                        title='Global IPv4 Allocation - Log',
                    ),
                    dbc.AccordionItem(
                        'The map is closely related to the logarithmically colored map, although similar, the grouping will better visualise the distinct group the country has been allotted to.',
                        item_id = 'normal',
                        title = 'Regional Internet Registry\'s Percent of Pool'
                    ),
                ]
                # Instantiating Contents
                #card_contents = self.get_accordion('Stuff about the choropleth map')
                card_controls = self.get_accordion(title, id, accordion_options)

                # Returning Contents
                return html.Div([
                    card_controls,
                    #card_contents
                ], className = 'dynamic-card-content')
        # SCATTER TAB
        elif active_tab == 'scatter-tab':
            if dataset == 'ipv4':
                # Intantianiating Keywords
                title = 'Scatter Plot Options'
                id = 'scatter-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'The scatter plot visualises the population in the x-axis and number of ipv4 addresses in the y-axis. The size of the plot is related to the cumulative sum of ipv4 addresses attributed to the distinct country. LOGx TODO: Fiks det her!',
                        item_id = 'log',
                        title='Logarithmic Sum of IPv4 Addresses x Population',
                    ),
                    dbc.AccordionItem(
                        'This scatter plot visualises the population in the x-axis and number of ipv4 addresses in the y-axis. The size of the plot is related to the cumulative sum of ipv4 addresses attributed to the distinct country.',
                        item_id = 'normal',
                        title='Custom Grouped Sum of IPv4 addresses from x Population',
                    ),
                ]
                
                # Instantiating Contents
                card_controls = self.get_accordion(title, id, accordion_options)
                #card_controls = self.get_dropdown(title, id, dropdown_options, value = 'log', clearable = False)

                # Returning Contents
                return html.Div([
                    card_controls,
                ], className='dynamic-card-content')
            
            if dataset == 'whoisv4':
                title = 'Scatter Plot Options'
                id = 'scatter-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This animated plot visualises the cumulative gain of IPv4 addresses since 1982 until 2023, in accordance with population growth.',
                        item_id = 'v4cumulativepoolpopulation',
                        title='Sum of IPv4 addresses from 1982 x Population',
                    ),
                ]

                #Instantiating Contents
                card_controls = self.get_accordion(title, id, accordion_options)
                # Return Contents
                return card_controls
            
        # PIE TAB
        elif active_tab == 'pie-tab':
            if dataset == 'ipv4':
                title = 'Pie Chart Options'
                id = 'pie-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the AFRINIC region.',
                        item_id='SUNBURST',
                        title='All countries sunburst IPv4 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart shows the total pool of allocated ipv4 addresses by country',
                        item_id = 'TotalPool',
                        title='Total IPv4 Pool Distribution by Country',
                    ),
                    dbc.AccordionItem(
                        'This chart visualises each RIR and how many percent of the total IPv4 they currently have allocated',
                        item_id = 'RIR',
                        title = 'Regional Internet Registry\'s Percent of Pool'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the ARIN region.',
                        item_id='ARIN',
                        title='ARIN IPv4 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the APNIC region.',
                        item_id='APNIC',
                        title='APNIC IPv4 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the RIPE NCC region.',
                        item_id='RIPENCC',
                        title='RIPE NCC IPv4 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the LACNIC region.',
                        item_id='LACNIC',
                        title='LACNIC IPv4 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the AFRINIC region.',
                        item_id='AFRINIC',
                        title='AFRINIC IPv4 Country Distribution'
                    ),
                ]


                card_controls = self.get_accordion(title, id, accordion_options)
                #toggle_button = self.get_toggle_button()
                return card_controls
        
        elif active_tab == 'bar-tab':
            #print(active_tab, 'we\'re here in the dyn card conditional')
            if dataset == 'ipv4':
                #print(dataset, 'dataset present in dy_car_hand conditional')
                title = 'Bar Chart Options'
                id = 'bar-selector-accordion'
                accordion_options = [
                    # dbc.AccordionItem(
                    #     'This chart shows the total pool of allocated ipv4 addresses by country',
                    #     item_id = 'TotalPool',
                    #     title='Total IPv4 Pool Distribution by Country',
                    # ),
                    dbc.AccordionItem(
                        'This chart visualises each RIR cumulative sum of currently allocated IPv4 addresses',
                        item_id = 'RIR',
                        title = 'Regional Internet Registry\'s Percent of Pool'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the RIPE NCC region.',
                        item_id='RIPENCC',
                        title='RIPE NCC IPv4 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the ARIN region.',
                        item_id='ARIN',
                        title='ARIN IPv4 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the APNIC region.',
                        item_id='APNIC',
                        title='APNIC IPv4 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the LACNIC region.',
                        item_id='LACNIC',
                        title='LACNIC IPv4 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the AFRINIC region.',
                        item_id='AFRINIC',
                        title='AFRINIC IPv4 Country Distribution'
                    )
                ]

                card_controls = self.get_accordion(title, id, accordion_options)
                toggle_button = self.get_scale_toggle_button()
                return card_controls, toggle_button
        elif active_tab == 'custom-tab':
            #print('we are in the dyn card elif active tab conditional') both of these are good
            if dataset == 'ipv4' or 'whoisv4':
                #print('we are in the dyn card in the if dataset conditional')
                id = 'custom-graph-accordion'
                title = 'Graph Options'
                accordion_options = [
                    dbc.AccordionItem(
                        'Testing Custom',
                        item_id='TEST',
                        title='Testing Custom Graph'
                    ),
                ]
                card_controls = self.get_accordion(title, id, accordion_options)

                return card_controls
        return 'Invalid tab selection.'