import streamlit as st
import datetime
import database
import auth
from modules import report_generator

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

user_id = auth.get_current_user_id()
user = database.get_user_by_id(user_id)
profile = database.get_health_profile(user_id)

if not profile:
    st.error("No health profile found. Configure profile details in settings first.")
    st.stop()

st.title("📊 Health Reports & Data Exports")
st.markdown("Compile comprehensive health reports and export your personal nutrition, hydration, and metric logs.")

# Date Range Picker Card
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("Select Report Window")
col_date1, col_date2 = st.columns(2)
with col_date1:
    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
with col_date2:
    end_date = st.date_input("End Date", datetime.date.today())
st.markdown("</div>", unsafe_allow_html=True)

# Query logs
food_logs = database.get_food_logs_by_date_range(user_id, start_date.isoformat(), end_date.isoformat())
water_logs = database.get_water_intake_by_date_range(user_id, start_date.isoformat(), end_date.isoformat())
progress_logs = database.get_progress_history(user_id, limit=50)
progress_logs_filtered = [p for p in progress_logs if start_date.isoformat() <= p['log_date'] <= end_date.isoformat()]

avg_cal = sum(f['calories'] for f in food_logs) / len(food_logs) if food_logs else 0.0
avg_water = sum(w['total_ml'] for w in water_logs) / len(water_logs) if water_logs else 0.0

col_metrics1, col_metrics2 = st.columns(2)

with col_metrics1:
    st.markdown(f"""
    <div class="glass-card" style="min-height:200px;">
        <h3 style="font-family:'Cormorant Garamond',serif; font-size:1.5rem; font-weight:400; color:#FFFFFF;">Report Summary Metrics</h3>
        <p style="color:#9CA3AF; font-size:0.9rem; font-family:'Plus Jakarta Sans',sans-serif;">
            Log entries found: <b style="color:#FFFFFF;">{len(food_logs)} foods, {len(water_logs)} water inputs</b><br>
            Average daily calories: <b style="color:#E5C483;">{int(avg_cal)} kcal</b><br>
            Average daily hydration: <b style="color:#A68B5C;">{int(avg_water)} ml</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
with col_metrics2:
    st.markdown("""
    <div class="glass-card" style="min-height:200px;">
        <h3>Export Guidelines</h3>
        <p style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">
            Generate documents in PDF or CSV formats. These exports can be directly shared with your fitness instructors or primary caregivers.
        </p>
    </div>
    """, unsafe_allow_html=True)

# PDF Generation Section
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("📄 Compile PDF Health Dossier")
st.write("Generate a styled PDF document including profile dimensions, macros breakdown, and hydration levels.")

if st.button("📄 Generate PDF Health Report", type="primary", key="pdf_comp_btn"):
    with st.spinner("Compiling ReportLab PDF templates..."):
        pdf_path = report_generator.generate_pdf_report(user, profile, food_logs, water_logs, progress_logs_filtered)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="📥 Download Compiled PDF Report File",
            data=pdf_bytes,
            file_name=f"NutriAI_FullReport_{user['username']}.pdf",
            mime="application/pdf",
            key="pdf_download_btn_link"
        )
        database.add_badge(user_id, "Archivist", "Compiled a comprehensive health report PDF", datetime.date.today().isoformat())
        st.success("Report compiled successfully! Click the download button above.")
st.markdown("</div>", unsafe_allow_html=True)

# Raw data exports
st.subheader("📊 Raw CSV Database Exports")
csv_col1, csv_col2 = st.columns(2)

with csv_col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4>Food Journal Records</h4>", unsafe_allow_html=True)
    if food_logs:
        food_csv = report_generator.generate_csv_export(food_logs, {
            "food_name": "Food Item",
            "calories": "Calories (kcal)",
            "protein": "Protein (g)",
            "carbs": "Carbs (g)",
            "fat": "Fat (g)",
            "fiber": "Fiber (g)",
            "log_date": "Logged Date",
            "meal_type": "Meal Category"
        })
        st.download_button(
            label="📥 Download Food Logs (CSV)",
            data=food_csv,
            file_name=f"NutriAI_FoodLogs_{user['username']}.csv",
            mime="text/csv",
            key="csv_food_btn"
        )
    else:
        st.caption("No food records logged in selected window.")
    st.markdown("</div>", unsafe_allow_html=True)

with csv_col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4>Progress Tracker Logs</h4>", unsafe_allow_html=True)
    if progress_logs_filtered:
        prog_csv = report_generator.generate_csv_export(progress_logs_filtered, {
            "weight": "Weight (kg)",
            "bmi": "BMI",
            "health_score": "Health Score",
            "log_date": "Logged Date"
        })
        st.download_button(
            label="📥 Download Progress Logs (CSV)",
            data=prog_csv,
            file_name=f"NutriAI_ProgressLogs_{user['username']}.csv",
            mime="text/csv",
            key="csv_prog_btn"
        )
    else:
        st.caption("No weight progress records logged in selected window.")
    st.markdown("</div>", unsafe_allow_html=True)
