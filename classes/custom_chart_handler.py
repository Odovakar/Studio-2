import pandas as pd
import plotly.express as px

class CustomChartHandler:
    def __init__ (self, data_handler):
        self.data_handler = data_handler

    def generate_figure(self, virtual_row_data, active_item, active_dataset, switch_on):
        df = None
        #virtual_row_data = None
        template = 'bootstrap' if switch_on else 'bootstrap_dark'
        dataset = active_dataset.get('dataset')
        

        if dataset == 'ipv4':
            print(dataset, 'cust chart handler dataset conditional')
            if active_item == 'TEST':
                #print(active_item, 'cust chart handler active item conditional')
                df = pd.DataFrame(virtual_row_data)
                df['ipv4'] = pd.to_numeric(df['ipv4'], errors='coerce')
                df['ipv4'] = df['ipv4'].fillna(0).astype('Int64')
                #print(df.dtypes)  # Expected output: ipv4 Int64
                #print(df['ipv4'].describe())  # This will show float stats due to the nature of describe()

                # Extra check for value counts and nulls
                #print(df['ipv4'].value_counts())  # See distribution of values
                #print(df['ipv4'].isnull().sum())  # Check if there are any remaining nulls
                grouped_df = df.groupby('RIR')['ipv4'].sum().reset_index()
                fig = px.histogram(
                    grouped_df,
                    x='RIR',
                    y='ipv4',
                    histfunc='sum',
                    nbins=5
                )
                return fig
            else:
                df = self.data_handler.json_df
                #print(df.columns.tolist())
                fig = px.histogram(
                    df,
                    x='RIR',
                    y='ipv4'
                )
                return fig
