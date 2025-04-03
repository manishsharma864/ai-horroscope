import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_text(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")  # Updated to gemini-1.5-flash
    response = model.generate_content(prompt)
    return response.text.strip()

# Geolocation with caching
geolocator = Nominatim(user_agent="vedic_horoscope_app")
@st.cache_data
def get_coordinates(place):
    location = geolocator.geocode(place)
    return (location.latitude, location.longitude) if location else (0, 0)

# Streamlit UI
st.set_page_config(page_title="Vedic Astrology Chat", page_icon="✨")
st.title("✨ Vedic Astrology Chat ✨")
messages = st.session_state.get("messages", [{"role": "bot", "content": "Hello! What's your name?"}])

for msg in messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    if "name" not in st.session_state:
        st.session_state.name = user_input
        response = f"Nice to meet you, {user_input}! Can you provide your date of birth (DD/MM/YYYY)?"
    elif "dob" not in st.session_state:
        try:
            st.session_state.dob = datetime.strptime(user_input, "%d/%m/%Y").date()
            response = "Got it! What time were you born? (HH:MM)"
        except ValueError:
            response = "Please enter a valid date (DD/MM/YYYY)."
    elif "tob" not in st.session_state:
        try:
            st.session_state.tob = datetime.strptime(user_input, "%H:%M").time()
            response = "Great! Where were you born? (City, Country)"
        except ValueError:
            response = "Please enter a valid time (HH:MM)."
    elif "place" not in st.session_state:
        st.session_state.place = user_input
        lat, lon = get_coordinates(st.session_state.place)
        response = f"Based on your birth details ({st.session_state.dob}, {st.session_state.tob}, {st.session_state.place}), would you like a career or marriage prediction?"
    else:
        prompt = f"Astrology insights for {st.session_state.name} born on {st.session_state.dob} at {st.session_state.tob} in {st.session_state.place}: {user_input}"
        response = generate_text(prompt)
    
    messages.append({"role": "bot", "content": response})
    st.chat_message("bot").write(response)
    
st.session_state.messages = messages
