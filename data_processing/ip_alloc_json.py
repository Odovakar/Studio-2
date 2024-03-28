from dash import Dash, html
import dash_ag_grid as dag
import requests

# Fetching raw population, percentage, and ipv4/6 JSON data
json_raw_data_url = 'https://raw.githubusercontent.com/impliedchaos/ip-alloc/main/ip_alloc.json'
response = requests.get(json_raw_data_url)
json_data = response.json()

# Transform the nested dictionary JSON data into a list of dictionaries
transformed_data = []
for country_code, details in json_data.items():
    # Optionally include the country code in the data if needed
    country_data = {"country_code": country_code, **details}
    transformed_data.append(country_data)

# Generate column definitions based on the keys of the first dictionary in the list, enabling sorting and filtering
column_defs = [{'field': col, 'sortable': True, 'filter': True} for col in transformed_data[0].keys()]

# Initialize the Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("JSON Data in AgGrid", style={'textAlign': 'center'}),
    html.Div(
        dag.AgGrid(
            id='json-data-grid',
            columnDefs=column_defs,
            rowData=transformed_data,  # Use the transformed data
            style={'height': '600px', 'width': '80%'},  # Adjust the size as needed
            className='ag-theme-balham',  # Use a theme suitable for your app design
        ),
        style={'display': 'flex', 'justifyContent': 'center'}
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
