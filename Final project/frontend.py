import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from database import help_stations

st.set_page_config(layout="wide")
st.title("🚨 Help Station Finder")
st.subheader("📍 Step 1: Detect Your Live Location")

# Detect location once on app load
location = get_geolocation()

if not location:
    st.warning("⚠️ Please allow location access in your browser.")
    st.stop()

latitude = location["coords"]["latitude"]
longitude = location["coords"]["longitude"]

st.success(f"📍 Your location: {latitude:.6f}, {longitude:.6f}")

# Step 2: Find nearest stations
if "phones" not in st.session_state:
    st.session_state.phones = []

# Use session_state to check if stations were already fetched
if "nearest_stations" not in st.session_state:
    st.session_state.nearest_stations = None

# When the button is clicked, find nearest stations
if st.button("Find Nearest Stations") and st.session_state.nearest_stations is None:
    user_location = {"latitude": latitude, "longitude": longitude}
    res = requests.post("http://127.0.0.1:8000/nearest_stations/", json=user_location)

    if res.status_code == 200:
        nearest = res.json()["nearest_stations"]
        st.session_state.nearest_stations = nearest
        phones = [station[0][1] for station in nearest]
        st.session_state.phones = phones
        st.success("✅ Found nearest stations!")
        st.write("📞 Phones of nearest stations:", phones)
    else:
        st.error("❌ Could not get stations. Please try again.")

# Handle the message input only after stations have been found
if st.session_state.nearest_stations:
    message = st.text_area("✉️ Enter your message to be sent to these stations")

    # Show a button to send message only if there is a message
    if message:
        if st.button("Send Message to Nearest Stations"):
            if st.session_state.phones:
                with st.spinner('Sending your message...'):
                    send_res = requests.post("http://127.0.0.1:8000/send_message/", json={"message": message, "phones": st.session_state.phones})

                    if send_res.status_code == 200:
                        st.success("📨 Message sent successfully!")
                        for r in send_res.json()["results"]:
                            st.write(r)
                    else:
                        st.error("❌ Failed to send message. Please try again.")
            else:
                st.warning("⚠️ No nearest stations found. Please try again.")
    else:
        st.warning("⚠️ Please enter a message to send.")
