import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_text(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# Geolocation with caching
geolocator = Nominatim(user_agent="vedic_horoscope_app")
@st.cache_data
def get_coordinates(place):
    location = geolocator.geocode(place)
    return (location.latitude, location.longitude) if location else (0, 0)

# App setup - Must be first Streamlit command
st.set_page_config(page_title="Vedic Astrology Chat", page_icon="✨", layout="wide")

# Custom CSS for professional look
st.markdown("""
    <style>
    .main { background: linear-gradient(to bottom, #1a1a2e, #16213e); color: #e0e0e0; }
    .stTextInput > div > div > input { background-color: #2a2a4a; color: #e0e0e0; border: 1px solid #4a4a8a; }
    .stButton > button { background-color: #4a4a8a; color: white; border-radius: 5px; }
    .stButton > button:hover { background-color: #6a6aaa; }
    h1 { color: #ffd700; text-align: center; font-family: 'Georgia', serif; }
    .stExpander { background-color: #2a2a4a; border: 1px solid #4a4a8a; }
    .disclaimer { font-size: 12px; color: #a0a0a0; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Password from secrets
PASSWORD = st.secrets["APP_PASSWORD"]  # Retrieve password from Streamlit secrets

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication logic
if not st.session_state.authenticated:
    st.title("✨ Vedic Astrology Chat - Login ✨")
    password_input = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted! Welcome to Vedic Astrology Chat.")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
else:
    # Main app content
    st.title("✨ Vedic Astrology Chat ✨")

    # Disclaimer
    st.markdown("""
        <div class="disclaimer">
        This app provides general astrology insights using AI and is not a substitute for a professional Vedic astrologer. 
        For accurate readings, including full Kundli analysis and predictions, consult a qualified astrologer.
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "bot", "content": "Welcome! Please enter your name to begin."}]
    if "step" not in st.session_state:
        st.session_state.step = "name"

    # Display chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # User input
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Step-by-step data collection
        if st.session_state.step == "name":
            st.session_state.name = user_input
            response = f"Nice to meet you, {user_input}! Please provide your date of birth (DD/MM/YYYY)."
            st.session_state.step = "dob"
        
        elif st.session_state.step == "dob":
            try:
                st.session_state.dob = datetime.strptime(user_input, "%d/%m/%Y").date()
                response = "Thank you! Now, what time were you born? (HH:MM, 24-hour format)"
                st.session_state.step = "tob"
            except ValueError:
                response = "Please enter a valid date (e.g., 09/12/1989)."
        
        elif st.session_state.step == "tob":
            try:
                st.session_state.tob = datetime.strptime(user_input, "%H:%M").time()
                response = "Great! Where were you born? (City, Country)"
                st.session_state.step = "place"
            except ValueError:
                response = "Please enter a valid time (e.g., 23:00)."
        
        elif st.session_state.step == "place":
            st.session_state.place = user_input
            lat, lon = get_coordinates(user_input)
            response = f"Got it! Your birth details: {st.session_state.dob}, {st.session_state.tob}, {st.session_state.place}. Would you like a personal insight or to check compatibility with a partner?"
            st.session_state.step = "choice"
        
        elif st.session_state.step == "choice":
            if user_input.lower() in ["personal", "personal insight", "insight"]:
                prompt = f"Provide general Vedic astrology insights for {st.session_state.name}, born on {st.session_state.dob} at {st.session_state.tob} in {st.session_state.place}. Focus on personality, career, and relationships without specific predictions."
                response = generate_text(prompt)
                st.session_state.step = "done"
            elif user_input.lower() in ["partner", "compatibility", "match"]:
                response = "Please enter your partner's name."
                st.session_state.step = "partner_name"
            else:
                response = "Please choose: 'personal insight' or 'compatibility'."
        
        elif st.session_state.step == "partner_name":
            st.session_state.partner_name = user_input
            response = f"Partner's name: {user_input}. Please provide their date of birth (DD/MM/YYYY)."
            st.session_state.step = "partner_dob"
        
        elif st.session_state.step == "partner_dob":
            try:
                st.session_state.partner_dob = datetime.strptime(user_input, "%d/%m/%Y").date()
                response = "Now, what time was your partner born? (HH:MM)"
                st.session_state.step = "partner_tob"
            except ValueError:
                response = "Please enter a valid date (e.g., 09/12/1989)."
        
        elif st.session_state.step == "partner_tob":
            try:
                st.session_state.partner_tob = datetime.strptime(user_input, "%H:%M").time()
                response = "Finally, where was your partner born? (City, Country)"
                st.session_state.step = "partner_place"
            except ValueError:
                response = "Please enter a valid time (e.g., 23:00)."
        
        elif st.session_state.step == "partner_place":
            st.session_state.partner_place = user_input
            partner_lat, partner_lon = get_coordinates(user_input)
            prompt = f"Provide a Vedic astrology compatibility overview (e.g., Guna Milan-inspired) for {st.session_state.name} (born {st.session_state.dob} at {st.session_state.tob} in {st.session_state.place}) and {st.session_state.partner_name} (born {st.session_state.partner_dob} at {st.session_state.partner_tob} in {st.session_state.partner_place}). Include a general compatibility score out of 36 and insights on relationship harmony, without precise chart calculations."
            response = generate_text(prompt)
            st.session_state.step = "done"
        
        elif st.session_state.step == "done":
            prompt = f"General Vedic astrology insights for {st.session_state.name} born on {st.session_state.dob} at {st.session_state.tob} in {st.session_state.place}: {user_input}"
            response = generate_text(prompt)

        st.session_state.messages.append({"role": "bot", "content": response})
        st.chat_message("bot").write(response)

    # Reset button
    if st.session_state.step == "done":
        if st.button("Start Over"):
            st.session_state.messages = [{"role": "bot", "content": "Welcome! Please enter your name to begin."}]
            st.session_state.step = "name"
            st.rerun()

    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.clear()
        st.rerun()
