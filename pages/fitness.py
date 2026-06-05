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

if not profile:
    st.error("No health profile found. Please configure your profile first in settings.")
    st.stop()

st.title("🏋️ AI Workout Planner")
st.markdown("Receive customized workout plans aligned with your physical conditions, targets, and locations.")

# Active Streak Banner
st.markdown("""
<div style="background: rgba(229, 196, 131, 0.02); border: 1px solid rgba(229, 196, 131, 0.08); border-radius: 28px; padding: 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom: 25px; font-family: 'Plus Jakarta Sans', sans-serif;">
    <div>
        <span style="font-size:0.72rem; text-transform:uppercase; font-weight:500; color:#E5C483; letter-spacing:0.08em;">Active Habit Streak</span>
        <h3 style="margin:4px 0 0 0; color:#FFFFFF; font-family:'Cormorant Garamond', serif; font-size: 1.6rem; font-weight: 400;">🔥 5 Days Active</h3>
    </div>
    <div style="display:flex; gap:8px;">
        <div style="width:26px; height:26px; border-radius:50%; background:#E5C483; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#05070B;">M</div>
        <div style="width:26px; height:26px; border-radius:50%; background:#E5C483; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#05070B;">T</div>
        <div style="width:26px; height:26px; border-radius:50%; background:#E5C483; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#05070B;">W</div>
        <div style="width:26px; height:26px; border-radius:50%; background:#E5C483; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#05070B;">T</div>
        <div style="width:26px; height:26px; border-radius:50%; background:#E5C483; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#05070B;">F</div>
        <div style="width:26px; height:26px; border-radius:50%; background:rgba(255,255,255,0.01); border:1px dashed rgba(229, 196, 131, 0.2); display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:500; color:#9CA3AF;">S</div>
        <div style="width:26px; height:26px; border-radius:50%; background:rgba(255,255,255,0.01); border:1px dashed rgba(229, 196, 131, 0.2); display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:500; color:#9CA3AF;">S</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Side Filters
st.sidebar.subheader("Adjust Fitness Parameters")
# Case-insensitive index resolvers
goal_options = ["Weight Loss", "Muscle Gain", "Fat Loss", "General Fitness"]
goal_idx = 3
if profile and profile['goal']:
    db_goal = profile['goal'].strip().lower()
    for idx, opt in enumerate(goal_options):
        if opt.lower() == db_goal:
            goal_idx = idx
            break
goal = st.sidebar.selectbox("Workout Goal", goal_options, index=goal_idx)

exp_options = ["Beginner", "Intermediate", "Advanced"]
exp_idx = 0
if profile and profile['fitness_experience']:
    db_exp = profile['fitness_experience'].strip().lower()
    for idx, opt in enumerate(exp_options):
        if opt.lower() == db_exp:
            exp_idx = idx
            break
experience = st.sidebar.selectbox("Experience Level", exp_options, index=exp_idx)
category = st.sidebar.selectbox("Preferred Focus Category", ["Home Workouts", "Gym Workouts", "Yoga", "Cardio", "HIIT"])

temp_profile = {
    "age": profile['age'],
    "gender": profile['gender'],
    "height": profile['height'],
    "weight": profile['weight'],
    "goal": goal,
    "activity_level": profile['activity_level'],
    "dietary_preferences": profile['dietary_preferences'],
    "allergies": profile['allergies'],
    "medical_conditions": profile['medical_conditions'],
    "fitness_experience": experience
}

# Fetch latest routine
latest_workout = database.get_latest_workout_plan(user_id)

generate_btn = st.button("✨ Generate AI Workout Plan", type="primary")

if generate_btn:
    with st.spinner("Compiling exercise routine based on sports science..."):
        new_workout = gemini_service.generate_workout_plan(temp_profile)
        database.save_workout_plan(user_id, category, new_workout)
        database.add_badge(user_id, "Iron Will", "Generated a custom exercise routine", datetime.date.today().isoformat())
        st.success("Custom Workout Plan generated and saved!")
        latest_workout = {"plan_type": category, "plan_data": new_workout}

if latest_workout:
    w_type = latest_workout['plan_type']
    w_data = latest_workout['plan_data']
    
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #E5C483; background: rgba(229, 196, 131, 0.02);">
        <span class="premium-badge badge-blue">{w_type}</span>
        <h3 style="margin:8px 0 2px 0; font-family:'Cormorant Garamond', serif; font-size:1.6rem; font-weight:400;">{w_data.get('routine_name', 'Custom Workout Routine')}</h3>
        <span style="font-size:0.8rem; color:#9CA3AF; font-family:'Plus Jakarta Sans',sans-serif;">Custom compiled for goals matching: <b>{goal}</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    exercises = w_data.get('exercises', [])
    if exercises:
        for idx, ex in enumerate(exercises):
            st.markdown(f"""
            <div class="glass-card" style="padding: 24px; border-radius: 20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; font-family:'Plus Jakarta Sans',sans-serif;">
                    <div>
                        <h4 style="margin:0 0 4px 0; color:#FFFFFF; font-family:'Cormorant Garamond',serif; font-size:1.25rem; font-weight:400;">{idx + 1}. {ex.get('name', 'Exercise')}</h4>
                        <span class="premium-badge badge-purple" style="font-size:0.7rem;">{ex.get('category', w_type)}</span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:1.25rem; font-weight:600; color:#E5C483; font-family:'Cormorant Garamond',serif;">{ex.get('sets', 3)} Sets x {ex.get('reps', '10')}</span><br>
                        <span style="font-size:0.75rem; color:#9CA3AF;">Duration: {ex.get('duration', 'N/A')} | Rest: {ex.get('rest', '60s')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No exercises compiled in this routine.")
else:
    st.info("No workout routine generated yet. Click 'Generate AI Workout Plan' above.")
