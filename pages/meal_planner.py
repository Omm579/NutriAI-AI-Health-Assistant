import streamlit as st
import datetime
import pandas as pd
import database
import auth
import plotly.graph_objects as go
from modules import gemini_service, report_generator
import importlib
try:
    importlib.reload(gemini_service)
except Exception:
    pass

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

user_id = auth.get_current_user_id()
profile = database.get_health_profile(user_id)
user = database.get_user_by_id(user_id)

if not profile:
    st.error("No health profile found. Please configure your profile first in settings.")
    st.stop()

st.title("🥗 AI Personalized Meal Planner")
st.markdown("Generate tailored nutrition plans matching your physical metrics, preferences, and dietary restrictions.")

# Sidebar Filters styled
st.sidebar.subheader("Adjust Nutrition Profile")
age = st.sidebar.slider("Age (years)", 10, 100, int(profile['age']))
height = st.sidebar.number_input("Height (cm)", 50.0, 250.0, float(profile['height']))
weight = st.sidebar.number_input("Weight (kg)", 10.0, 300.0, float(profile['weight']))

# Case-insensitive index resolvers
goal_options = ["Weight Loss", "Muscle Gain", "Maintenance", "General Fitness"]
goal_idx = 2
if profile and profile['goal']:
    db_goal = profile['goal'].strip().lower()
    for idx, opt in enumerate(goal_options):
        if opt.lower() == db_goal:
            goal_idx = idx
            break
goal = st.sidebar.selectbox("Fitness Goal", goal_options, index=goal_idx)

dietary_options = ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto", "High Protein", "Low Carb", "Diabetic Friendly", "Gluten Free"]
dietary_idx = 2
if profile and profile['dietary_preferences']:
    db_diet = profile['dietary_preferences'].strip().lower()
    for idx, opt in enumerate(dietary_options):
        if opt.lower() == db_diet:
            dietary_idx = idx
            break
dietary = st.sidebar.selectbox("Diet Type", dietary_options, index=dietary_idx)

allergies = st.sidebar.text_input("Allergies (comma-separated)", profile['allergies'])

activity_options = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
activity_idx = 2
if profile and profile['activity_level']:
    db_act = profile['activity_level'].strip().lower()
    for idx, opt in enumerate(activity_options):
        if opt.lower() == db_act:
            activity_idx = idx
            break
activity = st.sidebar.selectbox("Activity Level", activity_options, index=activity_idx)

# Save temporary overrides or updates
temp_profile = {
    "age": age,
    "gender": profile['gender'],
    "height": height,
    "weight": weight,
    "goal": goal,
    "activity_level": activity,
    "dietary_preferences": dietary,
    "allergies": allergies,
    "medical_conditions": profile['medical_conditions'],
    "fitness_experience": profile['fitness_experience']
}

plan_type = st.radio("Select Plan Schedule Duration", ["Daily", "Weekly", "Monthly"], horizontal=True)

# Function to extract ingredients for the shopping list
def build_shopping_list(meal_plan_data, duration_type):
    shopping_items = []
    
    # helper parser
    def parse_meal_ingredients(meal_obj, meal_name):
        if not meal_obj or not isinstance(meal_obj, dict):
            return
        ing_list = meal_obj.get('ingredients', [])
        for ing in ing_list:
            cost = round((len(ing) % 5) * 0.75 + 1.25, 2)
            shopping_items.append({
                "Ingredient": ing,
                "Meal Reference": meal_name,
                "Qty Estimate": meal_obj.get('portion', '1 serving'),
                "Estimated Cost ($)": cost
            })
            
    if duration_type.lower() == "daily":
        daily = meal_plan_data.get('daily_plan', {})
        for m_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            parse_meal_ingredients(daily.get(m_name), m_name.capitalize())
            
    elif duration_type.lower() == "weekly":
        weekly = meal_plan_data.get('weekly_plan', {})
        for day, daily in weekly.items():
            for m_name in ['breakfast', 'lunch', 'dinner', 'snack']:
                parse_meal_ingredients(daily.get(m_name), f"{day} - {m_name.capitalize()}")
                
    elif duration_type.lower() == "monthly":
        monthly = meal_plan_data.get('monthly_plan', {})
        for week, daily in monthly.items():
            if isinstance(daily, dict):
                for m_name in ['breakfast', 'lunch', 'dinner', 'snack']:
                    parse_meal_ingredients(daily.get(m_name), f"{week} - {m_name.capitalize()}")
                
    return shopping_items

# Retrieve latest plan
latest_plan = database.get_latest_meal_plan(user_id, plan_type)

generate_btn = st.button("✨ Generate New AI Meal Plan", type="primary")

if generate_btn:
    with st.spinner(f"Compiling your {plan_type} meal plan using medical AI context..."):
        new_plan = gemini_service.generate_meal_plan(temp_profile, plan_type)
        database.save_meal_plan(user_id, plan_type, datetime.date.today().isoformat(), new_plan)
        database.add_badge(user_id, "Nutrition Architect", f"Generated a personalized {plan_type} nutrition plan", datetime.date.today().isoformat())
        st.success(f"New {plan_type} Meal Plan generated and saved!")
        latest_plan = {"plan_data": new_plan}

