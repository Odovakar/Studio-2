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

    def generate_figure(self, active_item, active_dataset, switch_on):#, allocation_version
        trace_options = []
        layout_options = []
        fig = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        #print(active_dataset)
        data_json_stream = StringIO(active_dataset['data'])

        #(active_item, 'in generate figure scatter plot')
        ipv4_group_to_ticks = {
            '0-10k': 1e4,
            '10k-100k': 1e5,
            '100k-1M': 1e6,
            '1M-10M': 1e7,
            '10M-100M': 1e8,
            '100M-1B': 1e9,
            '1B+': 1e10
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
                    size='ipv4',
                    template=template,
                    hover_data={
                        'name': True,
                        'ipv4': True,
                        'pop': True,
                        'percentv4': True,
                        'pcv4': True
                    },
                    category_orders={"ipv4_grouping": ['0-10k', '10k-100k', '100k-1M', '1M-10M', '10M-100M', '100M-1B', '1B+']},
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
                scatter_fig.update_xaxes(type='log', title_text='Population Size (Logarithmic Scale)', tickvals=[1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10], ticktext=['1k', '10k', '100k', '1M', '10M', '100M', '1B', '10B'])
                scatter_fig.update_yaxes(type='log', title_text='Number of IPv4 Addresses')#, tickvals=list(ipv4_group_to_ticks.values()), ticktext=list(ipv4_group_to_ticks.keys())
                
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
                #print(df.columns.tolist())
                selected, unselected = self.selected_unselected_functionality()
                df['ipv6'] = df['ipv6'].apply(lambda x: x if x > 0 else 1.1)
                df['log_ipv6'] = np.log10(df['ipv6'])

                min_value = df['log_ipv6'].quantile(0.1)
                max_value = df['log_ipv6'].quantile(0.9)
                scatter_fig = px.scatter(
                    df,
                    y='pcv6',
                    x='pop',
                    size='ipv6',
                    size_max=50,
                    log_x=True,
                    log_y=True,
                    color='log_ipv6',
                    #color_continuous_scale=px.colors.sequential.Viridis,
                    color_continuous_scale=px.colors.sequential.Plasma_r,
                    range_color=[min_value, max_value],
                    template=template,
                    hover_data={
                        'name': True,
                        'ipv6': True,
                        'percentv6': True,
                        'pcv6': True
                    }
                )
                #scatter_fig.update_yaxes(type='log')
                #scatter_fig.update_xaxes(type='log')

                # Tweaks to the plots
                #desired_max_marker_size = 1
                #sizeref = 1. * max_ipv4 / (desired_max_marker_size ** 0.5)
                scatter_fig.update_traces(
                    marker=dict(sizemode='area',
                                #sizeref=sizeref,
                                sizemin=5),
                    selected=selected,
                    unselected=unselected,
                    #hovertemplate=hover_template
                )

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

            return scatter_fig
        if active_dataset.get('dataset') == 'ipv4_time_series':
            if active_item == 'animated':
                df = pd.read_json(data_json_stream, orient='split')
                selected, unselected = self.selected_unselected_functionality()
                x_values = [10e3, 100e3, 1e6, 10e6, 100e6, 1e9, 5e9]
                #print(df.head(100))
                scatter_fig = px.scatter(
                    df,
                    x='GDPPerCap',
                    y='Population',
                    size='Cumulative Value',
                    animation_frame='Year',
                    hover_name='Country',
                    size_max=100,
                    #log_x=True,
                    #log_y=True,
                    #color_continuous_scale=px.colors.sequential.Plasma_r,
                    template=template,
                    color='RIR',
                    #range_x=x_range,  # Set custom x-axis range
                    #range_y=[0, y_max]  # Adjusted y-axis range
                )

                scatter_fig.update_layout(
                    margin={'r':5, 't':50, 'l':5, 'b':5},
                    clickmode='event+select',
                    transition={'duration': 75},
                    xaxis_title='GDP Per Capita',
                    yaxis_title='Population',
                    xaxis_type='log',
                    yaxis_type='log',
                    yaxis_range=[4, 10],
                    xaxis_range=[2, 5.5]
                )

                # max_ipv4 = df['Cumulative Value'].max()
                # desired_max_marker_size = 75
                # sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 5)

                scatter_fig.update_traces(
                    marker=dict(sizemode='area',
                                #sizeref=sizeref,
                                sizemin=3),
                    selected=selected,
                    unselected=unselected,
                    #hovertemplate=hover_template
                )
            return scatter_fig