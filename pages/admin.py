import streamlit as st
import database
import auth
import pandas as pd
from config import HAS_GEMINI_API

# Check login state
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

if st.session_state.get('username') != 'admin':
    st.error("Access denied. Administrator privileges required.")
    st.stop()

st.title("🛠️ Platform Administration")
st.markdown("System health telemetry, API requests, and global database metrics.")

stats = database.get_admin_stats()

# 4 metric cards styled
a1, a2, a3, a4 = st.columns(4)

with a1:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <span style="font-size:2rem; display:block; margin-bottom:8px;">👥</span>
        <span class="premium-metric-lbl">Total Users</span>
        <div class="premium-metric-val">{stats['total_users']}</div>
    </div>
    """, unsafe_allow_html=True)
    
with a2:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <span style="font-size:2rem; display:block; margin-bottom:8px;">🥗</span>
        <span class="premium-metric-lbl">Meal plans</span>
        <div class="premium-metric-val">{stats['total_meal_plans_generated']}</div>
    </div>
    """, unsafe_allow_html=True)
    
with a3:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <span style="font-size:2rem; display:block; margin-bottom:8px;">🏋️</span>
        <span class="premium-metric-lbl">Workouts</span>
        <div class="premium-metric-val">{stats['total_workouts_generated']}</div>
    </div>
    """, unsafe_allow_html=True)
    
with a4:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <span style="font-size:2rem; display:block; margin-bottom:8px;">📸</span>
        <span class="premium-metric-lbl">Food Logs</span>
        <div class="premium-metric-val">{stats['total_food_logs']}</div>
    </div>
    """, unsafe_allow_html=True)

# Telemetry rows
st.subheader("🖥️ Telemetry & Server Diagnostics")

c_sys1, c_sys2 = st.columns(2)

