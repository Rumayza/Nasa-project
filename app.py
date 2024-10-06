
import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
from datetime import datetime, timedelta

# Function to fetch NDVI (Vegetation Index) data using the NASA API for a specific date
def fetch_ndvi_data(lat, lon, date):
    try:
        endpoint = "https://api.nasa.gov/planetary/earth/assets"
        params = {
            'lon': lon,
            'lat': lat,
            'dim': 0.1,
            'date': date,  # Pass the specific date
            'api_key': 'QrqseHmUxfH9XYE2o19kvY5NxBGIiUe1wwihpbwg'  # Your NASA API key
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if 'url' in data:
            return data['url']
        else:
            st.error(f"No NDVI data available for {date}.")
            return None
    except Exception as e:
        st.error(f"Error fetching NDVI data for {date}: {e}")
        return None

# Function to generate an interactive map with the NDVI overlay
def generate_ndvi_map(lat, lon, ndvi_url):
    m = folium.Map(location=[lat, lon], zoom_start=12)
    if ndvi_url:
        folium.raster_layers.ImageOverlay(
            image=ndvi_url,
            bounds=[[lat - 0.05, lon - 0.05], [lat + 0.05, lon + 0.05]],
            opacity=0.6
        ).add_to(m)
    folium.Marker([lat, lon], popup="NDVI Location").add_to(m)
    return m

# Streamlit UI Styling and Explanations
st.set_page_config(page_title="NDVI Data Viewer", layout="wide")

# Title and explanation
st.title("🌍 NASA NDVI Viewer and Agricultural Insights")
st.markdown('''
Welcome to the NDVI (Normalized Difference Vegetation Index) Viewer! This tool leverages NASA's Earth observation data 
to help you understand vegetation health in any location on Earth. 
You can analyze the NDVI for a single location or compare the vegetation in two different places side by side.
''')

st.info("NDVI values range from -1 to 1. Higher values represent healthier vegetation.")

# Styling headers with explanation
st.header("📍 Analyze NDVI for a Single Location")
st.markdown('''
Use this section to view the NDVI data for a specific location. Simply enter the coordinates (latitude and longitude), 
select the date range and interval between images, and visualize the NDVI data on the map.
''')

# Single location NDVI analysis
latitude = st.number_input("Enter Latitude", min_value=-90.0, max_value=90.0, value=50.0)
longitude = st.number_input("Enter Longitude", min_value=-180.0, max_value=180.0, value=-90.0)

# Date range selection
st.write("Select Date Range for NDVI Time Series:")
start_date = st.date_input("Start Date", value=datetime(2022, 1, 1))
end_date = st.date_input("End Date", value=datetime(2023, 1, 1))

# Interval between NDVI data points
interval_days = st.slider("Select Interval (Days Between Images)", min_value=30, max_value=60, value=15)

# Limit number of NDVI images to display
max_images = st.slider("Maximum Number of NDVI Images to Display", min_value=1, max_value=10, value=5)

# Display NDVI maps for the selected dates at the given interval
if st.button("Generate NDVI Time Series"):
    date_range = (end_date - start_date).days

    if date_range <= 0:
        st.error("Invalid date range.")
    else:
        displayed_images = 0
        current_date = start_date
        while displayed_images < max_images and current_date <= end_date:
            st.write(f"NDVI Map for Date: {current_date}")
            ndvi_url = fetch_ndvi_data(latitude, longitude, current_date.strftime('%Y-%m-%d'))
            if ndvi_url:
                ndvi_map = generate_ndvi_map(latitude, longitude, ndvi_url)
                folium_static(ndvi_map)
                st.markdown(f'<a href="{ndvi_url}" download="NDVI_{current_date}.png">Click to download NDVI Image</a>', unsafe_allow_html=True)
            
            displayed_images += 1
            current_date += timedelta(days=interval_days)

# ---------------- Comparison Feature -----------------
st.header("🌍 Compare NDVI for Two Locations")
st.markdown('''
This feature allows you to compare NDVI data for two different locations side by side. You can select the coordinates 
for both locations and see how vegetation health differs between the two places over time.
''')

# Layout with two locations side by side
col1, col2 = st.columns(2)

# Get user inputs for Location 1 (left side)
with col1:
    st.subheader("First Location")
    latitude_1 = st.number_input("Enter Latitude for Location 1", min_value=-90.0, max_value=90.0, value=50.0)
    longitude_1 = st.number_input("Enter Longitude for Location 1", min_value=-180.0, max_value=180.0, value=-90.0)

# Get user inputs for Location 2 (right side)
with col2:
    st.subheader("Second Location")
    latitude_2 = st.number_input("Enter Latitude for Location 2", min_value=-90.0, max_value=90.0, value=49.0)
    longitude_2 = st.number_input("Enter Longitude for Location 2", min_value=-180.0, max_value=180.0, value=-80.0)

# Unified controls below both locations
st.write("Select Date Range for Comparison:")
start_date_cmp = st.date_input("Start Date for Comparison", value=datetime(2022, 1, 1), key='start_cmp')
end_date_cmp = st.date_input("End Date for Comparison", value=datetime(2023, 1, 1), key='end_cmp')

# Interval between NDVI data points for comparison (with default of 15 days and range from 30 to 60 days)
interval_days_cmp = st.slider("Select Interval (Days Between Images) for Comparison", min_value=30, max_value=60, value=15, key='interval_cmp')

# Limit number of NDVI images to display for comparison
max_images_cmp = st.slider("Maximum Number of NDVI Images to Display for Comparison", min_value=1, max_value=10, value=5, key='max_cmp')

# Display NDVI maps for both locations side by side with smaller size
if st.button("Generate NDVI Time Series for Comparison"):
    date_range_cmp = (end_date_cmp - start_date_cmp).days

    if date_range_cmp <= 0:
        st.error("Invalid date range.")
    else:
        displayed_images = 0
        current_date_cmp = start_date_cmp

        # Creating two columns for side-by-side comparison with reduced size and added spacing
        col1_cmp, col2_cmp = st.columns(2)
        
        while displayed_images < max_images_cmp and current_date_cmp <= end_date_cmp:
            with col1_cmp:
                st.write(f"NDVI Map for Location 1 ({latitude_1}, {longitude_1}) on {current_date_cmp}")
                ndvi_url_1 = fetch_ndvi_data(latitude_1, longitude_1, current_date_cmp.strftime('%Y-%m-%d'))
                if ndvi_url_1:
                    ndvi_map_1 = generate_ndvi_map(latitude_1, longitude_1, ndvi_url_1)
                    folium_static(ndvi_map_1, width=300, height=300)  # Smaller size for maps
                    st.markdown(f'<a href="{ndvi_url_1}" download="NDVI_Location_1_{current_date_cmp}.png">Click to download NDVI Image for Location 1</a>', unsafe_allow_html=True)
            
            with col2_cmp:
                st.write(f"NDVI Map for Location 2 ({latitude_2}, {longitude_2}) on {current_date_cmp}")
                ndvi_url_2 = fetch_ndvi_data(latitude_2, longitude_2, current_date_cmp.strftime('%Y-%m-%d'))
                if ndvi_url_2:
                    ndvi_map_2 = generate_ndvi_map(latitude_2, longitude_2, ndvi_url_2)
                    folium_static(ndvi_map_2, width=300, height=300)  # Smaller size for maps
                    st.markdown(f'<a href="{ndvi_url_2}" download="NDVI_Location_2_{current_date_cmp}.png">Click to download NDVI Image for Location 2</a>', unsafe_allow_html=True)
            
            displayed_images += 1
            current_date_cmp += timedelta(days=interval_days_cmp)
