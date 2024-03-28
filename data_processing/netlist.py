import pandas as pd
from dash import Dash, html
import dash_ag_grid as ag
import requests

# Fetching data from github repository
def fetch_netlist_data(url):
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    data = [line.split(maxsplit=3) for line in lines if line]
    netlist_df = pd.DataFrame(data, columns=['Start', 'End', 'RIR', 'Description'])
    return netlist_df

# Function to tidy up and better granularity of netlist data
def process_netlist_data(netlist_df):
    # Splitting Description column into multiple columns
    netlist_df[['Status', 'IP']] = netlist_df['Description'].str.split(n=1, expand=True)
    # Further split IP column into IP address and Prefix columns
    netlist_df[['IP Address', 'Prefix']] = netlist_df['IP'].str.split("/", expand=True)
    # Dropping unnecessary columns
    netlist_df.drop(columns=['Description', 'IP'], inplace=True)
    # Convert 'Start' and 'End' columns to UInt64
    netlist_df['Start'] = netlist_df['Start'].astype('UInt64')
    netlist_df['End'] = netlist_df['End'].astype('UInt64')
    # Calculate aggregate as the difference between 'End' and 'Start'
    netlist_df['Nr of IPs'] = netlist_df['End'] - netlist_df['Start']
    return netlist_df

netlist_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/netlist.txt'
netlist_data_frame = fetch_netlist_data(netlist_url)

# Process the data
netlist_data_frame = process_netlist_data(netlist_data_frame)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Netlist Data in Ag-Grid"),
    ag.AgGrid(
        id='netlist-grid',
        columnDefs=[{"headerName": col, "field": col, "filter": True} for col in netlist_data_frame.columns],
        rowData=netlist_data_frame.to_dict('records'),
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
