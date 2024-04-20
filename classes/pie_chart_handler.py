import plotly.express as px

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

    def populate_custom_data(self, selected_value, dataset_selector):
        customdata = None
        if selected_value=='Totalpool':
            if dataset_selector=='IPv4':
                df = self.data_handler.json_df
                customdata=df[['name', 'ipv4', 'pop', 'percentv4', 'pcv4', 'iso_alpha_3', 'ipv4_grouping', 'log_ipv4']].to_dict('records')
                return customdata

    def calculate_rir_country_data(self, df, selected_value):
        if selected_value == 'ARIN':
            arin_data = df[df['RIR'] == 'ARIN']
            return arin_data
        elif selected_value == 'APNIC':
            apnic_data = df[df['RIR'] == 'APNIC']
            return apnic_data
        elif selected_value == 'RIPENCC':
            ripencc_data = df[df['RIR'] == 'RIPE NCC']
            return ripencc_data
        elif selected_value == 'LACNIC':
            lacnic_data = df[df['RIR'] == 'LACNIC']
            return lacnic_data
        elif selected_value == 'AFRINIC':
            afrinic_data = df[df['RIR'] == 'AFRINIC']
            return afrinic_data
        else:
            return None


    def generate_figure(self, dataset_selector, selected_value, show_legend=True, opacity=1.0):
        df = None
        values = None
        names = None
        customdata = None
        hover_template = None
        hover_data = None
        #hover_template = self.hover_template_handler.get_pie_hover_template(selected_value)
       # customdata = self.populate_custom_data(selected_value, dataset_selector)
        #hover_template = self.hover_template_handler.get_pie_hover_template(selected_value, customdata)


        trace_options = {
            'textposition': 'inside',
            'opacity': opacity,
            'hovertemplate': hover_template
        }
        #layout_options = {'showlegend': True, 'margin': dict(t=50, b=50, l=50, r=50), 'uniformtext_mode': 'hide', 'uniformtext_minsize': 12, 'height': 400, 'width': 400}
        layout_options = {
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
        if selected_value == 'TotalPool':
            if dataset_selector == 'IPv4':
                customdata = self.populate_custom_data(selected_value, dataset_selector)
                hover_template = self.hover_template_handler.get_pie_hover_template(selected_value, customdata)
                df = self.data_handler.json_df
                values = 'percentv4'
                names = 'name'

            elif dataset_selector == 'WHOIS':
                customdata = self.populate_custom_data(selected_value, dataset_selector)
                hover_template = self.hover_template_handler.get_pie_hover_template(selected_value, customdata)
                df = self.data_handler.whois_ipv4_df
                values = 'Value'
                names = 'Registry'

        elif selected_value == 'RIR':
            if dataset_selector == 'IPv4':
                df = self.calculate_rir_percentages()
                values = 'percentv4'
                names = 'RIR'
            elif dataset_selector=='WHOIS':
                df = self.data_handler.whois_ipv4_df
                values = 'Start' 
                names = 'Registry'
        elif selected_value == 'RIPENCC':
            ripencc_data = self.calculate_rir_country_data(self.data_handler.json_df, 'RIPENCC')
            df = ripencc_data
            values = 'percentv4'
            names = 'name'

        elif selected_value == 'ARIN':
            df = self.calculate_rir_country_data(self.data_handler.json_df, 'ARIN')
            #df = arin_data
            values = 'percentv4'
            names = 'name'
        
        elif selected_value == 'APNIC':
            df = self.calculate_rir_country_data(self.data_handler.json_df, 'APNIC')
            values = 'percentv4'
            names = 'name'
        
        elif selected_value == 'LACNIC':
            df = self.calculate_rir_country_data(self.data_handler.json_df, 'LACNIC')
            values = 'percentv4'
            names = 'name'

        elif selected_value == 'AFRINIC':
            df = self.calculate_rir_country_data(self.data_handler.json_df, 'AFRINIC')
            values = 'percentv4'
            names = 'name'
        
        else:
            df = self.get_data_by_rir(selected_value)
            values = 'percentv4'
            names = 'name'

        pie_fig = px.pie(df, values=values, names=names, custom_data=customdata) #, hover_data=hover_data
        pie_fig.update_traces(**trace_options)
        pie_fig.update_layout(**layout_options)

        return pie_fig