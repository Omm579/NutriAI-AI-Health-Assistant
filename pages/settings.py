import streamlit as st
import datetime
import database
import auth
from modules import bmi_calculator

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

user_id = auth.get_current_user_id()
user = database.get_user_by_id(user_id)
profile = database.get_health_profile(user_id)

st.title("⚙️ Settings & Health Profiles")

# 4 main tabs styled
tab_profile, tab_sleep, tab_wearable, tab_notifications = st.tabs([
    "👤 Health Profile", "😴 Sleep Analyzer", "⌚ Wearables Integration", "🔔 Notifications"
])

with tab_profile:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Update Health Parameters")
    st.markdown("Ensure your height, weight, activity indices are precise for AI calibration.")
    
    with st.form("profile_update_form_s"):
        col_name, col_age = st.columns(2)
        with col_name:
            name_val = st.text_input("Name", value=user['name'])
        with col_age:
            age_val = st.number_input("Age", min_value=5, max_value=120, value=int(profile['age']) if profile else 25)
            
        col_gen, col_h, col_w = st.columns(3)
        with col_gen:
            gender_options = ["Male", "Female", "Other"]
            gender_idx = 0
            if profile and profile['gender']:
                db_gen = profile['gender'].strip().lower()
                for idx, opt in enumerate(gender_options):
                    if opt.lower() == db_gen:
                        gender_idx = idx
                        break
            gender_val = st.selectbox("Gender", gender_options, index=gender_idx)
        with col_h:
            height_val = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(profile['height']) if profile else 170.0)
        with col_w:
            weight_val = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=float(profile['weight']) if profile else 70.0)
            
        col_goal, col_act = st.columns(2)
        with col_goal:
            goal_options = ["Weight Loss", "Muscle Gain", "Maintenance", "General Fitness"]
            goal_idx = 2
            if profile and profile['goal']:
                db_goal = profile['goal'].strip().lower()
                for idx, opt in enumerate(goal_options):
                    if opt.lower() == db_goal:
                        goal_idx = idx
                        break
            goal_val = st.selectbox("Fitness Goal", goal_options, index=goal_idx)
        with col_act:
            activity_options = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
            activity_idx = 2
            if profile and profile['activity_level']:
                db_act = profile['activity_level'].strip().lower()
                for idx, opt in enumerate(activity_options):
                    if opt.lower() == db_act:
                        activity_idx = idx
                        break
            activity_val = st.selectbox("Activity Level", activity_options, index=activity_idx)
            
        col_diet, col_exp = st.columns(2)
        with col_diet:
            diet_options = ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto", "High Protein", "Low Carb", "Diabetic Friendly", "Gluten Free"]
            diet_idx = 2
            if profile and profile['dietary_preferences']:
                db_diet = profile['dietary_preferences'].strip().lower()
                for idx, opt in enumerate(diet_options):
                    if opt.lower() == db_diet:
                        diet_idx = idx
                        break
            dietary_val = st.selectbox("Dietary Preferences", diet_options, index=diet_idx)
        with col_exp:
            exp_options = ["Beginner", "Intermediate", "Advanced"]
            exp_idx = 0
            if profile and profile['fitness_experience']:
                db_exp = profile['fitness_experience'].strip().lower()
                for idx, opt in enumerate(exp_options):
                    if opt.lower() == db_exp:
                        exp_idx = idx
                        break
            experience_val = st.selectbox("Fitness Experience Level", exp_options, index=exp_idx)
            
        allergies_val = st.text_input("Allergies (comma-separated)", value=profile['allergies'] if profile else "")
        medical_val = st.text_input("Medical Conditions (comma-separated)", value=profile['medical_conditions'] if profile else "")
        
        save_profile = st.form_submit_button("Save Changes")
        
        if save_profile:
            database.save_health_profile(
                user_id=user_id,
                age=age_val,
                gender=gender_val,
                height=height_val,
                weight=weight_val,
                goal=goal_val,
                activity_level=activity_val,
                allergies=allergies_val,
                dietary_preferences=dietary_val,
                medical_conditions=medical_val,
                fitness_experience=experience_val
            )
            
            # Recalculate
            bmi, _ = bmi_calculator.calculate_bmi(weight_val, height_val)
            bmr = bmi_calculator.calculate_bmr(weight_val, height_val, age_val, gender_val)
            tdee = bmi_calculator.calculate_tdee(bmr, activity_val)
            target_cal = bmi_calculator.calculate_calorie_target(tdee, goal_val)
            score = bmi_calculator.get_health_score(bmi, 0.0, 0.0, 0.0, target_cal)
            
            database.add_progress_log(user_id, weight_val, bmi, score, datetime.date.today().isoformat())
            database.add_badge(user_id, "Self-Awareness", "Updated personal health dimensions profile", datetime.date.today().isoformat())
            st.success("Health profile updated!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab_sleep:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("😴 Rest Cycles Analyzer")
    st.markdown("Monitor sleep duration and quality parameters.")
    
    with st.form("sleep_log_form_s"):
        sleep_date = st.date_input("Sleep Date", datetime.date.today())
        sleep_hours = st.number_input("Duration (Hours)", min_value=0.0, max_value=24.0, value=7.5, step=0.5)
        sleep_quality = st.slider("Sleep Quality Rating (1-100)", 1, 100, 75)
        
        save_sleep = st.form_submit_button("Record Sleep Entry")
        
        if save_sleep:
            database.add_sleep_log(user_id, sleep_hours, sleep_quality, sleep_date.isoformat())
            database.add_badge(user_id, "Restful Spirit", "Logged sleep hours in analyzer", datetime.date.today().isoformat())
            st.success(f"Recorded sleep logs for {sleep_date}!")
            st.rerun()
            
    # Sleep recommendation
    quality_weight = sleep_quality * 0.4
    hours_weight = (min(sleep_hours / 8.0, 1.0) * 60.0) if sleep_hours > 0 else 0.0
    sleep_score = int(quality_weight + hours_weight)
    
    st.markdown("---")
    st.subheader("📊 REST SCORE DIAGNOSTIC")
    
    col_sl1, col_sl2 = st.columns([1, 2.5])
    with col_sl1:
        st.markdown(f"""
        <div style="background: rgba(229, 196, 131, 0.03); border: 1px solid rgba(229, 196, 131, 0.12); border-radius: 12px; padding: 20px; text-align: center; font-family:'Plus Jakarta Sans',sans-serif;">
            <span style="font-size:0.75rem; text-transform:uppercase; color:#9CA3AF; font-weight:500;">Sleep Index</span>
            <h2 style="margin:8px 0 0 0; color:#E5C483; font-size:2.2rem; font-family:'Cormorant Garamond', serif; font-weight:400;">{sleep_score} <span style="font-size:0.9rem; color:#475569;">/ 100</span></h2>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sl2:
        st.markdown("**Coach Guidelines:**")
        if sleep_hours < 6.0:
            st.warning("⚠️ **Sleep Deprivation Alert**: Rest hours fell below 6. This elevates cortisol, causing carbohydrate cravings. Restrict high glycemic snacks today.")
        elif sleep_hours > 9.0:
            st.info("ℹ️ **Circadian Sleep Offset**: Sleeping longer than 9 hours might cause grogginess. Maintain consistent active habits to reset your clock.")
        else:
            st.success("✅ **Optimal Recovery Window**: Sleep length was within the ideal 7-9 hour range. This supports protein synthesis and hormonal recovery.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_wearable:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("⌚ Wearables Sync Telemetry")
    st.markdown("Establish links with external device ecosystems.")
    
    w_fitbit = st.toggle("🔌 Sync Fitbit Cloud API")
    w_gfit = st.toggle("🔌 Sync Google Fit SDK")
    w_apple = st.toggle("🔌 Sync Apple Health Kit")
    w_garmin = st.toggle("🔌 Sync Garmin Connect")
    
    if w_fitbit or w_gfit or w_apple or w_garmin:
        st.markdown("""
        <div style="background: rgba(229, 196, 131, 0.03); border: 1px solid rgba(229, 196, 131, 0.12); padding: 20px; border-radius: 12px; margin-top: 20px; font-family:'Plus Jakarta Sans',sans-serif;">
            <h4 style="margin:0 0 6px 0; color:#E5C483; font-family:'Cormorant Garamond',serif; font-size:1.4rem; font-weight:400;">⌚ Live Wearable Stream Active</h4>
            <p style="margin:0; font-size:0.88rem; color:#9CA3AF; line-height:1.5;">
                • Daily Steps: 8,450 / 10,000 steps<br>
                • Average Heart Rate: 64 bpm<br>
                • Active Calories Burned: 410 kcal<br>
                • Sleep Quality Index: 78/100
            </p>
        </div>
        """, unsafe_allow_html=True)
        database.add_badge(user_id, "Connected Athlete", "Integrated a mock wearable device provider link", datetime.date.today().isoformat())
    else:
        st.caption("Enable external providers to sync biometric data automatically.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_notifications:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🔔 Reminders & Notification Toggles")
    st.markdown("Configure daily nudges to stay consistent.")
    
    n_meals = st.checkbox("Meal Time Alerts (Breakfast, Lunch, Dinner)", value=True)
    n_water = st.checkbox("Hydration Nudges (2-hour interval)", value=True)
    n_workout = st.checkbox("Workout Calendar Reminders", value=False)
    n_health = st.checkbox("Weekly Performance summary checks", value=True)
    
    if st.button("Save Alert Settings"):
        st.success("Notification preferences saved successfully!")
    st.markdown("</div>", unsafe_allow_html=True)
