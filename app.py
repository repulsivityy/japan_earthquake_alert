import streamlit as st
import requests
import pandas as pd
import datetime
from config import MIN_LOCAL_SHINDO, PREFECTURE_TRANSLATIONS

# Page Config
st.set_page_config(
    page_title="Japan Safety Alert System",
    page_icon="🇯🇵",
    layout="wide"
)

# Constants
P2P_API_URL = "https://api.p2pquake.net/v2/history?codes=551&limit=20"

def fetch_quake_data():
    """Fetches recent earthquake data from P2P-Quake."""
    try:
        resp = requests.get(P2P_API_URL)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

def process_data(data):
    """Processes raw API data into a DataFrame for display."""
    processed = []
    for quake in data:
        eid = quake.get("id", "")
        time_str = quake.get("time", "")
        
        earthquake_info = quake.get("earthquake", {})
        hypo = earthquake_info.get("hypocenter", {})
        
        name_jp = hypo.get("name", "Unknown")
        name = name_jp
        # Attempt simple translation if exact match
        if name_jp in PREFECTURE_TRANSLATIONS:
            name = PREFECTURE_TRANSLATIONS[name_jp]
        else:
             # Try partial match (e.g. "Ishikawa-ken Noto" -> "Ishikawa Noto")
             for jp_pref, en_pref in PREFECTURE_TRANSLATIONS.items():
                 if jp_pref in name_jp:
                     name = name_jp.replace(jp_pref, en_pref)
                     break
        mag = hypo.get("magnitude", "-")
        depth = hypo.get("depth", "-")
        lat = hypo.get("latitude")
        lon = hypo.get("longitude")
        max_int = earthquake_info.get("maxScale", 0) / 10.0
        
        # Parse time safely
        try:
            # Format: '2023/10/25 10:30:45'
            dt = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        except:
            dt = time_str

        # Clean lat/lon for mapping
        # P2P Quake sometimes returns -1 or strings for unknowns?
        # Usually checking if valid float
        valid_loc = False
        try:
            if lat and lon:
                lat = float(lat)
                lon = float(lon)
                # Filter out -200 or generic invalid coordinates if any
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    valid_loc = True
        except:
            pass

        processed.append({
            "Time": dt,
            "Location": name,
            "Magnitude": mag,
            "Depth (km)": depth,
            "Max Intensity": max_int,
            "lat": lat if valid_loc else None,
            "lon": lon if valid_loc else None,
            "id": eid
        })
    
    return pd.DataFrame(processed)

# Sidebar
st.sidebar.title("JSAS Dashboard")
st.sidebar.info("Monitoring Real-time Earthquake Data from P2P-Quake.")
refresh = st.sidebar.button("Refresh Data")

# Main Content
st.title("🇯🇵 Japan Safety Alert System (JSAS)")
st.markdown("### Recent Seismic Activity")

data = fetch_quake_data()
if data:
    df = process_data(data)
    
    # 1. Metrics
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[0]
    
    col1.metric("Latest Quake Location", latest["Location"])
    col2.metric("Magnitude", latest["Magnitude"])
    col3.metric("Max Intensity", latest["Max Intensity"])

    # 2. Map
    st.markdown("#### Epicenter Map")
    map_data = df.dropna(subset=["lat", "lon"])
    if not map_data.empty:
        st.map(map_data)
    else:
        st.warning("No location data available for recent quakes.")

    # 3. Data Table
    st.markdown("#### Recent Events Log")
    
    # Highlight logic
    # MIN_LOCAL_SHINDO is, e.g., 30 (Shindo 3). 
    # API maxScale is integer (30). DF 'Max Intensity' is float (3.0).
    # So we compare df['Max Intensity'] * 10 >= MIN_LOCAL_SHINDO
    
    def highlight_significant(row):
        val = row["Max Intensity"]
        if (val * 10) >= MIN_LOCAL_SHINDO:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    styled_df = df[["Time", "Location", "Magnitude", "Max Intensity", "Depth (km)"]].style.\
        apply(highlight_significant, axis=1).\
        format({"Magnitude": "{:.1f}", "Max Intensity": "{:.1f}"})
    
    st.dataframe(styled_df)

    # 4. External Links
    st.markdown("---")
    st.markdown("#### Official Resources")
    st.markdown("- [JMA Tsunami Warnings](https://www.jma.go.jp/bosai/map.html#8/41.294/141.79/&elem=int&contents=earthquake_map&lang=en)")
    st.markdown("- [NHK World-Japan News](https://www3.nhk.or.jp/nhkworld/)")
    
else:
    st.write("No data currently available.")
