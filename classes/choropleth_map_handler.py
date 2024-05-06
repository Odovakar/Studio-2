import plotly.express as px
import numpy as np
import pandas as pd
from io import StringIO

class ChoroplethHandler:
    def __init__ (self, data_handler, hover_template_handler):
        self.data_handler = data_handler
        self.hover_template_handler = hover_template_handler

    # def get_hovertemplate(self, choropleth_accordion_selector):
    #     if choropleth_accordion_selector=='grouped':
    #         hover_template='<b>%{customdata[0]}</b><br>' + \
    #                     'IPv4: %{customdata[1]:,.0f}<br>' + \
    #                     'Population: %{customdata[2]:,.0f}<br>' + \
    #                     'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
    #                     'IPv4 per Cap: %{customdata[4]:.2f}%' + \
    #                     '<extra>IPv4 Grouping: %{customdata[6]}</extra>'
    #         return hover_template
    #     elif choropleth_accordion_selector=='log':
    #         hover_template='<b>%{customdata[0]}</b><br>' + \
    #                     'IPv4: %{customdata[1]:,.0f}<br>' + \
    #                     'Population: %{customdata[2]:,.0f}<br>' + \
    #                     'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
    #                     'IPv4 per Cap: %{customdata[4]:.2f}%' + \
    #                     '<extra>Log IPv4: %{customdata[7]:.2f}</extra>'
    #         return hover_template

    # Color scale in function for easier code reusability -- Might add some more conditionals later when scaling for other graphs
    def get_colorscale(self, choropleth_accordion_selector):
        if choropleth_accordion_selector == 'normal':
            colors = {
                '0-10K': 'rgb(15, 246, 228)',
                '10K-100K': 'rgb(0, 229, 255)',
                '100K-1M': 'rgb(0, 208, 255)',
                '1M-10M': 'rgb(86, 187, 255)',
                '10M-100M': 'rgb(141, 160, 255)',
                '100M-1B': 'rgb(207, 104, 255)',
                '1B+': 'rgb(250, 0, 196)'
            }
            return colors

    def generate_figure(self, active_item, active_dataset, switch_on):
        hover_template = self.hover_template_handler.get_hover_template(active_item)
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        #active_dataset = None
        # map_fig = None

        #print(active_dataset)
        # customdata = np.stack((
        #     self.data_handler.json_df['name'],          # Country name
        #     self.data_handler.json_df['ipv4'],          # IPv4 address count
        #     self.data_handler.json_df['pop'],           # Population size
        #     self.data_handler.json_df['percentv4'],     # Percent of IPv4 pool
        #     self.data_handler.json_df['pcv4'],          # IPv4 per capita percentage
        #     #json_df['log_ipv4']       # Log of IPv4 for the logarithmic map
        # ), axis=-1)
        # df = pd.read_json(active_dataset['data'], orient='split')
        # print(df.head())
        #print(active_item, 'in choropleth generate figure')
        data_json_stream = StringIO(active_dataset['data'])
        if active_item=='normal':
            colors=self.get_colorscale(active_item)
            hover_template = self.hover_template_handler.get_hover_template(active_item)
            df = pd.read_json(data_json_stream, orient='split') 
            map_fig = px.choropleth(
                data_frame=df,
                locations='iso_alpha_3',
                color='ipv4_grouping',
                hover_name='name',
                color_discrete_map=colors,
                locationmode='ISO-3',
                hover_data={
                    'name': True,
                    'ipv4': ':,.0f',
                    'pop': ':,.0f',
                    'percentv4': ':.2f',
                    'pcv4': ':.2f',
                    'iso_alpha_3': False,
                    'ipv4_grouping': True,
                    'log_ipv4': False
                }
            )
            map_fig.update_layout(
                autosize=True,
                legend=dict(
                    title="IPv4 Groups",
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.1,
                    yanchor="bottom",
                    itemsizing="constant",
                ),
                template=template
                #margin={"r":5, "t":5, "l":5, "b":5},
            )
            map_fig.update_traces(hovertemplate=hover_template)
            map_fig.update_geos(showframe=False, projection_type='equirectangular', lonaxis_range=[-180, 180], lataxis_range=[-60, 90])
            map_fig.update_layout()
            return map_fig
        elif active_item=='log':
            # Generate the choropleth map
            hover_template = self.hover_template_handler.get_hover_template(active_item)
            map_fig = px.choropleth(
                data_frame=pd.read_json(data_json_stream, orient='split'),
                locations='iso_alpha_3',
                color='log_ipv4',
                hover_name='name',
                color_continuous_scale=px.colors.sequential.Viridis,
                range_color=[self.data_handler.json_df['log_ipv4'].min(), self.data_handler.json_df['log_ipv4'].max()],
                locationmode='ISO-3',
                hover_data={
                    'name': True,
                    'ipv4': ':,.0f',
                    'pop': ':,.0f',
                    'percentv4': ':.2f',
                    'pcv4': ':.2f',
                    'iso_alpha_3': False,
                    'ipv4_grouping': False,
                    'log_ipv4': True
                },
            )
            map_fig.update_layout(
                coloraxis_colorbar=dict(
                    title="Log IPv4",
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.1,
                    yanchor="bottom",
                    thicknessmode="pixels",
                    thickness=20,
                    len=0.5,  
                ),
                template=template
            )

            map_fig.update_traces(hovertemplate=hover_template)
            map_fig.update_geos(showframe=False, projection_type='equirectangular', lonaxis_range=[-180, 180], lataxis_range=[-60, 90])
            return map_fig  
        
        if active_item == 'v6log':
            #df = pd.read_json(data_json_stream, orient='split')
            df = pd.read_json(data_json_stream, orient='split')
            print(df.columns.tolist())

            df['ipv6'] = df['ipv6'].apply(lambda x: x if x > 0 else 1.1)
            df['log_ipv6'] = np.log10(df['ipv6'])
            # highest = df['log_ipv6'].max()
            # lowest = df['log_ipv6'].min()
            # middle = df['log_ipv6'].median()
            # zero_count = (df['log_ipv6'] == 0).sum()
            # Apply log10

            # print(f"Number of zero values: {zero_count}")
            # print(f"Highest value: {highest}")
            # print(f"Lowest value: {lowest}")
            # print(f"Middle value: {middle}")
            min_value = df['log_ipv6'].quantile(0.1)
            max_value = df['log_ipv6'].quantile(0.9)

            map_fig = px.choropleth(
                df,
                locations='iso_alpha_3',
                color='log_ipv6',
                hover_name='name',
                color_continuous_scale=px.colors.sequential.Plasma_r,
                range_color=[min_value, max_value],
                locationmode='ISO-3',
            )
            map_fig.update_layout(
                coloraxis_colorbar=dict(
                    title="Log IPv4",
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.1,
                    yanchor="bottom",
                    thicknessmode="pixels",
                    thickness=20,
                    len=0.5,  
                ),
                template=template
            )
            map_fig.update_geos(showframe=False, projection_type='equirectangular', lonaxis_range=[-180, 180], lataxis_range=[-60, 90])

            #hover_template = self.hover_template_handler.get_hover_template(active_item)
            # map_fig = px.choropleth(
            #     data_frame=df,
            #     locations='iso_alpha_3',
            #     color='log_ipv6',
            #     hover_name='name',
            #     #color_continuous_scale=px.colors.sequential.Viridis,
            #     range_color=[0, 0.65],
            #     locationmode='ISO-3',
                # hover_data={
                #     'name': True,
                #     'ipv6': ':,.0f',
                #     'pop': ':,.0f',
                #     'percentv6': ':.2f',
                #     'pcv6': ':.2f',
                #     'iso_alpha_3': False,
                #     #'ipv4_grouping': False,
                #     'log_ipv6': True
                # },
            # )
            # map_fig.update_layout(
            #     coloraxis_colorbar=dict(
            #         title="Log IPv6",
            #         orientation="h",
            #         x=0.5,
            #         xanchor="center",
            #         y=-0.1,
            #         yanchor="bottom",
            #         thicknessmode="pixels",
            #         thickness=20,
            #         len=0.5,  
            #     ),
            #     template=template
            # )
            #map_fig.update_traces(hovertemplate=hover_template)
            #map_fig.update_geos(showframe=False, projection_type='equirectangular', lonaxis_range=[-180, 180], lataxis_range=[-60, 90])
            return map_fig