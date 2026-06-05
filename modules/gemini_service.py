import os
import json
import logging
from PIL import Image
import google.generativeai as genai
from config import HAS_GEMINI_API

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_api_available():
    """
    Check if the Gemini API key is configured.
    """
    return HAS_GEMINI_API

def get_gemini_model(model_name="gemini-2.5-flash"):
    """
    Instantiate generative model.
    """
    if is_api_available():
        return genai.GenerativeModel(model_name)
    return None

# ----------------- MOCK SERVICES -----------------
# These serve as robust fallbacks if no API key is provided, ensuring zero app crashes.

def get_mock_meal_plan(profile, plan_type="Daily"):
    """
    Generate realistic mock meal plan.
    """
    is_veg = "veg" in profile.get("dietary_preferences", "").lower()
    allergies = profile.get("allergies", "")
    goal = profile.get("goal", "Maintenance")
    
    breakfast = {
        "name": "Oatmeal with Berries & Almonds" if is_veg else "Scrambled Eggs with Avocado & Toast",
        "calories": 380, "protein": 14 if is_veg else 22, "carbs": 55 if is_veg else 30, "fat": 12 if is_veg else 16,
        "portion": "1 bowl" if is_veg else "2 eggs, 1 slice toast",
        "ingredients": ["Oats (50g)", "Blueberries (50g)", "Almonds (10g)"] if is_veg else ["Eggs (2)", "Avocado (1/2)", "Whole-wheat bread (1 slice)"]
    }
    
    lunch = {
        "name": "Quinoa Salad with Chickpeas" if is_veg else "Grilled Chicken Breast with Brown Rice & Broccoli",
        "calories": 550, "protein": 18 if is_veg else 42, "carbs": 75 if is_veg else 50, "fat": 15 if is_veg else 10,
        "portion": "1 large plate",
        "ingredients": ["Quinoa (80g)", "Chickpeas (100g)", "Cucumber & Tomato"] if is_veg else ["Chicken (150g)", "Brown Rice (100g)", "Broccoli (100g)"]
    }
    
    dinner = {
        "name": "Lentil Soup with Roasted Asparagus" if is_veg else "Baked Salmon with Sweet Potato & Spinach",
        "calories": 480, "protein": 20 if is_veg else 38, "carbs": 60 if is_veg else 40, "fat": 10 if is_veg else 18,
        "portion": "1 bowl soup" if is_veg else "1 fillet salmon, 1 medium sweet potato",
        "ingredients": ["Lentils (100g)", "Asparagus (150g)"] if is_veg else ["Salmon (150g)", "Sweet Potato (150g)", "Spinach (100g)"]
    }
    
    snack = {
        "name": "Greek Yogurt with Honey & Walnuts" if is_veg else "Protein Shake with a Banana",
        "calories": 210, "protein": 15 if is_veg else 25, "carbs": 24 if is_veg else 28, "fat": 6 if is_veg else 2,
        "portion": "150g yogurt" if is_veg else "1 shake",
        "ingredients": ["Greek yogurt (150g)", "Honey (1 tsp)"] if is_veg else ["Whey protein (1 scoop)", "Banana (1)"]
    }

    if plan_type.lower() == "daily":
        return {
            "daily_plan": {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "snack": snack
            }
        }
    elif plan_type.lower() == "weekly":
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_plan = {}
        for d in days:
            # Shift calories slightly to make it look dynamic
            weekly_plan[d] = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "snack": snack
            }
        return {"weekly_plan": weekly_plan}
    else: # Monthly
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        monthly_plan = {}
        for w in weeks:
            monthly_plan[w] = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "snack": snack
            }
        return {"monthly_plan": monthly_plan}

def get_mock_food_analysis():
    """
    Mock response for image analysis.
    """
    return {
        "food_name": "Healthy Chicken Salad",
        "calories": 420.0,
        "protein": 35.0,
        "carbs": 18.0,
        "fat": 15.0,
        "fiber": 4.5,
        "health_rating": 9.0,
        "suggestions": [
            "Opt for a light lemon-olive oil vinaigrette instead of heavy dressings.",
            "Add a handful of sunflower seeds for a boost of Vitamin E."
        ],
        "breakdown": [
            "Grilled Chicken Breast (150g) - ~250 kcal",
            "Mixed Salad Greens (2 cups) - ~20 kcal",
            "Avocado Slices (1/4) - ~80 kcal",
            "Olive Oil Dressing (1 tbsp) - ~70 kcal"
        ]
    }

