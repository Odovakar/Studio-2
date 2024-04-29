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


    def generate_figure(self, active_item, active_dataset, switch_on, show_legend=True):#, show_legendshow_legend=True, , opacity=1.0
        df = None
        values = None
        names = None
        customdata = None
        hover_template = None
        hover_data = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        opacity = 0.5 if show_legend else 1.0
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item)
       # customdata = self.populate_custom_data(active_item, active_dataset)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
        # print(active_item, active_dataset.get('dataset'))
        trace_options = {
            'textposition': 'inside',
            'opacity': opacity,
            'hovertemplate': hover_template
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
        # IPV4 POOL DATA

        if active_dataset.get('dataset') == 'ipv4':
            if active_item == 'TotalPool':
                #print('it works')
                customdata = self.populate_custom_data(active_item, active_dataset)
                hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
                df = self.data_handler.json_df
                values = 'percentv4'
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
                #values = 'percentv4'
                #names = 'name'
                sun_fig = px.sunburst(
                    df,
                    path=['RIR', 'name'],
                    values='ipv4', 
                    color='RIR',
                    #hover_data=['name', 'pop', 'percentv4'],
                    color_continuous_scale='Viridis',
                    template=template
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

        pie_fig = px.pie(df, values=values, names=names, color_discrete_sequence=px.colors.qualitative.Pastel) #, custom_data=customdata, hover_data=hover_data
        pie_fig.update_traces(**trace_options)
        pie_fig.update_layout(**layout_options)
        return pie_fig
