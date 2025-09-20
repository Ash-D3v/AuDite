"""
Viruddha Ahara (Incompatible Foods) Detection Service
"""

import structlog
from typing import Dict, List, Any, Set, Tuple
from functools import lru_cache

logger = structlog.get_logger()

class ViruddhaAharaDetector:
    """Detect incompatible food combinations according to Ayurveda"""
    
    def __init__(self):
        # Traditional incompatible food combinations
        self.incompatible_combinations = {
            # Milk combinations
            'milk': {'fish', 'sour_fruits', 'banana', 'yogurt', 'salt', 'meat'},
            'yogurt': {'milk', 'sour_fruits', 'hot_foods', 'fish'},
            
            # Fruit combinations
            'banana': {'milk', 'yogurt', 'sour_fruits'},
            'sour_fruits': {'milk', 'yogurt', 'banana', 'sweet_fruits'},
            
            # Protein combinations
            'fish': {'milk', 'yogurt', 'honey', 'jaggery'},
            'meat': {'milk', 'fish', 'honey'},
            
            # Sweet combinations
            'honey': {'fish', 'meat', 'hot_water', 'ghee'},
            'jaggery': {'fish', 'milk'},
            
            # Spice combinations
            'salt': {'milk', 'honey'},
            
            # General rules
            'hot_foods': {'cold_foods', 'yogurt'},
            'raw_foods': {'cooked_foods', 'milk'},
            'fermented': {'milk', 'sour_fruits'}
        }
        
        # Food categories for pattern matching
        self.food_categories = {
            'milk': ['milk', 'dairy', 'cheese', 'paneer'],
            'fish': ['fish', 'seafood', 'prawns', 'crab'],
            'meat': ['chicken', 'mutton', 'beef', 'pork', 'meat'],
            'sour_fruits': ['lemon', 'lime', 'orange', 'tamarind', 'vinegar'],
            'sweet_fruits': ['mango', 'grapes', 'dates', 'figs'],
            'banana': ['banana', 'plantain'],
            'yogurt': ['yogurt', 'curd', 'dahi'],
            'honey': ['honey', 'madhu'],
            'jaggery': ['jaggery', 'gur', 'brown_sugar'],
            'hot_foods': ['spicy', 'chili', 'pepper', 'garlic', 'onion'],
            'cold_foods': ['ice', 'cold_drinks', 'cucumber', 'watermelon'],
            'raw_foods': ['salad', 'raw_vegetables', 'sprouts'],
            'cooked_foods': ['rice', 'dal', 'curry', 'soup'],
            'fermented': ['pickle', 'fermented_foods', 'wine']
        }
    
    def check_incompatibility(self, food1: str, food2: str) -> Dict[str, Any]:
        """Check if two foods are incompatible"""
        try:
            food1_categories = self._get_food_categories(food1)
            food2_categories = self._get_food_categories(food2)
            
            # Check direct incompatibilities
            incompatible = False
            conflicts = []
            
            for cat1 in food1_categories:
                if cat1 in self.incompatible_combinations:
                    incompatible_cats = self.incompatible_combinations[cat1]
                    for cat2 in food2_categories:
                        if cat2 in incompatible_cats:
                            incompatible = True
                            conflicts.append({
                                'category1': cat1,
                                'category2': cat2,
                                'reason': self._get_incompatibility_reason(cat1, cat2)
                            })
            
            return {
                'incompatible': incompatible,
                'conflicts': conflicts,
                'severity': self._calculate_severity(conflicts),
                'recommendations': self._get_incompatibility_recommendations(conflicts)
            }
            
        except Exception as e:
            logger.error("Incompatibility check failed", error=str(e))
            return {'incompatible': False, 'error': 'Check failed'}
    
    def check_meal_incompatibilities(self, foods: List[str]) -> Dict[str, Any]:
        """Check for incompatibilities in a complete meal"""
        try:
            all_conflicts = []
            incompatible_pairs = []
            
            # Check all pairs
            for i in range(len(foods)):
                for j in range(i + 1, len(foods)):
                    result = self.check_incompatibility(foods[i], foods[j])
                    if result['incompatible']:
                        incompatible_pairs.append((foods[i], foods[j]))
                        all_conflicts.extend(result['conflicts'])
            
            # Calculate overall meal compatibility
            total_pairs = len(foods) * (len(foods) - 1) // 2
            incompatible_ratio = len(incompatible_pairs) / total_pairs if total_pairs > 0 else 0
            
            return {
                'incompatible_pairs': incompatible_pairs,
                'total_conflicts': len(all_conflicts),
                'incompatibility_ratio': incompatible_ratio,
                'severity': self._calculate_meal_severity(all_conflicts),
                'recommendations': self._get_meal_incompatibility_recommendations(incompatible_pairs, all_conflicts),
                'safe_to_eat': incompatible_ratio < 0.3  # Less than 30% incompatibility
            }
            
        except Exception as e:
            logger.error("Meal incompatibility check failed", error=str(e))
            return {'error': 'Failed to check meal incompatibilities'}
    
    def suggest_alternatives(self, incompatible_foods: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Suggest alternative food combinations"""
        try:
            alternatives = {}
            
            for food1, food2 in incompatible_foods:
                key = f"{food1}_with_{food2}"
                alternatives[key] = {
                    'incompatible_pair': [food1, food2],
                    'alternatives': self._get_food_alternatives(food1, food2),
                    'timing_suggestions': self._get_timing_suggestions(food1, food2)
                }
            
            return {
                'alternatives': alternatives,
                'general_advice': self._get_general_alternatives_advice()
            }
            
        except Exception as e:
            logger.error("Alternative suggestions failed", error=str(e))
            return {'error': 'Failed to generate alternatives'}
    
    def _get_food_categories(self, food: str) -> Set[str]:
        """Get all categories a food belongs to"""
        food_lower = food.lower().replace(' ', '_')
        categories = set()
        
        for category, foods in self.food_categories.items():
            if any(food_item in food_lower for food_item in foods):
                categories.add(category)
        
        # If no categories found, add the food name itself
        if not categories:
            categories.add(food_lower)
        
        return categories
    
    def _get_incompatibility_reason(self, cat1: str, cat2: str) -> str:
        """Get reason for incompatibility"""
        reasons = {
            ('milk', 'fish'): 'Milk and fish have opposite properties and cause digestive issues',
            ('milk', 'sour_fruits'): 'Sour fruits curdle milk and create toxins',
            ('milk', 'banana'): 'Banana and milk combination is heavy and hard to digest',
            ('honey', 'ghee'): 'Honey and ghee in equal quantities are considered poisonous',
            ('hot_foods', 'cold_foods'): 'Hot and cold foods together confuse digestive fire',
            ('raw_foods', 'cooked_foods'): 'Raw and cooked foods have different digestion times'
        }
        
        return reasons.get((cat1, cat2), f'{cat1} and {cat2} are incompatible according to Ayurveda')
    
    def _calculate_severity(self, conflicts: List[Dict]) -> str:
        """Calculate severity of incompatibility"""
        if not conflicts:
            return 'none'
        
        # Count different types of conflicts
        severe_conflicts = ['milk', 'fish', 'honey', 'ghee']
        has_severe = any(conflict['category1'] in severe_conflicts or 
                        conflict['category2'] in severe_conflicts 
                        for conflict in conflicts)
        
        if has_severe or len(conflicts) > 2:
            return 'high'
        elif len(conflicts) > 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_meal_severity(self, all_conflicts: List[Dict]) -> str:
        """Calculate overall meal severity"""
        if not all_conflicts:
            return 'none'
        
        # Count severe conflicts
        severe_count = sum(1 for conflict in all_conflicts 
                          if conflict['category1'] in ['milk', 'fish', 'honey'] or
                          conflict['category2'] in ['milk', 'fish', 'honey'])
        
        if severe_count > 0:
            return 'high'
        elif len(all_conflicts) > 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_incompatibility_recommendations(self, conflicts: List[Dict]) -> List[str]:
        """Get recommendations for incompatibility conflicts"""
        if not conflicts:
            return ['No incompatibilities found']
        
        recommendations = []
        for conflict in conflicts:
            recommendations.append(f"Avoid {conflict['category1']} with {conflict['category2']}: {conflict['reason']}")
        
        return recommendations
    
    def _get_meal_incompatibility_recommendations(self, incompatible_pairs: List[Tuple], all_conflicts: List[Dict]) -> Dict[str, Any]:
        """Get recommendations for meal incompatibilities"""
        if not incompatible_pairs:
            return {
                'status': 'Safe',
                'message': 'No incompatibilities found in the meal',
                'suggestions': []
            }
        
        return {
            'status': 'Incompatible',
            'message': f'Found {len(incompatible_pairs)} incompatible food pairs',
            'suggestions': [
                f'Remove {pair[0]} or {pair[1]} from the meal'
                for pair in incompatible_pairs[:3]  # Top 3 suggestions
            ],
            'priority': 'high' if len(all_conflicts) > 2 else 'medium'
        }
    
    def _get_food_alternatives(self, food1: str, food2: str) -> List[str]:
        """Get alternative food suggestions"""
        alternatives = {
            'milk': ['coconut_milk', 'almond_milk', 'soy_milk'],
            'fish': ['paneer', 'tofu', 'mushrooms'],
            'sour_fruits': ['sweet_fruits', 'neutral_fruits'],
            'banana': ['apple', 'pear', 'grapes'],
            'yogurt': ['coconut_yogurt', 'almond_yogurt']
        }
        
        # Return alternatives for the first food
        return alternatives.get(food1.lower(), ['Try different preparation method', 'Use in different meal'])
    
    def _get_timing_suggestions(self, food1: str, food2: str) -> List[str]:
        """Get timing suggestions for incompatible foods"""
        return [
            f'Eat {food1} and {food2} at least 2-3 hours apart',
            'Have one in the morning and other in the evening',
            'Consider having them on different days'
        ]
    
    def _get_general_alternatives_advice(self) -> List[str]:
        """Get general advice for avoiding incompatibilities"""
        return [
            'Follow traditional food combining principles',
            'Eat foods in their natural season',
            'Consider your dosha constitution when combining foods',
            'When in doubt, keep it simple and traditional'
        ]
