class HoverTemplateHandler:
    def __init__(self, data_handler):
        self.data_handler = data_handler
    
    def get_hover_template(self, scale_type):
        if scale_type=='normal':
            hover_template='<b>%{customdata[0]}</b><br>' + \
                        'IPv4: %{customdata[1]:,.0f}<br>' + \
                        'Population: %{customdata[2]:,.0f}<br>' + \
                        'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                        'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                        '<extra>IPv4 Grouping: %{customdata[6]}</extra>'
            return hover_template
        elif scale_type=='log':
            hover_template='<b>%{customdata[0]}</b><br>' + \
                        'IPv4: %{customdata[1]:,.0f}<br>' + \
                        'Population: %{customdata[2]:,.0f}<br>' + \
                        'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                        'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                        '<extra>Log IPv4: %{customdata[7]:.2f}</extra>'
            return hover_template
    
    def get_pie_hover_template(self, selected_value, customdata):
        if selected_value=='TotalPool':
            hover_template='<b>%{customdata[0]}</b><br>' + \
                            'IPv4: %{customdata[1]:,.0f}<br>' + \
                            'Population: %{customdata[2]:,.0f}<br>' + \
                            'Pct of Pool: %{customdata[3]:.2f}%<br>' + \
                            'IPv4 per Cap: %{customdata[4]:.2f}%' + \
                            '<extra>Log IPv4: %{customdata[7]:.2f}</extra>'
            return hover_template
        if selected_value=='WHOIS':
            hover_template = None
            return hover_template