def get_mock_workout_plan(profile):
    """
    Mock fitness routine generation.
    """
    exp = profile.get("fitness_experience", "Beginner")
    goal = profile.get("goal", "General Fitness")
    
    return {
        "routine_name": f"{exp} {goal} Routine",
        "exercises": [
            {"name": "Bodyweight Squats", "sets": 3, "reps": "12-15", "duration": "5 mins", "rest": "60s", "category": "Home Workouts"},
            {"name": "Pushups (or Incline Pushups)", "sets": 3, "reps": "10-12", "duration": "4 mins", "rest": "60s", "category": "Home Workouts"},
            {"name": "Plank Hold", "sets": 3, "reps": "30-45s", "duration": "3 mins", "rest": "45s", "category": "Home Workouts"},
            {"name": "Jumping Jacks", "sets": 3, "reps": "30s work", "duration": "5 mins", "rest": "30s", "category": "HIIT"},
            {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "10", "duration": "5 mins", "rest": "90s", "category": "Gym Workouts"}
        ]
    }

def get_mock_recipe(ingredients):
    """
    Mock recipe generation.
    """
    return {
        "recipe_name": "Stir-Fried Nutrient Bowl",
        "ingredients": [ingredients, "1 tsp Olive Oil", "Garlic (1 clove)", "Soy Sauce (1 tbsp)"],
        "instructions": [
            "Chop the ingredients into bite-sized pieces.",
            "Heat olive oil in a pan over medium heat and sauté minced garlic.",
            "Add the ingredients to the pan and stir-fry for 5-7 minutes.",
            "Drizzle soy sauce and serve warm."
        ],
        "cooking_time": "15 mins",
        "calories": 290.0,
        "protein": 10.0,
        "carbs": 35.0,
        "fat": 8.0
    }

def get_mock_health_insights(profile):
    """
    Mock health insights.
    """
    return {
        "insights": [
            "Your weight records reflect a stable, healthy progress curve.",
            "Current fiber levels are sufficient to maintain healthy digestion."
        ],
        "alerts": [
            "Ensure your daily water intake doesn't fall below 2 liters.",
            "Vary physical exercise parameters to avoid performance plateaus."
        ],
        "suggestions": [
            "Try consuming 20-30g of protein within 1 hour post-workout.",
            "Aim to reduce screen exposure 30 minutes before sleep for better rest quality."
        ]
    }

# ----------------- GEMINI LIVE SERVICES -----------------

