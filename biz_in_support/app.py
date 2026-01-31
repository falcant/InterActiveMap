import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="BUSINESSES AGAINST ICE IN UTAH")

# 2. DATA LOADING
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data_enriched.csv")
    
    if not os.path.exists(file_path):
        st.error(f"File not found. Please ensure 'data_enriched.csv' is in the same folder as this script.")
        st.stop()
        
    # header=1 skips the first row of the CSV
    # header=0 uses the very first row as the column names
    df = pd.read_csv(file_path, encoding="ISO-8859-1", engine='python', sep=',', header=0)
    
    # Clean hidden spaces from column names
    df.columns = df.columns.str.strip()
    
    return df.dropna(subset=['Lat', 'Lon'])

data = load_data()

# 3. HEADER
st.markdown("<h1 style='text-align: center; color: grey;'>Businesses Against ICE in UT</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: black;'>Please Support these businesses <3 </h2>", unsafe_allow_html=True)

# 4. FILTERS
col1, col2 = st.columns(2)

with col1:
    counties = sorted(data['County'].unique())
    selected_county = st.selectbox("Select County:", options=counties)

with col2:
    categories = ["All"] + sorted(data['Category'].unique().tolist())
    selected_category = st.selectbox("Select Category:", options=categories)

# 5. FILTER LOGIC
filtered_df = data[data['County'] == selected_county]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# 6. MAP GENERATION
if not filtered_df.empty:
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
        
        # Back to standard Blue Markers
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['Business'],
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # 7. DYNAMIC ZOOM (Recalculated for County + Category)
    if len(points) > 1:
        m.fit_bounds(points, padding=(50, 50))
    elif len(points) == 1:
        m.location = points[0]
        m.zoom_start = 15

    # 8. DISPLAY MAP
    st_folium(
        m, 
        width="100%", 
        height=600, 
        returned_objects=[],
        key=f"map_{selected_county}_{selected_category}" # Forces zoom update
    )
else:
    st.warning(f"No results found in {selected_county} for: {selected_category}")

# 9. FOOTER
st.write(f"Showing **{len(filtered_df)}** locations.")