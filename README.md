# NutriAI - Intelligent Health & Nutrition Management Platform

NutriAI is a comprehensive, production-ready AI-powered health management application designed to help users track calories, generate personalized AI meal and fitness plans, analyze food photos with computer vision, track sleep cycles, and consult an AI nutrition coach. 

It is built on top of **Streamlit** (Python) and leverages the **Google Gemini 1.5 Flash API** for intelligent food recognition, meal planning, and health assistant chat capabilities. It operates out of the box with a built-in Mock Mode fallback if a Gemini API key is not supplied.

---

## 🌟 Core Features

1. **User Authentication & Profiles**: Register and login securely with standard pbkdf2_sha256 password hashing. Create detailed health profiles containing age, height, weight, activity multipliers, goal indices, diet preferences, allergies, and experience level.
2. **Interactive Health Dashboard**: Track daily calories consumed, remaining targets, water logs, and BMI. Visualizes macronutrient ratios (Protein, Carbs, Fat) and weight histories with Plotly.
3. **AI Meal Planner**: Generate personalized breakfast, lunch, dinner, and snack options with full ingredient breakdowns, macros, portions, and cost targets. Support for Daily, Weekly, and Monthly durations across 8 distinct diet types (Vegan, Keto, Gluten-Free, etc.).
4. **Smart Shopping List Generator**: Automatically extracts ingredient inventories from meal plans, compiles total costs, and offers PDF or CSV exports.
5. **AI Food Image Analyzer**: Upload image snapshots of meals (PNG/JPG) to analyze ingredients, caloric values, macronutrients, health scores, and suggestions.
6. **Fitness Recommendation Engine**: Generates workouts by category (Gym, Home, Yoga, Cardio, HIIT) with target sets, reps, duration, and rests.
7. **AI Nutrition Coach Chatbot**: Maintain conversational context in a premium chat window powered by Gemini to ask fitness advice, alternatives, and recipes.
8. **Sleep Analyzer**: Log sleep duration and quality to calculate rest scores and view nutrition coach recommendations.
9. **Progress Reports & Data Exports**: Export logs to raw CSV or download consolidated, beautifully designed PDF documents compiled via ReportLab.
10. **Wearables & Notifications**: Sync diagnostics with mockup toggles for Fitbit/Apple Health, and adjust reminders for water, meals, and workouts.
11. **Platform Admin Panel**: Inspect total users registered, API requests, system resource loads, and view a global user database table.

---

## 📂 Project Structure

```plaintext
NutriAI/
├── app.py                      # Application Entry Point & Navigation Routing
├── database.py                 # SQLite Schema Setup & thread-safe CRUD Functions
├── auth.py                     # User Sessions, Registration & Hashing Functions
├── config.py                   # Folder creation, Environment variables, Gemini Config
├── requirements.txt            # Project Dependencies
├── Dockerfile                  # Container Deployment Configuration
├── .env                        # Local Environment Secrets Configuration
│
├── pages/                      # Multi-Page Streamlit App Files
│   ├── login.py                # Login Interface
│   ├── register.py             # User Signup Interface
│   ├── dashboard.py            # User Health Dashboard & Plots
│   ├── meal_planner.py         # AI Meal Planner & Shopping List compilation
│   ├── food_analyzer.py        # Food Image Recognition and Logging
│   ├── fitness.py              # Workout Planner Routine Builder
│   ├── chatbot.py              # AI Health Assistant Chat Interface
│   ├── reports.py              # PDF Compilation & CSV Downloads
│   ├── settings.py             # Profile, Sleep Logs, Wearables, notifications
│   └── admin.py                # Admin Statistics & Resource Telemetry
│
├── modules/                    # Core Calculations and Third-party APIs
│   ├── gemini_service.py       # Live Gemini API bindings & 100% Mock Fallbacks
│   ├── bmi_calculator.py       # BMI, BMR, TDEE, Health Score Equations
│   └── report_generator.py     # PDF & CSV Exporters (ReportLab & Pandas)
│
├── database/
│   └── health.db               # SQLite database file (created automatically)
├── assets/                     # Media & asset caches
└── exports/                    # Compiled PDF downloads cache
```

---

## 🚀 Local Installation & Setup

Ensure Python 3.10+ is installed on your local computer.

1. **Clone or Navigate to the Workspace**:
   ```bash
   cd C:\Users\USER\.gemini\antigravity\scratch\NutriAI
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv venv
   # On Windows (Powershell)
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets**:
   Open the `.env` file and enter your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   DB_PATH=database/health.db
   ```
   *Note: If `GEMINI_API_KEY` is left blank, the application automatically activates **Mock Mode** for all AI modules. It will populate realistic meal plans, food photo analyses, recipes, and workout routines so you can test the platform with full stability before plugging in a key.*

5. **Run the Streamlit Application**:
   ```bash
   streamlit run app.py
   ```

6. **Open in Browser**:
   Open your browser to: `http://localhost:8501`

---

## 🐳 Running with Docker

Build and run the platform in an isolated container environment using Docker.

1. **Build the Container Image**:
   ```bash
   docker build -t nutriai-app .
   ```

2. **Run the Container**:
   Map port 8501 of your host machine to port 8501 of the container.
   ```bash
   docker run -d -p 8501:8501 --env-file .env --name nutriai-container nutriai-app
   ```

3. **Access the Container App**:
   Navigate to: `http://localhost:8501`

---

## 🔒 Security Practices

- **Password Hashing**: Passwords are securely hashed with a unique random salt using Python's PBKDF2-HMAC-SHA256 algorithm (100,000 iterations). Raw passwords are never stored.
- **Environment Variables**: Credentials, database paths, and API keys are stored in a `.env` file, which should be added to `.gitignore` to prevent exposure.
- **API Protection**: User inputs to AI models are validated and formatted cleanly to prevent query disruption. SQLite handles connections with parametrized bindings to block SQL injection.
