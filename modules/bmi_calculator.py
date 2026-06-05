def calculate_bmi(weight_kg, height_cm):
    """
    Calculate Body Mass Index (BMI).
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Unknown"
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal Weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
        
    return round(bmi, 1), category

def calculate_bmr(weight_kg, height_cm, age, gender):
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation.
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return round(bmr, 1)

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on activity level.
    """
    multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9
    }
    
    # Standardize input string
    level = activity_level.strip().lower()
    multiplier = multipliers.get(level, 1.2)
    return round(bmr * multiplier, 1)

def calculate_calorie_target(tdee, goal):
    """
    Calculate custom daily calorie targets tailored to specific fitness goals.
    """
    goal = goal.strip().lower()
    if "loss" in goal or "deficit" in goal:
        target = tdee - 500  # Healthy 500 calorie deficit
    elif "gain" in goal or "surplus" in goal:
        target = tdee + 400  # Surplus for lean bulking
    elif "muscle" in goal:
        target = tdee + 300  # Lean muscle building surplus
    else:
        target = tdee        # Maintenance
        
    # Cap lower bound at 1200 kcal for safety
    return max(1200.0, round(target, 1))

def calculate_ideal_weight_range(height_cm):
    """
    Calculate ideal body weight range based on normal BMI limits (18.5 - 24.9).
    """
    height_m = height_cm / 100.0
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    return round(min_weight, 1), round(max_weight, 1)

def recommend_macros(calorie_target, diet_preference):
    """
    Recommend macronutrient distribution based on calorie target and dietary preference.
    Returns dictionary with protein_g, carbs_g, fat_g, fiber_g and percentages.
    """
    diet = diet_preference.strip().lower()
    
    # Default balance: 25% Protein, 45% Carbs, 30% Fat
    p_pct, c_pct, f_pct = 0.25, 0.45, 0.30
    
    if "keto" in diet:
        p_pct, c_pct, f_pct = 0.20, 0.05, 0.75
    elif "low carb" in diet:
        p_pct, c_pct, f_pct = 0.35, 0.20, 0.45
    elif "high protein" in diet:
        p_pct, c_pct, f_pct = 0.35, 0.40, 0.25
    elif "diabetic" in diet:
        p_pct, c_pct, f_pct = 0.30, 0.35, 0.35
        
    # 1g Protein = 4 kcal, 1g Carb = 4 kcal, 1g Fat = 9 kcal
    protein_g = (calorie_target * p_pct) / 4
    carbs_g = (calorie_target * c_pct) / 4
    fat_g = (calorie_target * f_pct) / 9
    
    # Fiber guideline: ~14g per 1000 calories
    fiber_g = (calorie_target / 1000) * 14
    
    return {
        "calories": calorie_target,
        "protein_g": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "fat_g": round(fat_g, 1),
        "fiber_g": round(fiber_g, 1),
        "protein_pct": int(p_pct * 100),
        "carbs_pct": int(c_pct * 100),
        "fat_pct": int(f_pct * 100)
    }

def get_health_score(bmi, water_ml, sleep_hours, log_calories, target_calories):
    """
    Calculate a composite health score out of 100 based on core metrics.
    """
    score = 100
    
    # 1. BMI Penalty
    if bmi < 18.5 or bmi >= 30:
        score -= 20
    elif bmi >= 25:
        score -= 10
        
    # 2. Water Penalty (Goal is 2000ml)
    water_ratio = min(water_ml / 2000.0, 1.0)
    score -= (1.0 - water_ratio) * 20
    
    # 3. Sleep Penalty (Goal is 7.5 hours)
    sleep_ratio = min(sleep_hours / 7.5, 1.0)
    score -= (1.0 - sleep_ratio) * 20
    
    # 4. Calorie Deviation Penalty
    if log_calories > 0 and target_calories > 0:
        dev = abs(log_calories - target_calories) / target_calories
        if dev > 0.2:  # over/under 20%
            score -= 15
        elif dev > 0.1:
            score -= 5
            
    return max(10, int(score))
