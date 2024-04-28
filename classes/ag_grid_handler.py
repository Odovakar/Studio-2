import pandas as pd

class AgGridHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def format_json_data_for_aggrid(self):
        df = self.data_handler.json_df
        if df is None or df.empty:
            print("JSON DataFrame is empty or not initialized.")
            return []
        formatted_df = df.copy()

        # Ensure 'log_ipv4' is a float before formatting
        formatted_df['log_ipv4'] = pd.to_numeric(formatted_df['log_ipv4'], errors='coerce')

        # Now apply formatting
        if 'log_ipv4' in formatted_df.columns:
            formatted_df['log_ipv4'] = formatted_df['log_ipv4'].apply(lambda x: "{:,.1f}".format(x))
        else:
            print("log_ipv4 column not found in DataFrame")

        formatted_df['ipv4'] = formatted_df['ipv4'].apply(lambda x: "{:,.0f}".format(x))
        formatted_df['pcv4'] = formatted_df['pcv4'].apply(lambda x: "{:.1f}%".format(x))
        formatted_df['percentv4'] = formatted_df['percentv4'].apply(lambda x: "{:.1f}%".format(x))

        return formatted_df.to_dict('records')

    def format_whois4_data_for_aggrid(self):
        df = self.data_handler.whois_ipv4_df
        if df is None or df.empty:
            print("WHOIS DataFrame is empty or not initialized.")
            return []
        # Filter out rows where 'Value' is 0
        df = df[df['Value'] != 0]
        formatted_df = df.copy()
        formatted_df['Value'] = formatted_df['Value'].apply(lambda x: "{:,.0f}".format(x) if pd.notnull(x) else x)
        formatted_df['Population'] = pd.to_numeric(formatted_df['Population'], errors='coerce')
        formatted_df['Population'] = formatted_df['Population'].apply(lambda x: "{:,.0f}".format(x) if pd.notnull(x) else x)
        formatted_df['Registry'] = formatted_df['Registry'].str.upper()
        formatted_df['Date'] = pd.to_datetime(formatted_df['Date'], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')
        return formatted_df.to_dict('records')
    

    def generate_column_definitions(self, data_type):
        if data_type == 'json':
            return [
                {'field': 'name', 'headerName': 'Country', 'sortable': True, 'filter': True},
                {'field': 'ipv4', 'headerName': 'Nr of IPv4 Addresses', 'sortable': True, 'filter': True},
                {'field': 'pcv4', 'headerName': 'IPv4 per Capita', 'sortable': True, 'filter': True},
                {'field': 'percentv4', 'headerName': 'Pct Total of v4 Pool', 'sortable': True, 'filter': True},
                {'field': 'RIR', 'headerName': 'RIR', 'sortable': True, 'filter': True},
                {'field': 'log_ipv4', 'headerName': 'Log of IPv4', 'sortable': True, 'filter': True}
            ]
        elif data_type == 'whoisv4':
            return [
                {'field': 'Country', 'headerName': 'Country', 'sortable': True, 'filter': True},
                {'field': 'Population', 'headerName': 'Population', 'sortable': True, 'filter': True},
                {'field': 'Registry', 'headerName': 'Registry', 'sortable': True, 'filter': True},
                {'field': 'Start', 'headerName': 'Start IP', 'sortable': True, 'filter': True},
                {'field': 'Value', 'headerName': 'Assigned IPs', 'sortable': True, 'filter': True},
                {'field': 'Year', 'headerName': 'Year', 'sortable': True, 'filter': True},
                {'field': 'Status', 'headerName': 'Status', 'sortable': True, 'filter': True},
                {'field': 'Prefix', 'headerName': 'Prefix', 'sortable': True, 'filter': True},
            ]