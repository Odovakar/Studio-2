import plotly.express as px
import pandas as pd

class ScatterHandler:
    def __init__(self, data_handler):#, hover_template_handler):
        self.data_handler = data_handler
        #self.hover_template_handler = hover_template_handler
    

    def generate_figure(self, scale_type):
        trace_options = []
        layout_options = []

        ipv4_group_to_ticks = {
        '0-10k': 0-10000,        # Midpoint of the range as representative value
        '10k-100k': 55000,
        '100k-1M': 550000,
        '1M-10M': 5500000,
        '10M-100M': 55000000,
        '100M-1B': 550000000,
        '1B+': 1500000000
        }

        if scale_type == 'normal':
            scatter_fig = px.scatter(
                data_frame=self.data_handler.json_df,
                x='pop',
                y='ipv4',
                hover_name="name",
                color='ipv4_grouping',
                size_max=60,
                title='Population Size vs. Number of IPv4 Addresses by Country',
                labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
                size="ipv4"
            )
            # Log scale settings
            scatter_fig.update_xaxes(type='log', title_text='Population Size (Log Scale)')
            scatter_fig.update_yaxes(type='log',
                                    tickvals=list(ipv4_group_to_ticks.values()),
                                    ticktext=list(ipv4_group_to_ticks.keys()))
            
            # Update marker sizes
            max_ipv4 = self.data_handler.json_df['ipv4'].max()
            desired_max_marker_size = 100
            sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 2)
            scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=sizeref, sizemin=4))

        elif scale_type == 'log':
            scatter_fig = px.scatter(
                data_frame=self.data_handler.json_df,
                x='pop',
                y='ipv4',
                hover_name="name",
                color='log_ipv4',
                size='ipv4',
                size_max=60,
                title='Population Size vs. Number of IPv4 Addresses by Country',
                labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
                log_x=True,
                log_y=True,
                color_continuous_scale='Viridis'
                #color_discrete_map=self.get_colorscale(scale_type)
            )
            
            # Highlight significant outliers (e.g., USA) with annotations if needed
            if 'USA' in self.data_handler.json_df['iso_alpha_3'].values:
                usa_ipv4 = self.data_handler.json_df.loc[self.data_handler.json_df['iso_alpha_3'] == 'USA', 'ipv4'].iloc[0]
                usa_pop = self.data_handler.json_df.loc[self.data_handler.json_df['iso_alpha_3'] == 'USA', 'pop'].iloc[0]
                scatter_fig.add_annotation(x=usa_pop, y=usa_ipv4, text="USA", showarrow=True, arrowhead=1)

            max_ipv4 = self.data_handler.json_df['ipv4'].max()
            desired_max_marker_size = 75
            sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 2)
            scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=sizeref, sizemin=4))

        return scatter_fig


    def update_traces(self, selected_value):
        if selected_value=='normal':
            pass