def generate_meal_plan(profile, plan_type="Daily"):
    """
    Generate personalized meal plans. Uses Gemini if key exists, else falls back to Mock.
    """
    if not is_api_available():
        logger.info("Gemini API key not found. Using Mock meal generator.")
        return get_mock_meal_plan(profile, plan_type)
        
    model = get_gemini_model()
    
    prompt = f"""
    You are an expert nutritionist. Create a personalized {plan_type} meal plan in JSON format.
    User Profile Details:
    - Age: {profile.get('age')}
    - Gender: {profile.get('gender')}
    - Height: {profile.get('height')} cm
    - Weight: {profile.get('weight')} kg
    - Fitness Goal: {profile.get('goal')}
    - Activity Level: {profile.get('activity_level')}
    - Dietary Preferences/Restrictions: {profile.get('dietary_preferences')}
    - Known Allergies: {profile.get('allergies') or 'None'}
    - Medical Conditions: {profile.get('medical_conditions') or 'None'}
    - Experience Level: {profile.get('fitness_experience')}
    
    If the plan_type is 'Daily', respond with a JSON object that has a single 'daily_plan' key containing 'breakfast', 'lunch', 'dinner', and 'snack'.
    Each meal must contain keys: 'name', 'calories' (integer kcal), 'protein' (integer grams), 'carbs' (integer grams), 'fat' (integer grams), 'portion' (text), and 'ingredients' (list of strings).
    
    If the plan_type is 'Weekly', respond with a JSON object containing a 'weekly_plan' key mapping days of the week ('Monday', 'Tuesday', etc.) to daily plans structured exactly as above.
    
    If the plan_type is 'Monthly', respond with a JSON object containing a 'monthly_plan' key mapping weeks ('Week 1', 'Week 2', 'Week 3', 'Week 4') to daily plans structured exactly as the daily plans (each containing 'breakfast', 'lunch', 'dinner', and 'snack' with name, calories, protein, carbs, fat, portion, and ingredients).

    Here are the exact JSON structures required for each plan type:

    Daily Plan Structure:
    {{
      "daily_plan": {{
        "breakfast": {{
          "name": "Oatmeal with mixed berries",
          "calories": 380,
          "protein": 14,
          "carbs": 55,
          "fat": 12,
          "portion": "1 bowl",
          "ingredients": ["Oats (50g)", "Blueberries (50g)", "Almonds (10g)"]
        }},
        "lunch": {{
          "name": "Quinoa Salad with Chickpeas",
          "calories": 550,
          "protein": 18,
          "carbs": 75,
          "fat": 15,
          "portion": "1 plate",
          "ingredients": ["Quinoa (80g)", "Chickpeas (100g)", "Cucumber", "Tomato"]
        }},
        "dinner": {{
          "name": "Lentil Soup with Asparagus",
          "calories": 480,
          "protein": 20,
          "carbs": 60,
          "fat": 10,
          "portion": "1 bowl",
          "ingredients": ["Lentils (100g)", "Asparagus (150g)"]
        }},
        "snack": {{
          "name": "Greek Yogurt with Honey",
          "calories": 210,
          "protein": 15,
          "carbs": 24,
          "fat": 6,
          "portion": "150g",
          "ingredients": ["Greek yogurt (150g)", "Honey (1 tsp)"]
        }}
      }}
    }}

    Weekly Plan Structure:
    {{
      "weekly_plan": {{
        "Monday": {{
          "breakfast": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "lunch": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "dinner": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "snack": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }}
        }},
        "Tuesday": {{ ... }},
        "Wednesday": {{ ... }},
        "Thursday": {{ ... }},
        "Friday": {{ ... }},
        "Saturday": {{ ... }},
        "Sunday": {{ ... }}
      }}
    }}

    Monthly Plan Structure:
    {{
      "monthly_plan": {{
        "Week 1": {{
          "breakfast": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "lunch": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "dinner": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }},
          "snack": {{ "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "...", "ingredients": [] }}
        }},
        "Week 2": {{ ... }},
        "Week 3": {{ ... }},
        "Week 4": {{ ... }}
      }}
    }}

    Avoid standard Markdown code blocks in your output, just return the JSON text directly.
    Ensure that all weeks of the Monthly plan are generated in full detail with the exact same structure as the Daily plan, and do not use simple text summaries or lists of strategies.
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        plan_data = json.loads(response.text)
        return normalize_plan_data(plan_data)
    except Exception as e:
        logger.error(f"Error calling Gemini API for Meal Plan: {e}")
        return normalize_plan_data(get_mock_meal_plan(profile, plan_type))

def analyze_food_image(image_bytes):
    """
    Analyze food images using Gemini 1.5 Flash Vision.
    """
    if not is_api_available():
        logger.info("Gemini API key not found. Using Mock image analyzer.")
        return get_mock_food_analysis()
        
    model = get_gemini_model()
    
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Analyze this food image. Provide detailed nutritional estimations.
        Return your analysis strictly as a JSON object containing the following keys:
        - 'food_name': name of the primary food items
        - 'calories': estimated total calories (float kcal)
        - 'protein': estimated total protein in grams (float)
        - 'carbs': estimated total carbohydrates in grams (float)
        - 'fat': estimated total fat in grams (float)
        - 'fiber': estimated total dietary fiber in grams (float)
        - 'health_rating': a health rating score out of 10 (float)
        - 'suggestions': list of strings with tips to make this meal healthier
        - 'breakdown': list of strings identifying specific food ingredients/items detected in the image and their estimated contribution.
        """
        
        response = model.generate_content(
            [prompt, img],
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error calling Gemini API for Image Analysis: {e}")
        return get_mock_food_analysis()

def generate_workout_plan(profile):
    """
    Generate custom workout plan.
    """
    if not is_api_available():
        return get_mock_workout_plan(profile)
        
    model = get_gemini_model()
    prompt = f"""
    You are an expert fitness coach. Generate a personalized exercise routine in JSON format.
    User Profile:
    - Goal: {profile.get('goal')}
    - Fitness Level: {profile.get('fitness_experience')}
    - Age: {profile.get('age')}
    - Weight: {profile.get('weight')} kg
    - Height: {profile.get('height')} cm
    - Medical Conditions: {profile.get('medical_conditions') or 'None'}
    
    Return a JSON object with:
    - 'routine_name': text name of the routine.
    - 'exercises': a list of objects, each containing:
      - 'name': name of the exercise
      - 'sets': integer count of sets
      - 'reps': text reps or hold duration (e.g. '10-12', '30s')
      - 'duration': approximate completion duration (e.g. '5 mins')
      - 'rest': rest interval description (e.g. '60s')
      - 'category': one of 'Home Workouts', 'Gym Workouts', 'Yoga', 'Cardio', 'HIIT'
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error calling Gemini for workouts: {e}")
        return get_mock_workout_plan(profile)

def chat_coach(history_list, new_message, profile):
    """
    Simulate conversational nutrition coach.
    """
    if not is_api_available():
        # Clean Mock responses
        msg_lower = new_message.lower()
        if "recipe" in msg_lower:
            return "Here's a simple, healthy recipe idea: Quinoa Stir-Fry! Just sauté cooked quinoa, bell peppers, broccoli, and tofu/chicken breast in 1 tsp olive oil. Season with soy sauce and black pepper. It provides ~350 kcal, 25g protein, and 45g carbs!"
        elif "calorie" in msg_lower or "carb" in msg_lower or "fat" in msg_lower:
            return f"Since your target goal is {profile.get('goal', 'Maintenance')}, I suggest maintaining a steady distribution of macros. Ensure your daily carbs come from complex sources (like oats, brown rice, vegetables) and healthy fats from avocados, nuts, or fish."
        else:
            return f"Hello! I am your AI Nutrition Coach. Based on your goal of **{profile.get('goal')}** and experience as a **{profile.get('fitness_experience')}**, I recommend eating nutrient-dense whole foods, staying hydrated (aim for 2-3 liters daily), and tracking your calories daily. How can I help you today?"

    model = get_gemini_model()
    
    # Format history for prompt context
    hist_formatted = ""
    for h in history_list[-10:]: # Keep last 10 messages for token efficiency
        role_label = "Coach" if h['role'] == 'assistant' else "User"
        hist_formatted += f"{role_label}: {h['content']}\n"
        
    prompt = f"""
    You are NutriAI, an expert medical nutritionist, dietitian, and personal trainer.
    Be encouraging, precise, and practical. Use bullet points where helpful.
    
    User Profile context:
    - Name: {profile.get('name', 'User')}
    - Goal: {profile.get('goal')}
    - Dietary preference: {profile.get('dietary_preferences')}
    - Medical/Allergies: {profile.get('medical_conditions') or 'None'} / {profile.get('allergies') or 'None'}
    
    Conversation History:
    {hist_formatted}
    
    User: {new_message}
    Coach:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini for chatbot: {e}")
        return "I apologize, but I encountered an error while processing your request. Please check your network connection or try again."

def generate_recipe(ingredients, goal, diet):
    """
    Generate recipes based on available ingredients.
    """
    if not is_api_available():
        return get_mock_recipe(ingredients)
        
    model = get_gemini_model()
    prompt = f"""
    Create a recipe based on available ingredients: {ingredients}.
    Goal: {goal}
    Dietary Preference: {diet}
    
    Return a JSON object with:
    - 'recipe_name': text name
    - 'ingredients': list of strings
    - 'instructions': list of strings
    - 'cooking_time': text
    - 'calories': float kcal
    - 'protein': float g
    - 'carbs': float g
    - 'fat': float g
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error calling Gemini for recipe: {e}")
        return get_mock_recipe(ingredients)

def generate_health_insights(profile, recent_logs_summary):
    """
    Analyze logs and profile to give actionable insights.
    """
    if not is_api_available():
        return get_mock_health_insights(profile)
        
    model = get_gemini_model()
    prompt = f"""
    Generate daily personalized health insights based on user activity.
    User Profile:
    - Goal: {profile.get('goal')}
    - Weight: {profile.get('weight')} kg
    
    Recent Weekly Logs Summary:
    {recent_logs_summary}
    
    Return a JSON object containing:
    - 'insights': list of 2-3 positive or analytical feedback points
    - 'alerts': list of 1-2 warnings (e.g. low water, high fats)
    - 'suggestions': list of 2-3 actionable improvement tips
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error calling Gemini for health insights: {e}")
        return get_mock_health_insights(profile)

def normalize_meal_object(meal_obj, default_type="breakfast"):
    """
    Ensures a meal object has name, calories, protein, carbs, fat, portion, ingredients.
    """
    defaults = {
        "breakfast": {"calories": 350, "protein": 15, "carbs": 45, "fat": 10},
        "lunch": {"calories": 550, "protein": 25, "carbs": 60, "fat": 15},
        "dinner": {"calories": 500, "protein": 25, "carbs": 50, "fat": 12},
        "snack": {"calories": 200, "protein": 10, "carbs": 20, "fat": 5}
    }
    def_vals = defaults.get(default_type.lower(), defaults["breakfast"])
    
    if not meal_obj:
        return {
            "name": "Healthy Selection",
            "calories": def_vals["calories"],
            "protein": def_vals["protein"],
            "carbs": def_vals["carbs"],
            "fat": def_vals["fat"],
            "portion": "1 serving",
            "ingredients": ["Balanced whole foods"]
        }
        
    if isinstance(meal_obj, str):
        desc = meal_obj.strip()
        ingredients = [i.strip() for i in desc.split(',') if i.strip()]
        if not ingredients:
            ingredients = [desc]
        return {
            "name": desc[:50] + "..." if len(desc) > 53 else desc,
            "calories": def_vals["calories"],
            "protein": def_vals["protein"],
            "carbs": def_vals["carbs"],
            "fat": def_vals["fat"],
            "portion": "1 serving",
            "ingredients": ingredients
        }
        
    if isinstance(meal_obj, dict):
        ingredients = meal_obj.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [ingredients]
        elif not isinstance(ingredients, list):
            ingredients = []
        if not ingredients:
            name = meal_obj.get('name', 'Balanced Meal')
            ingredients = [name]
            
        return {
            "name": meal_obj.get('name', 'Healthy Choice'),
            "calories": int(meal_obj.get('calories', def_vals["calories"])),
            "protein": int(meal_obj.get('protein', def_vals["protein"])),
            "carbs": int(meal_obj.get('carbs', def_vals["carbs"])),
            "fat": int(meal_obj.get('fat', def_vals["fat"])),
            "portion": meal_obj.get('portion', '1 serving'),
            "ingredients": ingredients
        }
        
    return {
        "name": "Healthy Option",
        "calories": def_vals["calories"],
        "protein": def_vals["protein"],
        "carbs": def_vals["carbs"],
        "fat": def_vals["fat"],
        "portion": "1 serving",
        "ingredients": ["Nutrient dense foods"]
    }

def parse_meal_guidelines_list(guidelines):
    """
    Parses a list of meal guideline strings like:
    ['Breakfast: Oatmeal...', 'Lunch: Salad...']
    into a structured dict mapping meal types to structured meal dicts.
    """
    res = {}
    for item in guidelines:
        if not isinstance(item, str):
            continue
        parts = item.split(':', 1)
        if len(parts) == 2:
            meal_type = parts[0].strip().lower()
            desc = parts[1].strip()
        else:
            parts = item.split('-', 1)
            if len(parts) == 2:
                meal_type = parts[0].strip().lower()
                desc = parts[1].strip()
            else:
                continue
                
        m_key = None
        if 'breakfast' in meal_type or 'morning' in meal_type:
            m_key = 'breakfast'
        elif 'lunch' in meal_type or 'noon' in meal_type:
            m_key = 'lunch'
        elif 'dinner' in meal_type or 'night' in meal_type:
            m_key = 'dinner'
        elif 'snack' in meal_type or 'afternoon' in meal_type or 'snacks' in meal_type:
            m_key = 'snack'
            
        if m_key:
            res[m_key] = normalize_meal_object(desc, default_type=m_key)
            
    for m_key in ['breakfast', 'lunch', 'dinner', 'snack']:
        if m_key not in res:
            res[m_key] = normalize_meal_object(None, default_type=m_key)
            
    return res

def normalize_plan_data(plan_data):
    """
    Normalizes the full plan_data dict structure so it has standard structured keys.
    """
    if not isinstance(plan_data, dict):
        return {}
        
    # Make a copy to avoid in-place mutation of cached dicts
    plan_data = json.loads(json.dumps(plan_data))
        
    # 1. Normalize daily plan
    if 'daily_plan' in plan_data:
        daily = plan_data['daily_plan']
        if not isinstance(daily, dict):
            daily = {}
        normalized_daily = {}
        for m_key in ['breakfast', 'lunch', 'dinner', 'snack']:
            normalized_daily[m_key] = normalize_meal_object(daily.get(m_key), default_type=m_key)
        plan_data['daily_plan'] = normalized_daily
        
    # 2. Normalize weekly plan
    if 'weekly_plan' in plan_data:
        weekly = plan_data['weekly_plan']
        if not isinstance(weekly, dict):
            weekly = {}
        normalized_weekly = {}
        for day, daily in weekly.items():
            if not isinstance(daily, dict):
                daily = {}
            normalized_daily = {}
            for m_key in ['breakfast', 'lunch', 'dinner', 'snack']:
                normalized_daily[m_key] = normalize_meal_object(daily.get(m_key), default_type=m_key)
            normalized_weekly[day] = normalized_daily
        plan_data['weekly_plan'] = normalized_weekly
        
    # 3. Normalize monthly plan
    if 'monthly_plan' in plan_data:
        monthly = plan_data['monthly_plan']
        normalized_monthly = {}
        
        if isinstance(monthly, list):
            for idx, item in enumerate(monthly):
                if isinstance(item, dict):
                    week_num = item.get('week_number', f"Week {idx + 1}")
                    if any(k in item for k in ['breakfast', 'lunch', 'dinner', 'snack']):
                        normalized_daily = {}
                        for m_key in ['breakfast', 'lunch', 'dinner', 'snack']:
                            normalized_daily[m_key] = normalize_meal_object(item.get(m_key), default_type=m_key)
                        normalized_monthly[week_num] = normalized_daily
                    elif 'sample_meals_guideline' in item:
                        normalized_monthly[week_num] = parse_meal_guidelines_list(item['sample_meals_guideline'])
                    else:
                        desc = []
                        for k, v in item.items():
                            if k not in ['week_number']:
                                desc.append(f"{k}: {v}")
                        normalized_monthly[week_num] = parse_meal_guidelines_list(desc)
                elif isinstance(item, str):
                    normalized_monthly[f"Week {idx + 1}"] = parse_meal_guidelines_list([item])
                    
        elif isinstance(monthly, dict):
            for week, daily in monthly.items():
                if 'guideline' in week.lower() or 'overall' in week.lower() or 'summary' in week.lower():
                    continue
                if isinstance(daily, dict):
                    if any(k in daily for k in ['breakfast', 'lunch', 'dinner', 'snack']):
                        normalized_daily = {}
                        for m_key in ['breakfast', 'lunch', 'dinner', 'snack']:
                            normalized_daily[m_key] = normalize_meal_object(daily.get(m_key), default_type=m_key)
                        normalized_monthly[week] = normalized_daily
                    elif 'sample_meals_guideline' in daily:
                        normalized_monthly[week] = parse_meal_guidelines_list(daily['sample_meals_guideline'])
                    else:
                        desc = []
                        for k, v in daily.items():
                            desc.append(f"{k}: {v}")
                        normalized_monthly[week] = parse_meal_guidelines_list(desc)
                elif isinstance(daily, list):
                    normalized_monthly[week] = parse_meal_guidelines_list(daily)
                elif isinstance(daily, str):
                    normalized_monthly[week] = parse_meal_guidelines_list([daily])
                    
        plan_data['monthly_plan'] = normalized_monthly
        
    return plan_data
