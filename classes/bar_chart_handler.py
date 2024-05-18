import plotly.express as px
import pandas as pd
import numpy as np
from io import StringIO

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
        # Match based on lists
        if active_item in ['ARIN', 'ARINV6']:
            return df[df['RIR'] == 'ARIN']
        elif active_item in ['APNIC', 'APNICV6']:
            return df[df['RIR'] == 'APNIC']
        elif active_item in ['RIPENCC', 'RIPENCCV6']:
            return df[df['RIR'] == 'RIPE NCC']
        elif active_item in ['LACNIC', 'LACNICV6']:
            return df[df['RIR'] == 'LACNIC']
        elif active_item in ['AFRINIC', 'AFRINICV6']:
            return df[df['RIR'] == 'AFRINIC']
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

    def generate_figure(self, active_item, active_dataset, switch_on, allocation_version, log_scale_active=False, view_mode='all'):
        data_frame = None
        x = None
        y = None
        customdata = None
        hover_template = None
        hover_data = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        x_axis = 'log' if log_scale_active else 'linear'
        data_json_stream = StringIO(active_dataset['data'])
        allocation_version = allocation_version.get('allocation_type')
        #print(allocation_version, 'not working?')
        #print('dataframe is', active_dataset.get('dataset'))
        #print('in bar chart generate figure', log_scale_active)
        #print('in bar chart generate figure', view_mode)
        #print("Log scale active:", log_scale_active)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item)
       # customdata = self.populate_custom_data(active_item, active_dataset)
        #hover_template = self.hover_template_handler.get_pie_hover_template(active_item, customdata)
        # print(active_item, active_dataset.get('dataset'))
        # trace_options = {
        #     'textposition': 'inside',
        #     #'hovertemplate': hover_template
        #     'textinfo': 'percent+label'
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
        #print(x_axis, 'outside conditional')
        #print(active_dataset)
        print(active_item)
        
        if allocation_version == 'ipv4':
            df = pd.read_json(data_json_stream, orient='split')
            if active_item == 'RIR':
                rir_sum = df.groupby('RIR')['ipv4'].sum().reset_index()
                df=rir_sum
                x='RIR'
                y='ipv4'
                color_continuous_scale=px.colors.sequential.Viridis
                layout_options = {
                    'xaxis_tickangle':-25,
                    'yaxis_type':'linear',
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'xaxis_title': 'Regional Internet Registry',
                    'yaxis_title': 'Sum of Total IPv4 Addresses',
                    'coloraxis_colorbar': dict(title='IPv4 Total')
                }
            elif active_item in ['RIPENCC', 'ARIN', 'AFRINIC', 'LACNIC', 'APNIC']:
                df=self.calculate_rir_country_data(df, active_item)    
                #print(active_item)
                log_values = np.log10(df['percentv4'] + 0.0001)
                df['log_percentv4'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))

                #print(df.columns.tolist())
                if view_mode == 'top10':
                    df = df.nlargest(10, 'percentv4').copy()
                elif view_mode == 'bottom10':
                    df = df.nsmallest(10, 'percentv4').copy()

                x=df['name']
                y=df['percentv4']
                color_continuous_scale=px.colors.sequential.Viridis
                layout_options = {
                    'xaxis_tickangle':-40,
                    'yaxis_type':x_axis,
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'xaxis_title': 'Country',
                    'yaxis_title': 'Percent of IPv4 Pool',
                    'coloraxis_colorbar': dict(title='Pct v4')
                }
                # trace_options = {
                #     'textposition': 'inside',
                #     #'hovertemplate': hover_template
                #     'textinfo': 'percent+label'
                # }
            elif active_item == 'GLOBALBAR':
                df = pd.read_json(data_json_stream, orient='split')
                log_values = np.log10(df['percentv4'] + 0.0001)
                df['log_percentv4'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))
                #print(df.columns.tolist())
                if view_mode == 'top10':
                    df = df.nlargest(10, 'percentv4').copy()
                elif view_mode == 'bottom10':
                    df = df.nsmallest(10, 'percentv4').copy()

                x=df['name']
                y=df['percentv4']
                color_continuous_scale=px.colors.sequential.Viridis
                layout_options = {
                    'xaxis_tickangle':-40,
                    'yaxis_type':x_axis,
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'xaxis_title': 'Country',
                    'yaxis_title': 'Percent of IPv4 Pool',
                    'coloraxis_colorbar': dict(title='Pct v4')
                }
                

        if allocation_version == 'ipv6':
            df = pd.read_json(data_json_stream, orient='split')
            if active_item == 'RIRV6':
                rir_sum = df.groupby('RIR')['ipv6'].sum().reset_index()
                df=rir_sum
                x='RIR'
                y='ipv6'
                color_continuous_scale=px.colors.sequential.Plasma_r
                layout_options = {
                    'xaxis_tickangle':-25,
                    'yaxis_type':'linear',
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'xaxis_title': 'Regional Internet Registry',
                    'yaxis_title': 'Sum of Total IPv6 Pool',
                    'coloraxis_colorbar': dict(title='IPv6 Total')
                }
            
            elif active_item in ['RIPENCCV6', 'ARINV6', 'AFRINICV6', 'LACNICV6', 'APNICV6']:
                df=self.calculate_rir_country_data(df, active_item) 

                log_values = np.log10(df['percentv6'] + 0.0001)
                df['log_percentv6'] = (log_values - np.min(log_values)) / (np.max(log_values) - np.min(log_values))

                if view_mode == 'top10':
                    df = df.nlargest(10, 'percentv4').copy()
                elif view_mode == 'bottom10':
                    df = df.nsmallest(10, 'percentv4').copy()
                color_continuous_scale=px.colors.sequential.Plasma_r

                x=df['name']
                y=df['percentv6']

                layout_options = {
                    'xaxis_tickangle':-40,
                    'yaxis_type':x_axis,
                    'autosize':True,
                    'margin': dict(t=50, b=50, l=50, r=50),
                    'xaxis_title': 'Country',
                    'yaxis_title': 'Percent of IPv6 Pool',
                    'coloraxis_colorbar': dict(title='Pct v6')
                }

        if active_dataset.get('dataset') == 'v4_allocation':  
            if active_item == 'UNVSALLOCATED':
                df = pd.read_json(active_dataset['data'], orient='split')
                #print('inside conditional in bar chart unvsallocated')
                stack_fig = px.bar(
                    df,
                    x = 'Registry',
                    y = 'Value',
                    barmode='group',
                    color='Status',
                    template=template,
                    color_continuous_scale=px.colors.sequential.Viridis,
                )



                return stack_fig
        
        fig = px.bar(df, x, y, color=y,color_continuous_scale=color_continuous_scale, template=template) #, custom_data=customdata, hover_data=hover_data
        #fig.update_traces(**trace_options)
        fig.update_layout(**layout_options)

        return fig

