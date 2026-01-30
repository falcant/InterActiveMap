import dash
from dash import dcc, html, Input, Output
import folium
import pandas as pd
import re

# 1. DATA LOADING
data = pd.read_csv("D:\\GIt\\InterActiveMap\\biz_in_support\\data.csv", 
                   encoding="ISO-8859-1", engine='python', sep=',', header=1, nrows=3)
data.columns = data.columns.str.strip()
data = data.dropna(subset=['Lat', 'Lon'])

app = dash.Dash(__name__)

# 2. LAYOUT
app.layout = html.Div([
    html.H2('Biz in Support', style={'fontFamily': 'Arial', 'textAlign': 'center'}),
    
    # Filter Row
    html.Div([
        # County Filter
        html.Div([
            html.Label("Select County:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='county-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(data['County'].unique())],
                value=data['County'].unique()[0] if not data.empty else None,
                clearable=False,
            ),
        ], style={'width': '300px', 'display': 'inline-block', 'marginRight': '20px'}),

        # FUTURE CATEGORY FILTER (Commented out)
        # html.Div([
        #     html.Label("Select Category:", style={'fontWeight': 'bold'}),
        #     dcc.Dropdown(
        #         id='category-dropdown',
        #         options=[{'label': cat, 'value': cat} for cat in sorted(data['Category'].unique())] if 'Category' in data.columns else [],
        #         value='All',
        #         clearable=True,
        #         placeholder="Search Categories..."
        #     ),
        # ], style={'width': '300px', 'display': 'inline-block'}),

    ], style={'padding': '20px', 'textAlign': 'center'}),

    html.Hr(),
    
    # Map Container
    html.Div([
        html.Iframe(
            id='map-display', 
            width='80%', 
            height='800', 
            style={'border': 'none', 'display': 'block', 'overflow': 'hidden'}
        )
    ], style={'padding': '0', 'overflow': 'hidden'})
])

# 3. CALLBACK
@app.callback(
    Output('map-display', 'srcDoc'),
    Input('county-dropdown', 'value'),
    # Input('category-dropdown', 'value')  # Uncomment this in the future
)
def update_map(selected_county, selected_category=None): # Add category to args in future
    if not selected_county:
        return "<h3>No County Selected</h3>"

    # Base Filter: County
    filtered_df = data[data['County'] == selected_county]
    
    # FUTURE FILTER LOGIC (Commented out)
    # if selected_category and selected_category != 'All':
    #     filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    if filtered_df.empty:
        return "<h3>No results match these filters</h3>"
    
    # Initialize Map
    m = folium.Map(tiles='cartodbpositron', scrollWheelZoom=False)
    
    points = [] 
    for _, row in filtered_df.iterrows():
        lat, lon = row['Lat'], row['Lon']
        points.append([lat, lon])
        
        popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 180px;">
                <a href="{row['Website']}" target="_blank" 
                   style="font-size: 14px; font-weight: bold; color: #1A73E8; text-decoration: none;">
                    {row['Business']}
                </a>
                <br><br>
                <a href="{row['Driving']}" target="_blank" 
                   style="font-size: 12px; color: #555; text-decoration: underline;">
                    {row['Address']}
                </a>
            </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['Business']
        ).add_to(m)
    
    # Perfect Auto-Zoom
    if len(points) > 1:
        m.fit_bounds(points, padding=(40, 40))
    elif len(points) == 1:
        m.location = points[0]
        m.zoom_start = 14
        
    return m._repr_html_()

if __name__ == '__main__':
    app.run(debug=True, port=8051)