import streamlit as st
import auth

# Inject local styles in case of routing updates
st.markdown("""
<style>
    .stApp {
        background-color: #05070B !important;
    }
</style>
""", unsafe_allow_html=True)

# Split Layout
col_brand, col_form = st.columns([1.2, 1])

with col_brand:
    st.markdown("""
    <div class="split-left-branding" style="padding-top: 40px;">
        <div style="margin-bottom: 40px;">
            <span style="font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 500; color: #E5C483; vertical-align: middle;">🥗 NutriAI</span>
        </div>
        <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 48px; font-weight: 400; line-height: 1.1; margin-bottom: 20px; color: #FFFFFF;">Transform Your Health with Precision AI.</h1>
        <p class="branding-slogan" style="color: #9CA3AF; font-size: 1.05rem; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif;">NutriAI aggregates health logs, calculates metabolic metrics, and uses visual intelligence to map out personalized nutrition guidelines.</p>
        <div style="margin-top: 50px; padding: 20px; border-left: 1px solid #E5C483; background: rgba(229,196,131,0.01); border-radius: 0 12px 12px 0;">
            <p style="font-style: italic; color:#9CA3AF; font-size: 0.95rem; line-height: 1.5; margin: 0; font-family: 'Cormorant Garamond', serif;">"Let food be thy medicine and medicine be thy food."</p>
            <span style="font-size: 0.8rem; color: #E5C483; font-weight: 600; margin-top: 8px; display: block; font-family: 'Plus Jakarta Sans', sans-serif;">— Hippocrates</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_form:
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; margin-bottom:8px; font-family:\"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: 400;'>Welcome Back</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF; font-size:0.9rem; margin-bottom:24px; font-family: \"Plus Jakarta Sans\", sans-serif;'>Enter credentials to access your dashboard</p>", unsafe_allow_html=True)
    
    # Social sign-in mocks
    st.markdown("""
    <div style="display:flex; gap:12px; margin-bottom:20px; font-family: 'Plus Jakarta Sans', sans-serif;">
        <div style="flex:1; padding:10px; border: 1px solid rgba(229,196,131,0.08); border-radius:8px; text-align:center; cursor:pointer; background:rgba(255,255,255,0.01); font-size:0.82rem; font-weight:500; color:#E5C483;">
            🔑 Google Sync
        </div>
        <div style="flex:1; padding:10px; border: 1px solid rgba(229,196,131,0.08); border-radius:8px; text-align:center; cursor:pointer; background:rgba(255,255,255,0.01); font-size:0.82rem; font-weight:500; color:#E5C483;">
            🍏 Apple ID
        </div>
    </div>
    <div style="text-align:center; color:#A68B5C; font-size:0.75rem; margin-bottom:20px; font-weight:500; text-transform:uppercase; letter-spacing:0.05em; font-family: 'Plus Jakarta Sans', sans-serif;">Or continue with email</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                success, message = auth.login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; margin-top: 25px; margin-bottom: 5px; font-size:0.9rem; color:#9CA3AF; font-family: \"Plus Jakarta Sans\", sans-serif;'>New to the platform?</p>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
    if st.button("Create account", key="go_to_register_btn", use_container_width=True):
        st.switch_page("pages/register.py")
    st.markdown("</div>", unsafe_allow_html=True)
