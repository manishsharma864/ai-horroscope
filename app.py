import streamlit as st
from datetime import datetime
import pyswisseph as swe
from geopy.geocoders import Nominatim
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_text(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# Geolocation with caching
geolocator = Nominatim(user_agent="vedic_horoscope_app")
@st.cache_data
def get_coordinates(place):
    location = geolocator.geocode(place)
    return (location.latitude, location.longitude) if location else (0, 0)

# Vedic calculations
def get_vedic_data(birth_date, birth_time, birth_place):
    lat, lon = get_coordinates(birth_place)
    jd = swe.julday(birth_date.year, birth_date.month, birth_date.day, birth_time.hour + birth_time.minute / 60.0)
    swe.set_topo(lat, lon, 0)
    
    sun_longitude = swe.calc_ut(jd, swe.SUN)[0]
    rashi = (int(sun_longitude / 30) + 1) % 12
    
    asc_longitude = swe.houses(jd, lat, lon, 'P')[1][0]
    lagna = (int(asc_longitude / 30) + 1) % 12
    
    moon_longitude = swe.calc_ut(jd, swe.MOON)[0]
    nakshatra = (int(moon_longitude / 13.3333) + 1) % 27
    
    return rashi, lagna, nakshatra

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
        rashi, lagna, nakshatra = get_vedic_data(st.session_state.dob, st.session_state.tob, st.session_state.place)
        response = f"Your Rashi: {rashi} | Lagna: {lagna} | Nakshatra: {nakshatra}\nWould you like a career or marriage prediction?"
    else:
        response = generate_text(f"Astrology insights for {st.session_state.name}: {user_input}")
    
    messages.append({"role": "bot", "content": response})
    st.chat_message("bot").write(response)
    
st.session_state.messages = messages
