import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Page config
st.set_page_config(page_title="Mental Health Companion", page_icon="🧠")

# Get API key from Streamlit secrets (we'll set this up)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
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
    prompt = f"""Analyze the emotion in this journal entry. Respond with ONLY a JSON object in this exact format:
{{"emotion": "one of: joy, sadness, anger, fear, surprise, neutral", "confidence": 0.85}}

Journal entry: {text}"""
    
    try:
        response = model.generate_content(prompt)
        # Parse the response
        import json
        result = json.loads(response.text)
        return result['emotion'], result['confidence']
    except:
        # Fallback
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
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("💾 Save Entry", type="primary"):
            if user_entry.strip():
                with st.spinner("🔍 Analyzing your entry..."):
                    # Detect emotion using Gemini
                    emotion, confidence = detect_emotion_with_gemini(user_entry)
                    
                    # Save entry
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry_data = {
                        'timestamp': timestamp,
                        'text': user_entry,
                        'emotion': emotion,
                        'confidence': confidence
                    }
                    st.session_state.entries.append(entry_data)
                    
                    # Success message
                    st.success("✅ Entry saved!")
                    
                    # Show emotion
                    st.info(f"**Detected emotion:** {emotion.capitalize()}")
                    st.progress(confidence)
                    st.caption(f"Confidence: {confidence:.1%}")
                    
                    # Get supportive response from Gemini
                    support_prompt = f"""You are a compassionate mental health companion. The user just journaled about their feelings (emotion: {emotion}).
Provide a brief, warm, supportive response (2-3 sentences maximum). Be validating and encouraging.

User's entry: {user_entry[:300]}"""
                    
                    support_response = model.generate_content(support_prompt)
                    st.write("💙 **Response:**")
                    st.write(support_response.text)
                    
            else:
                st.warning("⚠️ Please write something first")

# PAGE 2: Get Journaling Prompt
elif page == "💡 Get Prompt":
    st.header("Get a Journaling Prompt")
    st.write("Need inspiration? Generate a thoughtful prompt to guide your journaling.")
    
    topic = st.selectbox(
        "Choose a focus area:",
        ["General Reflection", "Stress & Anxiety", "Gratitude", 
         "Self-Compassion", "Relationships", "Personal Growth", "Emotions"]
    )
    
    if st.button("✨ Generate Prompt", type="primary"):
        with st.spinner("🤔 Creating your prompt..."):
            prompt_request = f"""Create a thoughtful, open-ended journaling prompt about {topic.lower()}.
Make it compassionate, encouraging self-reflection. Keep it 2-3 sentences. Be specific and actionable."""
            
            response = model.generate_content(prompt_request)
            prompt_text = response.text
            
            st.write("### 💭 Your Journaling Prompt:")
            st.info(prompt_text)
            
            st.write("---")
            st.write("**Ready to write?** Use the space below:")
            
            quick_entry = st.text_area("Your response:", height=150, key="quick_journal")
            
            if st.button("Save This Entry"):
                if quick_entry.strip():
                    with st.spinner("Analyzing..."):
                        emotion, confidence = detect_emotion_with_gemini(quick_entry)
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        entry_data = {
                            'timestamp': timestamp,
                            'text': f"Prompt: {prompt_text}\n\nResponse: {quick_entry}",
                            'emotion': emotion,
                            'confidence': confidence
                        }
                        st.session_state.entries.append(entry_data)
                        st.success("✅ Entry saved!")

# PAGE 3: Therapy Prep
elif page == "📊 Therapy Prep":
    st.header("Therapy Session Preparation")
    st.write("Review your journal entries and identify patterns to discuss in therapy.")
    
    if len(st.session_state.entries) == 0:
        st.info("📝 No journal entries yet. Start journaling to generate insights for therapy!")
    else:
        st.write(f"**Total entries:** {len(st.session_state.entries)}")
        
        # Emotion distribution
        st.write("### 📊 Your Emotional Patterns")
        emotions = [entry['emotion'] for entry in st.session_state.entries]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Display as a simple chart
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(emotions)) * 100
            st.write(f"**{emotion.capitalize()}**: {count} entries ({percentage:.1f}%)")
            st.progress(percentage / 100)
        
        st.write("---")
        
        # AI-generated therapy prep
        st.write("### 🤖 AI-Generated Therapy Prep Summary")
        
        if st.button("Generate Therapy Summary", type="primary"):
            with st.spinner("📊 Analyzing your journal entries..."):
                # Compile recent entries
                recent_entries = st.session_state.entries[-10:]
                entries_text = "\n\n".join([
                    f"[{e['timestamp']}] Emotion: {e['emotion']}\n{e['text'][:400]}"
                    for e in recent_entries
                ])
                
                summary_prompt = f"""You are a mental health assistant helping prepare for therapy.

Based on these journal entries, create a concise summary with:
1. Key emotional themes (3-5 bullet points)
2. Suggested discussion topics for therapy (3-4 topics)
3. Questions to explore with therapist (2-3 questions)

Keep it professional, concise, and actionable.

Recent journal entries:
{entries_text}"""
                
                response = model.generate_content(summary_prompt)
                
                st.write(response.text)
                
                # Export option
                st.write("---")
                full_summary = f"""THERAPY SESSION PREP SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d")}

{response.text}

EMOTIONAL DISTRIBUTION:
"""
                for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(emotions)) * 100
                    full_summary += f"- {emotion.capitalize()}: {count} entries ({percentage:.1f}%)\n"
                
                st.download_button(
                    "📄 Download Summary",
                    data=full_summary,
                    file_name=f"therapy_prep_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

# PAGE 4: View History
elif page == "📖 View History":
    st.header("Your Journal History")
    
    if len(st.session_state.entries) == 0:
        st.info("📝 No entries yet. Start journaling to see your history here!")
    else:
        st.write(f"**Total entries:** {len(st.session_state.entries)}")
        
        # Filter by emotion
        all_emotions = list(set([e['emotion'] for e in st.session_state.entries]))
        filter_emotion = st.selectbox("Filter by emotion:", ["All"] + all_emotions)
        
        # Display entries
        filtered_entries = st.session_state.entries
        if filter_emotion != "All":
            filtered_entries = [e for e in st.session_state.entries if e['emotion'] == filter_emotion]
        
        st.write(f"Showing {len(filtered_entries)} entries")
        
        for i, entry in enumerate(reversed(filtered_entries)):
            with st.expander(f"📅 {entry['timestamp']} - {entry['emotion'].capitalize()}"):
                st.write(entry['text'])
                st.caption(f"Confidence: {entry['confidence']:.1%}")
        
        # Export all
        st.write("---")
        if st.button("📥 Export All Entries"):
            export_text = ""
            for entry in st.session_state.entries:
                export_text += f"\n{'='*60}\n"
                export_text += f"Date: {entry['timestamp']}\n"
                export_text += f"Emotion: {entry['emotion']} (confidence: {entry['confidence']:.1%})\n"
                export_text += f"\n{entry['text']}\n"
            
            st.download_button(
                "💾 Download Complete Journal",
                data=export_text,
                file_name=f"complete_journal_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

# Sidebar info
st.sidebar.write("---")
st.sidebar.write("### 💙 About This App")
st.sidebar.info("""
This is a free mental health companion powered by Google Gemini AI.

**Features:**
- AI emotion detection
- Personalized journaling prompts
- Therapy session preparation
- Secure and private
""")
st.sidebar.write(f"**Your entries:** {len(st.session_state.entries)}")
