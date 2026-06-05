import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from config import DB_PATH

def get_connection():
    """
    Establish a thread-safe connection to the SQLite database.
    """
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize all database tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Health Profiles Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_profiles (
        user_id INTEGER PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        height REAL, -- in cm
        weight REAL, -- in kg
        goal TEXT, -- Weight Loss, Muscle Gain, General Fitness, Maintenance
        activity_level TEXT, -- Sedentary, Lightly Active, Moderately Active, Very Active
        allergies TEXT, -- Comma-separated or empty
        dietary_preferences TEXT, -- Vegetarian, Vegan, Keto, Gluten Free, Low Carb, Diabetic Friendly, High Protein, Non-Vegetarian
        medical_conditions TEXT, -- Comma-separated or empty
        fitness_experience TEXT, -- Beginner, Intermediate, Advanced
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 3. Meal Plans Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_type TEXT NOT NULL, -- Daily, Weekly, Monthly
        start_date DATE NOT NULL,
        plan_data TEXT NOT NULL, -- JSON text
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 4. Food Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        calories REAL NOT NULL,
        protein REAL NOT NULL,
        carbs REAL NOT NULL,
        fat REAL NOT NULL,
        fiber REAL DEFAULT 0,
        log_date DATE NOT NULL,
        meal_type TEXT NOT NULL, -- Breakfast, Lunch, Dinner, Snack
        image_path TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 5. Workout Plans Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workout_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_type TEXT NOT NULL, -- Gym, Home, Yoga, Cardio, HIIT
        plan_data TEXT NOT NULL, -- JSON text
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 6. Water Intake Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS water_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        intake_ml REAL NOT NULL,
        log_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 7. Chat History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL, -- user, assistant
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 8. Progress Data Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        weight REAL NOT NULL,
        bmi REAL NOT NULL,
        health_score REAL NOT NULL,
        log_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 9. Sleep Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sleep_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hours REAL NOT NULL,
        quality_score INTEGER NOT NULL, -- 1 to 100
        log_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # 10. Badges Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        badge_name TEXT NOT NULL,
        badge_desc TEXT NOT NULL,
        date_earned DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

# ----------------- CRUD HELPERS -----------------

def create_user(username, password_hash, name):
    """Create a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)",
            (username.lower().strip(), password_hash, name.strip())
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieve user details by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    """Retrieve user details by user ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Health Profile Helpers
def get_health_profile(user_id):
    """Retrieve user health profile details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_health_profile(user_id, age, gender, height, weight, goal, activity_level, allergies, dietary_preferences, medical_conditions, fitness_experience):
    """Save or update user health profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM health_profiles WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if exists:
        cursor.execute('''
        UPDATE health_profiles 
        SET age=?, gender=?, height=?, weight=?, goal=?, activity_level=?, allergies=?, dietary_preferences=?, medical_conditions=?, fitness_experience=?, updated_at=?
        WHERE user_id=?
        ''', (age, gender, height, weight, goal, activity_level, allergies, dietary_preferences, medical_conditions, fitness_experience, now, user_id))
    else:
        cursor.execute('''
        INSERT INTO health_profiles (user_id, age, gender, height, weight, goal, activity_level, allergies, dietary_preferences, medical_conditions, fitness_experience, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, age, gender, height, weight, goal, activity_level, allergies, dietary_preferences, medical_conditions, fitness_experience, now))
    
    conn.commit()
    conn.close()

# Meal Plan Helpers
def save_meal_plan(user_id, plan_type, start_date, plan_data_dict):
    """Save generated AI meal plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO meal_plans (user_id, plan_type, start_date, plan_data)
    VALUES (?, ?, ?, ?)
    ''', (user_id, plan_type, start_date, json.dumps(plan_data_dict)))
    conn.commit()
    conn.close()

def get_latest_meal_plan(user_id, plan_type):
    """Fetch the latest meal plan of a specific type (Daily/Weekly/Monthly) for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM meal_plans 
    WHERE user_id = ? AND plan_type = ? 
    ORDER BY created_at DESC LIMIT 1
    ''', (user_id, plan_type))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res['plan_data'] = json.loads(res['plan_data'])
        return res
    return None

# Food Log Helpers
def add_food_log(user_id, food_name, calories, protein, carbs, fat, fiber, log_date, meal_type, image_path=None):
    """Add item to food log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO food_logs (user_id, food_name, calories, protein, carbs, fat, fiber, log_date, meal_type, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, food_name, calories, protein, carbs, fat, fiber, log_date, meal_type, image_path))
    conn.commit()
    conn.close()

def get_food_logs_by_date(user_id, log_date):
    """Retrieve food logs for a specific user and date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM food_logs WHERE user_id = ? AND log_date = ?
    ''', (user_id, log_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_food_logs_by_date_range(user_id, start_date, end_date):
    """Retrieve food logs for a date range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM food_logs 
    WHERE user_id = ? AND log_date BETWEEN ? AND ?
    ORDER BY log_date ASC
    ''', (user_id, start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_food_log(log_id, user_id):
    """Delete a food log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_logs WHERE id = ? AND user_id = ?", (log_id, user_id))
    conn.commit()
    conn.close()

# Workout Plans
def save_workout_plan(user_id, plan_type, plan_data_dict):
    """Save generated AI workout plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO workout_plans (user_id, plan_type, plan_data)
    VALUES (?, ?, ?)
    ''', (user_id, plan_type, json.dumps(plan_data_dict)))
    conn.commit()
    conn.close()

