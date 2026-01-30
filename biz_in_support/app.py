import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
#from streamlit_folium import folium_static

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Biz in Support")

# 2. DATA LOADING
@st.cache_data # This keeps the app fast by not reloading the CSV every click
def load_data():
    # Use a relative path for deployment (e.g., 'data/data.csv')
    # this right here is only for local drive------------------------------------------
    #path = "D:\\GIt\\InterActiveMap\\biz_in_support\\data.csv"
    #df = pd.read_csv(path, encoding="ISO-8859-1", engine='python', sep=',',header=1)
    #----------------------------------------------------------------------------------
    df = pd.read_csv('data.csv', encoding="ISO-8859-1", engine='python', sep=',',header=1)
    #df = pd.read_csv('D:\\GIt\\InterActiveMap\\biz_in_support\\data.csv', engine='python', sep=',')
    df.columns = df.columns.str.strip()
    return df.dropna(subset=['Lat', 'Lon'])

data = load_data()

# 3. HEADER
st.markdown("<h2 style='text-align: center;'>Biz in Support</h2>", unsafe_allow_html=True)

# 4. FILTERS (Sidebar or Top Columns)
col1, col2 = st.columns(2)

with col1:
    counties = sorted(data['County'].unique())
    selected_county = st.selectbox("Select County:", options=counties)

with col2:
    # FUTURE CATEGORY FILTER (Commented out)
    # categories = ["All"] + sorted(data['Category'].unique().tolist())
    # selected_category = st.selectbox("Select Category:", options=categories)
    st.write("") # Placeholder

# 5. FILTER LOGIC
filtered_df = data[data['County'] == selected_county]

# FUTURE CATEGORY LOGIC
# if selected_category != "All":
#     filtered_df = filtered_df[filtered_df['Category'] == selected_category]

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
        
        # Using CircleMarker instead of the standard Marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Auto-Zoom
    if len(points) > 1:
        m.fit_bounds(points, padding=(40, 40))
    else:
        m.location = points[0]
        m.zoom_start = 14

    # 7. DISPLAY MAP
    st_folium(
    m, 
    width=800,           # Adjust width as needed
    height=600,          # Adjust height as needed
    returned_objects=[] # THIS IS THE KEY: it makes it act like the old folium_static
    )
    #folium_static(m, width=800, height=600)
else:
    st.warning("No results match these filters.")