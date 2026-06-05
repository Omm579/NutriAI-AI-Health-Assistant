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
        <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 48px; font-weight: 400; line-height: 1.1; margin-bottom: 20px; color: #FFFFFF;">Start Your Personalized Health Journey.</h1>
        <p class="branding-slogan" style="color: #9CA3AF; font-size: 1.05rem; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif;">NutriAI aggregates health logs, calculates metabolic metrics, and uses visual intelligence to map out personalized nutrition guidelines.</p>
        <div style="margin-top: 50px; padding: 20px; border-left: 1px solid #E5C483; background: rgba(229,196,131,0.01); border-radius: 0 12px 12px 0;">
            <p style="font-style: italic; color:#9CA3AF; font-size: 0.95rem; line-height: 1.5; margin: 0; font-family: 'Cormorant Garamond', serif;">"To keep the body in good health is a duty... otherwise we shall not be able to keep our mind strong and clear."</p>
            <span style="font-size: 0.8rem; color: #E5C483; font-weight: 600; margin-top: 8px; display: block; font-family: 'Plus Jakarta Sans', sans-serif;">— Buddha</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_form:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; margin-bottom:8px; font-family:\"Cormorant Garamond\", serif; font-size: 1.8rem; font-weight: 400;'>Create Account</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF; font-size:0.9rem; margin-bottom:24px; font-family: \"Plus Jakarta Sans\", sans-serif;'>Enter details to configure your initial profile</p>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        name = st.text_input("Full Name").strip()
        username = st.text_input("Choose Username").strip()
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not name or not username or not password or not confirm_password:
                st.error("All fields are required.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                success, message = auth.register_user(username, password, name)
                if success:
                    st.success(message)
                    st.info("Redirecting to login...")
                    st.session_state["register_success"] = True
                    st.balloons()
                else:
                    st.error(message)
                    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; margin-top: 25px; margin-bottom: 5px; font-size:0.9rem; color:#9CA3AF; font-family: \"Plus Jakarta Sans\", sans-serif;'>Already have an account?</p>", unsafe_allow_html=True)
    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
    if st.button("Login here", key="go_to_login_btn", use_container_width=True):
        st.switch_page("pages/login.py")
    st.markdown("</div>", unsafe_allow_html=True)
