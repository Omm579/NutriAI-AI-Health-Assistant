import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

if not profile:
    st.error("No health profile found. Please create your profile in settings.")
    st.stop()

# ----------------- MATH & LOGS QUERY -----------------
bmr = bmi_calculator.calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'])
tdee = bmi_calculator.calculate_tdee(bmr, profile['activity_level'])
cal_target = bmi_calculator.calculate_calorie_target(tdee, profile['goal'])
macros_target = bmi_calculator.recommend_macros(cal_target, profile['dietary_preferences'])
bmi, bmi_category = bmi_calculator.calculate_bmi(profile['weight'], profile['height'])

today = datetime.date.today().isoformat()
food_logs_today = database.get_food_logs_by_date(user_id, today)
water_today = database.get_water_intake_by_date(user_id, today)

consumed_cal = sum(f['calories'] for f in food_logs_today)
consumed_prot = sum(f['protein'] for f in food_logs_today)
consumed_carb = sum(f['carbs'] for f in food_logs_today)
consumed_fat = sum(f['fat'] for f in food_logs_today)

cal_remaining = max(0.0, cal_target - consumed_cal)
cal_pct = min(1.0, consumed_cal / cal_target) if cal_target > 0 else 0.0

# Sleep log
sleep_logs_today = database.get_sleep_logs_by_date_range(user_id, today, today)
sleep_hours = sleep_logs_today[0]['hours'] if sleep_logs_today else 0.0

# Calculate daily health score
health_score = bmi_calculator.get_health_score(bmi, water_today, sleep_hours, consumed_cal, cal_target)

# Auto-save today's progress data if changed or not exists
database.add_progress_log(user_id, profile['weight'], bmi, health_score, today)

# ----------------- UI / LAYOUT -----------------

# Welcome Banner Component (Startup Dashboard Style)
st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(229, 196, 131, 0.04) 0%, rgba(5, 7, 11, 0) 100%); border: 1px solid rgba(229, 196, 131, 0.08); border-radius: 28px; padding: 32px; margin-bottom: 30px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
    <div>
        <h1 style="margin:0; font-size:32px; font-weight:400; color: #FFFFFF; font-family: 'Cormorant Garamond', serif;">Welcome Back, {user['name']}!</h1>
        <p style="margin:8px 0 0 0; color:#9CA3AF; font-size:1.02rem; font-family: 'Plus Jakarta Sans', sans-serif;">"Your body achieves what your mind believes. Today is a great day to crush your macros."</p>
    </div>
    <div style="background:rgba(229,196,131,0.01); border:1px solid rgba(229,196,131,0.08); border-radius:12px; padding:12px 20px; text-align:right;">
        <span style="font-size:0.72rem; font-weight:500; color:#A68B5C; text-transform:uppercase; letter-spacing:0.08em; font-family: 'Plus Jakarta Sans', sans-serif;">Daily Vitality Index</span>
        <h3 style="margin:4px 0 0 0; color:#E5C483; font-size:1.8rem; font-family: 'Cormorant Garamond', serif; font-weight:400;">{health_score} <span style="font-size:1.1rem; color:#475569;">/ 100</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Stat Cards Row
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #E5C483;">
        <div class="premium-metric-lbl">🔥 Calorie Balance</div>
        <div class="premium-metric-val">{int(consumed_cal)} <span style="font-size:1.1rem; color:#475569;">/ {int(cal_target)} kcal</span></div>
        <div class="premium-metric-sub">
            <span style="color: {'#E5C483' if cal_remaining > 0 else '#ef4444'}; font-weight:600;">{int(cal_remaining)} kcal</span> remaining
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #C5A880;">
        <div class="premium-metric-lbl">💧 Hydration Level</div>
        <div class="premium-metric-val">{int(water_today)} <span style="font-size:1.1rem; color:#475569;">/ 2000 ml</span></div>
        <div class="premium-metric-sub">
            <span style="color:#C5A880; font-weight:600;">{int((water_today/2000)*100)}%</span> of daily goal completed
        </div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #A68B5C;">
        <div class="premium-metric-lbl">⚖️ Body Mass Index</div>
        <div class="premium-metric-val">{bmi}</div>
        <div class="premium-metric-sub">
            <span class="premium-badge {'badge-green' if bmi_category=='Normal Weight' else 'badge-blue' if bmi_category=='Underweight' else 'badge-purple'}">{bmi_category}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #856C42;">
        <div class="premium-metric-lbl">😴 Sleep Hours</div>
        <div class="premium-metric-val">{sleep_hours} <span style="font-size:1.1rem; color:#475569;">/ 7.5 hrs</span></div>
        <div class="premium-metric-sub">
            <span style="color:#A68B5C; font-weight:600;">{"Optimal Rest" if sleep_hours >= 7 else "Needs Improvement" if sleep_hours > 0 else "Not Tracked Today"}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Grid: Left column for logging counters, Right column for Plotly SaaS graphics
col_left, col_right = st.columns([1, 1.25])

