import streamlit as st
import datetime
import database
import auth
from modules import gemini_service

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

user_id = auth.get_current_user_id()
profile = database.get_health_profile(user_id)
user = database.get_user_by_id(user_id)

st.title("💬 AI Health Assistant")
st.markdown("Consult your personalized AI coach regarding daily targets, nutrient profiles, ingredients, or fitness schedules.")

# Fetch chat history
chat_logs = database.get_chat_history(user_id, limit=50)

# Sidebar utilities
st.sidebar.subheader("Coach Configurations")
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    database.clear_chat_history(user_id)
    st.success("Chat history cleared!")
    st.rerun()

st.sidebar.markdown("""
<div class="glass-card" style="padding:15px; font-size:0.8rem; line-height:1.4; color:#94a3b8; margin-top:15px;">
    <b>Assistant Contexts:</b><br>
    - Analyzes caloric distributions<br>
    - Recommends custom recipes<br>
    - Builds training schedules<br>
    - Explains medical implications
</div>
""", unsafe_allow_html=True)

# Render Chat History using custom styled glassmorphism containers
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
for msg in chat_logs:
    role = msg['role']
    if role == "user":
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin-bottom:18px;">
            <div class="chat-bubble-user" style="max-width:75%; font-size:0.92rem; line-height:1.5; font-family:'Inter';">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-start; margin-bottom:18px; gap:12px; align-items: flex-start;">
            <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg, #E5C483 0%, #A68B5C 100%); display:flex; align-items:center; justify-content:center; font-weight:bold; color:#05070B; font-size:0.8rem; font-family:'Plus Jakarta Sans'; flex-shrink:0;">AI</div>
            <div class="chat-bubble-coach" style="max-width:75%; font-size:0.92rem; line-height:1.5; font-family:'Plus Jakarta Sans';">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat Input Box
user_prompt = st.chat_input("Message your AI Health Coach...")

if user_prompt:
    # Render user prompt locally immediately
    st.markdown(f"""
    <div style="display:flex; justify-content:flex-end; margin-bottom:18px;">
        <div class="chat-bubble-user" style="max-width:75%; font-size:0.92rem; line-height:1.5; font-family:'Inter';">
            {user_prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    database.add_chat_message(user_id, "user", user_prompt)
    
    # Render loader and coach reply
    with st.spinner("Coach is writing..."):
        current_history = database.get_chat_history(user_id, limit=10)
        coach_reply = gemini_service.chat_coach(current_history, user_prompt, profile)
        
    st.markdown(f"""
    <div style="display:flex; justify-content:flex-start; margin-bottom:18px; gap:12px; align-items: flex-start;">
        <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg, #E5C483 0%, #A68B5C 100%); display:flex; align-items:center; justify-content:center; font-weight:bold; color:#05070B; font-size:0.8rem; font-family:'Plus Jakarta Sans'; flex-shrink:0;">AI</div>
        <div class="chat-bubble-coach" style="max-width:75%; font-size:0.92rem; line-height:1.5; font-family:'Plus Jakarta Sans';">
            {coach_reply}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    database.add_chat_message(user_id, "assistant", coach_reply)
    database.add_badge(user_id, "Inquisitive Mind", "Consulted the AI Nutrition Coach", datetime.date.today().isoformat())
    st.rerun()
