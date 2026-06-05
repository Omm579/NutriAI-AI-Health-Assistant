import streamlit as st
import os
import auth
import database
from config import HAS_GEMINI_API

# 1. Page Configuration
st.set_page_config(
    page_title="NutriAI - Intelligent Health Platform",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize database
database.init_db()

# 3. Global CSS Inject for Premium Dark SaaS Aesthetics
css_path = os.path.join(os.path.dirname(__file__), "styles", "premium_theme.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 4. Programmatic Navigation & Routing
if not auth.is_logged_in():
    # Authentication views
    pg = st.navigation([
        st.Page("pages/login.py", title="Login", icon="🔒"),
        st.Page("pages/register.py", title="Register", icon="👤")
    ])
else:
    # Authenticated user routes grouped in sidebar
    insights_pages = [
        st.Page("pages/reports.py", title="Reports & Exports", icon="📊"),
        st.Page("pages/settings.py", title="Profile & Settings", icon="⚙"),
    ]
    if st.session_state.get('username') == 'admin':
        insights_pages.append(st.Page("pages/admin.py", title="System Analytics", icon="🛠"))
        
    pg = st.navigation({
        "NutriAI Tracker": [
            st.Page("pages/dashboard.py", title="Dashboard", icon="🏠"),
            st.Page("pages/food_analyzer.py", title="Food Image Analyzer", icon="📷"),
        ],
        "AI Co-Pilots": [
            st.Page("pages/meal_planner.py", title="AI Meal Planner", icon="🍽"),
            st.Page("pages/fitness.py", title="Workout Planner", icon="🏋"),
            st.Page("pages/chatbot.py", title="AI Health Assistant", icon="💬"),
        ],
        "Insights & Reports": insights_pages
    })

st.sidebar.markdown("""
<div style="padding: 10px 0; margin-bottom: 15px; display:flex; align-items:center; gap:8px;">
    <span style="font-size: 1.8rem;">🥗</span>
    <span style="font-weight: 600; font-size: 1.35rem; color: #FFFFFF; font-family: 'Cormorant Garamond', serif; letter-spacing: -0.01em;">NutriAI</span>
    <span style="background: rgba(229, 196, 131, 0.08); color: #E5C483; font-size: 0.65rem; font-weight: 600; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(229, 196, 131, 0.2); margin-left: 4px;">PRO</span>
</div>
""", unsafe_allow_html=True)

if auth.is_logged_in():
    user_name = st.session_state.get('name', 'User')
    initials = "".join([part[0] for part in user_name.split()[:2]]).upper()
    
    st.sidebar.markdown(f"""
    <div style='display:flex; align-items:center; gap:12px; margin: 15px 0 20px 0; background: rgba(255,255,255,0.01); border: 1px solid rgba(229, 196, 131, 0.08); padding: 12px; border-radius: 12px;'>
        <div style='width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg, #E5C483 0%, #A68B5C 100%); display:flex; align-items:center; justify-content:center; font-weight:bold; color:#05070B; font-size:0.85rem; font-family: "Plus Jakarta Sans", sans-serif;'>{initials}</div>
        <div style="line-height: 1.2;">
            <b style='font-size:0.85rem; color:#FFFFFF;'>{user_name}</b><br>
            <span style='font-size:0.75rem; color:#9CA3AF;'>Active Profile</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not HAS_GEMINI_API:
        st.sidebar.markdown("""
        <div style="background: rgba(229, 196, 131, 0.03); border: 1px solid rgba(229, 196, 131, 0.15); padding: 8px 12px; border-radius: 8px; font-size: 0.75rem; color: #E5C483; margin-bottom: 15px;">
            ⚠️ <b>Running in Mock Mode</b><br>Gemini API key missing.
        </div>
        """, unsafe_allow_html=True)
        
    st.sidebar.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.sidebar.button("Logout", key="logout_btn"):
        auth.logout_user()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Run page router
pg.run()
