"""
Unit tests for ML models
"""

import pytest
import numpy as np
from src.services.ml.dosha_classifier import DoshaClassifier
from src.services.ml.compat_gnn import CompatibilityGNN
from src.services.ml.rasa_recommender import RasaRecommender
from src.services.ml.nutrient_calculator import NutrientCalculator
from src.services.ml.agni_predictor import AgniPredictor

class TestDoshaClassifier:
    """Test Dosha Classifier"""
    
    def test_analyze_patient_features(self):
        """Test patient feature analysis"""
        classifier = DoshaClassifier()
        
        patient_data = {
            'age': 30,
            'gender': 'male',
            'body_type': 'medium',
            'skin_type': 'normal',
            'appetite': 'normal',
            'digestion': 'normal',
            'sleep_pattern': 'normal',
            'energy_level': 'moderate',
            'mood_stability': 'stable',
            'weather_preference': 'moderate',
            'exercise_tolerance': 'moderate'
        }
        
        features = classifier.analyze_patient_features(patient_data)
        assert len(features) == 12  # Should match feature_names length
        assert all(0 <= f <= 1 for f in features)  # All features should be normalized
    
    def test_predict_dosha_default(self):
        """Test dosha prediction with default model"""
        classifier = DoshaClassifier()
        
        # Test with default features when model is not available
        features = (0.3, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        result = classifier.predict_dosha(features)
        
        assert 'primary_dosha' in result
        assert 'dosha_scores' in result
        assert 'confidence' in result
        assert 'recommendations' in result
        assert result['primary_dosha'] in ['vata', 'pitta', 'kapha']

class TestCompatibilityGNN:
    """Test Compatibility GNN"""
    
    def test_check_compatibility_default(self):
        """Test compatibility check with default model"""
        gnn = CompatibilityGNN()
        
        result = gnn.check_compatibility('rice', 'dal')
        
        assert 'compatible' in result
        assert 'score' in result
        assert 'explanation' in result
        assert 'recommendations' in result
        assert isinstance(result['compatible'], bool)
        assert 0 <= result['score'] <= 1
    
    def test_check_meal_compatibility(self):
        """Test meal compatibility check"""
        gnn = CompatibilityGNN()
        
        foods = ['rice', 'dal', 'vegetables']
        result = gnn.check_meal_compatibility(foods)
        
        assert 'compatible' in result
        assert 'score' in result
        assert 'conflicts' in result
        assert 'recommendations' in result
        assert isinstance(result['compatible'], bool)

class TestRasaRecommender:
    """Test Rasa Recommender"""
    
    def test_recommend_rasas(self):
        """Test rasa recommendations"""
        recommender = RasaRecommender()
        
        dosha_scores = {'vata': 0.4, 'pitta': 0.35, 'kapha': 0.25}
        result = recommender.recommend_rasas(dosha_scores)
        
        assert 'primary_dosha' in result
        assert 'recommended_rasas' in result
        assert 'avoid_rasas' in result
        assert 'balance_score' in result
        assert 'recommendations' in result
        assert 'food_suggestions' in result
    
    def test_analyze_meal_rasas(self):
        """Test meal rasa analysis"""
        recommender = RasaRecommender()
        
        foods = [
            {'ayurvedic_properties': {'rasa': ['sweet', 'sour']}},
            {'ayurvedic_properties': {'rasa': ['pungent', 'bitter']}}
        ]
        
        result = recommender.analyze_meal_rasas(foods)
        
        assert 'rasa_composition' in result
        assert 'rasa_balance' in result
        assert 'balance_analysis' in result
        assert 'recommendations' in result

class TestNutrientCalculator:
    """Test Nutrient Calculator"""
    
    def test_calculate_meal_nutrition(self):
        """Test meal nutrition calculation"""
        calculator = NutrientCalculator()
        
        foods = [
            {'name': 'rice', 'quantity': 100, 'unit': 'grams'},
            {'name': 'dal', 'quantity': 50, 'unit': 'grams'}
        ]
        
        result = calculator.calculate_meal_nutrition(foods)
        
        assert 'calories' in result
        assert 'protein' in result
        assert 'carbs' in result
        assert 'fat' in result
        assert 'fiber' in result
        assert all(isinstance(v, (int, float)) for v in result.values())
    
    def test_analyze_diet_balance(self):
        """Test diet balance analysis"""
        calculator = NutrientCalculator()
        
        daily_meals = [
            {'foods': [{'name': 'rice', 'quantity': 100, 'unit': 'grams'}]},
            {'foods': [{'name': 'dal', 'quantity': 50, 'unit': 'grams'}]}
        ]
        
        patient_info = {'age': 30, 'gender': 'male'}
        
        result = calculator.analyze_diet_balance(daily_meals, patient_info)
        
        assert 'daily_totals' in result
        assert 'daily_requirements' in result
        assert 'balance_scores' in result
        assert 'overall_balance' in result
        assert 'recommendations' in result
        assert 'status' in result

class TestAgniPredictor:
    """Test Agni Predictor LSTM Model"""
    
    def test_predict_agni_trend(self):
        """Test Agni trend prediction"""
        predictor = AgniPredictor()
        
        historical_data = [
            {
                'appetite_score': 7,
                'digestion_quality': 6,
                'bowel_movement_frequency': 1,
                'energy_level': 7,
                'sleep_quality': 6,
                'stress_level': 4,
                'meal_timing_consistency': True,
                'water_intake': 2.5,
                'exercise_frequency': 3,
                'weather_impact': 0
            }
        ] * 7  # 7 days of data
        
        result = predictor.predict_agni_trend(historical_data)
        
        assert 'agni_score' in result
        assert 'trend_direction' in result
        assert 'confidence' in result
        assert 'prediction_date' in result
        assert 'recommendations' in result
        assert 'next_week_forecast' in result
        assert 0 <= result['agni_score'] <= 1
        assert result['trend_direction'] in ['improving', 'declining', 'stable']
    
    def test_assess_daily_agni(self):
        """Test daily Agni assessment"""
        predictor = AgniPredictor()
        
        daily_metrics = {
            'appetite_score': 8,
            'digestion_quality': 7,
            'bowel_movement_frequency': 1,
            'energy_level': 8,
            'sleep_quality': 7,
            'stress_level': 3,
            'meal_timing_consistency': True,
            'water_intake': 2.0,
            'exercise_frequency': 4,
            'weather_impact': 1
        }
        
        result = predictor.assess_daily_agni(daily_metrics)
        
        assert 'agni_score' in result
        assert 'agni_level' in result
        assert 'strength' in result
        assert 'recommendations' in result
        assert 'improvement_areas' in result
        assert 'assessment_date' in result
        assert 0 <= result['agni_score'] <= 1
        assert result['agni_level'] in ['excellent', 'good', 'moderate', 'poor', 'very_poor']
        assert result['strength'] in ['strong', 'moderate', 'weak']
    
    def test_predict_meal_agni_impact(self):
        """Test meal Agni impact prediction"""
        predictor = AgniPredictor()
        
        meal_data = {
            'heating_properties': 0.7,
            'digestibility': 0.8,
            'meal_size': 0.6,
            'meal_timing': 0.9,
            'spice_level': 0.5
        }
        
        current_agni = 0.6
        
        result = predictor.predict_agni_impact_of_meal(meal_data, current_agni)
        
        assert 'impact_score' in result
        assert 'agni_change' in result
        assert 'impact_level' in result
        assert 'recommendations' in result
        assert 'timing_advice' in result
        assert 0 <= result['impact_score'] <= 1
        assert 0 <= result['agni_change'] <= 1
        assert result['impact_level'] in ['high_positive', 'positive', 'neutral', 'negative', 'high_negative']
