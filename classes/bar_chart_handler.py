import plotly.express as px
import pandas as pd
import numpy as np

class BarChartHandler:
    def __init__(self,  data_handler):
        self.data_handler = data_handler

    def calculate_rir_percentages(self):
        df = self.data_handler.json_df
        return df.groupby('RIR')['percentv4'].sum().reset_index()

    def get_data_by_rir(self, RIR):
        df = self.data_handler.json_df
        return df[df['RIR'] == RIR]

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

    def case_df_processing(self, df, log_scale_active, view_mode):
        value_column = 'log_percentv4' if log_scale_active else 'percentv4'

        log_values = np.log10(df['percentv4'] + 0.0001)
        df['log_percentv4'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))

        if view_mode == 'top10':
            df = df.nlargest(10, 'percentv4').copy()
        elif view_mode == 'bottom10':
            df = df.nsmallest(10, 'percentv4').copy()

        return df, value_column

    def generate_figure(self, active_item, active_dataset, switch_on, log_scale_active=False, view_mode='all'):
        data_frame = None
        x = None
        y = None
        customdata = None
        hover_template = None
        hover_data = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'

        print('in bar chart generate figure', log_scale_active)
        print('in bar chart generate figure', view_mode)
        print("Log scale active:", log_scale_active)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item)
       # customdata = self.populate_custom_data(active_item, active_dataset)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
        # print(active_item, active_dataset.get('dataset'))
        # trace_options = {
        #     'textposition': 'inside',
        #     #'hovertemplate': hover_template
        # }
        #layout_options = {'showlegend': True, 'margin': dict(t=50, b=50, l=50, r=50), 'uniformtext_mode': 'hide', 'uniformtext_minsize': 12, 'height': 400, 'width': 400}
        # layout_options = {
        #     'showlegend': True,
        #     'margin': dict(t=50, b=50, l=50, r=50),
        #     'uniformtext_mode': 'hide',
        #     'uniformtext_minsize': 12,
        #     'legend': {
        #         'orientation': 'h',
        #         'x': 0,
        #         'y': 1.1, 
        #         'bgcolor':
        #         'rgba(255, 255, 255, 0)',
        #         'bordercolor':'rgba(255, 255, 255, 0)'
        #     }
        # }
        if active_dataset.get('dataset') == 'ipv4':
            if active_item == 'RIR':
                rir_sum = self.data_handler.json_df.groupby('RIR')['ipv4'].sum().reset_index() 
                data_frame=rir_sum
                x='RIR'
                y='ipv4'

                layout_options = {
                    'xaxis_tickangle':-25,
                    'yaxis_type':'linear',
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                }
            elif active_item in ['RIPENCC', 'ARIN', 'AFRINIC', 'LACNIC', 'APNIC']:
                modified_df=self.calculate_rir_country_data(self.data_handler.json_df, active_item)    
                df=modified_df

                x_axis = 'log' if log_scale_active else 'linear'

                log_values = np.log10(df['percentv4'] + 0.0001)
                df['log_percentv4'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))

                if view_mode == 'top10':
                    df = df.nlargest(10, 'percentv4').copy()
                elif view_mode == 'bottom10':
                    df = df.nsmallest(10, 'percentv4').copy()


                x=df['name']
                y=df['percentv4']

                layout_options = {
                    'xaxis_tickangle':-40,
                    'yaxis_type':x_axis,
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                }
        
        fig = px.bar(data_frame, x, y, color=y,color_continuous_scale=px.colors.sequential.Viridis, template=template) #, custom_data=customdata, hover_data=hover_data
        #fig.update_traces(**trace_options)
        fig.update_layout(**layout_options)

        return fig

