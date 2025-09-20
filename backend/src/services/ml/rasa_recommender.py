"""
Rasa (Six Tastes) Recommender Service
"""

import numpy as np
import structlog
from typing import Dict, List, Any
from functools import lru_cache

logger = structlog.get_logger()

class RasaRecommender:
    """Six tastes (Rasa) recommendation service"""
    
    def __init__(self):
        self.rasa_properties = {
            'sweet': {'elements': ['earth', 'water'], 'gunas': ['heavy', 'cooling', 'moist']},
            'sour': {'elements': ['earth', 'fire'], 'gunas': ['light', 'heating', 'moist']},
            'salty': {'elements': ['water', 'fire'], 'gunas': ['heavy', 'heating', 'moist']},
            'pungent': {'elements': ['fire', 'air'], 'gunas': ['light', 'heating', 'dry']},
            'bitter': {'elements': ['air', 'space'], 'gunas': ['light', 'cooling', 'dry']},
            'astringent': {'elements': ['air', 'earth'], 'gunas': ['light', 'cooling', 'dry']}
        }
        
        self.dosha_rasa_balance = {
            'vata': {'increase': ['sweet', 'sour', 'salty'], 'decrease': ['pungent', 'bitter', 'astringent']},
            'pitta': {'increase': ['sweet', 'bitter', 'astringent'], 'decrease': ['sour', 'salty', 'pungent']},
            'kapha': {'increase': ['pungent', 'bitter', 'astringent'], 'decrease': ['sweet', 'sour', 'salty']}
        }
    
    def recommend_rasas(self, dosha_scores: Dict[str, float], current_rasas: List[str] = None) -> Dict[str, Any]:
        """Recommend optimal rasa balance based on dosha constitution"""
        try:
            # Determine primary dosha
            primary_dosha = max(dosha_scores, key=dosha_scores.get)
            
            # Get rasa recommendations for primary dosha
            recommended_rasas = self.dosha_rasa_balance[primary_dosha]['increase']
            avoid_rasas = self.dosha_rasa_balance[primary_dosha]['decrease']
            
            # Calculate rasa balance score
            balance_score = self._calculate_rasa_balance(current_rasas or [], recommended_rasas, avoid_rasas)
            
            return {
                'primary_dosha': primary_dosha,
                'recommended_rasas': recommended_rasas,
                'avoid_rasas': avoid_rasas,
                'balance_score': balance_score,
                'recommendations': self._get_rasa_recommendations(primary_dosha, balance_score),
                'food_suggestions': self._get_rasa_food_suggestions(recommended_rasas)
            }
            
        except Exception as e:
            logger.error("Rasa recommendation failed", error=str(e))
            return self._default_rasa_recommendation()
    
    def analyze_meal_rasas(self, foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze rasa composition of a meal"""
        try:
            meal_rasas = []
            for food in foods:
                food_rasas = food.get('ayurvedic_properties', {}).get('rasa', [])
                meal_rasas.extend(food_rasas)
            
            # Count rasa frequencies
            rasa_counts = {}
            for rasa in meal_rasas:
                rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
            
            # Calculate balance
            total_rasas = len(meal_rasas)
            rasa_balance = {rasa: count/total_rasas for rasa, count in rasa_counts.items()}
            
            return {
                'rasa_composition': rasa_counts,
                'rasa_balance': rasa_balance,
                'balance_analysis': self._analyze_rasa_balance(rasa_balance),
                'recommendations': self._get_meal_rasa_recommendations(rasa_balance)
            }
            
        except Exception as e:
            logger.error("Meal rasa analysis failed", error=str(e))
            return {'error': 'Failed to analyze meal rasas'}
    
    def _calculate_rasa_balance(self, current_rasas: List[str], recommended: List[str], avoid: List[str]) -> float:
        """Calculate how well current rasas match recommendations"""
        if not current_rasas:
            return 0.5  # Neutral score for empty list
        
        recommended_count = sum(1 for rasa in current_rasas if rasa in recommended)
        avoid_count = sum(1 for rasa in current_rasas if rasa in avoid)
        
        # Score: (recommended - avoid) / total
        score = (recommended_count - avoid_count) / len(current_rasas)
        return max(0, min(1, (score + 1) / 2))  # Normalize to 0-1
    
    def _analyze_rasa_balance(self, rasa_balance: Dict[str, float]) -> Dict[str, Any]:
        """Analyze the balance of rasas in a meal"""
        dominant_rasa = max(rasa_balance, key=rasa_balance.get) if rasa_balance else None
        dominant_percentage = rasa_balance.get(dominant_rasa, 0) if dominant_rasa else 0
        
        # Check for imbalance
        is_balanced = len(rasa_balance) >= 3 and dominant_percentage < 0.6
        is_dominant = dominant_percentage > 0.7
        
        return {
            'dominant_rasa': dominant_rasa,
            'dominant_percentage': dominant_percentage,
            'is_balanced': is_balanced,
            'is_dominant': is_dominant,
            'rasa_diversity': len(rasa_balance)
        }
    
    def _get_rasa_recommendations(self, primary_dosha: str, balance_score: float) -> Dict[str, str]:
        """Get personalized rasa recommendations"""
        recommendations = {
            'vata': {
                'good': 'Focus on sweet, sour, and salty tastes to balance Vata',
                'moderate': 'Include some sweet and sour foods to pacify Vata',
                'poor': 'Increase sweet, sour, and salty foods; reduce pungent, bitter, astringent'
            },
            'pitta': {
                'good': 'Good balance of sweet, bitter, and astringent tastes',
                'moderate': 'Include more sweet and bitter foods to cool Pitta',
                'poor': 'Focus on sweet, bitter, astringent; avoid sour, salty, pungent'
            },
            'kapha': {
                'good': 'Good use of pungent, bitter, and astringent tastes',
                'moderate': 'Include more pungent and bitter foods to stimulate Kapha',
                'poor': 'Increase pungent, bitter, astringent; reduce sweet, sour, salty'
            }
        }
        
        if balance_score > 0.7:
            level = 'good'
        elif balance_score > 0.4:
            level = 'moderate'
        else:
            level = 'poor'
        
        return {
            'dosha_advice': recommendations[primary_dosha][level],
            'balance_score': balance_score,
            'priority': 'high' if balance_score < 0.4 else 'medium' if balance_score < 0.7 else 'low'
        }
    
    def _get_rasa_food_suggestions(self, recommended_rasas: List[str]) -> Dict[str, List[str]]:
        """Get food suggestions for each recommended rasa"""
        rasa_foods = {
            'sweet': ['rice', 'wheat', 'milk', 'ghee', 'dates', 'honey', 'sweet fruits'],
            'sour': ['lemon', 'lime', 'tamarind', 'yogurt', 'fermented foods', 'citrus fruits'],
            'salty': ['sea salt', 'rock salt', 'seaweed', 'pickles', 'salted nuts'],
            'pungent': ['ginger', 'garlic', 'onion', 'chili', 'black pepper', 'mustard'],
            'bitter': ['bitter gourd', 'neem', 'turmeric', 'coffee', 'dark leafy greens'],
            'astringent': ['pomegranate', 'green tea', 'unripe banana', 'lentils', 'cabbage']
        }
        
        return {rasa: rasa_foods.get(rasa, []) for rasa in recommended_rasas}
    
    def _get_meal_rasa_recommendations(self, rasa_balance: Dict[str, float]) -> Dict[str, Any]:
        """Get recommendations for meal rasa balance"""
        analysis = self._analyze_rasa_balance(rasa_balance)
        
        if analysis['is_balanced']:
            return {
                'status': 'Good',
                'message': 'Meal has good rasa balance',
                'suggestions': []
            }
        elif analysis['is_dominant']:
            return {
                'status': 'Imbalanced',
                'message': f'Too much {analysis["dominant_rasa"]} taste',
                'suggestions': [
                    f'Reduce {analysis["dominant_rasa"]} foods',
                    'Add more variety of tastes',
                    'Include complementary rasas'
                ]
            }
        else:
            return {
                'status': 'Needs variety',
                'message': 'Meal needs more rasa diversity',
                'suggestions': [
                    'Include more different tastes',
                    'Add herbs and spices',
                    'Consider seasonal foods'
                ]
            }
    
    def _default_rasa_recommendation(self) -> Dict[str, Any]:
        """Return default rasa recommendation"""
        return {
            'primary_dosha': 'vata',
            'recommended_rasas': ['sweet', 'sour', 'salty'],
            'avoid_rasas': ['pungent', 'bitter', 'astringent'],
            'balance_score': 0.5,
            'recommendations': {
                'dosha_advice': 'Follow traditional Ayurvedic taste principles',
                'balance_score': 0.5,
                'priority': 'medium'
            },
            'food_suggestions': {
                'sweet': ['rice', 'milk', 'ghee'],
                'sour': ['lemon', 'yogurt'],
                'salty': ['sea salt', 'seaweed']
            }
        }
