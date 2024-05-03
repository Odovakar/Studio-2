import plotly.express as px
import numpy as np

class PieChartHandler:
    def __init__(self, data_handler, hover_template_handler):
        self.data_handler = data_handler
        self.hover_template_handler = hover_template_handler

    def calculate_rir_percentages(self):
        df = self.data_handler.json_df
        return df.groupby('RIR')['percentv4'].sum().reset_index()

    def get_data_by_rir(self, rir):
        df = self.data_handler.json_df
        return df[df['RIR'] == rir]

    def populate_custom_data(self, active_item, active_dataset):
        customdata = None
        if active_item=='TotalPool':
            if active_dataset=='ipv4':
                df = self.data_handler.json_df
                customdata=df[['name', 'ipv4', 'pop', 'percentv4', 'pcv4', 'iso_alpha_3', 'ipv4_grouping', 'log_ipv4']].to_dict('records')
                return customdata

    def calculate_rir_country_data(self, df, active_item):
        if active_item == 'ARIN':
            arin_data = df[df['RIR'] == 'ARIN']
            return arin_data
        elif active_item == 'APNIC':
            apnic_data = df[df['RIR'] == 'APNIC']
            return apnic_data
        elif active_item == 'RIPENCC':
            ripencc_data = df[df['RIR'] == 'RIPE NCC']
            return ripencc_data
        elif active_item == 'LACNIC':
            lacnic_data = df[df['RIR'] == 'LACNIC']
            return lacnic_data
        elif active_item == 'AFRINIC':
            afrinic_data = df[df['RIR'] == 'AFRINIC']
            return afrinic_data
        else:
            return None

    def get_hover_label():
        hovertemplate = "<b>%{label}</b><br>Population: %{customdata[1]:,}<br>IPv4: %{customdata[2]:,}"

    def generate_figure(self, active_item, active_dataset, switch_on, show_legend=True, view_mode='all', log_scale_active=False):#, show_legendshow_legend=True, , opacity=1.0
        df = None
        values = None
        names = None
        customdata = None
        hover_template = None
        hover_data = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        opacity = 0.5 if show_legend else 1.0
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item)
        #customdata = self.populate_custom_data(active_item, active_dataset)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
        # print(active_item, active_dataset.get('dataset'))
        customdata = np.stack((
            self.data_handler.json_df['name'],          # Country name
            self.data_handler.json_df['ipv4'],          # IPv4 address count
            self.data_handler.json_df['pop'],           # Population size
            self.data_handler.json_df['percentv4'],     # Percent of IPv4 pool
            self.data_handler.json_df['pcv4'],          # IPv4 per capita percentage
            #json_df['log_ipv4']       # Log of IPv4 for the logarithmic map
        ), axis=-1)

        print("Log scale active:", log_scale_active)
        trace_options = {
            'textposition': 'inside',
            'opacity': opacity,
            #'hovertemplate': hover_template
        }
        #layout_options = {'showlegend': True, 'margin': dict(t=50, b=50, l=50, r=50), 'uniformtext_mode': 'hide', 'uniformtext_minsize': 12, 'height': 400, 'width': 400}
        layout_options = {
            'template': template,
            'showlegend': show_legend,
            'margin': dict(t=50, b=50, l=50, r=50),
            'uniformtext_mode': 'hide',
            'uniformtext_minsize': 12,
            'legend': {
                'orientation': 'h',
                'x': 0,
                'y': 1.1, 
                'bgcolor':
                'rgba(255, 255, 255, 0)',
                'bordercolor':'rgba(255, 255, 255, 0)'
            }
        }

        value_column = 'log_percentv4' if log_scale_active else 'percentv4'
        #print("Using column for values:", value_column)
        if active_dataset.get('dataset') == 'ipv4':
            if active_item == 'TotalPool':
                
                df = self.data_handler.json_df
                log_values = np.log10(df['percentv4'] + 0.0001)
                df['log_percentv4'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))
                #print("View Mode before conditional:", view_mode)
                #print('it works')
                if view_mode == 'top10':
                    df = df.nlargest(10, 'percentv4')
                elif view_mode == 'bottom10':
                    df = df.nsmallest(10, 'percentv4')
                    #print(df.tail(10))
                #print("View Mode afcter:", view_mode)
                #print("Data preview:", df.head())
                hover_data={
                    'name': True,
                    'ipv4': ':,.0f',
                    'pop': ':,.0f',
                    'percentv4': ':.2f',
                    #'pcv4': ':.2f',
                    #'iso_alpha_3': False,
                    #'ipv4_grouping': True,
                    #'log_ipv4': False
                }
                #customdata = self.populate_custom_data(active_item, active_dataset)
                #hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
                
                values = value_column
                names = 'name'
            elif active_item == 'RIR':
                df = self.calculate_rir_percentages()
                values = 'percentv4'
                names = 'RIR'

            elif active_item == 'RIPENCC':
                ripencc_data = self.calculate_rir_country_data(self.data_handler.json_df, 'RIPENCC')
                df = ripencc_data
                values = 'percentv4'
                names = 'name'

            elif active_item == 'ARIN':
                df = self.calculate_rir_country_data(self.data_handler.json_df, 'ARIN')
                values = 'percentv4'
                names = 'name'
            
            elif active_item == 'APNIC':
                df = self.calculate_rir_country_data(self.data_handler.json_df, 'APNIC')
                values = 'percentv4'
                names = 'name'
            
            elif active_item == 'LACNIC':
                df = self.calculate_rir_country_data(self.data_handler.json_df, 'LACNIC')
                values = 'percentv4'
                names = 'name'

            elif active_item == 'AFRINIC':
                df = self.calculate_rir_country_data(self.data_handler.json_df, 'AFRINIC')
                values = 'percentv4'
                names = 'name'
            elif active_item == 'SUNBURST':
                df = self.data_handler.json_df
                print(df.dtypes)
                #print(customdata[0])
                '''Bug Squashing'''
                # Check for any unique non-numeric values that might be interpreted as strings
                print(df['pop'].apply(lambda x: type(x)).unique())

                # Quick summary to find any other anomalies
                print(df['pop'].describe())

                # columns_to_check = ['pop', 'ipv4', 'percentv4', 'pcv4']

                # # Step 1: Check for NaNs in each column and print the counts
                # print("NaN counts in each column:")
                # for column in columns_to_check:
                #     nan_count = df[column].isna().sum()
                #     print(f"{column}: {nan_count}")

                # # Step 2: Print rows where any of the specified columns have NaN values
                # print("\nSample rows with NaN values:")
                # nan_rows = df[df[columns_to_check].isna().any(axis=1)]
                # print(nan_rows.head())
                # df['ipv4'] = df['ipv4'].astype(int)
                # df['pop'] = df['pop'].astype(int)
                # df['percentv4'] = df['percentv4'].astype(float)
                # df['pcv4'] = df['pcv4'].astype(float)


                df['percentv4'] = df['percentv4'] / 100
                #values = 'percentv4'
                #names = 'name'
                sun_fig = px.sunburst(
                    df,
                    path=['RIR', 'name'],
                    values='ipv4', 
                    color='RIR',
                    #hover_data=['name', 'pop', 'percentv4'],
                    color_continuous_scale='Viridis',
                    template=template,
                    hover_data={
                        'pop':True,
                        'ipv4':True,
                        'percentv4':True
                    }
                )
                layout_options = {
                    #'template': template,
                    'showlegend': show_legend,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'uniformtext_mode': 'hide',
                    'uniformtext_minsize': 12,
                    'legend': {
                        'orientation': 'h',
                        'x': 0,
                        'y': 1.1, 
                        'bgcolor':
                        'rgba(255, 255, 255, 0)',
                        'bordercolor':'rgba(255, 255, 255, 0)'
                    }
                }
                sun_fig.update_traces(
                    hovertemplate=(
                        "<b>%{label}</b><br>" +
                        "Population: %{customdata[0]:,}<br>" +  # Adds commas as thousands separators
                        "IPv4 Address Count: %{customdata[1]:,}<br>" +  # Adds commas here too, if needed
                        "Percent of IPv4 Pool: %{customdata[2]:.2%}<br>"  # Correctly formats percentage
                    )
                )
                    
                # trace_options = {
                #     'hovertemplate':"<b>%{label}</b><br>Population: %{customdata[1]:,}<br>IPv4: %{customdata[2]:,}<br>Percent IPv4: %{customdata[3]:.2%}<extra></extra>",
                #     'hoverinfo': 'label+percent+name',
                #     'customdata':df[['name', 'pop', 'ipv4', 'percentv4']]
                # }
                #print("Custom Data: ", sun_fig.data[0].customdata)
                #print("Current Hover Template: ", sun_fig.data[0].hovertemplate)
                return sun_fig
            else:
                df = self.get_data_by_rir(active_item)
                values = 'percentv4'
                names = 'name'


        if active_dataset == 'whoisv4':
            customdata = self.populate_custom_data(active_item, active_dataset)
            hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
            df = self.data_handler.whois_ipv4_df
            values = 'Value'
            names = 'Registry'

        elif active_dataset=='whoisv4':
            df = self.data_handler.whois_ipv4_df
            values = 'Start' 
            names = 'Registry'

        pie_fig = px.pie(
            df,
            values=values,
            names=names,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hover_data=hover_data,
        ) #, custom_data=customdata, hover_data=hover_data
        pie_fig.update_traces(**trace_options)
        pie_fig.update_layout(**layout_options)
        return pie_fig
