import plotly.express as px
import pandas as pd
import numpy as np
from io import StringIO

class ScatterHandler:
    def __init__(self, data_handler):#, hover_template_handler
        self.data_handler = data_handler
        #self.hover_template_handler = hover_template_handler
    
    def update_traces(self, selected_value):
        if selected_value=='normal':
            pass

    def selected_unselected_functionality(self):
        selected = dict(marker=dict(opacity=1))
        unselected = dict(marker=dict(opacity=0.1)) # Dim non-selected points
        return selected, unselected

    def generate_figure(self, active_item, active_dataset, switch_on):
        trace_options = []
        layout_options = []
        fig = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        print(active_dataset)
        data_json_stream = StringIO(active_dataset['data'])

        ipv4_group_to_ticks = {
            '0-10k': 0-10000,        # Midpoint of the range as representative value
            '10k-100k': 55000,
            '100k-1M': 550000,
            '1M-10M': 5500000,
            '10M-100M': 55000000,
            '100M-1B': 550000000,
            '1B+': 1500000000
        }

        
        if active_dataset.get('dataset') == 'ipv4':
            if active_item == 'normal':
                df = pd.read_json(data_json_stream, orient='split')
                selected, unselected = self.selected_unselected_functionality()
                
                scatter_fig = px.scatter(
                    df,
                    x='pop',
                    y='ipv4',
                    color='ipv4_grouping',
                    size_max=60,
                    title='Population Size vs. Number of IPv4 Addresses by Country',
                    size='ipv4',
                    template=template,
                    hover_data={
                        'name': True,
                        'ipv4': True,
                        'pop': True,
                        'percentv4': True,
                        'pcv4': True
                    }
                )
                
                scatter_fig.update_xaxes(type='log', title_text='Population Size (Logarithmic Scale)')
                scatter_fig.update_yaxes(type='log', title_text='Number of IPv4 Addresses', tickvals=list(ipv4_group_to_ticks.values()), ticktext=list(ipv4_group_to_ticks.keys()))
                
                hover_template='<b>%{customdata[0]}</b><br>' + \
                                'IPv4: %{y:,.0f}<br>' + \
                                'Population: %{x:,.0f}<br>' + \
                                'Pct of IPv4 Pool: %{customdata[1]:.2f}%<br>' + \
                                'Pct Per Capita: %{customdata[2]:.2f}%'
                
                # Update marker sizes
                max_ipv4 = df['ipv4'].max()
                desired_max_marker_size = 25
                sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 3)
                scatter_fig.update_traces(
                    marker=dict(
                        sizemode='area',
                        sizeref=sizeref,
                        sizemin=6.5
                    ),
                    hovertemplate=hover_template,
                    selected=selected,
                    unselected=unselected
                )
                scatter_fig.update_layout(
                    legend=dict(
                        title='IPv4 Grouping',
                        orientation="h",
                        xanchor="center",
                        x=0.5,
                        yanchor="top",
                        y=-0.2
                    ),
                    margin=dict(b=150),
                    clickmode='event+select'
                )

            elif active_item == 'log':
                df = pd.read_json(data_json_stream, orient='split')
                selected, unselected = self.selected_unselected_functionality()
                scatter_fig = px.scatter(
                    df,
                    y='pcv4',
                    x='pop',
                    size='ipv4',
                    size_max=30,
                    title='Population Size vs. Number of IPv4 Addresses by Country',
                    color='log_ipv4',
                    log_x=True,
                    log_y=True,
                    color_continuous_scale='Viridis',
                    template=template,
                    hover_data={
                        'name': True,
                        'ipv4': True,
                        'percentv4': True,
                        'pcv4': True
                    }
                )
                
                # Tweaks to the plots
                max_ipv4 = df['ipv4'].max()
                desired_max_marker_size = 27
                sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 3.5)

                hover_template='<b>%{customdata[0]}</b><br>' + \
                                'IPv4: %{customdata[1]:,.0f}<br>' + \
                                'Population: %{x}<br>' + \
                                'Pct of IPv4 Pool: %{customdata[2]:.2f}%<br>' + \
                                'Pct Per Capita: %{y:.2f}%'

                scatter_fig.update_traces(
                    marker=dict(sizemode='area',
                                sizeref=sizeref,
                                sizemin=7),
                    selected=selected,
                    unselected=unselected,
                    hovertemplate=hover_template
                )
                
                scatter_fig.update_xaxes(title_text='Population Size (Logarithmic Scale)')
                scatter_fig.update_yaxes(title_text='IPv4 Percentage of Pool per Capita (Logarithmic Scale)')
                
                scatter_fig.update_layout(
                    coloraxis_colorbar=dict(
                    title='Log IPv4',
                    orientation='h',
                    x=0.5,
                    xanchor='center',
                    y=-0.3,
                    yanchor='bottom',
                    thicknessmode='pixels',
                    thickness=20,
                    len=0.5,  # Adjusts the length of the colorbar to 80% of the axis length
                    ),
                    margin={'r':5, 't':50, 'l':5, 'b':20},
                    clickmode='event+select'
                )

            if active_item == 'v6log':
                df = pd.read_json(data_json_stream, orient='split')
                print(df.columns.tolist())

                df['ipv6'] = df['ipv6'].apply(lambda x: x if x > 0 else 1.1)
                df['log_ipv6'] = np.log10(df['ipv6'])
                px.scatter(

                )
            return scatter_fig