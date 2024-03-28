from dash import Dash, html
import dash_ag_grid as ag
from data_processing.netlist import fetch_netlist_data, process_netlist_data

netlist_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/netlist.txt'
netlist_data_frame = fetch_netlist_data(netlist_url)

# Process the data
netlist_data_frame = process_netlist_data(netlist_data_frame)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Netlist Data in Ag-Grid"),
    ag.AgGrid(
        id='netlist-grid',
        columnDefs=[{"headerName": col, "field": col} for col in netlist_data_frame.columns],
        rowData=netlist_data_frame.to_dict('records'),
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
