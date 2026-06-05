import streamlit as st
import datetime
import plotly.graph_objects as go
import database
import auth
from modules import gemini_service

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

user_id = auth.get_current_user_id()

st.title("📷 AI Food Image Analyzer")
st.markdown("Upload a photo of your meal. Our intelligent vision module will identify the dish, estimate its ingredients, and break down its macro-nutrients.")

# File Uploader Container
st.markdown("<div class='glass-card' style='padding:20px;'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload meal photo...", type=["jpg", "png", "jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    
    col_img, col_res = st.columns([1, 1.2])
    
    with col_img:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Your Meal Capture")
        st.image(image_bytes, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_res:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("AI Vision Diagnostics")
        
        analyze_btn = st.button("🔍 Run Image Recognition Analysis", type="primary")
        
        analysis_key = f"food_analysis_{uploaded_file.name}"
        if analyze_btn or analysis_key in st.session_state:
            if analysis_key not in st.session_state:
                with st.spinner("Analyzing image features and estimated portions..."):
                    res = gemini_service.analyze_food_image(image_bytes)
                    st.session_state[analysis_key] = res
                    database.add_badge(user_id, "Visual Eater", "Analyzed a food meal using image recognition", datetime.date.today().isoformat())
            else:
                res = st.session_state[analysis_key]
                
            # Stats Card
            st.markdown(f"""
            <div style="background: rgba(229, 196, 131, 0.02); border: 1px solid rgba(229, 196, 131, 0.08); border-radius: 16px; padding: 20px; margin-bottom: 20px; font-family: 'Plus Jakarta Sans', sans-serif;">
                <h3 style="margin:0 0 4px 0; color:#FFFFFF; font-family:'Cormorant Garamond',serif; font-size:1.6rem; font-weight: 400;">{res.get('food_name', 'Identified Food')}</h3>
                <h2 style="margin:0 0 10px 0; color:#E5C483; font-family:'Cormorant Garamond',serif; font-size:2.2rem; font-weight: 400;">{int(res.get('calories', 0))} kcal</h2>
                <div style="display:flex; justify-content:space-between; margin-top:15px; font-size:0.9rem; color:#cbd5e1;">
                    <div><b>Protein:</b> {int(res.get('protein', 0))}g</div>
                    <div><b>Carbs:</b> {int(res.get('carbs', 0))}g</div>
                    <div><b>Fat:</b> {int(res.get('fat', 0))}g</div>
                    <div><b>Fiber:</b> {int(res.get('fiber', 0))}g</div>
                </div>
                <div style="margin-top:15px; font-weight:500; color:#E5C483; font-size:0.95rem;">Health Score: {res.get('health_rating', 0)}/10</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Donut chart
            labels = ['Protein (g)', 'Carbs (g)', 'Fat (g)']
            values = [res.get('protein', 0), res.get('carbs', 0), res.get('fat', 0)]
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#E5C483', '#A68B5C', '#161925'])])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=180,
                font=dict(color='#FFFFFF'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#FFFFFF'))
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 🥗 Detected Ingredients")
            for item in res.get('breakdown', []):
                st.markdown(f"- {item}")
                
            st.markdown("#### 💡 Health Suggestions")
            for sug in res.get('suggestions', []):
                st.markdown(f"- {sug}")
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Log Confirmation form
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📝 Confirm and Save to Journal")
            
            with st.form("confirm_log_form"):
                log_name = st.text_input("Meal Label", value=res.get('food_name', ''))
                log_meal = st.selectbox("Log Category", ["Breakfast", "Lunch", "Dinner", "Snack"])
                
                col_n1, col_n2, col_n3, col_n4 = st.columns(4)
                with col_n1:
                    log_cal = st.number_input("Calories", value=float(res.get('calories', 0.0)))
                with col_n2:
                    log_prot = st.number_input("Protein", value=float(res.get('protein', 0.0)))
                with col_n3:
                    log_carbs = st.number_input("Carbs", value=float(res.get('carbs', 0.0)))
                with col_n4:
                    log_fat = st.number_input("Fat", value=float(res.get('fat', 0.0)))
                    
                log_fib = st.number_input("Fiber", value=float(res.get('fiber', 0.0)))
                
                confirm_submit = st.form_submit_button("Confirm & Save to Journal")
                
                if confirm_submit:
                    database.add_food_log(
                        user_id=user_id,
                        food_name=log_name,
                        calories=log_cal,
                        protein=log_prot,
                        carbs=log_carbs,
                        fat=log_fat,
                        fiber=log_fib,
                        log_date=datetime.date.today().isoformat(),
                        meal_type=log_meal
                    )
                    st.success(f"Logged {log_name} to today's database!")
                    if analysis_key in st.session_state:
                        del st.session_state[analysis_key]
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Upload a food photo above to begin.")