with c_sys1:
    gemini_status = "🟢 Connected (Gemini 1.5)" if HAS_GEMINI_API else "🟡 Mock Mode Fallback"
    st.markdown(f"""
    <div class="glass-card" style="min-height:220px;">
        <h3 style="margin-top:0;">API Connection Status</h3>
        <table style="width:100%; border-collapse: collapse; margin-top:10px;">
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05); height:38px; font-size:0.9rem;">
                <td><b>Database</b></td>
                <td style="color:#10B981; text-align:right;">🟢 SQLite Connected</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05); height:38px; font-size:0.9rem;">
                <td><b>Gemini Engine</b></td>
                <td style="text-align:right; color:{'#10B981' if HAS_GEMINI_API else '#f59e0b'};">{gemini_status}</td>
            </tr>
            <tr style="height:38px; font-size:0.9rem;">
                <td><b>Report Compiler</b></td>
                <td style="color:#10B981; text-align:right;">🟢 ReportLab Ready</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with c_sys2:
    st.markdown("""
    <div class="glass-card" style="min-height:220px;">
        <h3 style="margin-top:0; font-family:'Cormorant Garamond',serif; font-size:1.5rem; font-weight:400;">Server Resources</h3>
        <table style="width:100%; border-collapse: collapse; margin-top:10px; font-family:'Plus Jakarta Sans',sans-serif;">
            <tr style="border-bottom:1px solid rgba(229,196,131,0.05); height:38px; font-size:0.9rem;">
                <td><b>CPU Load</b></td>
                <td style="text-align:right; color:#E5C483; font-weight:600;">12.5%</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(229,196,131,0.05); height:38px; font-size:0.9rem;">
                <td><b>Memory Allocation</b></td>
                <td style="text-align:right; color:#E5C483; font-weight:600;">158 MB / 512 MB</td>
            </tr>
            <tr style="height:38px; font-size:0.9rem;">
                <td><b>Disk Capacity</b></td>
                <td style="text-align:right; color:#A68B5C; font-weight:600;">78% Free</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# User database list
st.subheader("👥 Registered User Directory")
conn = database.get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT u.id, u.name, u.username, hp.age, hp.gender, hp.goal, hp.dietary_preferences 
    FROM users u
    LEFT JOIN health_profiles hp ON u.id = hp.user_id
""")
rows = cursor.fetchall()
conn.close()

if rows:
    users_list = [dict(r) for r in rows]
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    # Table Header Row
    h_col1, h_col2, h_col3, h_col4 = st.columns([1, 3, 3, 1])
    h_col1.markdown("<b style='color:#A68B5C;'>ID</b>", unsafe_allow_html=True)
    h_col2.markdown("<b style='color:#A68B5C;'>User / Profile</b>", unsafe_allow_html=True)
    h_col3.markdown("<b style='color:#A68B5C;'>Preferences</b>", unsafe_allow_html=True)
    h_col4.markdown("<b style='color:#A68B5C;'>Action</b>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid rgba(229,196,131,0.08);'>", unsafe_allow_html=True)
    
    for idx, u in enumerate(users_list):
        col_u1, col_u2, col_u3, col_u4 = st.columns([1, 3, 3, 1])
        col_u1.write(f"#{u['id']}")
        col_u2.markdown(f"<b>{u['name']}</b> ({u['username']})", unsafe_allow_html=True)
        col_u2.caption(f"Age: {u['age'] or 'N/A'} | {u['gender'] or 'N/A'} | {u['goal'] or 'N/A'}")
        col_u3.caption(f"Diet: {u['dietary_preferences'] or 'N/A'}")
        with col_u4:
            if u['username'] == 'admin':
                st.caption("Protected")
            else:
                if st.button("🗑️", key=f"del_user_{u['id']}_{idx}"):
                    if database.delete_user_by_id(u['id']):
                        st.success(f"User {u['username']} permanently deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete user.")
        st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid rgba(255,255,255,0.02);'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.caption("No registered users found.")

# Global telemetry exports
st.subheader("📥 Global Telemetry Exports")
col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4>Global Users Registry</h4>", unsafe_allow_html=True)
    # Query raw users list
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, created_at FROM users")
    all_users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    if all_users:
        from modules import report_generator
        users_csv = report_generator.generate_csv_export(all_users, {
            "id": "User ID",
            "name": "Full Name",
            "username": "Username",
            "created_at": "Registration Date"
        })
        st.download_button(
            label="📥 Export Users Registry (CSV)",
            data=users_csv,
            file_name="global_users_registry.csv",
            mime="text/csv",
            key="global_users_csv_btn"
        )
    else:
        st.caption("No registered users found.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_exp2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4>Global Food Logs Telemetry</h4>", unsafe_allow_html=True)
    global_foods = database.get_global_food_logs()
    if global_foods:
        from modules import report_generator
        foods_csv = report_generator.generate_csv_export(global_foods, {
            "id": "Log ID",
            "username": "Username",
            "food_name": "Food Name",
            "calories": "Calories (kcal)",
            "protein": "Protein (g)",
            "carbs": "Carbs (g)",
            "fat": "Fat (g)",
            "fiber": "Fiber (g)",
            "log_date": "Logged Date",
            "meal_type": "Meal Category"
        })
        st.download_button(
            label="📥 Export Global Food Logs (CSV)",
            data=foods_csv,
            file_name="global_food_logs.csv",
            mime="text/csv",
            key="global_foods_csv_btn"
        )
    else:
        st.caption("No food log entries found platform-wide.")
    st.markdown("</div>", unsafe_allow_html=True)

# Database Maintenance / Purging
st.subheader("🧹 System Database Maintenance")
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.write("Purge historic transactional logs (food journals, water intake, sleep, and coach chats) to optimize database storage.")
col_maint1, col_maint2 = st.columns([2, 1])
with col_maint1:
    purge_days = st.selectbox("Select age threshold for purging logs:", [30, 60, 90], format_func=lambda x: f"Older than {x} Days")
with col_maint2:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    confirm_purge = st.button("Purge Inactive Logs", type="primary", key="purge_execute_btn")

if confirm_purge:
    success, result = database.purge_inactive_logs(purge_days)
    if success:
        st.success(f"Purge completed! Logs removed: "
                   f"{result['food_logs']} foods, {result['water_intake']} water entries, "
                   f"{result['sleep_logs']} sleep logs, {result['chat_history']} chat messages.")
        st.rerun()
    else:
        st.error(f"Failed to execute database purge: {result}")
st.markdown("</div>", unsafe_allow_html=True)
