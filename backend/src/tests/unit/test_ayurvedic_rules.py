"""
Unit tests for Ayurvedic calculation rules
"""

import pytest
from src.services.ayurvedic.guna_calculator import GunaCalculator, GunaType, ViryaType
from src.services.ayurvedic.viruddha_ahara import ViruddhaAharaDetector
from src.services.ayurvedic.agni_analyzer import AgniAnalyzer, AgniType

class TestGunaCalculator:
    """Test Guna Calculator"""
    
    def test_calculate_food_guna(self):
        """Test food guna calculation"""
        calculator = GunaCalculator()
        
        result = calculator.calculate_food_guna('ginger')
        
        assert 'food' in result
        assert 'guna' in result
        assert 'virya' in result
        assert 'intensity' in result
        assert 'description' in result
        assert result['guna'] in ['hot', 'cold', 'neutral']
        assert result['virya'] in ['heating', 'cooling', 'neutral']
        assert 0 <= result['intensity'] <= 1
    
    def test_analyze_meal_guna(self):
        """Test meal guna analysis"""
        calculator = GunaCalculator()
        
        foods = [
            {'name': 'ginger', 'quantity': 10},
            {'name': 'coconut', 'quantity': 50}
        ]
        
        result = calculator.analyze_meal_guna(foods)
        
        assert 'foods' in result
        assert 'overall_energy' in result
        assert 'heating_ratio' in result
        assert 'cooling_ratio' in result
        assert 'balance_score' in result
        assert 'recommendations' in result
        assert result['overall_energy'] in ['heating', 'cooling', 'neutral']
    
    def test_recommend_guna_for_dosha(self):
        """Test guna recommendations for dosha"""
        calculator = GunaCalculator()
        
        dosha_scores = {'vata': 0.4, 'pitta': 0.35, 'kapha': 0.25}
        current_gunas = ['hot', 'neutral']
        
        result = calculator.recommend_guna_for_dosha(dosha_scores, current_gunas)
        
        assert 'primary_dosha' in result
        assert 'preferred_gunas' in result
        assert 'avoid_gunas' in result
        assert 'current_balance' in result
        assert 'suggestions' in result
        assert 'food_recommendations' in result

class TestViruddhaAharaDetector:
    """Test Viruddha Ahara Detector"""
    
    def test_check_incompatibility(self):
        """Test food incompatibility check"""
        detector = ViruddhaAharaDetector()
        
        result = detector.check_incompatibility('milk', 'fish')
        
        assert 'incompatible' in result
        assert 'conflicts' in result
        assert 'severity' in result
        assert 'recommendations' in result
        assert isinstance(result['incompatible'], bool)
        assert result['severity'] in ['low', 'medium', 'high', 'none']
    
    def test_check_meal_incompatibilities(self):
        """Test meal incompatibility check"""
        detector = ViruddhaAharaDetector()
        
        foods = ['milk', 'fish', 'rice']
        result = detector.check_meal_incompatibilities(foods)
        
        assert 'incompatible_pairs' in result
        assert 'total_conflicts' in result
        assert 'incompatibility_ratio' in result
        assert 'severity' in result
        assert 'recommendations' in result
        assert 'safe_to_eat' in result
        assert isinstance(result['safe_to_eat'], bool)
    
    def test_suggest_alternatives(self):
        """Test alternative suggestions"""
        detector = ViruddhaAharaDetector()
        
        incompatible_foods = [('milk', 'fish')]
        result = detector.suggest_alternatives(incompatible_foods)
        
        assert 'alternatives' in result
        assert 'general_advice' in result
        assert len(result['alternatives']) > 0

class TestAgniAnalyzer:
    """Test Agni Analyzer"""
    
    def test_analyze_agni(self):
        """Test Agni analysis"""
        analyzer = AgniAnalyzer()
        
        patient_data = {
            'symptoms': {
                'appetite': 'regular',
                'digestion': 'smooth',
                'bowel_movement': 'regular',
                'energy_level': 'stable'
            },
            'dietary_habits': {
                'appetite': 'regular',
                'digestion': 'smooth',
                'bowel_movement': 'regular',
                'energy_level': 'stable'
            },
            'prakriti_analysis': {'vata': 0.4, 'pitta': 0.35, 'kapha': 0.25}
        }
        
        result = analyzer.analyze_agni(patient_data)
        
        assert 'agni_type' in result
        assert 'agni_scores' in result
        assert 'strength' in result
        assert 'recommendations' in result
        assert 'balancing_strategies' in result
        assert 'food_recommendations' in result
        assert result['agni_type'] in ['vishama', 'tikshna', 'manda', 'sama']
        assert result['strength'] in ['weak', 'moderate', 'strong']
    
    def test_assess_meal_agni_impact(self):
        """Test meal Agni impact assessment"""
        analyzer = AgniAnalyzer()
        
        meal_foods = [
            {'name': 'ginger', 'quantity': 10},
            {'name': 'rice', 'quantity': 100}
        ]
        
        agni_type = AgniType.SAMA
        
        result = analyzer.assess_meal_agni_impact(meal_foods, agni_type)
        
        assert 'overall_impact' in result
        assert 'food_impacts' in result
        assert 'recommendations' in result
        assert result['overall_impact'] in ['positive', 'negative', 'neutral']
    
    def test_suggest_agni_balancing_foods(self):
        """Test Agni balancing food suggestions"""
        analyzer = AgniAnalyzer()
        
        agni_type = AgniType.VISHAMA
        dosha_scores = {'vata': 0.4, 'pitta': 0.35, 'kapha': 0.25}
        
        result = analyzer.suggest_agni_balancing_foods(agni_type, dosha_scores)
        
        assert 'agni_type' in result
        assert 'primary_dosha' in result
        assert 'beneficial_foods' in result
        assert 'avoid_foods' in result
        assert 'timing_advice' in result
        assert 'dosha_specific_advice' in result
        assert len(result['beneficial_foods']) > 0