# Render view with premium tabs
if latest_plan:
    p_data = gemini_service.normalize_plan_data(latest_plan['plan_data'])
    
    tab_view, tab_shopping = st.tabs(["📋 View Meal Plan", "🛒 Smart Shopping List"])
    
    with tab_view:
        if plan_type == "Daily":
            daily = p_data.get('daily_plan', {})
            m_cols = st.columns(4)
            for i, m_key in enumerate(['breakfast', 'lunch', 'dinner', 'snack']):
                meal = daily.get(m_key, {})
                with m_cols[i]:
                    st.markdown(f"""
                    <div class="glass-card" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                <span style="font-size: 2rem; background:rgba(255,255,255,0.03); padding:8px; border-radius:10px;">
                                    {"🌅" if m_key=="breakfast" else "☀️" if m_key=="lunch" else "🌙" if m_key=="dinner" else "🍌"}
                                </span>
                                <span class="premium-badge badge-blue">AI Choice</span>
                            </div>
                            <h3 style="margin:4px 0 8px 0; font-size:1.2rem; font-family:'Cormorant Garamond',serif; font-weight: 500;">{m_key.capitalize()}</h3>
                            <p style="font-size:0.95rem; font-weight:600; margin-bottom:4px; color:#FFFFFF; font-family:'Plus Jakarta Sans',sans-serif;">{meal.get('name', 'N/A')}</p>
                            <p style="color:#E5C483; font-family:'Cormorant Garamond',serif; font-weight:400; font-size:1.25rem; margin-bottom:10px;">{meal.get('calories', 0)} kcal</p>
                            <div style="font-size:0.8rem; color:#94a3b8; line-height:1.4; margin-bottom:15px;">
                                <b>Macros allocation:</b><br>
                                Protein: {meal.get('protein', 0)}g | Carbs: {meal.get('carbs', 0)}g | Fat: {meal.get('fat', 0)}g
                            </div>
                        </div>
                        <div>
                            <b style="font-size:0.85rem; color:#FFFFFF;">Ingredients Checklist:</b>
                            <ul style="font-size:0.8rem; padding-left:16px; margin:4px 0 0 0; color:#cbd5e1; line-height:1.4;">
                                {"".join([f"<li>{item}</li>" for item in meal.get('ingredients', [])])}
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        elif plan_type == "Weekly":
            weekly = p_data.get('weekly_plan', {})
            if weekly:
                days = list(weekly.keys())
                day_tabs = st.tabs(days)
                for idx, day_name in enumerate(days):
                    with day_tabs[idx]:
                        st.subheader(f"{day_name}'s Schedule")
                        daily = weekly.get(day_name, {})
                        m_cols = st.columns(4)
                        for i, m_key in enumerate(['breakfast', 'lunch', 'dinner', 'snack']):
                            meal = daily.get(m_key, {})
                            with m_cols[i]:
                                st.markdown(f"""
                                <div class="glass-card" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
                                    <div>
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                            <span style="font-size: 2rem; background:rgba(255,255,255,0.03); padding:8px; border-radius:10px;">
                                                {"🌅" if m_key=="breakfast" else "☀️" if m_key=="lunch" else "🌙" if m_key=="dinner" else "🍌"}
                                            </span>
                                            <span class="premium-badge badge-blue">AI Choice</span>
                                        </div>
                                        <h3 style="margin:4px 0 8px 0; font-size:1.2rem; font-family:'Cormorant Garamond',serif; font-weight: 500;">{m_key.capitalize()}</h3>
                                        <p style="font-size:0.95rem; font-weight:600; margin-bottom:4px; color:#FFFFFF; font-family:'Plus Jakarta Sans',sans-serif;">{meal.get('name', 'N/A')}</p>
                                        <p style="color:#E5C483; font-family:'Cormorant Garamond',serif; font-weight:400; font-size:1.25rem; margin-bottom:10px;">{meal.get('calories', 0)} kcal</p>
                                        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.4; margin-bottom:15px;">
                                            <b>Macros allocation:</b><br>
                                            Protein: {meal.get('protein', 0)}g | Carbs: {meal.get('carbs', 0)}g | Fat: {meal.get('fat', 0)}g
                                        </div>
                                    </div>
                                    <div>
                                        <b style="font-size:0.85rem; color:#FFFFFF;">Ingredients Checklist:</b>
                                        <ul style="font-size:0.8rem; padding-left:16px; margin:4px 0 0 0; color:#cbd5e1; line-height:1.4;">
                                            {"".join([f"<li>{item}</li>" for item in meal.get('ingredients', [])])}
                                        </ul>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No weekly plan format detected.")
                
        else: # Monthly
            monthly = p_data.get('monthly_plan', {})
            if monthly:
                if isinstance(monthly, dict):
                    weeks = list(monthly.keys())
                    tab_titles = [w.replace('_', ' ').title() for w in weeks]
                    week_tabs = st.tabs(tab_titles)
                    for idx, week_name in enumerate(weeks):
                        with week_tabs[idx]:
                            st.subheader(f"{week_name.replace('_', ' ').title()} Nutrition Plan")
                            daily = monthly.get(week_name, {})
                            
                            is_structured = isinstance(daily, dict) and any(k in daily for k in ['breakfast', 'lunch', 'dinner', 'snack'])
                            
                            if is_structured:
                                m_cols = st.columns(4)
                                for i, m_key in enumerate(['breakfast', 'lunch', 'dinner', 'snack']):
                                    meal = daily.get(m_key, {})
                                    with m_cols[i]:
                                        st.markdown(f"""
                                        <div class="glass-card" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
                                            <div>
                                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                                    <span style="font-size: 2rem; background:rgba(255,255,255,0.03); padding:8px; border-radius:10px;">
                                                        {"🌅" if m_key=="breakfast" else "☀️" if m_key=="lunch" else "🌙" if m_key=="dinner" else "🍌"}
                                                    </span>
                                                    <span class="premium-badge badge-blue">AI Choice</span>
                                                </div>
                                                <h3 style="margin:4px 0 8px 0; font-size:1.25rem; font-family:'Cormorant Garamond',serif; font-weight: 500;">{m_key.capitalize()}</h3>
                                                <p style="font-size:0.9rem; font-weight:600; margin-bottom:4px; color:#FFFFFF; font-family:'Plus Jakarta Sans',sans-serif;">{meal.get('name', 'N/A')}</p>
                                                <p style="color:#E5C483; font-family:'Cormorant Garamond',serif; font-weight:400; font-size:1.2rem; margin-bottom:10px;">{meal.get('calories', 0)} kcal</p>
                                                <div style="font-size:0.8rem; color:#94a3b8; line-height:1.4; margin-bottom:15px; font-family:'Plus Jakarta Sans',sans-serif;">
                                                    <b>Macros allocation:</b><br>
                                                    Protein: {meal.get('protein', 0)}g | Carbs: {meal.get('carbs', 0)}g | Fat: {meal.get('fat', 0)}g
                                                </div>
                                            </div>
                                            <div>
                                                <b style="font-size:0.85rem; color:#FFFFFF; font-family:'Plus Jakarta Sans',sans-serif;">Ingredients Checklist:</b>
                                                <ul style="font-size:0.8rem; padding-left:16px; margin:4px 0 0 0; color:#cbd5e1; line-height:1.4; font-family:'Plus Jakarta Sans',sans-serif;">
                                                    {"".join([f"<li>{item}</li>" for item in meal.get('ingredients', [])])}
                                                </ul>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                if isinstance(daily, dict):
                                    desc = "<br>".join([f"• <b>{k.replace('_', ' ').title()}:</b> {v}" for k, v in daily.items()])
                                elif isinstance(daily, list):
                                    desc = "<br>".join([f"• {item}" for item in daily])
                                else:
                                    desc = str(daily)
                                    
                                st.markdown(f"""
                                <div class="glass-card">
                                    <p style="color:#e2e8f0; font-size:0.95rem; line-height:1.5;">{desc}</p>
                                </div>
                                """, unsafe_allow_html=True)
                elif isinstance(monthly, list):
                    for idx, item in enumerate(monthly):
                        st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="color:#E5C483; font-family:'Cormorant Garamond',serif; font-weight: 500;">Week {idx + 1}</h3>
                            <p style="color:#e2e8f0; font-size:0.95rem; line-height:1.5;">{item}</p>
                        </div>
                        """, unsafe_allow_html=True)
                elif isinstance(monthly, str):
                    st.markdown(f"""
                    <div class="glass-card">
                        <p style="color:#e2e8f0; font-size:0.95rem; line-height:1.5;">{monthly}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No monthly plan format detected.")
                
    with tab_shopping:
        st.subheader("🛒 Smart Shopping List")
        shopping_list = build_shopping_list(p_data, plan_type)
        
        if shopping_list:
            df_shopping = pd.DataFrame(shopping_list)
            
            # Show summary cost metrics in glass card
            total_est_cost = df_shopping["Estimated Cost ($)"].sum()
            
            col_sc1, col_sc2 = st.columns([1.5, 1])
            with col_sc1:
                st.markdown(f"""
                <div class="glass-card" style="padding:15px; margin-bottom:20px;">
                    <div class="premium-metric-lbl">Total Estimated Cost</div>
                    <div class="premium-metric-val" style="color:#E5C483;">${total_est_cost:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.dataframe(df_shopping, use_container_width=True)
            
            csv_data = report_generator.generate_csv_export(shopping_list)
            st.download_button(
                label="📥 Download Shopping List (CSV)",
                data=csv_data,
                file_name=f"NutriAI_ShoppingList_{plan_type}.csv",
                mime="text/csv"
            )
        else:
            st.caption("Generate a daily or weekly plan first to build ingredients inventory.")
else:
    st.info("No meal plan generated yet. Adjust parameters on the sidebar and click 'Generate New AI Meal Plan'.")
