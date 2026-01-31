import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# 1. SETUP
INPUT_FILE = "data.csv"
OUTPUT_FILE = "data_enriched.csv"

# Using a very specific User-Agent prevents being blocked
geolocator = Nominatim(user_agent="utah_business_map_project_final_v1")

# Configure the Rate Limiter (Auto-retries on timeouts)
geocode = RateLimiter(
    geolocator.geocode, 
    min_delay_seconds=1.5, 
    max_retries=3, 
    error_wait_seconds=2.0
)

def prepare_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Load data
    df = pd.read_csv(INPUT_FILE, encoding="ISO-8859-1", engine='python', header=3,delimiter=',')
    df.columns = df.columns.str.strip()

    # --- CLEANING PHASE ---
    initial_count = len(df)

    # 1. Remove Nulls/NaNs from Address
    df = df.dropna(subset=['Address'])
    
    # 2. Remove empty strings or rows with only spaces
    df = df[df['Address'].str.strip() != ""]
    
    # 3. Remove 'Online' addresses (case-insensitive)
    df = df[df['Address'].str.lower() != 'online']

    print(f"Cleaned data: {initial_count - len(df)} rows removed. {len(df)} physical locations remaining.")

    # Prepare final columns
    for col in ['Lat', 'Lon', 'County', 'Driving']:
        if col not in df.columns: df[col] = None

    # --- ENRICHMENT PHASE ---
    for index, row in df.iterrows():
        # Only search if Lat is empty
        if pd.isna(row['Lat']):
            search_query = f"{row['Address']}, Utah"
            print(f"Geocoding: {row['Business']}...")
            
            try:
                # addressdetails=True is needed to pull the 'county'
                location = geocode(search_query, addressdetails=True, timeout=10)
                
                if location:
                    df.at[index, 'Lat'] = location.latitude
                    df.at[index, 'Lon'] = location.longitude
                    
                    # Pull County
                    raw_addr = location.raw.get('address', {})
                    df.at[index, 'County'] = raw_addr.get('county', 'Unknown')
                    
                    # Create precise Google Driving Directions link
                    df.at[index, 'Driving'] = f"https://www.google.com/maps/dir/?api=1&destination={location.latitude},{location.longitude}"
                else:
                    print(f"  ❌ Could not find: {search_query}")
                    
            except Exception as e:
                print(f"  ⚠️ Error processing {row['Business']}: {e}")

    # Save the cleaned and enriched data
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSUCCESS! File saved as {OUTPUT_FILE}")
    print("You can now use this file in your Streamlit app.")

if __name__ == "__main__":
    prepare_data()