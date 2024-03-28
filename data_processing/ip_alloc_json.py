import requests

# Fetching raw population, percentage, and ipv4/6 JSON data
def fetch_and_transform_json_data(json_raw_data_url):
    response = requests.get(json_raw_data_url)
    json_data = response.json()

    # Transform the nested dictionary JSON data into a list of dictionaries
    transformed_data = []
    for country_code, details in json_data.items():
        # Optionally include the country code in the data if needed
        country_data = {"country_code": country_code, **details}
        transformed_data.append(country_data)

    if transformed_data:  # Check if the list is not empty to avoid KeyError
        column_defs = [{'field': col, 'sortable': True, 'filter': True} for col in transformed_data[0].keys()]
    else:
        column_defs = []

    return transformed_data, column_defs