def get_latest_workout_plan(user_id):
    """Fetch the user's latest generated workout plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM workout_plans 
    WHERE user_id = ? 
    ORDER BY created_at DESC LIMIT 1
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res['plan_data'] = json.loads(res['plan_data'])
        return res
    return None

# Water Intake Helpers
def add_water_intake(user_id, intake_ml, log_date):
    """Log water intake. Merges entries if date exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, intake_ml FROM water_intake WHERE user_id = ? AND log_date = ?", (user_id, log_date))
    row = cursor.fetchone()
    if row:
        new_intake = row['intake_ml'] + intake_ml
        cursor.execute("UPDATE water_intake SET intake_ml = ? WHERE id = ?", (new_intake, row['id']))
    else:
        cursor.execute("INSERT INTO water_intake (user_id, intake_ml, log_date) VALUES (?, ?, ?)", (user_id, intake_ml, log_date))
    conn.commit()
    conn.close()

def get_water_intake_by_date(user_id, log_date):
    """Get water intake volume for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(intake_ml) as total FROM water_intake WHERE user_id = ? AND log_date = ?", (user_id, log_date))
    val = cursor.fetchone()['total']
    conn.close()
    return val if val else 0.0

def get_water_intake_by_date_range(user_id, start_date, end_date):
    """Get water intake logs over a range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT log_date, SUM(intake_ml) as total_ml FROM water_intake 
    WHERE user_id = ? AND log_date BETWEEN ? AND ?
    GROUP BY log_date ORDER BY log_date ASC
    ''', (user_id, start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Chat History
def add_chat_message(user_id, role, content):
    """Record chat history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=50):
    """Retrieve chat history logs for memory context."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?", (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_chat_history(user_id):
    """Clear chat logs for user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Progress and Metrics Tracking
def add_progress_log(user_id, weight, bmi, health_score, log_date):
    """Log current physical metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM progress_data WHERE user_id = ? AND log_date = ?", (user_id, log_date))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE progress_data SET weight = ?, bmi = ?, health_score = ? WHERE id = ?", (weight, bmi, health_score, row['id']))
    else:
        cursor.execute("INSERT INTO progress_data (user_id, weight, bmi, health_score, log_date) VALUES (?, ?, ?, ?, ?)", (user_id, weight, bmi, health_score, log_date))
    conn.commit()
    conn.close()

def get_progress_history(user_id, limit=30):
    """Fetch weight and fitness score histories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_data WHERE user_id = ? ORDER BY log_date ASC LIMIT ?", (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_progress(user_id):
    """Fetch latest progress entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_data WHERE user_id = ? ORDER BY log_date DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Sleep Logs Helpers
def add_sleep_log(user_id, hours, quality_score, log_date):
    """Log sleep metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sleep_logs WHERE user_id = ? AND log_date = ?", (user_id, log_date))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE sleep_logs SET hours = ?, quality_score = ? WHERE id = ?", (hours, quality_score, row['id']))
    else:
        cursor.execute("INSERT INTO sleep_logs (user_id, hours, quality_score, log_date) VALUES (?, ?, ?, ?)", (user_id, hours, quality_score, log_date))
    conn.commit()
    conn.close()

def get_sleep_logs_by_date_range(user_id, start_date, end_date):
    """Retrieve sleep logs for a range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM sleep_logs 
    WHERE user_id = ? AND log_date BETWEEN ? AND ?
    ORDER BY log_date ASC
    ''', (user_id, start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Badges Helpers
def add_badge(user_id, badge_name, badge_desc, date_earned):
    """Give user a badge (ignoring duplicate awards)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM badges WHERE user_id = ? AND badge_name = ?", (user_id, badge_name))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO badges (user_id, badge_name, badge_desc, date_earned) VALUES (?, ?, ?, ?)", (user_id, badge_name, badge_desc, date_earned))
        conn.commit()
    conn.close()

def get_user_badges(user_id):
    """Retrieve all badges earned by user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM badges WHERE user_id = ? ORDER BY date_earned DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Admin Dashboard Operations
def get_admin_stats():
    """Retrieve total platform user and generation analytics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM health_profiles")
    profile_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM meal_plans")
    total_meal_plans = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM food_logs")
    total_food_logs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM workout_plans")
    total_workout_plans = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_users": total_users,
        "profile_users": profile_users,
        "total_meal_plans_generated": total_meal_plans,
        "total_food_logs": total_food_logs,
        "total_workouts_generated": total_workout_plans
    }

def delete_user_by_id(user_id):
    """Permanently delete a user account and cascade delete all their data."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_global_food_logs():
    """Retrieve all food logs from all users for global admin telemetry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fl.id, fl.food_name, fl.calories, fl.protein, fl.carbs, fl.fat, fl.fiber, fl.log_date, fl.meal_type, u.username 
        FROM food_logs fl
        JOIN users u ON fl.user_id = u.id
        ORDER BY fl.log_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def purge_inactive_logs(days_threshold):
    """Purge food logs, water intake, sleep logs, and chat messages older than specified days."""
    import datetime
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=days_threshold)).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    purged_counts = {}
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Purge food logs
        cursor.execute("DELETE FROM food_logs WHERE log_date < ?", (cutoff_date,))
        purged_counts['food_logs'] = cursor.rowcount
        
        # Purge water logs
        cursor.execute("DELETE FROM water_intake WHERE log_date < ?", (cutoff_date,))
        purged_counts['water_intake'] = cursor.rowcount
        
        # Purge sleep logs
        cursor.execute("DELETE FROM sleep_logs WHERE log_date < ?", (cutoff_date,))
        purged_counts['sleep_logs'] = cursor.rowcount
        
        # Purge chat history
        cursor.execute("DELETE FROM chat_history WHERE date(timestamp) < ?", (cutoff_date,))
        purged_counts['chat_history'] = cursor.rowcount
        
        conn.commit()
        return True, purged_counts
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
