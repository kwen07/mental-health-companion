import streamlit as st
from transformers import pipeline
from datetime import datetime

# Page config
st.set_page_config(page_title="Mental Health Companion", page_icon="🧠")

# Load models (cached so they only load once)
@st.cache_resource
def load_emotion_detector():
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=False
    )

@st.cache_resource
def load_text_generator():
    return pipeline(
        'text-generation',
        model='distilgpt2',
        max_length=100,
        pad_token_id=50256
    )

# Load models with progress
with st.spinner("🔄 Loading AI models... (first time takes 2-3 minutes)"):
    emotion_detector = load_emotion_detector()
    text_generator = load_text_generator()

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
                    # Detect emotion
                    result = emotion_detector(user_entry)[0]
                    emotion = result['label']
                    confidence = result['score']
                    
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
                    
                    # Supportive message based on emotion
                    supportive_messages = {
                        'joy': "💛 It's wonderful to see you feeling positive!",
                        'sadness': "💙 Thank you for sharing. It's okay to feel this way.",
                        'anger': "❤️ Your feelings are valid. Take time to process them.",
                        'fear': "💜 It's brave of you to acknowledge these feelings.",
                        'surprise': "💚 Life can be unexpected. You're handling it well.",
                        'disgust': "🧡 Your feelings matter. Take care of yourself.",
                        'neutral': "💙 Thank you for taking time to journal today."
                    }
                    
                    message = supportive_messages.get(emotion, "💙 Thank you for sharing.")
                    st.write(message)
                    
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
            # Create prompt based on topic
            prompt_starters = {
                "General Reflection": "Write a reflective journaling prompt that encourages self-awareness:",
                "Stress & Anxiety": "Write a calming journaling prompt about managing stress and anxiety:",
                "Gratitude": "Write an uplifting journaling prompt about gratitude and appreciation:",
                "Self-Compassion": "Write a kind journaling prompt about self-compassion and self-care:",
                "Relationships": "Write a thoughtful journaling prompt about relationships and connections:",
                "Personal Growth": "Write an inspiring journaling prompt about personal growth and goals:",
                "Emotions": "Write a gentle journaling prompt about understanding and expressing emotions:"
            }
            
            starter = prompt_starters.get(topic, "Write a reflective journaling prompt:")
            
            # Generate with the model
            generated = text_generator(starter, max_length=60, num_return_sequences=1)[0]['generated_text']
            
            # Clean up the output (remove the starter text)
            prompt_text = generated.replace(starter, "").strip()
            
            # If generation isn't great, use fallback prompts
            fallback_prompts = {
                "General Reflection": "What were three moments today that made you feel something? Describe each moment and the emotion it brought up.",
                "Stress & Anxiety": "What's weighing on your mind right now? Write about one thing you're worried about and one small step you could take to address it.",
                "Gratitude": "List five small things from today that you're grateful for. Why did each one matter to you?",
                "Self-Compassion": "If your best friend was going through what you're experiencing, what would you say to them? Now, say those words to yourself.",
                "Relationships": "Think of someone who matters to you. What do you appreciate about them? When did you last tell them?",
                "Personal Growth": "What's one thing you'd like to improve about yourself? What's one small action you could take this week?",
                "Emotions": "What emotion have you been feeling most lately? Where do you feel it in your body? What might it be trying to tell you?"
            }
            
            # Use fallback if generated text is too short or unclear
            if len(prompt_text) < 20:
                prompt_text = fallback_prompts[topic]
            
            st.write("### 💭 Your Journaling Prompt:")
            st.info(prompt_text)
            
            st.write("---")
            st.write("**Ready to write?** Use the space below:")
            
            quick_entry = st.text_area("Your response:", height=150, key="quick_journal")
            
            if st.button("Save This Entry"):
                if quick_entry.strip():
                    with st.spinner("Analyzing..."):
                        result = emotion_detector(quick_entry)[0]
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        entry_data = {
                            'timestamp': timestamp,
                            'text': f"Prompt: {prompt_text}\n\nResponse: {quick_entry}",
                            'emotion': result['label'],
                            'confidence': result['score']
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
        
        # Recent entries summary
        st.write("### 📋 Key Themes to Discuss")
        st.write("Based on your recent entries:")
        
        recent_entries = st.session_state.entries[-5:]  # Last 5 entries
        recent_emotions = [e['emotion'] for e in recent_entries]
        most_common = max(set(recent_emotions), key=recent_emotions.count)
        
        st.write(f"- Your most frequent emotion recently has been **{most_common}**")
        st.write(f"- You've made **{len(st.session_state.entries)}** journal entries")
        st.write("- Consider discussing patterns you've noticed in your emotional responses")
        
        st.write("---")
        
        # Export for therapist
        st.write("### 📥 Export Summary for Your Therapist")
        
        if st.button("Generate Summary"):
            summary = f"""THERAPY SESSION PREP SUMMARY
Generated: {datetime.now().strftime("%Y-%m-%d")}

EMOTIONAL OVERVIEW:
"""
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(emotions)) * 100
                summary += f"- {emotion.capitalize()}: {count} entries ({percentage:.1f}%)\n"
            
            summary += f"\nRECENT ENTRIES ({len(recent_entries)} most recent):\n\n"
            
            for i, entry in enumerate(reversed(recent_entries), 1):
                summary += f"{i}. [{entry['timestamp']}] - {entry['emotion'].capitalize()}\n"
                summary += f"   {entry['text'][:200]}...\n\n"
            
            st.text_area("Copy this summary:", summary, height=300)
            
            st.download_button(
                "📄 Download as Text File",
                data=summary,
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
This is a free, private mental health companion powered by AI.

**Features:**
- Emotion detection in your writing
- AI-generated journaling prompts
- Therapy session preparation
- Complete privacy (data stays on your device)
""")
st.sidebar.write(f"**Your entries:** {len(st.session_state.entries)}")