with col_left:
    # 1. Quick Add Water Tracker
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💧 Hydration Tracker")
    st.write("Record fluid intake dynamically.")
    
    # Progress indicator
    progress_val = min(1.0, water_today / 2000.0)
    st.progress(progress_val)
    
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        if st.button("➕ 250ml", key="add_250_d"):
            database.add_water_intake(user_id, 250, today)
            st.rerun()
    with w_col2:
        if st.button("➕ 500ml", key="add_500_d"):
            database.add_water_intake(user_id, 500, today)
            if water_today + 500 >= 2000:
                database.add_badge(user_id, "Hydration Hero", "Drank 2L or more of water in a single day", today)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Food Logger
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🍳 Quick Log Meal")
    with st.form("manual_food_form_d", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            food_name = st.text_input("Food Item Name", placeholder="e.g. Salmon Bowl")
            meal_type = st.selectbox("Meal Category", ["Breakfast", "Lunch", "Dinner", "Snack"])
        with f_col2:
            calories = st.number_input("Calories (kcal)", min_value=0.0, step=10.0)
            protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
        
        f_col3, f_col4 = st.columns(2)
        with f_col3:
            carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
        with f_col4:
            fat = st.number_input("Fat (g)", min_value=0.0, step=1.0)
            
        fiber = st.number_input("Fiber (g) [Optional]", min_value=0.0, step=1.0)
        submit_food = st.form_submit_button("Add to Journal")
        
        if submit_food:
            if not food_name:
                st.error("Food name cannot be empty.")
            else:
                database.add_food_log(user_id, food_name, calories, protein, carbs, fat, fiber, today, meal_type)
                if consumed_cal + calories >= cal_target * 0.9 and consumed_cal + calories <= cal_target * 1.1:
                    database.add_badge(user_id, "Calorie Matcher", "Ate within 10% of daily calorie target", today)
                st.success(f"Logged: {food_name}")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Today's Logs list
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📋 Today's Journal Logs")
    if food_logs_today:
        for idx, fl in enumerate(food_logs_today):
            c1, c2, c3 = st.columns([3, 1.5, 0.8])
            with c1:
                st.markdown(f"**{fl['food_name']}**")
                st.caption(f"{fl['meal_type']} | P: {int(fl['protein'])}g | C: {int(fl['carbs'])}g | F: {int(fl['fat'])}g")
            with c2:
                st.markdown(f"<div style='font-family:\"Plus Jakarta Sans\",sans-serif; font-weight:600; font-size:1.15rem; color:#E5C483;'>{int(fl['calories'])} kcal</div>", unsafe_allow_html=True)
            with c3:
                # Custom trash key
                if st.button("🗑️", key=f"del_d_{fl['id']}_{idx}"):
                    database.delete_food_log(fl['id'], user_id)
                    st.success("Log removed")
                    st.rerun()
    else:
        st.caption("No foods logged yet today.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # 1. Macro Target Donut & Progress comparison
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 Macronutrient Allocation vs. Target")
    
    macro_labels = ['Protein (g)', 'Carbohydrates (g)', 'Fat (g)']
    macro_targets = [macros_target['protein_g'], macros_target['carbs_g'], macros_target['fat_g']]
    macro_consumed = [consumed_prot, consumed_carb, consumed_fat]
    
    fig_macros = go.Figure(data=[
        go.Bar(name='Target Target', x=macro_labels, y=macro_targets, marker_color='rgba(255,255,255,0.03)', marker_line=dict(color='rgba(229,196,131,0.1)', width=1)),
        go.Bar(name='Consumed Actual', x=macro_labels, y=macro_consumed, marker=dict(color='#E5C483', line=dict(color='#A68B5C', width=1)))
    ])
    fig_macros.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        font=dict(color='#FFFFFF', family='Inter'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)', color='#FFFFFF'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', color='#FFFFFF'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#FFFFFF'))
    )
    st.plotly_chart(fig_macros, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Weight History curve
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📈 Weight Progress Trend")
    hist = database.get_progress_history(user_id, limit=30)
    if len(hist) > 1:
        df_hist = pd.DataFrame(hist)
        df_hist['log_date'] = pd.to_datetime(df_hist['log_date'])
        
        fig_weight = px.line(
            df_hist, x='log_date', y='weight',
            labels={'log_date': 'Date', 'weight': 'Weight (kg)'},
            markers=True
        )
        fig_weight.update_traces(
            line=dict(color='#A68B5C', width=2),
            marker=dict(size=6, color='#E5C483', line=dict(color='#0C0F1A', width=1))
        )
        fig_weight.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            font=dict(color='#FFFFFF', family='Inter'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.03)', color='#FFFFFF'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.03)', color='#FFFFFF')
        )
        st.plotly_chart(fig_weight, use_container_width=True)
    else:
        st.caption("Weight progression graph will generate once 2 or more weight logs are recorded.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Badges Grid
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🏆 Earned Achievements")
    badges = database.get_user_badges(user_id)
    if badges:
        badge_cols = st.columns(3)
        for i, b in enumerate(badges[:3]):
            with badge_cols[i % 3]:
                st.markdown(f"""
                <div style="background: rgba(229, 196, 131, 0.03); border: 1px solid rgba(229, 196, 131, 0.1); border-radius: 12px; padding: 12px; text-align: center;">
                    <span style="font-size: 2.2rem; display:block; margin-bottom:8px;">🏅</span>
                    <b style="font-size: 0.85rem; color: #E5C483; font-family: 'Plus Jakarta Sans', sans-serif; font-weight:600;">{b['badge_name']}</b><br>
                    <span style="font-size: 0.7rem; color: #9CA3AF; display:block; margin-top:4px; font-family: 'Plus Jakarta Sans', sans-serif;">{b['badge_desc']}</span>
                </div>
                """, unsafe_allow_html=True)
        if len(badges) > 3:
            with st.expander("View all earned badges"):
                st.write(", ".join([b['badge_name'] for b in badges]))
    else:
        st.caption("Match physical targets or log hydration parameters to unlock startup health badges.")
    st.markdown("</div>", unsafe_allow_html=True)
