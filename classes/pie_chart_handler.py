import plotly.express as px

class PieChartHandler:
    def __init__(self, data_handler): #, hover_template_handler
        self.data_handler = data_handler
        #self.hover_template_handler = hover_template_handler

    def calculate_rir_percentages(self):
        df = self.data_handler.json_df
        return df.groupby('RIR')['percentv4'].sum().reset_index()

    def get_data_by_rir(self, rir):
        df = self.data_handler.json_df
        return df[df['RIR'] == rir]

    def generate_figure(self, dataset_selector, selected_value, show_legend=True, opacity=1.0):
        df = None
        value = None
        names = None
        
        trace_options = {
            'textposition': 'inside',
            'opacity': opacity,
            #'hovertemplate': hover_template
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
                df = self.data_handler.json_df
                values = 'percentv4'
                names = 'name'
            elif dataset_selector == 'WHOIS':
                df = self.data_handler.whois_ipv4_df
                values = 'Value'
                names = 'Registry'
        elif selected_value == 'RIR':
            if dataset_selector == 'IPv4':
                df = self.calculate_rir_percentages()
                values = 'percentv4'
                names = 'RIR'
            else:
                df = self.data_handler.whois_ipv4_df
                values = 'Start' 
                names = 'Registry'
        else:
            df = self.get_data_by_rir(selected_value)
            values = 'percentv4'
            names = 'name'

        pie_fig = px.pie(df, values=values, names=names)
        pie_fig.update_traces(**trace_options)
        pie_fig.update_layout(**layout_options)

        return pie_fig