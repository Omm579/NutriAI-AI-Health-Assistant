import os
import unittest
import database
import auth
from modules import bmi_calculator, report_generator

class TestNutriAIBackend(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize database
        database.init_db()

    def test_database_creation(self):
        """Verify SQLite database file is created and reachable."""
        self.assertTrue(os.path.exists(database.DB_PATH))
        
    def test_password_hashing(self):
        """Verify PBKDF2 hashing security checks."""
        password = "SecurePassword123!"
        hashed = auth.hash_password(password)
        
        # Verify split format (salt:hash)
        self.assertIn(":", hashed)
        
        # Verify checking matching passwords works
        self.assertTrue(auth.verify_password(hashed, password))
        # Verify mismatch fails
        self.assertFalse(auth.verify_password(hashed, "wrongPassword"))

    def test_bmi_equations(self):
        """Verify body mass index category thresholds."""
        # Underweight (BMI < 18.5)
        bmi, cat = bmi_calculator.calculate_bmi(50, 175)
        self.assertEqual(cat, "Underweight")
        
        # Normal (18.5 <= BMI < 25)
        bmi, cat = bmi_calculator.calculate_bmi(70, 175)
        self.assertEqual(cat, "Normal Weight")
        
        # Overweight (25 <= BMI < 30)
        bmi, cat = bmi_calculator.calculate_bmi(80, 175)
        self.assertEqual(cat, "Overweight")
        
        # Obese (BMI >= 30)
        bmi, cat = bmi_calculator.calculate_bmi(100, 175)
        self.assertEqual(cat, "Obese")

    def test_bmr_calculations(self):
        """Verify Mifflin-St Jeor math outputs."""
        # Male
        bmr_male = bmi_calculator.calculate_bmr(weight_kg=70.0, height_cm=175.0, age=25, gender="Male")
        # Formula: 10 * 70 + 6.25 * 175 - 5 * 25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
        self.assertAlmostEqual(bmr_male, 1673.8, places=1)
        
        # Female
        bmr_female = bmi_calculator.calculate_bmr(weight_kg=60.0, height_cm=165.0, age=30, gender="Female")
        # Formula: 10 * 60 + 6.25 * 165 - 5 * 30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
        self.assertAlmostEqual(bmr_female, 1320.2, places=1)

    def test_calorie_targets(self):
        """Verify TDEE multipliers and target deficit bounds."""
        bmr = 1673.8
        tdee_sedentary = bmi_calculator.calculate_tdee(bmr, "Sedentary")
        # 1673.8 * 1.2 = 2008.56
        self.assertAlmostEqual(tdee_sedentary, 2008.6, places=1)
        
        # Test targets
        target_loss = bmi_calculator.calculate_calorie_target(2008.6, "Weight Loss")
        self.assertEqual(target_loss, 1508.6)
        
        # Test floor bound safety (minimum 1200 kcal)
        target_low = bmi_calculator.calculate_calorie_target(1300.0, "Weight Loss")
        self.assertEqual(target_low, 1200.0)

    def test_macro_recommendations(self):
        """Verify macronutrient divisions for specialized diets."""
        calories = 2000.0
        macros_keto = bmi_calculator.recommend_macros(calories, "Keto")
        
        # Keto has 5% Carbs: (2000 * 0.05) / 4 = 25g
        self.assertEqual(macros_keto['carbs_g'], 25.0)
        
        # Keto has 75% Fat: (2000 * 0.75) / 9 = 166.7g
        self.assertAlmostEqual(macros_keto['fat_g'], 166.7, places=1)

    def test_normalize_plan_data(self):
        """Verify normalization of raw meal plans into standard schema."""
        from modules.gemini_service import normalize_plan_data
        
        # Test case 1: List-based monthly plan
        raw_list_monthly = {
            "monthly_plan": [
                {
                    "week_number": "Week 1",
                    "theme": "Adaptation",
                    "sample_meals_guideline": [
                        "Breakfast: Oatmeal with mixed berries, flax seeds",
                        "Lunch: Salad with beans",
                        "Dinner: Tofu stir-fry",
                        "Snacks: Apple slices, hummus"
                    ]
                }
            ]
        }
        normalized = normalize_plan_data(raw_list_monthly)
        self.assertIn("monthly_plan", normalized)
        self.assertIsInstance(normalized["monthly_plan"], dict)
        self.assertIn("Week 1", normalized["monthly_plan"])
        week_1 = normalized["monthly_plan"]["Week 1"]
        self.assertIn("breakfast", week_1)
        self.assertEqual(week_1["breakfast"]["name"], "Oatmeal with mixed berries, flax seeds")
        self.assertEqual(week_1["breakfast"]["calories"], 350)
        self.assertIn("Oatmeal with mixed berries", week_1["breakfast"]["ingredients"])
        self.assertIn("flax seeds", week_1["breakfast"]["ingredients"])
        self.assertIn("snack", week_1)
        self.assertEqual(week_1["snack"]["name"], "Apple slices, hummus")

if __name__ == '__main__':
    unittest.main()
