import streamlit as st
from streamlit_folium import st_folium
import folium
import osmnx as ox
import pickle
import os
from datetime import datetime

class SimpleMapGenerator:
    def __init__(self):
        self.cache_dir = "map_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_city_center(self, city_name):
        city_centers = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.6139, 77.2090),
            'bangalore': (12.9716, 77.5946),
            'chennai': (13.0827, 80.2707),
            'kolkata': (22.5726, 88.3639)
        }
        return city_centers.get(city_name.lower(), (19.0760, 72.8777))
    
    def download_basic_city_data(self, city_name):
        cache_file = os.path.join(self.cache_dir, f"{city_name.lower()}_basic.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        try:
            st.info(f"Downloading {city_name} boundary data...")
            city_boundary = ox.geocode_to_gdf(f"{city_name}, India")
            amenities = ox.features_from_place(
                f"{city_name}, India", 
                tags={'amenity': ['hospital', 'school', 'police', 'fire_station']},
            )
            if not amenities.empty:
                amenities = amenities.head(3)
            
            data = {
                'boundary': city_boundary,
                'amenities': amenities,
                'download_time': datetime.now().isoformat(),
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            st.success(f"✅ {city_name} data cached successfully!")
            return data
            
        except Exception as e:
            st.error(f"❌ Error downloading {city_name}: {str(e)}")
            return None
    
    def create_simple_map(self, city_name):
        center_lat, center_lon = self.get_city_center(city_name)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='OpenStreetMap')

        folium.Marker(
            [center_lat, center_lon],
            popup=f"{city_name} City Center",
            tooltip=f"Click for {city_name} info",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

        try:
            data = self.download_basic_city_data(city_name)
            if data and 'amenities' in data and not data['amenities'].empty:
                for idx, amenity in data['amenities'].iterrows():
                    try:
                        if hasattr(amenity.geometry, 'centroid'):
                            point = amenity.geometry.centroid
                            amenity_type = amenity.get('amenity', 'Unknown')
                            amenity_name = amenity.get('name', f'{amenity_type.title()}')
                            color = {
                                'hospital': 'red',
                                'school': 'green',
                                'police': 'blue',
                                'fire_station': 'orange'
                            }.get(amenity_type, 'gray')
                            
                            folium.Marker(
                                [point.y, point.x],
                                popup=f"{amenity_name} ({amenity_type})",
                                tooltip=amenity_name,
                                icon=folium.Icon(color=color, icon='info-sign')
                            ).add_to(m)
                    except Exception:
                        continue
        except Exception as e:
            st.warning(f"Could not load detailed data for {city_name}: {str(e)}")
        
        return m

def main():
    st.set_page_config(page_title="Military Map System", layout="wide")
    st.title("🗺️ Military Map System - Simplified")
    
    if 'current_city' not in st.session_state:
        st.session_state.current_city = None
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("🏙️ City Selection")
        cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
        selected_city = st.selectbox("Choose a city:", cities)
        
        if st.button(f"🚀 Load {selected_city}", use_container_width=True):
            st.session_state.current_city = selected_city
            st.rerun()  # trigger UI update
        
        if st.session_state.current_city:
            st.subheader("🎛️ Map Controls")
            if st.button("🔄 Refresh Map", use_container_width=True):
                st.rerun()
            if st.button("🗑️ Clear Map", use_container_width=True):
                st.session_state.current_city = None
                st.rerun()
        
        st.subheader("ℹ️ Info")
        if st.session_state.current_city:
            st.info(f"Current: {st.session_state.current_city}")
        else:
            st.info("No city loaded")
    
    with col2:
        st.subheader("🗺️ Interactive Map")
        
        if st.session_state.current_city:
            generator = SimpleMapGenerator()
            map_obj = generator.create_simple_map(st.session_state.current_city)
            
            map_data = st_folium(
                map_obj,
                width=900,
                height=600,
                returned_objects=["last_clicked", "center", "zoom"],
                key=f"map_{st.session_state.current_city}"  # stable key
            )

            st.subheader("📊 Map Interactions")
            interact_col1, interact_col2 = st.columns(2)
            with interact_col1:
                if map_data.get('last_clicked'):
                    click = map_data['last_clicked']
                    st.write("**🎯 Last Clicked:**")
                    st.write(f"📍 Lat: {click.get('lat', 0):.6f}")
                    st.write(f"📍 Lng: {click.get('lng', 0):.6f}")
                else:
                    st.write("**🎯 Click on map to see coordinates**")
            with interact_col2:
                st.write("**🔍 Map Status:**")
                st.write(f"🔎 Zoom: {map_data.get('zoom', 'N/A')}")
                if map_data.get('center'):
                    center = map_data['center']
                    st.write(f"📍 Center: {center.get('lat', 0):.4f}, {center.get('lng', 0):.4f}")
        else:
            st.info("👈 Select a city from the sidebar to load the map")
            st.markdown("""
            ### 🚀 Features:
            - **🔒 Offline Ready**
            - **🖱️ Interactive**
            - **🏥 Key Locations**
            - **💾 Cached Data**
            - **🎯 Military Ready**
            """)

if __name__ == "__main__":
    main()
