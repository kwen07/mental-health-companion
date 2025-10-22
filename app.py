import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Page config
st.set_page_config(page_title="Mental Health Companion", page_icon="🧠")

# Get API key and configure
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("⚠️ API key not configured. Please add your Gemini API key in Streamlit secrets.")
    st.stop()

# App title
st.title("🧠 Mental Health Companion")
st.write("Your free, private space for reflective journaling")

# Initialize session state
if 'entries' not in st.session_state:
    st.session_state.entries = []

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["📝 Journal Entry", "💡 Get Prompt", "📊 Therapy Prep", "📖 View History"]
)

# Helper function for emotion detection
def detect_emotion_with_gemini(text):
    prompt = "Analyze the emotion in this journal entry. Respond with ONLY one word from this list: joy, sadness, anger, fear, surprise, neutral\n\nJournal entry: " + text + "\n\nEmotion:"
    
    try:
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()
        valid_emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']
        if emotion not in valid_emotions:
            emotion = 'neutral'
        confidence = 0.85
        return emotion, confidence
    except:
        return "neutral", 0.5

# PAGE 1: Journal Entry
if page == "📝 Journal Entry":
    st.header("Write Your Thoughts")
    st.write("This is a safe, private space. Write freely about what's on your mind.")
    
    user_entry = st.text_area(
        "What's on your mind?",
        height=200,
        placeholder="Take your time... express whatever you're feeling..."
    )
    
    if st.button("💾 Save Entry", type="primary"):
        if user_entry.strip():
            with st.spinner("🔍 Analyzing your entry..."):
                emotion, confidence = detect_emotion_with_gemini(user_entry)
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry_data = {
                    'timestamp': timestamp,
                    'text': user_entry,
                    'emotion': emotion,
                    'confidence': confidence
                }
                st.session_state.entries.append(entry_data)
                
                st.success("✅ Entry saved!")
                
                st.info(f"**Detected emotion:** {emotion.capitalize()}")
                st.progress(confidence)
                st.caption(f"Confidence: {confidence:.1%}")
                
                support_prompt = f"You are a compassionate mental health companion. The user just journaled about their feelings (emotion: {emotion}). Provide a brief, warm, supportive response (2-3 sentences maximum). Be validating and encouraging.\n\nUser's entry: {user_entry[:300]}"
                
                try:
                    support_response = model.generate_content(support_prompt)
                    st.write("💙 **Response:**")
                    st.write(support_response.text)
                except:
                    supportive_messages = {
                        'joy': "💛 It's wonderful to see you feeling positive!",
                        'sadness': "💙 Thank you for sharing. It's okay to feel this way.",
