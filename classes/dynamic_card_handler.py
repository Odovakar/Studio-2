from dash import html, dcc
import dash_bootstrap_components as dbc

'''The main concept of the dynamic card handler is revolving around '''

class DynamicCardHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def get_card(self, card_contents):
        return html.Div([
            dbc.Card([
                html.P(card_contents)
            ])#, style={'padding': '10px'}
        ])#, style={'margin-top': 'auto', 'height': '33%'}
 
    def get_control_buttons(self, active_item, active_tab):
        #print(f'Generating controls for {active_item} on {active_tab}')
        
        if active_tab == 'pie-tab':
            if active_item == 'SUNBURST':
                return html.Div()
            elif active_item in ['TotalPool', 'ARIN', 'RIPENCC', 'APNIC', 'LACNIC', 'AFRINIC', 'GLOBALBAR']:
                button_group = dbc.ButtonGroup([
                                    dbc.Button('Top 10', id='top10-button', key='top10-button', outline=True, className='btn-outline-primary', n_clicks=0),
                                    dbc.Button('Legend', id='toggle-legend-button', outline=True, className='btn-outline-primary'),
                                    dbc.Button('Log', id='toggle-log-button', outline=True, className='btn-outline-primary'),
                                    dbc.Button('Bottom 10', id='bottom10-button', outline=True, className='btn-outline-primary')
                                ], className='mb-2')
                return button_group
            elif active_item == 'RIR':
                return dbc.Button('Legend', id='toggle-legend-button', outline=True, className='btn-outline-primary')
            elif active_item == 'RIRV6':
                return dbc.Button('Legend', id='toggle-legend-button', outline=True, className='btn-outline-primary')
            elif active_item in ['ARINV6', 'RIPENCCV6', 'APNICV6', 'LACNICV6', 'AFRINICV6']:
                button_group = dbc.ButtonGroup([
                                    dbc.Button('Top 10', id='top10-button', key='top10-button', outline=True, className='btn-outline-primary', n_clicks=0),
                                    dbc.Button('Legend', id='toggle-legend-button', outline=True, className='btn-outline-primary'),
                                    dbc.Button('Log', id='toggle-log-button', outline=True, className='btn-outline-primary'),
                                    dbc.Button('Bottom 10', id='bottom10-button', outline=True, className='btn-outline-primary')
                                ], className='mb-2')
                return button_group
            else:
                return html.Div()
        elif active_tab == 'bar-tab':
            if active_item in ['ARINV6', 'RIPENCCV6', 'APNICV6', 'LACNICV6', 'AFRINICV6', 'AFRINIC', 'ARIN', 'RIPENCC', 'APNIC', 'LACNIC', 'GLOBALBARV6', 'GLOBALBAR']:
                button_group = dbc.ButtonGroup([
                                    dbc.Button('Top 10', id='top10-button', key='top10-button', outline=True, className='btn-outline-primary', n_clicks=0),
                                    dbc.Button('Log', id='toggle-log-button', outline=True, className='btn-outline-primary'),
                                    dbc.Button('Bottom 10', id='bottom10-button', outline=True, className='btn-outline-primary')
                ], className='mb-2')
                return button_group
        return html.Div()

    def get_accordion(self, title, id, accordion_options, **kwargs):
        return html.Div([
            html.H4(f'{title}'),
            dbc.Accordion(
                accordion_options,
                id=id,
                **kwargs
            ),
        ])

    def get_content(self, active_dataset, active_tab, allocation_version):
        if not active_dataset or 'data' not in active_dataset:
            return 'Please select a dataset and ensure data is loaded.'
        dataset = active_dataset.get('dataset')

        #print(allocation_version.get('allocation_type'))
        # CHOROPLETH TAB
        if active_tab == 'choropleth-tab':
            if allocation_version.get('allocation_type') == 'ipv4':
                title = 'Choropleth Map Options'
                id = 'choropleth-accordion-selector'
                accordion_options = [
                    dbc.AccordionItem(
                        'If you hover over each country, a tooltip with IPv4 information related to that respective country will show. The coloring of the map is based on the amount of IPv4 addresses allocated to each respective country modified with a logarithmic scale for better visualisation. You can see that the smaller nations are still represented with an appropriate color, although not visible on the legend.',
                        item_id = 'log',
                        title='Global IPv4 Allocation - Log',
                    ),
                    dbc.AccordionItem(
                        'Although similar to the visualisation above, this map shows manually grouped values into respective groups. The groupings will help distinguish the number of allocated addresses even further.',
                        item_id = 'normal',
                        title='Global IPv4 Allocation - Grouped',
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
            if allocation_version.get('allocation_type') == 'ipv6':
                title = 'Choropleth Map Options'
                id = 'choropleth-accordion-selector'
                accordion_options = [
                    dbc.AccordionItem(
                        'The map shows a quantile of the upper ranges of the log10 scale of the number of allocated addresses per country. The reasoning for setting the log scale more sensitive to the upper ranges of the scale is to better differentiate the number of allocations to each nation. ',
                        item_id = 'v6log',
                        title='IPv6 Logarithmic View',
                    ),
                ]
                # Instantiating Contents
                #card_contents = self.get_accordion('Stuff about the choropleth map')
                #card_controls = self.get_accordion(title, id, accordion_options)
            return html.Div([
                html.H4(f'{title}'),
                dbc.Accordion(
                    accordion_options,
                    id=id,
                ),
            ])
        # SCATTER TAB
        elif active_tab == 'scatter-tab':
            if allocation_version.get('allocation_type') == 'ipv4':
                # Intantianiating Keywords
                title = 'Scatter Plot Options'
                id = 'scatter-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'The scatter plot visualises the population in the x-axis and number of ipv4 addresses in the y-axis. The size of the plot is related to the cumulative sum of ipv4 addresses attributed to the distinct country.',
                        item_id = 'log',
                        title='Logarithmic Sum of IPv4 Addresses x Population',
                    ),
                    dbc.AccordionItem(
                        'This scatter plot visualises the population in the x-axis and number of ipv4 addresses in the y-axis. The size of the plot is related to the cumulative sum of ipv4 addresses attributed to the distinct country.',
                        item_id = 'normal',
                        title='Custom Grouped Sum of IPv4 addresses from x Population',
                    ),
                    dbc.AccordionItem(
                        '123',
                        item_id = 'animated',
                        title='1231233',
                    ),
                ]
                
                # Instantiating Contents
                card_controls = self.get_accordion(title, id, accordion_options)
                #card_controls = self.get_dropdown(title, id, dropdown_options, value = 'log', clearable = False)

                # Returning Contents
                return html.Div([
                    card_controls,
                ], className='dynamic-card-content')
            
            if allocation_version.get('allocation_type') == 'ipv6':
                title = 'Scatter Plot Options'
                id = 'scatter-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'something something ',
                        item_id = 'v6log',
                        title='Log ipv6 stuff',
                    ),
                    dbc.AccordionItem(
                        'farts',
                        #item_id = 'normal',
                        title='v6 poop',
                    ),
                ]

                #Instantiating Contents
                card_controls = self.get_accordion(title, id, accordion_options)
                # Return Contents
                return card_controls 
        # PIE TAB
        elif active_tab == 'pie-tab':
            if allocation_version.get('allocation_type') == 'ipv4':
                title = 'Pie Chart Options'
                id = 'pie-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the RIR in the inner branch and by country in the outer branch.',
                        item_id='SUNBURST',
                        title='Total IPv4 Addresses Allocated by RIR',
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
                    dbc.AccordionItem(
                        'The visualisation shows how many of the address ranges are allocated vs unallocated',
                        item_id='UNVSALLOCATED',
                        title='Allocated vs Assigned'
                    ),
                ]


                card_controls = self.get_accordion(title, id, accordion_options)
                #toggle_button = self.get_toggle_button()
                return card_controls
            if allocation_version.get('allocation_type') == 'ipv6':
                title = 'Pie Chart Options'
                id = 'pie-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the RIR in the inner branch and by country in the outer branch.',
                        item_id='SUNBURSTV6',
                        title='Total IPv6 Addresses Allocated by RIR',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage-wise distribution of IPv6 addresses between the RIRs.',
                        item_id='RIRV6',
                        title='Percentage-Wise Division of IPv6 Pool ',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the countries within the ARIN region.',
                        item_id='ARINV6',
                        title='ARIN',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the countries within the RIPE NCC region.',
                        item_id='RIPENCCV6',
                        title='RIPE NCC',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the countries within the APNIC region.',
                        item_id='APNICV6',
                        title='APNIC',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the countries within the LACNIC region.',
                        item_id='LACNICV6',
                        title='LACNIC',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv6 addresses between the countries within the AFRINIC region.',
                        item_id='AFRINICV6',
                        title='AFRINIC',
                    ),
                ]
                card_controls = self.get_accordion(title, id, accordion_options)
                #toggle_button = self.get_toggle_button()
                return card_controls
        # BAR TAB
        elif active_tab == 'bar-tab':
            #print(active_tab, 'we\'re here in the dyn card conditional')
            if allocation_version.get('allocation_type') == 'ipv4':

                #print(dataset, 'dataset present in dy_car_hand conditional')
                title = 'Bar Chart Options'
                id = 'bar-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This chart visualises each RIR cumulative sum of currently allocated IPv4 addresses',
                        item_id = 'RIR',
                        title = 'Regional Internet Registry\'s Percent of Pool'
                    ),
                    dbc.AccordionItem(
                        'The visualisation shows how many of the address ranges are allocated vs unallocated',
                        item_id='UNVSALLOCATED',
                        title='Allocated vs Assigned'
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
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the AFRINIC region.',
                        item_id='GLOBALBAR',
                        title='GLOBALBAR IPv4 Country Distribution'
                    ),
                ]
                card_controls = self.get_accordion(title, id, accordion_options)
                return card_controls
            if allocation_version.get('allocation_type') == 'ipv6':
                print('this works')
            
                #print(dataset, 'dataset present in dy_car_hand conditional')
                title = 'Bar Chart Options'
                id = 'bar-selector-accordion'
                accordion_options = [
                    dbc.AccordionItem(
                        'This chart visualises each RIR cumulative sum of currently allocated IPv4 addresses',
                        item_id = 'RIRV6',
                        title = 'Regional Internet Registry\'s Percent of Pool'
                    ),
                    # dbc.AccordionItem(
                    #     'The visualisation shows how many of the address ranges are allocated vs unallocated',
                    #     item_id='UNVSALLOCATED',
                    #     title='Allocated vs Assigned'
                    # ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the RIPE NCC region.',
                        item_id='RIPENCCV6',
                        title='RIPE NCC IPv6 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the ARIN region.',
                        item_id='ARINV6',
                        title='ARIN IPv6 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the APNIC region.',
                        item_id='APNICV6',
                        title='APNIC IPv6 Country Distribution',
                    ),
                    dbc.AccordionItem(
                        'This chart displays the cumulative distribution of IPv4 addresses between the countries within the LACNIC region.',
                        item_id='LACNICV6',
                        title='LACNIC IPv6 Country Distribution'
                    ),
                    dbc.AccordionItem(
                        'This chart displays the percentage wise distribution of IPv4 addresses between the countries within the AFRINIC region.',
                        item_id='AFRINICV6',
                        title='AFRINIC IPv6 Country Distribution'
                    ),
                ]
                card_controls = self.get_accordion(title, id, accordion_options)
                return card_controls    
        # CUSTOM TAB
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