"""
Dosha Classifier Service
Integrates with the existing dosha_classifier.pkl model
"""

import pickle
import numpy as np
import structlog
from typing import Dict, List, Any
from functools import lru_cache
import os

logger = structlog.get_logger()

class DoshaClassifier:
    """Dosha (Prakriti) classification service"""
    
    def __init__(self, model_path: str = "model/dosha_classifier.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained dosha classifier model"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found: {self.model_path}")
                return
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Handle different model formats
            if isinstance(model_data, dict):
                self.model = model_data.get('model')
                self.feature_names = model_data.get('feature_names', [])
            else:
                self.model = model_data
                # Default feature names for dosha classification
                self.feature_names = [
                    'age', 'gender', 'body_type', 'skin_type', 'hair_type',
                    'appetite', 'digestion', 'sleep_pattern', 'energy_level',
                    'mood_stability', 'weather_preference', 'exercise_tolerance'
                ]
            
            logger.info("Dosha classifier model loaded successfully")
            
        except Exception as e:
            logger.error("Failed to load dosha classifier model", error=str(e))
            self.model = None
    
    @lru_cache(maxsize=128)
    def predict_dosha(self, features: tuple) -> Dict[str, Any]:
        """Predict dosha constitution from patient features"""
        if self.model is None:
            logger.warning("Dosha classifier model not available")
            return self._default_dosha_prediction()
        
        try:
            # Convert tuple back to numpy array
            features_array = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(features_array)[0]
            probabilities = self.model.predict_proba(features_array)[0]
            
            # Map to dosha names
            dosha_names = ['vata', 'pitta', 'kapha']
            dosha_scores = dict(zip(dosha_names, probabilities))
            
            # Determine primary dosha
            primary_dosha = dosha_names[np.argmax(probabilities)]
            
            return {
                'primary_dosha': primary_dosha,
                'dosha_scores': dosha_scores,
                'confidence': float(np.max(probabilities)),
                'recommendations': self._get_dosha_recommendations(primary_dosha, dosha_scores)
            }
            
        except Exception as e:
            logger.error("Dosha prediction failed", error=str(e))
            return self._default_dosha_prediction()
    
    def _default_dosha_prediction(self) -> Dict[str, Any]:
        """Return default dosha prediction when model is unavailable"""
        return {
            'primary_dosha': 'vata',
            'dosha_scores': {'vata': 0.4, 'pitta': 0.35, 'kapha': 0.25},
            'confidence': 0.5,
            'recommendations': {
                'diet': 'Warm, moist, grounding foods',
                'lifestyle': 'Regular routine, gentle exercise',
                'avoid': 'Cold, dry, raw foods'
            }
        }
    
    def _get_dosha_recommendations(self, primary_dosha: str, dosha_scores: Dict[str, float]) -> Dict[str, str]:
        """Get personalized recommendations based on dosha analysis"""
        recommendations = {
            'vata': {
                'diet': 'Warm, cooked, moist foods. Sweet, sour, and salty tastes.',
                'lifestyle': 'Regular routine, gentle exercise, adequate rest.',
                'avoid': 'Cold, dry, raw foods. Excessive travel and irregular schedule.'
            },
            'pitta': {
                'diet': 'Cooling, sweet, bitter, and astringent foods.',
                'lifestyle': 'Moderate exercise, avoid excessive heat.',
                'avoid': 'Hot, spicy, sour foods. Excessive sun exposure.'
            },
            'kapha': {
                'diet': 'Light, warm, dry foods. Pungent, bitter, astringent tastes.',
                'lifestyle': 'Regular vigorous exercise, variety in routine.',
                'avoid': 'Heavy, oily, sweet foods. Excessive sleep and inactivity.'
            }
        }
        
        base_rec = recommendations.get(primary_dosha, recommendations['vata'])
        
        # Adjust based on secondary dosha
        secondary_dosha = max(dosha_scores, key=dosha_scores.get)
        if secondary_dosha != primary_dosha and dosha_scores[secondary_dosha] > 0.3:
            # Blend recommendations
            base_rec['note'] = f"Balanced {primary_dosha}-{secondary_dosha} constitution"
        
        return base_rec
    
    def analyze_patient_features(self, patient_data: Dict[str, Any]) -> tuple:
        """Convert patient data to feature vector for prediction"""
        # Map patient data to numerical features
        feature_mapping = {
            'age': lambda x: min(x / 100.0, 1.0),  # Normalize age
            'gender': lambda x: 1.0 if x.lower() == 'male' else 0.0,
            'body_type': lambda x: {'thin': 0.0, 'medium': 0.5, 'heavy': 1.0}.get(x.lower(), 0.5),
            'skin_type': lambda x: {'dry': 0.0, 'normal': 0.5, 'oily': 1.0}.get(x.lower(), 0.5),
            'hair_type': lambda x: {'dry': 0.0, 'normal': 0.5, 'oily': 1.0}.get(x.lower(), 0.5),
            'appetite': lambda x: {'low': 0.0, 'normal': 0.5, 'high': 1.0}.get(x.lower(), 0.5),
            'digestion': lambda x: {'slow': 0.0, 'normal': 0.5, 'fast': 1.0}.get(x.lower(), 0.5),
            'sleep_pattern': lambda x: {'light': 0.0, 'normal': 0.5, 'deep': 1.0}.get(x.lower(), 0.5),
            'energy_level': lambda x: {'low': 0.0, 'moderate': 0.5, 'high': 1.0}.get(x.lower(), 0.5),
            'mood_stability': lambda x: {'unstable': 0.0, 'moderate': 0.5, 'stable': 1.0}.get(x.lower(), 0.5),
            'weather_preference': lambda x: {'cold': 0.0, 'moderate': 0.5, 'warm': 1.0}.get(x.lower(), 0.5),
            'exercise_tolerance': lambda x: {'low': 0.0, 'moderate': 0.5, 'high': 1.0}.get(x.lower(), 0.5)
        }
        
        features = []
        for feature_name in self.feature_names:
            if feature_name in patient_data:
                try:
                    value = feature_mapping[feature_name](patient_data[feature_name])
                    features.append(value)
                except (KeyError, TypeError):
                    features.append(0.5)  # Default neutral value
            else:
                features.append(0.5)  # Default neutral value
        
        return tuple(features)
