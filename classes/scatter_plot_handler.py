import plotly.express as px

class ScatterHandler:
    def __init__(self, data_handler):#, hover_template_handler):
        self.data_handler = data_handler
        #self.hover_template_handler = hover_template_handler
    
    def update_traces(self, selected_value):
        if selected_value=='normal':
            pass

    def generate_figure(self, active_item, active_dataset, switch_on):
        trace_options = []
        layout_options = []
        template = 'bootstrap' if switch_on else 'bootstrap_dark'


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
                scatter_fig = px.scatter(
                    data_frame=self.data_handler.json_df,
                    x='pop',
                    y='ipv4',
                    hover_name="name",
                    color='ipv4_grouping',
                    size_max=60,
                    title='Population Size vs. Number of IPv4 Addresses by Country',
                    labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
                    size="ipv4",
                    template=template
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

            elif active_item == 'log':
                scatter_fig = px.scatter(
                    data_frame=self.data_handler.json_df,
                    x='pop',
                    y='pcv4',
                    hover_name="name",
                    color='log_ipv4',
                    size='ipv4',
                    size_max=60,

                    title='Population Size vs. Number of IPv4 Addresses by Country',
                    labels={"pop": "Population Size", "ipv4": "Number of IPv4 Addresses"},
                    log_x=True,
                    log_y=True,
                    color_continuous_scale='Viridis',
                    template=template
                    #color_discrete_map=self.get_colorscale(active_item)
                )
                
                # Highlight significant outliers (e.g., USA) with annotations if needed
                if 'USA' in self.data_handler.json_df['iso_alpha_3'].values:
                    usa_ipv4 = self.data_handler.json_df.loc[self.data_handler.json_df['iso_alpha_3'] == 'USA', 'ipv4'].iloc[0]
                    usa_pop = self.data_handler.json_df.loc[self.data_handler.json_df['iso_alpha_3'] == 'USA', 'pop'].iloc[0]
                    scatter_fig.add_annotation(x=usa_pop, y=usa_ipv4, text="USA", showarrow=True, arrowhead=1)

                max_ipv4 = self.data_handler.json_df['ipv4'].max()
                desired_max_marker_size = 30
                sizeref = 2. * max_ipv4 / (desired_max_marker_size ** 3.5)
                scatter_fig.update_traces(marker=dict(sizemode='area', sizeref=sizeref, sizemin=7))
                scatter_fig.update_layout(
                    coloraxis_colorbar=dict(
                    title="Log IPv4",
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.3,
                    yanchor="bottom",
                    thicknessmode="pixels",
                    thickness=20,
                    len=0.5,  # Adjusts the length of the colorbar to 80% of the axis length
                ),margin={"r":5, "t":50, "l":5, "b":20},
                )

            return scatter_fig

        print("Type of active_dataset:", type(active_dataset))
        print("Dataset key's value:", active_dataset.get('dataset'))  # Confirm what value this key holds
        if active_dataset.get('dataset') == 'whoisv4':
            print('Correct dataset type confirmed.')
            if active_item == 'v4cumulativepoolpopulation':
                print('Correct active_item confirmed.')
                
                # Fetch and prepare the data
                df = self.data_handler.whois_ipv4_df[self.data_handler.whois_ipv4_df['Registry'].notna()]
                df.sort_values(by=['Registry', 'Year', 'Population'], inplace=True)  # Sort by registry and year for correct cumulative sum
                
                # Calculate cumulative sum for each registry across years
                df['Cumulative_Value'] = df.groupby('Registry')['Value'].cumsum()
                
                # Clip the cumulative values at 2.2 billion if needed (adjust as per your max limit)
                df['Cumulative_Value'] = df['Cumulative_Value'].clip(upper=2.2e9)

                # Create the animated scatter plot
                fig = px.scatter(
                    df,
                    x='Population',
                    y='Cumulative_Value',
                    size='Cumulative_Value',  # Use cumulative value for size
                    color='Registry',  # Differentiating each registry with color
                    animation_frame='Year',
                    animation_group='Registry',  # Group animations by registry
                    size_max=55,  # Adjust the maximum size of points
                    range_x=[df['Population'].min(), df['Population'].max()],  # Dynamic range based on data
                    range_y=[0, df['Cumulative_Value'].max() + 1],  # Dynamic y-range based on data
                    labels={'Cumulative_Value': 'Cumulative Value of Registry'},
                    title='Cumulative Value of Registry by Year',
                    #template=template
                )

                fig.update_layout(transition={'duration': 1000})  # Smooth transitions
                return fig

            #fig.update_layout(transition={'duration': 1000})
            #return fig