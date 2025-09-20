"""
Guna (Hot/Cold Properties) Calculator Service
"""

import structlog
from typing import Dict, List, Any, Tuple
from enum import Enum

logger = structlog.get_logger()

class GunaType(Enum):
    HOT = "hot"
    COLD = "cold"
    NEUTRAL = "neutral"

class ViryaType(Enum):
    HEATING = "heating"
    COOLING = "cooling"
    NEUTRAL = "neutral"

class GunaCalculator:
    """Calculate food properties (Guna) and energy (Virya)"""
    
    def __init__(self):
        # Food properties database
        self.food_properties = {
            'ginger': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.8},
            'garlic': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.9},
            'onion': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.6},
            'chili': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 1.0},
            'black_pepper': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.9},
            'cinnamon': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.7},
            'cardamom': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.6},
            'cumin': {'guna': GunaType.HOT, 'virya': ViryaType.HEATING, 'intensity': 0.5},
            'coriander': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.4},
            'mint': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.8},
            'coconut': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.6},
            'cucumber': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.7},
            'watermelon': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.8},
            'milk': {'guna': GunaType.COLD, 'virya': ViryaType.COOLING, 'intensity': 0.5},
            'ghee': {'guna': GunaType.NEUTRAL, 'virya': ViryaType.NEUTRAL, 'intensity': 0.3},
            'rice': {'guna': GunaType.NEUTRAL, 'virya': ViryaType.NEUTRAL, 'intensity': 0.2},
            'wheat': {'guna': GunaType.NEUTRAL, 'virya': ViryaType.NEUTRAL, 'intensity': 0.3},
            'dal': {'guna': GunaType.NEUTRAL, 'virya': ViryaType.NEUTRAL, 'intensity': 0.2}
        }
        
        # Dosha-specific guna preferences
        self.dosha_guna_preferences = {
            'vata': {'preferred': [GunaType.HOT, GunaType.NEUTRAL], 'avoid': [GunaType.COLD]},
            'pitta': {'preferred': [GunaType.COLD, GunaType.NEUTRAL], 'avoid': [GunaType.HOT]},
            'kapha': {'preferred': [GunaType.HOT], 'avoid': [GunaType.COLD, GunaType.NEUTRAL]}
        }
    
    def calculate_food_guna(self, food_name: str) -> Dict[str, Any]:
        """Calculate guna properties for a specific food"""
        try:
            food_key = food_name.lower().replace(' ', '_')
            properties = self.food_properties.get(food_key, {
                'guna': GunaType.NEUTRAL,
                'virya': ViryaType.NEUTRAL,
                'intensity': 0.3
            })
            
            return {
                'food': food_name,
                'guna': properties['guna'].value,
                'virya': properties['virya'].value,
                'intensity': properties['intensity'],
                'description': self._get_guna_description(properties['guna'], properties['virya'], properties['intensity'])
            }
            
        except Exception as e:
            logger.error("Guna calculation failed", error=str(e), food=food_name)
            return self._default_guna_properties(food_name)
    
    def analyze_meal_guna(self, foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze guna properties of a complete meal"""
        try:
            meal_properties = []
            total_heating = 0
            total_cooling = 0
            total_neutral = 0
            
            for food in foods:
                food_name = food.get('name', '')
                quantity = food.get('quantity', 100)
                
                guna_data = self.calculate_food_guna(food_name)
                meal_properties.append(guna_data)
                
                # Weight by quantity
                intensity = guna_data['intensity'] * (quantity / 100)
                
                if guna_data['virya'] == 'heating':
                    total_heating += intensity
                elif guna_data['virya'] == 'cooling':
                    total_cooling += intensity
                else:
                    total_neutral += intensity
            
            # Determine overall meal properties
            total_energy = total_heating + total_cooling + total_neutral
            if total_energy > 0:
                heating_ratio = total_heating / total_energy
                cooling_ratio = total_cooling / total_energy
            else:
                heating_ratio = cooling_ratio = 0.33
            
            # Determine dominant energy
            if heating_ratio > 0.5:
                dominant_energy = 'heating'
            elif cooling_ratio > 0.5:
                dominant_energy = 'cooling'
            else:
                dominant_energy = 'neutral'
            
            return {
                'foods': meal_properties,
                'overall_energy': dominant_energy,
                'heating_ratio': heating_ratio,
                'cooling_ratio': cooling_ratio,
                'neutral_ratio': 1 - heating_ratio - cooling_ratio,
                'balance_score': self._calculate_balance_score(heating_ratio, cooling_ratio),
                'recommendations': self._get_meal_guna_recommendations(dominant_energy, heating_ratio, cooling_ratio)
            }
            
        except Exception as e:
            logger.error("Meal guna analysis failed", error=str(e))
            return {'error': 'Failed to analyze meal guna properties'}
    
    def recommend_guna_for_dosha(self, dosha_scores: Dict[str, float], current_gunas: List[str]) -> Dict[str, Any]:
        """Recommend guna properties based on dosha constitution"""
        try:
            primary_dosha = max(dosha_scores, key=dosha_scores.get)
            preferences = self.dosha_guna_preferences[primary_dosha]
            
            # Analyze current guna balance
            current_analysis = self._analyze_current_gunas(current_gunas)
            
            # Generate recommendations
            recommendations = {
                'primary_dosha': primary_dosha,
                'preferred_gunas': [g.value for g in preferences['preferred']],
                'avoid_gunas': [g.value for g in preferences['avoid']],
                'current_balance': current_analysis,
                'suggestions': self._get_dosha_guna_suggestions(primary_dosha, current_analysis),
                'food_recommendations': self._get_dosha_food_recommendations(primary_dosha)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error("Dosha guna recommendation failed", error=str(e))
            return {'error': 'Failed to generate guna recommendations'}
    
    def _get_guna_description(self, guna: GunaType, virya: ViryaType, intensity: float) -> str:
        """Get human-readable description of guna properties"""
        intensity_desc = "mildly" if intensity < 0.4 else "moderately" if intensity < 0.7 else "strongly"
        
        if virya == ViryaType.HEATING:
            return f"{intensity_desc} heating, good for cold conditions and Vata/Kapha constitution"
        elif virya == ViryaType.COOLING:
            return f"{intensity_desc} cooling, good for hot conditions and Pitta constitution"
        else:
            return f"neutral energy, suitable for all constitutions"
    
    def _calculate_balance_score(self, heating_ratio: float, cooling_ratio: float) -> float:
        """Calculate how balanced the meal is"""
        # Ideal balance is around 0.3-0.4 for each
        ideal_heating = 0.35
        ideal_cooling = 0.35
        
        heating_deviation = abs(heating_ratio - ideal_heating)
        cooling_deviation = abs(cooling_ratio - ideal_cooling)
        
        # Score based on deviation from ideal (lower deviation = higher score)
        max_deviation = 0.5
        score = 1 - ((heating_deviation + cooling_deviation) / (2 * max_deviation))
        return max(0, min(1, score))
    
    def _analyze_current_gunas(self, current_gunas: List[str]) -> Dict[str, Any]:
        """Analyze current guna distribution"""
        guna_counts = {}
        for guna in current_gunas:
            guna_counts[guna] = guna_counts.get(guna, 0) + 1
        
        total = len(current_gunas)
        if total > 0:
            return {
                'distribution': {guna: count/total for guna, count in guna_counts.items()},
                'dominant_guna': max(guna_counts, key=guna_counts.get) if guna_counts else 'neutral',
                'diversity': len(guna_counts)
            }
        else:
            return {'distribution': {}, 'dominant_guna': 'neutral', 'diversity': 0}
    
    def _get_meal_guna_recommendations(self, dominant_energy: str, heating_ratio: float, cooling_ratio: float) -> Dict[str, Any]:
        """Get recommendations for meal guna balance"""
        if dominant_energy == 'heating' and heating_ratio > 0.7:
            return {
                'status': 'Too heating',
                'message': 'Meal is too heating, add cooling foods',
                'suggestions': ['Add cucumber', 'Include mint', 'Use coconut', 'Add yogurt']
            }
        elif dominant_energy == 'cooling' and cooling_ratio > 0.7:
            return {
                'status': 'Too cooling',
                'message': 'Meal is too cooling, add heating foods',
                'suggestions': ['Add ginger', 'Use spices', 'Include garlic', 'Add warm foods']
            }
        else:
            return {
                'status': 'Balanced',
                'message': 'Meal has good guna balance',
                'suggestions': ['Maintain current balance', 'Consider seasonal adjustments']
            }
    
    def _get_dosha_guna_suggestions(self, dosha: str, current_analysis: Dict[str, Any]) -> List[str]:
        """Get specific guna suggestions for dosha"""
        suggestions = {
            'vata': [
                'Include more heating foods to balance cold nature',
                'Use warming spices like ginger and cinnamon',
                'Avoid excessive cold foods',
                'Prefer cooked over raw foods'
            ],
            'pitta': [
                'Include more cooling foods to balance hot nature',
                'Use cooling herbs like mint and coriander',
                'Avoid excessive heating foods',
                'Include fresh, cooling foods'
            ],
            'kapha': [
                'Include heating foods to stimulate sluggish nature',
                'Use warming spices and pungent foods',
                'Avoid heavy, cold foods',
                'Prefer light, warm, dry foods'
            ]
        }
        
        return suggestions.get(dosha, ['Follow balanced approach'])
    
    def _get_dosha_food_recommendations(self, dosha: str) -> Dict[str, List[str]]:
        """Get specific food recommendations for dosha"""
        recommendations = {
            'vata': {
                'heating': ['ginger', 'garlic', 'cinnamon', 'cardamom', 'cumin'],
                'neutral': ['rice', 'ghee', 'milk', 'wheat'],
                'avoid': ['cucumber', 'watermelon', 'mint', 'coconut']
            },
            'pitta': {
                'cooling': ['mint', 'coconut', 'cucumber', 'watermelon', 'coriander'],
                'neutral': ['rice', 'ghee', 'milk'],
                'avoid': ['ginger', 'garlic', 'chili', 'black_pepper']
            },
            'kapha': {
                'heating': ['ginger', 'garlic', 'chili', 'black_pepper', 'cinnamon'],
                'avoid': ['milk', 'coconut', 'cucumber', 'heavy foods']
            }
        }
        
        return recommendations.get(dosha, {'neutral': ['balanced foods']})
    
    def _default_guna_properties(self, food_name: str) -> Dict[str, Any]:
        """Return default guna properties for unknown foods"""
        return {
            'food': food_name,
            'guna': 'neutral',
            'virya': 'neutral',
            'intensity': 0.3,
            'description': 'Unknown food, assume neutral properties'
        }
