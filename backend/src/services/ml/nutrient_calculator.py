"""
Nutrient Calculator Service
"""

import numpy as np
import structlog
from typing import Dict, List, Any, Optional
from functools import lru_cache

logger = structlog.get_logger()

class NutrientCalculator:
    """Nutritional analysis and calculation service"""
    
    def __init__(self):
        # Base nutritional data for common foods (per 100g)
        self.nutritional_database = {
            'rice': {
                'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3,
                'fiber': 0.4, 'vitamins': {'B1': 0.07, 'B3': 1.6}, 'minerals': {'iron': 0.8, 'zinc': 0.6}
            },
            'wheat': {
                'calories': 340, 'protein': 13.7, 'carbs': 71, 'fat': 2.0,
                'fiber': 10.7, 'vitamins': {'B1': 0.4, 'B3': 5.5}, 'minerals': {'iron': 3.6, 'zinc': 2.8}
            },
            'milk': {
                'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1.0,
                'fiber': 0, 'vitamins': {'B2': 0.18, 'B12': 0.5}, 'minerals': {'calcium': 113, 'phosphorus': 84}
            },
            'ghee': {
                'calories': 900, 'protein': 0, 'carbs': 0, 'fat': 100,
                'fiber': 0, 'vitamins': {'A': 3069, 'E': 2.8}, 'minerals': {'sodium': 0}
            },
            'dal': {
                'calories': 116, 'protein': 7.6, 'carbs': 20, 'fat': 0.4,
                'fiber': 7.6, 'vitamins': {'B1': 0.2, 'B9': 0.2}, 'minerals': {'iron': 2.5, 'zinc': 1.0}
            },
            'vegetables': {
                'calories': 25, 'protein': 2, 'carbs': 5, 'fat': 0.2,
                'fiber': 2.5, 'vitamins': {'C': 60, 'A': 500}, 'minerals': {'iron': 0.8, 'calcium': 30}
            }
        }
        
        # Daily nutritional requirements by age and gender
        self.daily_requirements = {
            'male': {
                'adult': {'calories': 2500, 'protein': 65, 'carbs': 300, 'fat': 83, 'fiber': 38},
                'elderly': {'calories': 2200, 'protein': 60, 'carbs': 275, 'fat': 73, 'fiber': 30}
            },
            'female': {
                'adult': {'calories': 2000, 'protein': 50, 'carbs': 250, 'fat': 67, 'fiber': 25},
                'elderly': {'calories': 1800, 'protein': 45, 'carbs': 225, 'fat': 60, 'fiber': 21}
            },
            'child': {
                '1-3': {'calories': 1000, 'protein': 13, 'carbs': 130, 'fat': 30, 'fiber': 14},
                '4-8': {'calories': 1200, 'protein': 19, 'carbs': 130, 'fat': 25, 'fiber': 20},
                '9-13': {'calories': 1600, 'protein': 34, 'carbs': 130, 'fat': 25, 'fiber': 25}
            }
        }
    
    def calculate_meal_nutrition(self, foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate nutritional content of a meal"""
        try:
            total_nutrition = {
                'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0,
                'vitamins': {}, 'minerals': {}
            }
            
            for food in foods:
                food_name = food.get('name', '').lower()
                quantity = food.get('quantity', 100)  # Default to 100g
                unit = food.get('unit', 'grams')
                
                # Convert quantity to grams
                quantity_grams = self._convert_to_grams(quantity, unit)
                
                # Get nutritional data
                nutrition = self._get_food_nutrition(food_name)
                
                # Calculate nutrition for this quantity
                for nutrient, value in nutrition.items():
                    if nutrient in ['vitamins', 'minerals']:
                        if nutrient not in total_nutrition[nutrient]:
                            total_nutrition[nutrient] = {}
                        for sub_nutrient, sub_value in value.items():
                            total_nutrition[nutrient][sub_nutrient] = total_nutrition[nutrient].get(sub_nutrient, 0) + (sub_value * quantity_grams / 100)
                    else:
                        total_nutrition[nutrient] += value * quantity_grams / 100
            
            return total_nutrition
            
        except Exception as e:
            logger.error("Meal nutrition calculation failed", error=str(e))
            return {}
    
    def analyze_diet_balance(self, daily_meals: List[Dict[str, Any]], patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall diet balance for a patient"""
        try:
            # Calculate total daily nutrition
            total_daily = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
            
            for meal in daily_meals:
                meal_nutrition = self.calculate_meal_nutrition(meal.get('foods', []))
                for nutrient, value in meal_nutrition.items():
                    if nutrient in total_daily:
                        total_daily[nutrient] += value
            
            # Get daily requirements
            requirements = self._get_daily_requirements(patient_info)
            
            # Calculate balance scores
            balance_scores = {}
            for nutrient, total in total_daily.items():
                required = requirements.get(nutrient, 1)
                balance_scores[nutrient] = min(total / required, 1.0) if required > 0 else 0
            
            # Overall balance score
            overall_balance = np.mean(list(balance_scores.values()))
            
            return {
                'daily_totals': total_daily,
                'daily_requirements': requirements,
                'balance_scores': balance_scores,
                'overall_balance': overall_balance,
                'recommendations': self._get_balance_recommendations(balance_scores, requirements),
                'status': self._get_balance_status(overall_balance)
            }
            
        except Exception as e:
            logger.error("Diet balance analysis failed", error=str(e))
            return {'error': 'Failed to analyze diet balance'}
    
    def suggest_nutritional_improvements(self, current_nutrition: Dict[str, Any], target_nutrition: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest improvements to meet nutritional targets"""
        try:
            improvements = {}
            
            for nutrient, current in current_nutrition.items():
                target = target_nutrition.get(nutrient, 0)
                if target > 0:
                    deficit = target - current
                    if deficit > 0:
                        improvements[nutrient] = {
                            'deficit': deficit,
                            'percentage': (deficit / target) * 100,
                            'suggestions': self._get_nutrient_suggestions(nutrient, deficit)
                        }
            
            return {
                'improvements_needed': improvements,
                'priority_nutrients': sorted(improvements.keys(), key=lambda x: improvements[x]['percentage'], reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error("Nutritional improvement suggestions failed", error=str(e))
            return {'error': 'Failed to generate suggestions'}
    
    def _convert_to_grams(self, quantity: float, unit: str) -> float:
        """Convert different units to grams"""
        conversion_factors = {
            'grams': 1.0,
            'kg': 1000.0,
            'cups': 250.0,  # Approximate for most foods
            'tbsp': 15.0,
            'tsp': 5.0,
            'pieces': 50.0,  # Average piece weight
            'slices': 25.0   # Average slice weight
        }
        
        return quantity * conversion_factors.get(unit.lower(), 1.0)
    
    def _get_food_nutrition(self, food_name: str) -> Dict[str, Any]:
        """Get nutritional data for a food item"""
        # Try exact match first
        if food_name in self.nutritional_database:
            return self.nutritional_database[food_name]
        
        # Try partial match
        for key, nutrition in self.nutritional_database.items():
            if key in food_name or food_name in key:
                return nutrition
        
        # Default nutrition for unknown foods
        return {
            'calories': 50, 'protein': 2, 'carbs': 10, 'fat': 1,
            'fiber': 2, 'vitamins': {'C': 20}, 'minerals': {'iron': 0.5}
        }
    
    def _get_daily_requirements(self, patient_info: Dict[str, Any]) -> Dict[str, float]:
        """Get daily nutritional requirements for patient"""
        age = patient_info.get('age', 30)
        gender = patient_info.get('gender', 'male').lower()
        
        if age < 18:
            if age <= 3:
                age_group = '1-3'
            elif age <= 8:
                age_group = '4-8'
            else:
                age_group = '9-13'
            return self.daily_requirements['child'][age_group]
        elif age >= 65:
            age_group = 'elderly'
        else:
            age_group = 'adult'
        
        return self.daily_requirements[gender][age_group]
    
    def _get_balance_recommendations(self, balance_scores: Dict[str, float], requirements: Dict[str, float]) -> List[str]:
        """Get recommendations based on balance scores"""
        recommendations = []
        
        for nutrient, score in balance_scores.items():
            if score < 0.7:  # Less than 70% of requirement
                deficit = requirements[nutrient] * (1 - score)
                recommendations.append(f"Increase {nutrient} by {deficit:.1f}g")
            elif score > 1.3:  # More than 130% of requirement
                excess = requirements[nutrient] * (score - 1)
                recommendations.append(f"Reduce {nutrient} by {excess:.1f}g")
        
        return recommendations
    
    def _get_balance_status(self, overall_balance: float) -> str:
        """Get overall balance status"""
        if overall_balance >= 0.9:
            return "Excellent"
        elif overall_balance >= 0.7:
            return "Good"
        elif overall_balance >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def _get_nutrient_suggestions(self, nutrient: str, deficit: float) -> List[str]:
        """Get food suggestions for specific nutrient deficit"""
        nutrient_foods = {
            'protein': ['dal', 'milk', 'paneer', 'nuts', 'seeds'],
            'carbs': ['rice', 'wheat', 'oats', 'quinoa', 'sweet potato'],
            'fat': ['ghee', 'nuts', 'seeds', 'avocado', 'coconut'],
            'fiber': ['vegetables', 'fruits', 'whole grains', 'legumes'],
            'calories': ['nuts', 'dried fruits', 'ghee', 'whole grains']
        }
        
        return nutrient_foods.get(nutrient, ['varied diet'])
