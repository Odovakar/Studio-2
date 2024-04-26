import pandas as pd
import plotly.express as px

class TimeSeriesHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler

class TimeSeriesHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def generate_figure(self, active_item):
        if active_item == 'v4cumulativepoolpopulation':
            grouped_df = self.data_handler.time_series_data[self.data_handler.time_series_data['Registry'].notna()]
            fig = px.scatter(
                grouped_df,
                x='Year',
                y='Value',
                size='Value',
                color='Registry',
                animation_frame='Year',
                animation_group='Registry',
                size_max=55,  # Adjust the maximum size of points
                range_x=[grouped_df['Year'].min(), grouped_df['Year'].max()],
                range_y=[0, grouped_df['Value'].max() + 1]
            )

        elif active_item == 'global':
            # Use the global data already processed in DataHandler
            grouped_df = self.data_handler.time_series_data[self.data_handler.time_series_data['Country'].notna()]
            fig = px.scatter(
                grouped_df,
                x='Year',
                y='Cumulative Value',
                size='Cumulative Value',
                color='Country',
                animation_frame='Year',
                animation_group='Country',
                size_max=55,
                range_x=[grouped_df['Year'].min(), grouped_df['Year'].max()],
                range_y=[0, grouped_df['Cumulative Value'].max() + 1]
            )

        fig.update_layout(transition={'duration': 1000})
        return fig
